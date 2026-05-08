import asyncio
import json
from typing import Any
from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self.clients: set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, ws: WebSocket):
        await ws.accept()
        async with self._lock:
            self.clients.add(ws)
        print(f"[ws] client connected ({len(self.clients)} total)")

    async def disconnect(self, ws: WebSocket):
        async with self._lock:
            self.clients.discard(ws)
        print(f"[ws] client disconnected ({len(self.clients)} total)")

    async def broadcast(self, message: dict[str, Any]):
        if not self.clients:
            return
        payload = json.dumps(message, default=str)
        dead: list[WebSocket] = []
        for ws in list(self.clients):
            try:
                await ws.send_text(payload)
            except Exception:
                dead.append(ws)
        if dead:
            async with self._lock:
                for ws in dead:
                    self.clients.discard(ws)


manager = ConnectionManager()