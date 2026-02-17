import asyncio
import websockets

async def test():
    async with websockets.connect("ws://localhost:8001/ws/signals") as ws:
        print(await ws.recv())

asyncio.run(test())
