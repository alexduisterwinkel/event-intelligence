from fastapi import FastAPI
from core.bootstrap.service import BaseService


class APIService(BaseService):

    def __init__(self, name, event_bus, intelligence_service):
        super().__init__(name, event_bus)
        self.intelligence_service = intelligence_service
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
        async def get_signals():
            return {
                "count": len(self.intelligence_service.signals),
                "signals": self.intelligence_service.signals,
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