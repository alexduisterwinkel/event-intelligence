import asyncio
import json
from typing import Dict, List

import redis.asyncio as redis

from core.events import Event
from .bus import EventBus, EventHandler


class RedisEventBus(EventBus):

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url, decode_responses=True)

        self.subscribers: Dict[str, List[EventHandler]] = {}
        self.pubsub = self.redis.pubsub()

    async def publish(self, event: Event) -> None:
        await self.redis.publish(
            event.event_type,
            event.model_dump_json(),
        )

    async def subscribe(
        self,
        event_type: str,
        handler: EventHandler,
    ) -> None:
        if event_type not in self.subscribers:
            self.subscribers[event_type] = []
            await self.pubsub.subscribe(event_type)

        self.subscribers[event_type].append(handler)

    async def start(self) -> None:
        asyncio.create_task(self._listener())

    async def _listener(self):
        async for message in self.pubsub.listen():

            if message["type"] != "message":
                continue

            event_type = message["channel"]
            raw_data = message["data"]

            event = Event.model_validate_json(raw_data)

            handlers = self.subscribers.get(event_type, [])

            try:
                await asyncio.gather(*(h(event) for h in handlers))
            except Exception:
                self.logger.info(
                    "Exception raised",
                    extra={
                        "event_id": str(event.event_id),
                        "correlation_id": str(event.correlation_id),
                    },
                )
