import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import intake, profile, trips

log = structlog.get_logger()


# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="EmotiTrip AI",
    description="Emotionally-aware travel planner",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(intake.router)
app.include_router(trips.router)
app.include_router(profile.router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
