import asyncio

from core.messaging.redis_bus import RedisEventBus
from services.persistence.service import SignalPersistenceService


async def main():
    bus = RedisEventBus()

    service = SignalPersistenceService(
        name="signal-persister",
        event_bus=bus,
    )

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
