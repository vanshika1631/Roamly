from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    environment: str = "development"
    frontend_url: str = "http://localhost:5173"
    openai_api_key: str = ""
    # Database
    database_url: str

    # Redis
    redis_url: str = "redis://localhost:6379"

    # Auth
    secret_key: str

    # Anthropic
    # anthropic_api_key: str
    
    groq_api_key: str

    # Google Places
    google_places_api_key: str = ""

    # Amadeus
    amadeus_client_id: str = ""
    amadeus_client_secret: str = ""

    # Mapbox
    mapbox_public_token: str = ""

    # OpenWeatherMap
    openweather_api_key: str = ""
    
    foursquare_api_key: str = ""


settings = Settings()  # type: ignore[call-arg]
