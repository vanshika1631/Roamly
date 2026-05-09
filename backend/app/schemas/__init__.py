from typing import Literal

from pydantic import BaseModel, Field


# ── Travel Emotional Brief ────────────────────────────────────────────────────

class TravelEmotionalBrief(BaseModel):
    travel_mood: Literal[
        "restorative", "adventurous", "celebratory", "exploratory", "romantic"
    ]
    energy_level: Literal["low", "medium", "high"]
    social_context: Literal["solo", "couple", "group", "family"]
    motivation: str = Field(description="e.g. burnout recovery, milestone celebration")
    stimulation_preference: Literal["low", "medium", "high"]
    risk_appetite: Literal["low", "medium", "high"]
    soft_constraints: list[str] = Field(
        description="e.g. avoid crowds, nature preferred"
    )
    deal_breakers: list[str] = Field(description="e.g. no hostels, no red-eye flights")
    confidence_score: float = Field(ge=0.0, le=1.0)


# ── Intake ────────────────────────────────────────────────────────────────────

class ConversationMessage(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class IntakeMessageRequest(BaseModel):
    messages: list[ConversationMessage]


class FinalizeIntakeRequest(BaseModel):
    user_id: str
    conversation_history: list[ConversationMessage]


# ── Trip / Constraints ────────────────────────────────────────────────────────

class TripConstraints(BaseModel):
    departure_city: str
    destination: str
    start_date: str  # ISO 8601 e.g. "2025-06-01"
    end_date: str
    total_budget_usd: float = Field(gt=0)
    traveler_count: int = Field(ge=1, le=20)


class TripCreateRequest(BaseModel):
    user_id: str
    constraints: TripConstraints
    teb_snapshot: dict | None = None


class TripStatusResponse(BaseModel):
    trip_id: str
    status: Literal["pending", "generating", "auditing", "ready", "failed"]


# ── Itinerary ─────────────────────────────────────────────────────────────────

class ItineraryStop(BaseModel):
    name: str
    place_id: str | None = None
    category: str
    address: str | None = None
    lat: float | None = None
    lng: float | None = None
    duration_minutes: int
    teb_explanation: str = Field(
        description="Why this stop was chosen — references a specific TEB field"
    )
    # popularity_tier: Literal["hidden_gem", "local_favourite", "well_known", "tourist_trap"] = "well_known"
    popularity_tier: str = "well_known"

class ItineraryDay(BaseModel):
    day_number: int
    date: str
    theme: str
    stops: list[ItineraryStop]


class Itinerary(BaseModel):
    trip_id: str
    destination: str
    days: list[ItineraryDay]
    teb_snapshot: TravelEmotionalBrief
    audit_passed: bool = False


# ── Refinement ────────────────────────────────────────────────────────────────

class RefineRequest(BaseModel):
    instruction: str = Field(description="Natural language refinement instruction")
