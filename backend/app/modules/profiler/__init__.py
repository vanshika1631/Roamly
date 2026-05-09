import json
from groq import AsyncGroq
from app.config import settings
from app.schemas import ConversationMessage, TravelEmotionalBrief

client = AsyncGroq(api_key=settings.groq_api_key)

INTAKE_SYSTEM_PROMPT = """You are EmotiTrip's emotional intake specialist.
Your job is to have a warm, curious conversation to understand WHY the user
wants to travel — not just where. Ask about their current emotional state,
what they need from this trip, and what would make it feel meaningful.
After 5-7 exchanges, you will have enough to generate a Travel Emotional Brief.
Keep responses concise and conversational."""

async def stream_intake_response(messages: list[ConversationMessage]):
    formatted = [{"role": m.role, "content": m.content} for m in messages]
    stream = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": INTAKE_SYSTEM_PROMPT}] + formatted,
        stream=True,
    )
    async for chunk in stream:
        text = chunk.choices[0].delta.content
        if text:
            yield f"data: {text}\n\n"
    yield "data: [DONE]\n\n"

async def generate_teb(conversation: list[ConversationMessage]) -> TravelEmotionalBrief:
    formatted = [{"role": m.role, "content": m.content} for m in conversation]
    prompt = """Based on this conversation, generate a Travel Emotional Brief as a JSON object
with exactly these fields:
- travel_mood: one of restorative, adventurous, celebratory, exploratory, romantic
- energy_level: one of low, medium, high
- social_context: one of solo, couple, group, family
- motivation: string describing why they are travelling
- stimulation_preference: one of low, medium, high
- risk_appetite: one of low, medium, high
- soft_constraints: list of strings
- deal_breakers: list of strings
- confidence_score: float between 0.0 and 1.0

Return only valid JSON, no markdown, no explanation."""

    response = await client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": INTAKE_SYSTEM_PROMPT},
            *formatted,
            {"role": "user", "content": prompt}
        ],
    )
    raw = response.choices[0].message.content.strip()
    raw = raw.replace("```json", "").replace("```", "")
    return TravelEmotionalBrief.model_validate(json.loads(raw))