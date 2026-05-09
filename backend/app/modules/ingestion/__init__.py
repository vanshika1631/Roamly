import asyncio
import httpx
from openai import RateLimitError
from sqlalchemy import select, func
from app.db.session import AsyncSessionLocal
from app.db.models import Destination
from app.modules.embeddings import embed
from app.modules.geocoding import geocode


async def destination_has_places(city: str) -> bool:
    """Check if we already have places for this destination."""
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(func.count(Destination.id)).where(
                Destination.metadata_json["city"].astext == city
            )
        )
        count = result.scalar()
        return count > 10


def _infer_tags(tier: str, category: str) -> list[str]:
    """Infer emotional tags from category and popularity tier."""
    tags = []
    category_tags = {
        "restaurant": ["food", "social", "celebratory"],
        "cafe": ["restorative", "peaceful", "solo", "low energy"],
        "bar": ["social", "celebratory", "high energy", "group"],
        "museum": ["cultural", "low energy", "exploratory", "solo"],
        "theatre": ["cultural", "celebratory", "group"],
        "cinema": ["social", "group", "medium energy"],
        "attraction": ["exploratory", "cultural", "adventurous"],
        "gallery": ["creative", "exploratory", "cultural", "solo"],
        "viewpoint": ["peaceful", "restorative", "scenic", "low energy"],
        "artwork": ["creative", "exploratory", "cultural"],
        "park": ["nature", "peaceful", "restorative", "low energy"],
        "garden": ["nature", "peaceful", "restorative", "solo", "low energy"],
        "nature_reserve": ["nature", "adventurous", "low energy", "restorative"],
        "place_of_worship": ["cultural", "peaceful", "solo", "restorative"],
        "marketplace": ["social", "exploratory", "medium energy"],
    }
    tags.extend(category_tags.get(category, ["exploratory"]))

    if tier == "hidden_gem":
        tags.extend(["hidden_gem", "local", "avoid crowds"])
    elif tier == "local_favourite":
        tags.extend(["local_favourite", "authentic"])
    elif tier == "tourist_trap":
        tags.extend(["popular", "crowded", "high energy"])
    elif tier == "well_known":
        tags.extend(["well_known", "popular"])

    return list(set(tags))


def _estimate_tier(tags: dict) -> str:
    """Estimate popularity tier from OSM tags."""
    # Wikipedia/Wikidata = internationally well known
    if tags.get("wikipedia") or tags.get("wikidata"):
        return "well_known"
    # UNESCO or heritage = well known
    if tags.get("heritage") or tags.get("UNESCO"):
        return "well_known"
    # Explicit tourism attraction
    if tags.get("tourism") == "attraction":
        return "well_known"
    # Viewpoints and artwork tend to be local favourites
    if tags.get("tourism") in ("viewpoint", "artwork", "gallery"):
        return "local_favourite"
    # Places of worship that are tourist sites
    if tags.get("tourism") == "yes":
        return "local_favourite"
    # Everything else — likely hidden gem
    return "hidden_gem"


def _calculate_hidden_gem_score(tags: dict) -> float:
    """Calculate hidden gem score. Higher = more hidden."""
    score = 0.8
    if tags.get("wikipedia") or tags.get("wikidata"):
        score -= 0.5
    if tags.get("tourism") == "attraction":
        score -= 0.4
    if tags.get("heritage"):
        score -= 0.3
    if tags.get("tourism") == "viewpoint":
        score -= 0.1
    return max(0.1, round(score, 2))


def _get_category(tags: dict) -> str:
    """Extract primary category from OSM tags."""
    return (
        tags.get("amenity")
        or tags.get("tourism")
        or tags.get("leisure")
        or tags.get("historic")
        or tags.get("shop")
        or "place"
    )


def _build_description(name: str, tags: dict, city: str) -> str:
    """Build a human-readable description from OSM tags."""
    parts = [name]

    category = _get_category(tags)
    if category and category != "place":
        parts.append(f"a {category.replace('_', ' ')}")

    if tags.get("description"):
        return tags["description"]

    if tags.get("historic"):
        parts.append(f"historic {tags['historic'].replace('_', ' ')} in {city}")
    elif tags.get("cuisine"):
        parts.append(f"{tags['cuisine']} cuisine in {city}")
    else:
        parts.append(f"in {city}")

    if tags.get("wikipedia"):
        parts.append("notable landmark")

    return ", ".join(parts[:3])


async def fetch_overpass_places(
    lat: float,
    lng: float,
    city: str,
    country: str,
    client: httpx.AsyncClient,
) -> list[dict]:
    """Fetch places from OpenStreetMap Overpass API."""
    radius = 5000  # 5km radius

    query = f"""
    [out:json][timeout:60];
    (
      node["amenity"~"restaurant|cafe|bar|pub|museum|theatre|cinema|arts_centre|library|place_of_worship|marketplace"](around:{radius},{lat},{lng});
      node["tourism"~"attraction|museum|gallery|viewpoint|artwork|hotel"](around:{radius},{lat},{lng});
      node["leisure"~"park|garden|nature_reserve|beach_resort"](around:{radius},{lat},{lng});
      node["historic"~"monument|memorial|castle|ruins|archaeological_site|building"](around:{radius},{lat},{lng});
      way["tourism"~"attraction|museum|gallery|viewpoint"](around:{radius},{lat},{lng});
      way["leisure"~"park|garden|nature_reserve"](around:{radius},{lat},{lng});
      way["historic"~"monument|castle|ruins|archaeological_site"](around:{radius},{lat},{lng});
    );
    out center 200;
    """

    try:
        print(f"  Querying Overpass for {city}...")
        response = await client.post(
            "https://overpass-api.de/api/interpreter",
            data={"data": query.strip()},
            headers={
                "Accept": "application/json",
                "User-Agent": "Roamly/1.0 (testing ingestion flow)",
            },
            timeout=60,
        )
        response.raise_for_status()
        data = response.json()
        places = []

        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name", "")
            if not name:
                continue

            # Get coordinates — nodes have lat/lon directly, ways have center
            if element.get("type") == "node":
                place_lat = element.get("lat")
                place_lng = element.get("lon")
            else:
                center = element.get("center", {})
                place_lat = center.get("lat")
                place_lng = center.get("lon")

            category = _get_category(tags)
            tier = _estimate_tier(tags)
            hidden_gem_score = _calculate_hidden_gem_score(tags)
            description = _build_description(name, tags, city)

            # Build address
            address_parts = []
            if tags.get("addr:housenumber") and tags.get("addr:street"):
                address_parts.append(f"{tags['addr:housenumber']} {tags['addr:street']}")
            elif tags.get("addr:street"):
                address_parts.append(tags["addr:street"])
            if tags.get("addr:city"):
                address_parts.append(tags["addr:city"])
            address = ", ".join(address_parts) if address_parts else city

            places.append({
                "name": name,
                "country": country,
                "metadata_json": {
                    "city": city,
                    "category": category,
                    "description": description,
                    "popularity_tier": tier,
                    "hidden_gem_score": hidden_gem_score,
                    "tags": _infer_tags(tier, category),
                    "source": "openstreetmap",
                    "osm_id": element.get("id"),
                    "osm_type": element.get("type"),
                    "address": address,
                    "lat": place_lat,
                    "lng": place_lng,
                    "website": tags.get("website", ""),
                    "opening_hours": tags.get("opening_hours", ""),
                    "cuisine": tags.get("cuisine", ""),
                    "wikipedia": tags.get("wikipedia", ""),
                },
            })

        print(f"  Fetched {len(places)} places from Overpass")
        return places

    except httpx.TimeoutException:
        print(f"  Overpass timeout for {city} — try again later")
        return []
    except httpx.HTTPStatusError as e:
        print(
            f"  Overpass error for {city}: HTTP {e.response.status_code} "
            f"- {e.response.text[:300]}"
        )
        return []
    except Exception as e:
        print(f"  Overpass error for {city}: {e}")
        return []


async def ingest_destination(
    destination: str,
    country: str = "",
    skip_embeddings: bool = False,
) -> int:
    """
    Main ingestion function called by ARQ worker.
    Geocodes destination, fetches from OpenStreetMap, embeds and saves.
    Returns number of places saved.
    """
    print(f"\nIngesting places for {destination}...")

    # 1. Check if already ingested
    if await destination_has_places(destination):
        print(f"  {destination} already has places — skipping ingestion")
        return 0

    # 2. Geocode
    coords = await geocode(destination)
    if not coords:
        print(f"  Could not geocode {destination}")
        return 0

    lat, lng = coords
    print(f"  Geocoded: {lat}, {lng}")

    # 3. Fetch from Overpass
    async with httpx.AsyncClient(timeout=90) as client:
        all_places = await fetch_overpass_places(lat, lng, destination, country, client)

    if not all_places:
        print(f"  No places fetched for {destination}")
        return 0

    # 4. Deduplicate by name
    seen = set()
    unique_places = []
    for place in all_places:
        key = f"{place['name'].lower()}_{destination.lower()}"
        if key not in seen:
            seen.add(key)
            unique_places.append(place)

    print(f"  {len(unique_places)} unique places after deduplication")

    # 5. Embed and save
    saved = 0
    failed = 0
    supports_embedding = hasattr(Destination, "embedding")
    should_embed = not skip_embeddings and supports_embedding

    if skip_embeddings:
        print("  Skipping embeddings for this run")
    elif not supports_embedding:
        print("  Destination model has no embedding field; saving without embeddings")

    async with AsyncSessionLocal() as db:
        for place in unique_places:
            try:
                meta = place["metadata_json"]
                embedding = None

                if should_embed:
                    embed_text = (
                        f"{place['name']} in {destination}, {place['country']}. "
                        f"{meta['description']}. "
                        f"Category: {meta['category'].replace('_', ' ')}. "
                        f"Tags: {', '.join(meta.get('tags', []))}. "
                        f"Popularity: {meta['popularity_tier'].replace('_', ' ')}."
                    )

                    try:
                        embedding = await embed(embed_text)
                    except RateLimitError:
                        should_embed = False
                        print(
                            "  OpenAI embeddings unavailable (429 insufficient_quota). "
                            "Continuing without embeddings for the rest of this run."
                        )

                destination_kwargs = {
                    "name": place["name"],
                    "country": place["country"],
                    "metadata_json": meta,
                }
                if embedding is not None and supports_embedding:
                    destination_kwargs["embedding"] = embedding

                destination_record = Destination(**destination_kwargs)
                db.add(destination_record)
                saved += 1

                # Commit every 50 records
                if saved % 50 == 0:
                    await db.commit()
                    print(f"  Saved {saved}/{len(unique_places)}...")

                # Rate limit OpenAI embeddings
                if embedding is not None:
                    await asyncio.sleep(0.05)

            except Exception as e:
                failed += 1
                print(f"  Failed to save '{place['name']}': {e}")

        await db.commit()

    print(f"✅ Ingested {saved} places for {destination} ({failed} failed)")
    return saved
