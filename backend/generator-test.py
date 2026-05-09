import asyncio
import json
from app.modules.generator import generate_itinerary
from app.modules.solver import get_feasibility
from app.schemas import TravelEmotionalBrief, TripConstraints

teb = TravelEmotionalBrief(
    travel_mood="restorative",
    energy_level="low",
    social_context="solo",
    motivation="burnout recovery",
    stimulation_preference="low",
    risk_appetite="low",
    soft_constraints=["avoid crowds", "nature preferred"],
    deal_breakers=["no clubs", "no loud bars"],
    confidence_score=0.85
)

constraints = TripConstraints(
    departure_city="New York",
    destination="Lisbon",
    start_date="2025-06-01",
    end_date="2025-06-04",
    total_budget_usd=1500,
    traveler_count=1
)

async def main():
    feasibility = await get_feasibility(constraints)
    print(f"Feasibility: {feasibility.feasible}, {feasibility.nights} nights, ${feasibility.budget_per_day_usd}/day")
    
    itinerary = await generate_itinerary(teb, feasibility, constraints)
    print(f"\nItinerary for {itinerary.destination}:")
    for day in itinerary.days:
        print(f"\nDay {day.day_number} — {day.theme}")
        for stop in day.stops:
            print(f"  • {stop.name} ({stop.category})")
            print(f"    → {stop.teb_explanation}")

asyncio.run(main())