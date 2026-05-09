# import anthropic
import httpx
from app.config import settings
from app.schemas import Itinerary, ItineraryStop

# client = anthropic.AsyncAnthropic()

from groq import AsyncGroq
groq_client = AsyncGroq(api_key=settings.groq_api_key)

POPULARITY_THRESHOLD_PERCENTILE = 0.8  # Top 20% = flagged as potentially over-popular


async def _get_popularity_tier(stop: ItineraryStop) -> str:
    """
    Look up popularity percentile via Google Places.
    Returns one of: hidden_gem | local_favourite | well_known | tourist_trap

    TODO: implement real percentile lookup using Places user_ratings_total
    compared against top-N venues in same city + category.
    """
    if not settings.google_places_api_key or not stop.place_id:
        return stop.popularity_tier

    # Stub — real implementation fetches rating counts and compares percentiles
    return stop.popularity_tier


async def _replace_flagged_stop(
    stop: ItineraryStop,
    teb_json: str,
    destination: str,
) -> ItineraryStop:
    """Ask Claude to suggest a lesser-known alternative for a flagged stop."""
    # response = await client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=512,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": (
    #                 f"The place '{stop.name}' in {destination} is too tourist-heavy. "
    #                 f"Suggest a lesser-known alternative that fits this TEB:\n{teb_json}\n"
    #                 "Respond with a JSON object matching the ItineraryStop schema."
    #             ),
    #         }
    #     ],
    # )
    
    prompt = (
    f"The place '{stop.name}' in {destination} is too tourist-heavy. "
    f"Suggest a lesser-known alternative that fits this TEB:\n{teb_json}\n"
    "Return only a JSON object matching the ItineraryStop schema."
)
    response = await groq_client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[{"role": "user", "content": prompt}],
)
    # TODO: parse and validate response as ItineraryStop
    # For now return original stop to avoid breaking the pipeline
    return stop


async def run_bias_audit(itinerary: Itinerary) -> tuple[Itinerary, dict]:
    """
    1. Check each stop's popularity tier.
    2. Flag stops above threshold.
    3. Replace flagged stops via Claude.
    4. Verify 100% of stops have teb_explanation.
    Returns (audited_itinerary, audit_log).
    """
    audit_log: dict = {
        "flagged": [],
        "replaced": [],
        "explainability_failures": [],
        "passed": False,
    }

    # Handle case where teb_snapshot might be None
    if itinerary.teb_snapshot:
        teb_json = itinerary.teb_snapshot.model_dump_json()
    else:
        teb_json = "{}"

    for day in itinerary.days:
        for i, stop in enumerate(day.stops):
            # Explainability check
            if not stop.teb_explanation:
                audit_log["explainability_failures"].append(stop.name)

            # Popularity check
            tier = await _get_popularity_tier(stop)
            stop.popularity_tier = tier  # type: ignore[assignment]

            if tier == "tourist_trap":
                audit_log["flagged"].append(stop.name)
                replacement = await _replace_flagged_stop(
                    stop, teb_json, itinerary.destination
                )
                day.stops[i] = replacement
                audit_log["replaced"].append(
                    {"original": stop.name, "replacement": replacement.name}
                )

    audit_log["passed"] = (
        len(audit_log["explainability_failures"]) == 0
    )
    itinerary.audit_passed = audit_log["passed"]

    return itinerary, audit_log
