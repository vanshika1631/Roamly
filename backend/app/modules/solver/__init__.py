import asyncio
from dataclasses import dataclass

from ortools.sat.python import cp_model

from app.schemas import TripConstraints


@dataclass
class FeasibilityResult:
    feasible: bool
    budget_per_day_usd: float
    nights: int
    relaxed_suggestion: str | None = None


def _solve(constraints: TripConstraints) -> FeasibilityResult:
    from datetime import date

    start = date.fromisoformat(constraints.start_date)
    end = date.fromisoformat(constraints.end_date)
    nights = (end - start).days

    if nights <= 0:
        return FeasibilityResult(
            feasible=False,
            budget_per_day_usd=0,
            nights=0,
            relaxed_suggestion="End date must be after start date.",
        )

    model = cp_model.CpModel()
    solver = cp_model.CpSolver()

    budget_cents = int(constraints.total_budget_usd * 100)
    min_daily_cents = 5000  # $50/day floor

    # Actual daily budget = total / nights
    actual_daily_cents = budget_cents // nights

    if actual_daily_cents < min_daily_cents:
        return FeasibilityResult(
            feasible=False,
            budget_per_day_usd=0,
            nights=nights,
            relaxed_suggestion=(
                f"Budget of ${constraints.total_budget_usd:.0f} is too low for "
                f"{nights} nights. Minimum is ${nights * 50:.0f}. "
                f"Try increasing your budget or reducing trip length."
            ),
        )

    # OR-Tools validates the constraint is satisfiable
    daily_budget = model.new_int_var(
        min_daily_cents, budget_cents, "daily_budget_cents"
    )
    model.add(daily_budget * nights <= budget_cents)
    model.add(daily_budget >= min_daily_cents)

    # Maximize daily budget (use full budget)
    model.maximize(daily_budget)

    status = solver.solve(model)

    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return FeasibilityResult(
            feasible=True,
            budget_per_day_usd=round(solver.value(daily_budget) / 100, 2),
            nights=nights,
        )

    return FeasibilityResult(
        feasible=False,
        budget_per_day_usd=0,
        nights=nights,
        relaxed_suggestion=(
            f"Budget of ${constraints.total_budget_usd:.0f} is too low for "
            f"{nights} nights."
        ),
    )


async def get_feasibility(constraints: TripConstraints) -> FeasibilityResult:
    """Run the synchronous OR-Tools solver without blocking the event loop."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _solve, constraints)
