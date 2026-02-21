import asyncio
from datetime import datetime

from core.bootstrap.service import BaseService
from core.events import Event, create_event
from core.events.types import EventTypes
from core.messaging.streams import PROCESSED_EVENTS, SIGNALS

from .detectors.trend_detector import TrendDetector
from .detectors.anomaly_detector import AnomalyDetector
from .detectors.keyword_stats import KeywordStatsStore
from .scoring.composite import compute_trend_score


class IntelligenceService(BaseService):

    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)
        self.detector = TrendDetector(window_seconds=60, threshold=3)

        self.anomaly_detector = AnomalyDetector(
            window_seconds=120,
            anomaly_threshold=2.5,
        )
        self.keyword_store = KeywordStatsStore(
            short_window_seconds=60,
            long_window_seconds=300,
        )
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

        trend_detected, score = self.detector.add_event(
            category,
            timestamp,
        )

        is_anomaly, z_score = self.anomaly_detector.add_event(
            category,
            timestamp,
        )

        importance = event.payload.get("importance_score", 0.0)
        category_confidence = event.payload.get("category_confidence", 0.0)


        keywords = event.payload.get("keywords", [])

        keyword_stats = self.keyword_store.add_keywords(
            keywords,
            timestamp,
        )

        # compute max burst for the article
        max_burst = 0.0
        top_keyword = None

        for kw, (_, _, burst) in keyword_stats.items():
            if burst > max_burst:
                max_burst = burst
                top_keyword = kw

        composite_score = compute_trend_score(
            importance=importance,
            category_confidence=category_confidence,
            keyword_burst=max_burst,
        )

        if trend_detected:
            signal_payload = {
                "category": category,
                "message": f"Trend detected in {category}",
                "confidence": composite_score,
                "composite_score": composite_score,
                "top_keyword": top_keyword,
                "trend_score": score,
                "keyword_burst": max_burst,
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

            # ------------------------------
            # anomaly detection
            # ------------------------------
            if is_anomaly:
                anomaly_payload = {
                    "category": category,
                    "message": f"Anomaly spike in {category}",
                    "confidence": min(1.0, z_score / self.anomaly_detector.threshold),
                    "z_score": z_score,
                    "signal_type": "anomaly",
                }

                anomaly_event = create_event(
                    event_type=EventTypes.SIGNAL_TREND_DETECTED,
                    source=self.name,
                    payload=anomaly_payload,
                    correlation_id=event.correlation_id,
                    causation_id=event.event_id,
                )

                self.logger.info(
                    "Anomaly detected",
                    extra={
                        "event_id": str(anomaly_event.event_id),
                        "correlation_id": str(anomaly_event.correlation_id),
                        "z_score": z_score,
                    },
                )

                await self.event_bus.publish(SIGNALS, anomaly_event)


    async def run(self):
        while True:
            await asyncio.sleep(3600)
