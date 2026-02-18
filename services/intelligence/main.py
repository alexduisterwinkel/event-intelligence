import asyncio

from core.messaging.redis_bus import RedisEventBus
from services.intelligence.service import IntelligenceService


async def main():
    event_bus = RedisEventBus()

    service = IntelligenceService(
        name="intelligence",
        event_bus=event_bus,
    )

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
