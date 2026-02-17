import asyncio
from datetime import datetime

from core.bootstrap.service import BaseService
from core.events import Event, create_event
from core.events.types import EventTypes

from .detectors.trend_detector import TrendDetector


class IntelligenceService(BaseService):

    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)
        self.detector = TrendDetector(window_seconds=60, threshold=3)

    async def register_handlers(self):
        await self.event_bus.subscribe(
            EventTypes.NEWS_ARTICLE_ENRICHED,
            self.handle_enriched_article,
        )

    async def handle_enriched_article(self, event: Event):

        category = event.payload.get("category", "general")
        timestamp = event.timestamp

        trend_detected = self.detector.add_event(category, timestamp)

        if trend_detected:
            signal_payload = {
                "category": category,
                "message": f"Trend detected in {category}",
                "confidence": 0.8,
            }

            signal_event = create_event(
                event_type=EventTypes.SIGNAL_TREND_DETECTED,
                source=self.name,
                payload=signal_payload,
                correlation_id=event.correlation_id,
                causation_id=event.event_id,
            )

            self.logger.info(
                "Trend detected",
                extra={
                    "event_id": str(signal_event.event_id),
                    "correlation_id": str(signal_event.correlation_id),
                },
            )

            await self.event_bus.publish(signal_event)

    async def run(self):
        while True:
            await asyncio.sleep(3600)
