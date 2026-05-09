from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.models import TEBProfile
from app.db.session import get_db
from app.modules.profiler import generate_teb, stream_intake_response
from app.schemas import FinalizeIntakeRequest, IntakeMessageRequest, TravelEmotionalBrief

router = APIRouter(prefix="/api/intake", tags=["intake"])


@router.post("/message")
async def intake_message(body: IntakeMessageRequest) -> StreamingResponse:
    """Stream Claude's intake conversation response as SSE."""
    return StreamingResponse(
        stream_intake_response(body.messages),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@router.post("/finalize", response_model=TravelEmotionalBrief)
async def finalize_intake(
    body: FinalizeIntakeRequest,
    db: AsyncSession = Depends(get_db),
) -> TravelEmotionalBrief:
    teb = await generate_teb(body.conversation_history)

    # Check if profile exists for this user
    result = await db.execute(
        select(TEBProfile).where(TEBProfile.user_id == body.user_id)
    )
    existing = result.scalar_one_or_none()

    if existing:
        existing.teb_json = teb.model_dump()
        existing.confidence_score = teb.confidence_score
        existing.version += 1
    else:
        profile = TEBProfile(
            user_id=body.user_id,
            teb_json=teb.model_dump(),
            confidence_score=teb.confidence_score,
        )
        db.add(profile)

    await db.commit()
    return teb
