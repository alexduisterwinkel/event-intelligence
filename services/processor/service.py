import asyncio

from core.bootstrap.service import BaseService
from core.events import Event, create_event
from core.events.types import EventTypes

from .enrichers import extract_keywords, categorize, score_article

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

        #Extract content and process
        content = event.payload.get("content", "")

        keywords = extract_keywords(content)
        category = categorize(content)
        score = score_article(content)

        enriched_payload = {
            **event.payload,
            "keywords": keywords,
            "category": category,
            "importance_score": score,
        }

        enriched_event = create_event(
            event_type=EventTypes.NEWS_ARTICLE_ENRICHED,
            source=self.name,
            payload={"example": "data"},
            correlation_id=event.correlation_id,
            causation_id=event.event_id,
        )

        self.logger.info(
            "Article enriched",
            extra={
                "event_id": str(enriched_event.event_id),
                "correlation_id": str(enriched_event.correlation_id),
            },
        )

        await self.event_bus.publish(enriched_event)

    async def run(self) -> None:
        while True:
            await asyncio.sleep(3600)
