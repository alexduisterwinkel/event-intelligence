import asyncio
import json
from typing import Callable

import redis.asyncio as redis

from core.events import Event
from .bus import EventBus, EventHandler
from .serializer import serialize_event, deserialize_event


class RedisEventBus(EventBus):

    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url, decode_responses=True)

    async def publish(self, stream: str, event: Event) -> None:
        await self.redis.xadd(
            stream,
            serialize_event(event),
        )

    async def ensure_group(
        self,
        stream: str,
        group: str,
    ) -> None:
        try:
            await self.redis.xgroup_create(
                stream,
                group,
                id="0",
                mkstream=True,
            )
        except Exception:
            # group already exists
            pass

    async def consume(
        self,
        stream: str,
        group: str,
        consumer: str,
        handler: EventHandler,
    ):
        while True:
            messages = await self.redis.xreadgroup(
                groupname=group,
                consumername=consumer,
                streams={stream: ">"},
                count=10,
                block=5000,
            )

            for _, entries in messages:
                for message_id, data in entries:
                    event = deserialize_event(data)

                    try:
                        await handler(event)

                        await self.redis.xack(
                            stream,
                            group,
                            message_id,
                        )

                    except Exception:
                        self.logger.exception(
                            "Processing failed",
                            extra={
                                "event_id": str(event.event_id),
                                "correlation_id": str(event.correlation_id),
                            },
                        )

