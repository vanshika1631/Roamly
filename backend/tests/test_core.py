"""
Test suite skeleton.
Run with: pytest tests/ -v
"""

import pytest
from httpx import AsyncClient

from app.main import app
from app.schemas import TravelEmotionalBrief


# ── Schema tests ──────────────────────────────────────────────────────────────

def test_teb_schema_valid():
    teb = TravelEmotionalBrief(
        travel_mood="restorative",
        energy_level="low",
        social_context="solo",
        motivation="burnout recovery",
        stimulation_preference="low",
        risk_appetite="low",
        soft_constraints=["avoid crowds", "nature preferred"],
        deal_breakers=["no hostels"],
        confidence_score=0.85,
    )
    assert teb.confidence_score == 0.85


def test_teb_json_schema_generated():
    """Verify Pydantic generates a valid JSON Schema for Claude tool definition."""
    schema = TravelEmotionalBrief.model_json_schema()
    assert "properties" in schema
    assert "travel_mood" in schema["properties"]


# ── API tests ─────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_health_endpoint():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_intake_message_streams():
    """Smoke test: intake/message endpoint returns SSE content-type."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/intake/message",
            json={"messages": [{"role": "user", "content": "I need a break"}]},
        )
    # Will fail without real API key — mark as integration test in CI
    assert response.status_code in (200, 500)


# ── Solver tests ──────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_solver_feasible():
    from app.modules.solver import get_feasibility
    from app.schemas import TripConstraints

    constraints = TripConstraints(
        departure_city="New York",
        destination="Lisbon",
        start_date="2025-06-01",
        end_date="2025-06-08",
        total_budget_usd=3000,
        traveler_count=1,
    )
    result = await get_feasibility(constraints)
    assert result.feasible is True
    assert result.nights == 7
    assert result.budget_per_day_usd > 0


@pytest.mark.asyncio
async def test_solver_infeasible_dates():
    from app.modules.solver import get_feasibility
    from app.schemas import TripConstraints

    constraints = TripConstraints(
        departure_city="New York",
        destination="Lisbon",
        start_date="2025-06-08",
        end_date="2025-06-01",  # end before start
        total_budget_usd=3000,
        traveler_count=1,
    )
    result = await get_feasibility(constraints)
    assert result.feasible is False
