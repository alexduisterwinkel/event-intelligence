import asyncio

from core.messaging.in_memory_bus import InMemoryEventBus
from services.processor.service import ProcessorService


async def main():
    event_bus = InMemoryEventBus()
    service = ProcessorService(name="processor", event_bus=event_bus)

    await service.start()


if __name__ == "__main__":
    asyncio.run(main())
