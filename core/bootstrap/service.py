import asyncio
from abc import ABC, abstractmethod

from core.logging.logger import setup_logger
from core.messaging.bus import EventBus


class BaseService(ABC):

    def __init__(self, name: str, event_bus: EventBus):
        self.name = name
        self.event_bus = event_bus
        self.logger = setup_logger(service_name=name)

    @abstractmethod
    async def register_handlers(self) -> None:
        """
        Register event handlers with the event bus.
        """
        pass

    async def start(self) -> None:
        self.logger.info("Service starting")

        await self.register_handlers()
        await self.event_bus.start()

        self.logger.info("Service started")

        await self.run()

    @abstractmethod
    async def run(self) -> None:
        """
        Long-running execution loop if needed.
        """
        pass

    async def stop(self) -> None:
        self.logger.info("Service stopping")
