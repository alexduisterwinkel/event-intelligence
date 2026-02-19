import asyncio
from fastapi.responses import HTMLResponse

from core.messaging.redis_bus import RedisEventBus
from services.ingestion.service import IngestionService
from services.ingestion.sources.news_api import MockNewsSource
from services.processor.service import ProcessorService
from services.intelligence.service import IntelligenceService
from services.api.service import APIService
from services.realtime.service import RealtimeService
from services.persistence.service import SignalPersistenceService


async def main():

    event_bus = RedisEventBus()

    ingestion = IngestionService(
        name="ingestion",
        event_bus=event_bus,
        sources=[MockNewsSource()],
        interval=3,
    )

    processor = ProcessorService(
        name="processor",
        event_bus=event_bus,
    )

    intelligence = IntelligenceService(
        name="intelligence",
        event_bus=event_bus,
    )

    api = APIService(
        name="api",
        event_bus=event_bus,
    )

    realtime = RealtimeService(
        name="realtime",
        event_bus=event_bus,
    )

    persistence = SignalPersistenceService(
        name="persistence",
        event_bus=event_bus,
    )

    await asyncio.gather(
        ingestion.start(),
        processor.start(),
        intelligence.start(),
        api.start(),
        realtime.start(),
        persistence.start(),
    )


if __name__ == "__main__":
    asyncio.run(main())
