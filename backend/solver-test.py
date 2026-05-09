import asyncio
from app.modules.solver import get_feasibility
from app.schemas import TripConstraints

constraints = TripConstraints(
    departure_city="New York",
    destination="Lisbon",
    start_date="2025-06-01",
    end_date="2025-06-08",
    total_budget_usd=1500,
    traveler_count=1
)

result = asyncio.run(get_feasibility(constraints))
print("Feasible:", result.feasible)
print("Nights:", result.nights)
print("Budget per day:", result.budget_per_day_usd)