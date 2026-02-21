import asyncio
import uuid
from datetime import datetime

from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert

from core.bootstrap.service import BaseService
from core.events import Event
from core.events.types import EventTypes
from core.messaging.streams import SIGNALS
from core.db.session import AsyncSessionLocal
from core.db.models.signal import Signal


class SignalPersistenceService(BaseService):

    async def register_handlers(self) -> None:
        await self.event_bus.ensure_group(
            SIGNALS,
            "signal-persister",
        )

        asyncio.create_task(
            self.event_bus.consume(
                stream=SIGNALS,
                group="signal-persister",
                consumer="signal-persister-1",
                handler=self.handle_event,
            )
        )

    async def handle_event(self, event: Event) -> None:
        if event.event_type != EventTypes.SIGNAL_TREND_DETECTED:
            return

        payload = event.payload

        async with AsyncSessionLocal() as session:
            stmt = pg_insert(Signal).values(
                id=event.event_id,
                category=payload.get("category"),
                message=payload.get("message"),
                confidence=payload.get("confidence"),
                trend_score=payload.get("trend_score"),
                composite_score=payload.get("composite_score"),
                keyword_burst=payload.get("keyword_burst"),
                top_keyword=payload.get("top_keyword"),
                story_id=payload.get("story_id"),
                signal_type=payload.get("signal_type", "trend"),
                created_at=event.timestamp,
            )

            stmt = stmt.on_conflict_do_nothing(
                index_elements=["id"],
            )

            result = await session.execute(stmt)
            await session.commit()

            if result.rowcount == 0:
                self.logger.debug(
                    "Duplicate signal ignored",
                    extra={"event_id": str(event.event_id)},
                )
            else:
                self.logger.info(
                    "Signal persisted",
                    extra={
                        "event_id": str(event.event_id),
                        "correlation_id": str(event.correlation_id),
                    },
    )

    async def run(self) -> None:
        while True:
            await asyncio.sleep(3600)
