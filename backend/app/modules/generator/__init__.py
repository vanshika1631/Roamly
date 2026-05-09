import json

# import anthropic
import httpx
import structlog

from app.config import settings
from app.modules.solver import FeasibilityResult
from app.schemas import Itinerary, TravelEmotionalBrief, TripConstraints

# client = anthropic.AsyncAnthropic()

from groq import AsyncGroq
groq_client = AsyncGroq(api_key=settings.groq_api_key)
log = structlog.get_logger()

def _build_system_prompt(
    teb: TravelEmotionalBrief,
    feasibility: FeasibilityResult,
    constraints: TripConstraints,
    places_context: str,
) -> str:
    return f"""You are EmotiTrip's itinerary architect.

## Travel Emotional Brief
{teb.model_dump_json(indent=2)}

## Trip Parameters
- Destination: {constraints.destination}
- Dates: {constraints.start_date} → {constraints.end_date} ({feasibility.nights} nights)
- Daily budget: ${feasibility.budget_per_day_usd:.0f} USD
- Travelers: {constraints.traveler_count}

## Available Places (from Google Places)
{places_context}

## Instructions
Generate a day-by-day itinerary that deeply reflects the TEB above.
Every stop MUST include a teb_explanation field that cites a specific TEB field
(e.g. "Chosen for your low energy_level — this garden requires no planning").
Prefer lesser-known places over tourist traps unless the TEB explicitly favours
popular/social venues.

Return a JSON object with exactly this structure:
{{
  "trip_id": "placeholder",
  "destination": "{constraints.destination}",
  "days": [
    {{
      "day_number": 1,
      "date": "{constraints.start_date}",
      "theme": "one sentence describing the day vibe",
      "stops": [
        {{
          "name": "Place name",
          "place_id": null,
          "category": "e.g. cafe, garden, museum",
          "address": "full address",
          "lat": null,
          "lng": null,
          "duration_minutes": 90,
          "teb_explanation": "why this stop fits the TEB",
          "popularity_tier": "hidden_gem"
        }}
      ]
    }}
  ],
  "teb_snapshot": {teb.model_dump_json()},
  "audit_passed": false
}}

Return only valid JSON. No markdown, no explanation, no extra text."""


def _format_places(places: list[dict]) -> str:
    """Format retrieved places for injection into prompt."""
    if not places:
        return "No places found in index — use your knowledge of the destination."
    
    lines = []
    for p in places:
        lines.append(
            f"- {p['name']} ({p.get('category', 'place')}): "
            f"{p.get('description', '')} "
            f"[{p.get('popularity_tier', 'unknown')}] "
            f"[similarity: {p.get('similarity', 0)}]"
        )
    return "\n".join(lines)

def _normalize_popularity_tier(tier: str) -> str:
    valid = {"hidden_gem", "local_favourite", "well_known", "tourist_trap"}
    if tier in valid:
        return tier
    # Default everything else to well_known — auditor will re-evaluate
    return "well_known"


# async def generate_itinerary(
#     teb: TravelEmotionalBrief,
#     feasibility: FeasibilityResult,
#     constraints: TripConstraints,
#     refinement_instruction: str | None = None,
# ) -> Itinerary:
#     """Generate a full itinerary via Claude tool-use."""
#     places_context = await _fetch_places(constraints.destination)

#     system = _build_system_prompt(teb, feasibility, constraints, places_context)
#     messages: list[dict] = [{"role": "user", "content": "Generate my itinerary."}]

#     if refinement_instruction:
#         messages.append(
#             {
#                 "role": "user",
#                 "content": f"Refinement request: {refinement_instruction}",
#             }
#         )

#     from app.schemas import Itinerary  # local import to avoid circular

#     # response = await client.messages.create(
#     #     model="claude-sonnet-4-20250514",
#     #     max_tokens=4096,
#     #     system=system,
#     #     tools=[
#     #         {
#     #             "name": "generate_itinerary",
#     #             "description": "Return the complete structured itinerary",
#     #             "input_schema": Itinerary.model_json_schema(),
#     #         }
#     #     ],
#     #     tool_choice={"type": "tool", "name": "generate_itinerary"},
#     #     messages=messages,
#     # )
#     # tool_block = next(b for b in response.content if b.type == "tool_use")
#     # return Itinerary.model_validate(tool_block.input)
    
#     prompt = system + "\n\nGenerate the itinerary as a JSON object. Return only valid JSON, no markdown."
#     response = await groq_client.chat.completions.create(
#         model="llama-3.3-70b-versatile",
#         messages=[{"role": "user", "content": prompt}],
#     )
#     raw = response.choices[0].message.content.strip()
#     raw = raw.replace("```json", "").replace("```", "").strip()
#     data = json.loads(raw)

#     data["trip_id"] = constraints.destination.lower().replace(" ", "-")
#     data["teb_snapshot"] = teb.model_dump()
#     data["audit_passed"] = False
#     data["destination"] = constraints.destination

#     for day in data.get("days", []):
#         for stop in day.get("stops", []):
#             raw_tier = stop.get("popularity_tier", "well_known")
#             stop["popularity_tier"] = _normalize_popularity_tier(raw_tier)

#     return Itinerary.model_validate(data)

async def generate_itinerary(
    teb: TravelEmotionalBrief,
    feasibility: FeasibilityResult,
    constraints: TripConstraints,
    db=None,
    refinement_instruction: str | None = None,
) -> Itinerary:
    """Generate a full itinerary using RAG-retrieved places."""
    # Use RAG retrieval if db session available
    if db:
        try:
            from app.modules.retrieval import retrieve_places
            places = await retrieve_places(teb, constraints.destination, db)
            places_context = _format_places(places)
        except Exception as e:
            log.warning(
                "generator.retrieval_failed",
                destination=constraints.destination,
                error=str(e),
            )
            places_context = _format_places([])
    else:
        places_context = "No places found in index — use your knowledge of the destination."

    system = _build_system_prompt(teb, feasibility, constraints, places_context)
    messages: list[dict] = [{"role": "user", "content": "Generate my itinerary."}]

    if refinement_instruction:
        messages.append(
            {
                "role": "user",
                "content": f"Refinement request: {refinement_instruction}",
            }
        )

    from app.schemas import Itinerary  # local import to avoid circular

    prompt = system + "\n\nGenerate the itinerary as a JSON object. Return only valid JSON, no markdown."
    response = await groq_client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()
    data = json.loads(raw)

    data["trip_id"] = constraints.destination.lower().replace(" ", "-")
    data["teb_snapshot"] = teb.model_dump()
    data["audit_passed"] = False
    data["destination"] = constraints.destination

    for day in data.get("days", []):
        for stop in day.get("stops", []):
            raw_tier = stop.get("popularity_tier", "well_known")
            stop["popularity_tier"] = _normalize_popularity_tier(raw_tier)

    return Itinerary.model_validate(data)
