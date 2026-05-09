from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.openai_api_key)

async def embed(text: str) -> list[float]:
    """Convert text to a 1536-dimension embedding vector."""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text,
    )
    return response.data[0].embedding


async def embed_teb(teb) -> list[float]:
    """Convert a TEB to an embedding for similarity search."""
    text = f"""
    Travel mood: {teb.travel_mood}
    Energy level: {teb.energy_level}
    Social context: {teb.social_context}
    Motivation: {teb.motivation}
    Stimulation preference: {teb.stimulation_preference}
    Risk appetite: {teb.risk_appetite}
    Soft constraints: {', '.join(teb.soft_constraints)}
    Deal breakers: {', '.join(teb.deal_breakers)}
    """
    return await embed(text.strip())