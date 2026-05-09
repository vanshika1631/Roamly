import structlog
from arq import create_pool
from arq.connections import RedisSettings
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import ItineraryRecord, TEBProfile, Trip
from app.db.session import AsyncSessionLocal
from app.modules.auditor import run_bias_audit
from app.modules.generator import generate_itinerary
from app.modules.solver import get_feasibility
from app.schemas import TravelEmotionalBrief, TripConstraints

log = structlog.get_logger()

from app.modules.ingestion import ingest_destination

async def ingest_destination_job(ctx: dict, destination: str, country: str = "") -> None:
    """ARQ job to ingest places for a destination."""
    log.info("ingest_job.start", destination=destination)
    count = await ingest_destination(destination, country)
    log.info("ingest_job.complete", destination=destination, count=count)

async def generate_itinerary_job(ctx: dict, trip_id: str) -> None:
    """
    Main ARQ worker job. Runs the full pipeline:
    solve → generate → audit → save.
    """
    log.info("itinerary_job.start", trip_id=trip_id)

    async with AsyncSessionLocal() as db:
        # 1. Load trip
        trip = await db.get(Trip, trip_id)
        if not trip:
            log.error("itinerary_job.trip_not_found", trip_id=trip_id)
            return

        await _set_status(db, trip, "generating")

        constraints = TripConstraints.model_validate(trip.constraints_json)
        teb = TravelEmotionalBrief.model_validate(trip.teb_snapshot) if trip.teb_snapshot else None

        if not teb:
            result = await db.execute(
                select(TEBProfile)
                .where(TEBProfile.user_id == trip.user_id)
                .order_by(TEBProfile.version.desc())
                .limit(1)
            )
            teb_profile = result.scalar_one_or_none()
            if teb_profile:
                trip.teb_snapshot = teb_profile.teb_json
                await db.commit()
                teb = TravelEmotionalBrief.model_validate(teb_profile.teb_json)
            else:
                log.error("itinerary_job.no_teb", trip_id=trip_id)
                await _set_status(db, trip, "failed")
                return

        try:
            # 2. Constraint solving
            feasibility = await get_feasibility(constraints)
            if not feasibility.feasible:
                log.warning("itinerary_job.infeasible", suggestion=feasibility.relaxed_suggestion)
                await _set_status(db, trip, "failed")
                return

            # 3. Itinerary generation
            # itinerary = await generate_itinerary(teb, feasibility, constraints)
            
            # In generate_itinerary_job, update the generation call:
            itinerary = await generate_itinerary(teb, feasibility, constraints, db=db)

            # 4. Bias audit
            await _set_status(db, trip, "auditing")
            audited_itinerary, audit_log = await run_bias_audit(itinerary)

            # 5. Save
            record = ItineraryRecord(
                trip_id=trip_id,
                itinerary_json=audited_itinerary.model_dump(),
                audit_log=audit_log,
            )
            db.add(record)
            await _set_status(db, trip, "ready")
            await db.commit()

            log.info("itinerary_job.complete", trip_id=trip_id)

        except Exception:
            log.exception("itinerary_job.failed", trip_id=trip_id)
            await _set_status(db, trip, "failed")
            await db.commit()
            raise


async def _set_status(db: AsyncSession, trip: Trip, status: str) -> None:
    trip.status = status
    await db.commit()


class WorkerSettings:
    redis_settings = RedisSettings.from_dsn(settings.redis_url)
    functions = [generate_itinerary_job, ingest_destination_job]
    max_jobs = 10
    job_timeout = 300  # 5 minutes max per job
