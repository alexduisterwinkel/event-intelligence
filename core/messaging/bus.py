from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from core.events import Event


EventHandler = Callable[[Event], Awaitable[None]]


class EventBus(ABC):

    @abstractmethod
    async def publish(
        self,
        stream: str,
        event: Event,
    ) -> None:
        """
        Append an event to a stream.
        """
        pass

    @abstractmethod
    async def ensure_group(
        self,
        stream: str,
        group: str,
    ) -> None:
        """
        Ensure a consumer group exists for a stream.
        """
        pass

    @abstractmethod
    async def consume(
        self,
        stream: str,
        group: str,
        consumer: str,
        handler: EventHandler,
    ) -> None:
        """
        Consume events from a stream using a consumer group.
        """
        pass
