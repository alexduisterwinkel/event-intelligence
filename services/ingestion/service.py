import asyncio
import hashlib
from datetime import datetime

from core.bootstrap.service import BaseService
from core.events import create_event
from core.events.types import EventTypes
from core.messaging.streams import RAW_EVENTS


class IngestionService(BaseService):

    def __init__(self, name, event_bus, sources, interval: int = 5):
        super().__init__(name, event_bus)
        self.sources = sources
        self.interval = interval
        self._seen_hashes = set()

    def _fingerprint(self, item: dict) -> str:
        raw = f"{item.get('title','')}|{item.get('published_at','')}"
        return hashlib.sha256(raw.encode()).hexdigest()

    async def register_handlers(self):
        # Ingestion service typically does not subscribe
        pass

    async def run(self):
        while True:
            for source in self.sources:
                items = await source.fetch()

                for item in items:
                    fp = self._fingerprint(item)

                    if fp in self._seen_hashes:
                        continue

                    self._seen_hashes.add(fp)
                    event = create_event(
                        event_type=EventTypes.NEWS_ARTICLE_DETECTED,
                        source=self.name,
                        payload=item,
                    )

                    self.logger.info(
                        "Publishing news article",
                        extra={
                            "event_id": str(event.event_id),
                            "correlation_id": str(event.correlation_id),
                        },
                    )

                    await self.event_bus.publish(RAW_EVENTS,event,)

            await asyncio.sleep(self.interval)
