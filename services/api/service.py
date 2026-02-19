from fastapi import FastAPI
from core.bootstrap.service import BaseService

from fastapi.responses import HTMLResponse
from sqlalchemy import select

from core.db.session import AsyncSessionLocal
from core.db.models.signal import Signal



class APIService(BaseService):

    def __init__(self, name, event_bus):
        super().__init__(name, event_bus)
        self.app = FastAPI()

        self._register_routes()

    async def register_handlers(self):
        # API does not consume events (for now)
        pass

    def _register_routes(self):

        @self.app.get("/")
        async def home():
            return HTMLResponse("""
            <html>
            <body>
            <script>
            const ws = new WebSocket("ws://localhost:8001/ws/signals");
            ws.onmessage = (event) => {
                console.log("Signal:", JSON.parse(event.data));
            };
            </script>
            </body>
            </html>
            """)


        @self.app.get("/signals")
        async def get_signals(limit: int = 50):
            async with AsyncSessionLocal() as session:
                stmt = (
                    select(Signal)
                    .order_by(Signal.created_at.desc())
                    .limit(limit)
                )

                result = await session.execute(stmt)
                rows = result.scalars().all()

                signals = [
                    {
                        "id": str(row.id),
                        "category": row.category,
                        "message": row.message,
                        "confidence": row.confidence,
                        "created_at": row.created_at.isoformat(),
                    }
                    for row in rows
                ]

                return {
                    "count": len(signals),
                    "signals": signals,
                }

    async def run(self):
        import uvicorn
        config = uvicorn.Config(
            self.app,
            host="0.0.0.0",
            port=8000,
            loop="asyncio",
        )

        server = uvicorn.Server(config)

        await server.serve()