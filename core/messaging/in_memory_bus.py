from collections import defaultdict
from typing import Dict, List

from core.events import Event
from .bus import EventBus, EventHandler


class InMemoryEventBus(EventBus):

    def __init__(self):
        self.subscribers: Dict[str, List[EventHandler]] = defaultdict(list)

    async def publish(self, event: Event) -> None:
        handlers = self.subscribers.get(event.event_type, [])

        for handler in handlers:
            await handler(event)

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        self.subscribers[event_type].append(handler)

    async def start(self) -> None:
        pass
