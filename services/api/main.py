import asyncio

from core.messaging.in_memory_bus import InMemoryEventBus
from services.ingestion.service import IngestionService
from services.ingestion.sources.news_api import MockNewsSource
from services.processor.service import ProcessorService
from services.intelligence.service import IntelligenceService
from services.api.service import APIService


async def main():

    event_bus = InMemoryEventBus()

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

    await asyncio.gather(
        ingestion.start(),
        processor.start(),
        intelligence.start(),
        api.start(),
    )


if __name__ == "__main__":
    asyncio.run(main())
