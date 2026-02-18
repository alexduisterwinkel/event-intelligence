import asyncio
from fastapi.responses import HTMLResponse

from core.messaging.redis_bus import RedisEventBus
from services.ingestion.service import IngestionService
from services.ingestion.sources.news_api import MockNewsSource
from services.processor.service import ProcessorService
from services.intelligence.service import IntelligenceService
from services.api.service import APIService
from services.realtime.service import RealtimeService


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
        intelligence_service=intelligence,
    )

    realtime = RealtimeService(
        name="realtime",
        event_bus=event_bus,
    )


    await asyncio.gather(
        ingestion.start(),
        processor.start(),
        intelligence.start(),
        api.start(),
        realtime.start(),
    )


if __name__ == "__main__":
    asyncio.run(main())
