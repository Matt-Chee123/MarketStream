import asyncio
import websockets

class WebsocketClient:
    def __init__(self, url, on_message, reconnect=True):
        self.url = url
        self.on_message = on_message
        self.reconnect = reconnect

    async def connect(self):
        while True:
            try:
                async with websockets.connect(self.url, ping_interval=20) as ws:
                    async for msg in ws:
                        await self.on_message(msg)

            except Exception as e:
                print(f"[WS ERROR] {e}")
                if not self.reconnect:
                    break
                await asyncio.sleep(5)