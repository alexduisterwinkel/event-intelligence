from core.bootstrap.service import BaseService
from core.events import Event, create_event
from core.events.types import EventTypes


class ProcessorService(BaseService):

    async def register_handlers(self) -> None:
        await self.event_bus.subscribe(
            EventTypes.NEWS_ARTICLE_DETECTED,
            self.handle_article_detected,
        )

    async def handle_article_detected(self, event: Event) -> None:
        self.logger.info(
            "Processing article",
            extra={
                "event_id": str(event.event_id),
                "correlation_id": str(event.correlation_id),
            },
        )

        enriched_event = create_event(
            event_type=EventTypes.NEWS_ARTICLE_ENRICHED,
            source=self.name,
            payload={"example": "data"},
            correlation_id=event.correlation_id,
            causation_id=event.event_id,
        )

        await self.event_bus.publish(enriched_event)

    async def run(self) -> None:
        while True:
            await asyncio.sleep(3600)
