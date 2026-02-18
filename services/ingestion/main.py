import asyncio

from core.messaging.redis_bus import RedisEventBus
from services.ingestion.service import IngestionService
from services.ingestion.sources.news_api import MockNewsSource


async def main():
    event_bus = RedisEventBus()

    source = MockNewsSource()

    service = IngestionService(
        name="ingestion",
        event_bus=event_bus,
        sources=[source],
        interval=5,
    )

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
