import asyncio
import json
import logging
from typing import Callable

import redis.asyncio as redis

from core.events import Event
from .bus import EventBus, EventHandler
from .serializer import serialize_event, deserialize_event


class RedisEventBus(EventBus):

    def __init__(
            self,
            redis_url: str = "redis://localhost:6379",
            max_retries: int = 3,
            base_backoff: float = 0.5,
    ):
        self.redis_url = redis_url
        self.redis = redis.from_url(redis_url, decode_responses=True)
        self.max_retries = max_retries
        self.base_backoff = base_backoff
        self.logger = logging.getLogger("redis_event_bus")

    async def publish(self, stream: str, event: Event) -> None:
        await self.redis.xadd(
            stream,
            serialize_event(event),
        )

    async def _send_to_dlq(
            self,
            stream: str,
            event: Event,
            error: Exception,
            message_id: str,
    ) -> None:
        dlq_stream = f"{stream}_DLQ"

        payload = serialize_event(event)
        payload.update(
            {
                "dlq_error": str(error),
                "dlq_original_stream": stream,
                "dlq_message_id": message_id,
            }
        )
        await self.redis.xadd(dlq_stream, payload)

        self.logger.error(
            "Message sent to DLQ",
            extra={
                "stream": stream,
                "dlq_stream": dlq_stream,
                "event_id": str(event.event_id),
            },
        )

    async def _handle_with_retry(
            self,
            handler: EventHandler,
            event: Event,
    ) -> None:
        attempt = 0

        while True:
            try:
                await handler(event)
                return

            except Exception as e:
                attempt += 1

                if attempt > self.max_retries:
                    raise

                backoff = self.base_backoff * (2 ** (attempt - 1))

                self.logger.warning(
                    "Handler failed, retrying",
                    extra={
                        "event_id": str(event.event_id),
                        "attempt": attempt,
                        "backoff": backoff,
                    },
                )

                await asyncio.sleep(backoff)

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
                        await self._handle_with_retry(handler, event)

                        await self.redis.xack(
                            stream,
                            group,
                            message_id,
                        )

                    except Exception as e:
                        self.logger.exception(
                            "Processing failed",
                            extra={
                                "event_id": str(event.event_id),
                                "correlation_id": str(event.correlation_id),
                            },
                        )

                        # send to DLQ
                        await self._send_to_dlq(
                            stream=stream,
                            event=event,
                            error=e,
                            message_id=message_id,
                        )

                        # IMPORTANT: ACK so it doesn't loop forever
                        await self.redis.xack(
                            stream,
                            group,
                            message_id,
                        )

