from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import Destination
from app.modules.embeddings import embed_teb
from app.schemas import TravelEmotionalBrief


async def retrieve_places(
    teb: TravelEmotionalBrief,
    destination: str,
    db: AsyncSession,
    limit: int = 20,
) -> list[dict]:
    """
    Find places that emotionally match the TEB using cosine similarity.
    Filters by destination city.
    """
    plain_query = text("""
        SELECT
            name,
            country,
            metadata_json
        FROM destinations
        WHERE metadata_json->>'city' ILIKE :city
        ORDER BY name
        LIMIT :limit
    """)

    embedded_count_query = text("""
        SELECT count(*)
        FROM destinations
        WHERE metadata_json->>'city' ILIKE :city
          AND embedding IS NOT NULL
    """)

    embedded_count_result = await db.execute(
        embedded_count_query,
        {"city": destination},
    )
    embedded_count = embedded_count_result.scalar_one()

    if embedded_count == 0:
        rows = await db.execute(
            plain_query,
            {"city": destination, "limit": limit},
        )
        return [
            {
                "name": row.name,
                "country": row.country,
                "similarity": 0.0,
                **row.metadata_json,
            }
            for row in rows.fetchall()
        ]

    # Embed the TEB only when there are indexed place embeddings to compare against.
    teb_embedding = await embed_teb(teb)
    embedding_str = f"[{','.join(map(str, teb_embedding))}]"

    # Cosine similarity search filtered by city
    query = text("""
        SELECT 
            name,
            country,
            metadata_json,
            1 - (embedding <=> :embedding::vector) as similarity
        FROM destinations
        WHERE metadata_json->>'city' ILIKE :city
          AND embedding IS NOT NULL
        ORDER BY embedding <=> :embedding::vector
        LIMIT :limit
    """)

    result = await db.execute(
        query,
        {
            "embedding": embedding_str,
            "city": destination,
            "limit": limit,
        }
    )

    rows = result.fetchall()
    places = []
    for row in rows:
        place = {
            "name": row.name,
            "country": row.country,
            "similarity": round(row.similarity, 3),
            **row.metadata_json,
        }
        places.append(place)

    return places
