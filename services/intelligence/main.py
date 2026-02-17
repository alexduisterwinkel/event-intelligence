import asyncio

from core.messaging.in_memory_bus import InMemoryEventBus
from services.intelligence.service import IntelligenceService


async def main():
    event_bus = InMemoryEventBus()

    service = IntelligenceService(
        name="intelligence",
        event_bus=event_bus,
    )

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
