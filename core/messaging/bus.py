from abc import ABC, abstractmethod
from typing import Callable, Awaitable

from core.events import Event


EventHandler = Callable[[Event], Awaitable[None]]


class EventBus(ABC):

    @abstractmethod
    async def publish(self, event: Event) -> None:
        pass

    @abstractmethod
    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        pass

    @abstractmethod
    async def start(self) -> None:
        pass
