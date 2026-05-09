from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TEBProfile
from app.db.session import get_db
from app.schemas import TravelEmotionalBrief

router = APIRouter(prefix="/api/profile", tags=["profile"])


@router.get("/teb", response_model=TravelEmotionalBrief)
async def get_teb(
    user_id: str,
    db: AsyncSession = Depends(get_db),
) -> TravelEmotionalBrief:
    result = await db.execute(
        select(TEBProfile)
        .where(TEBProfile.user_id == user_id)
        .order_by(TEBProfile.version.desc())
        .limit(1)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="TEB profile not found")
    return TravelEmotionalBrief.model_validate(profile.teb_json)


@router.patch("/teb", response_model=TravelEmotionalBrief)
async def update_teb(
    user_id: str,
    updates: dict,
    db: AsyncSession = Depends(get_db),
) -> TravelEmotionalBrief:
    """Manually update TEB fields. Pydantic validates the merged result."""
    result = await db.execute(
        select(TEBProfile)
        .where(TEBProfile.user_id == user_id)
        .order_by(TEBProfile.version.desc())
        .limit(1)
    )
    profile = result.scalar_one_or_none()
    if not profile:
        raise HTTPException(status_code=404, detail="TEB profile not found")

    merged = {**profile.teb_json, **updates}
    validated = TravelEmotionalBrief.model_validate(merged)

    profile.teb_json = validated.model_dump()
    profile.confidence_score = validated.confidence_score
    profile.version += 1
    await db.commit()

    return validated
