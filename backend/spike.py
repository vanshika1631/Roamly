"""
Phase 0 Validation Spike
Run with: python spike.py

Proves the core hypothesis: same destination + budget, opposite TEBs
→ meaningfully different itineraries.

Requires: ANTHROPIC_API_KEY in environment.
"""

import json
import os
from urllib import response

# import anthropic

# client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# from google import genai as google_genai
# client = google_genai.Client(api_key=os.environ["GEMINI_API_KEY"])

from groq import Groq
client = Groq(api_key=os.environ["GROQ_API_KEY"])

TEB_RESTORATIVE = {
    "travel_mood": "restorative",
    "energy_level": "low",
    "social_context": "solo",
    "motivation": "burnout recovery after intense work period",
    "stimulation_preference": "low",
    "risk_appetite": "low",
    "soft_constraints": ["avoid crowds", "nature preferred", "slow pace", "quiet areas"],
    "deal_breakers": ["no clubs", "no loud bars", "no packed tourist sites"],
    "confidence_score": 0.9,
}

TEB_CELEBRATORY = {
    "travel_mood": "celebratory",
    "energy_level": "high",
    "social_context": "group",
    "motivation": "promotion celebration with close friends",
    "stimulation_preference": "high",
    "risk_appetite": "high",
    "soft_constraints": ["nightlife", "social venues", "upscale dining", "iconic spots"],
    "deal_breakers": ["no early mornings", "no solo activities"],
    "confidence_score": 0.9,
}

DESTINATION = "Lisbon"
DAYS = 3
BUDGET_USD = 1500


def generate_itinerary(teb: dict, destination: str, days: int, budget_usd: int) -> dict:
    prompt = f"""Generate a {days}-day itinerary for {destination} with a total budget of ${budget_usd}.

The traveler's emotional profile:
{json.dumps(teb, indent=2)}

Return a JSON object with this structure:
{{
  "theme": "one sentence describing the trip vibe",
  "days": [
    {{
      "day": 1,
      "stops": [
        {{
          "name": "Place name",
          "type": "category",
          "why": "Why this fits the TEB — reference a specific TEB field"
        }}
      ]
    }}
  ]
}}

Only return valid JSON. No markdown, no explanation."""

    # response = client.messages.create(
    #     model="claude-sonnet-4-20250514",
    #     max_tokens=2048,
    #     messages=[{"role": "user", "content": prompt}],
    # )

    # raw = response.content[0].text.strip()
    # return json.loads(raw)

#     response = client.models.generate_content(
#     model="gemini-2.0-flash",
#     contents=prompt
# )
#     raw = response.text.strip().replace("```json", "").replace("```", "")
#     return json.loads(raw)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7,
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "")
    return json.loads(raw)

def main() -> None:
    print("=" * 60)
    print(f"EmotiTrip Phase 0 Spike — {DESTINATION}, {DAYS} days, ${BUDGET_USD}")
    print("=" * 60)

    print("\n🧘 Generating RESTORATIVE itinerary...")
    restorative = generate_itinerary(TEB_RESTORATIVE, DESTINATION, DAYS, BUDGET_USD)
    print(f"Theme: {restorative['theme']}")
    for day in restorative["days"]:
        print(f"\n  Day {day['day']}:")
        for stop in day["stops"]:
            print(f"    • {stop['name']} ({stop['type']})")
            print(f"      → {stop['why']}")

    print("\n🎉 Generating CELEBRATORY itinerary...")
    celebratory = generate_itinerary(TEB_CELEBRATORY, DESTINATION, DAYS, BUDGET_USD)
    print(f"Theme: {celebratory['theme']}")
    for day in celebratory["days"]:
        print(f"\n  Day {day['day']}:")
        for stop in day["stops"]:
            print(f"    • {stop['name']} ({stop['type']})")
            print(f"      → {stop['why']}")

    print("\n" + "=" * 60)
    print("✅ Spike complete. Manually evaluate: are the outputs meaningfully different?")
    print("If yes — the project is worth building.")


if __name__ == "__main__":
    main()
