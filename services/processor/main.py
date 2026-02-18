import asyncio

from core.messaging.redis_bus import RedisEventBus
from services.processor.service import ProcessorService


async def main():
    event_bus = RedisEventBus()
    service = ProcessorService(name="processor", event_bus=event_bus)

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
