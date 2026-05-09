
import asyncio
from app.modules.ingestion import ingest_destination
asyncio.run(ingest_destination('Lisbon', 'Portugal'))