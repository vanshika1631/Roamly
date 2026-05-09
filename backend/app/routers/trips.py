import structlog
from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.ingestion import destination_has_places
import asyncio
from app.config import settings
from app.db.models import ItineraryRecord, TEBProfile, Trip
from app.db.session import get_db
from app.schemas import (
    Itinerary,
    RefineRequest,
    TripCreateRequest,
    TripStatusResponse,
)

log = structlog.get_logger()
router = APIRouter(prefix="/api/trips", tags=["trips"])


async def get_arq_pool():
    return await create_pool(
        RedisSettings.from_dsn(
            settings.redis_url
        )
    )


# @router.post("", response_model=TripStatusResponse)
# async def create_trip(
#     body: TripCreateRequest,
#     db: AsyncSession = Depends(get_db),
#     arq=Depends(get_arq_pool),
# ) -> TripStatusResponse:
#     """Create trip, attach TEB snapshot, enqueue generation job."""
#     # Load latest TEB for user
#     result = await db.execute(
#         select(TEBProfile)
#         .where(TEBProfile.user_id == body.user_id)
#         .order_by(TEBProfile.version.desc())
#         .limit(1)
#     )
#     teb_profile = result.scalar_one_or_none()

#     trip = Trip(
#         user_id=body.user_id,
#         teb_snapshot=teb_profile.teb_json if teb_profile else None,
#         constraints_json=body.constraints.model_dump(),
#         status="pending",
#     )
#     db.add(trip)
#     await db.commit()
#     await db.refresh(trip)

#     await arq.enqueue_job("generate_itinerary_job", trip.id)
#     log.info("trip.created", trip_id=trip.id)

#     return TripStatusResponse(trip_id=trip.id, status="pending")

@router.post("", response_model=TripStatusResponse)
async def create_trip(
    body: TripCreateRequest,
    db: AsyncSession = Depends(get_db),
    arq=Depends(get_arq_pool),
) -> TripStatusResponse:
    teb_snapshot = body.teb_snapshot
    if not teb_snapshot:
        result = await db.execute(
            select(TEBProfile)
            .where(TEBProfile.user_id == body.user_id)
            .order_by(TEBProfile.version.desc())
            .limit(1)
        )
        teb_profile = result.scalar_one_or_none()
        if not teb_profile:
            raise HTTPException(
                status_code=400,
                detail="No TEB profile found for this user. Complete intake first.",
            )
        teb_snapshot = teb_profile.teb_json

    # Save trip
    trip = Trip(
        user_id=body.user_id,
        constraints_json=body.constraints.model_dump(),
        teb_snapshot=teb_snapshot,
        status="pending",
    )
    db.add(trip)
    await db.commit()
    await db.refresh(trip)

    # Trigger ingestion if destination not in DB
    has_places = await destination_has_places(body.constraints.destination)
    if not has_places:
        await arq.enqueue_job(
            "ingest_destination_job",
            body.constraints.destination,
        )
        # Small delay so ingestion runs before generation
        await asyncio.sleep(2)

    # Enqueue generation
    await arq.enqueue_job("generate_itinerary_job", trip.id)

    return TripStatusResponse(trip_id=trip.id, status="pending")

@router.get("/{trip_id}/status", response_model=TripStatusResponse)
async def get_trip_status(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
) -> TripStatusResponse:
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return TripStatusResponse(trip_id=trip_id, status=trip.status)  # type: ignore[arg-type]


@router.get("/{trip_id}/itinerary", response_model=Itinerary)
async def get_itinerary(
    trip_id: str,
    db: AsyncSession = Depends(get_db),
) -> Itinerary:
    result = await db.execute(
        select(ItineraryRecord)
        .where(ItineraryRecord.trip_id == trip_id)
        .order_by(ItineraryRecord.version.desc())
        .limit(1)
    )
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Itinerary not ready")
    return Itinerary.model_validate(record.itinerary_json)


@router.post("/{trip_id}/refine", response_model=TripStatusResponse)
async def refine_trip(
    trip_id: str,
    body: RefineRequest,
    db: AsyncSession = Depends(get_db),
    arq=Depends(get_arq_pool),
) -> TripStatusResponse:
    """Re-enqueue generation job with a refinement instruction."""
    trip = await db.get(Trip, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    trip.status = "pending"
    # Store refinement instruction in constraints for worker to pick up
    constraints = dict(trip.constraints_json)
    constraints["refinement_instruction"] = body.instruction
    trip.constraints_json = constraints
    await db.commit()

    await arq.enqueue_job("generate_itinerary_job", trip_id)
    return TripStatusResponse(trip_id=trip_id, status="pending")
