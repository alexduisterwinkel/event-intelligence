import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from core.bootstrap.service import BaseService
from core.events import Event
from core.events.types import EventTypes
from core.messaging.streams import SIGNALS

from .connection_manager import ConnectionManager


class RealtimeService(BaseService):

    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)

        self.manager = ConnectionManager()
        self.app = FastAPI()

        self._register_routes()

    async def register_handlers(self):
        await self.event_bus.subscribe(
            EventTypes.SIGNAL_TREND_DETECTED,
            self.handle_signal_detected,
        )

    async def register_handlers(self) -> None:
            await self.event_bus.ensure_group(
                SIGNALS,
                "realtime",
            )

            asyncio.create_task(
                self.event_bus.consume(
                    stream=SIGNALS,
                    group="realtime",
                    consumer="realtime-1",
                    handler=self.handle_event,
                )
            )

    def _register_routes(self):

        @self.app.websocket("/ws/signals")
        async def websocket_endpoint(websocket: WebSocket):
            await self.manager.connect(websocket)

            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.manager.disconnect(websocket)

    async def handle_event(self, event: Event):

        if event.event_type != EventTypes.NEWS_ARTICLE_ENRICHED:
            return
        await self.manager.broadcast(event.payload)

    async def run(self):
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8001,
            loop="asyncio",
        )

        server = uvicorn.Server(config)

        await server.serve()
