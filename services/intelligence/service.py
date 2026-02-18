import asyncio
from datetime import datetime

from core.bootstrap.service import BaseService
from core.events import Event, create_event
from core.events.types import EventTypes
from core.messaging.streams import PROCESSED_EVENTS, SIGNALS

from .detectors.trend_detector import TrendDetector


class IntelligenceService(BaseService):

    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)
        self.detector = TrendDetector(window_seconds=60, threshold=3)
        self.signals = []   # store emitted signals

    async def register_handlers(self):
        await self.event_bus.ensure_group(
            PROCESSED_EVENTS,
            "intelligence",
        )

        asyncio.create_task(
            self.event_bus.consume(
                stream=PROCESSED_EVENTS,
                group="intelligence",
                consumer="intelligence-1",
                handler=self.handle_event,
            )
        )

    async def handle_event(self, event: Event):

        if event.event_type != EventTypes.NEWS_ARTICLE_ENRICHED:
            return

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

            self.signals.append(signal_payload)

            self.logger.info(
                "Trend detected",
                extra={
                    "event_id": str(signal_event.event_id),
                    "correlation_id": str(signal_event.correlation_id),
                },
            )

            await self.event_bus.publish(SIGNALS,signal_event,)

    async def run(self):
        while True:
            await asyncio.sleep(3600)
