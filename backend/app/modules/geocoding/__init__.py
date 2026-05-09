import httpx

async def geocode(destination: str) -> tuple[float, float] | None:
    """Convert destination name to lat/lng using OpenStreetMap Nominatim."""
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": destination,
        "format": "json",
        "limit": 1,
    }
    headers = {
        "User-Agent": "Roamly/1.0 (travel planner app)"  # Nominatim requires this
    }

    async with httpx.AsyncClient(timeout=10) as client:
        try:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()
            results = response.json()
            if results:
                return float(results[0]["lat"]), float(results[0]["lon"])
            return None
        except Exception as e:
            print(f"Geocoding error for {destination}: {e}")
            return None