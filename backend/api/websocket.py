import logging
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger("gardenflow.ws")


class BroadcastRegistry:
    def __init__(self):
        self._clients: set[WebSocket] = set()

    async def connect(self, ws: WebSocket) -> None:
        await ws.accept()
        self._clients.add(ws)
        logger.debug("WS client connected, total=%d", len(self._clients))

    def disconnect(self, ws: WebSocket) -> None:
        self._clients.discard(ws)
        logger.debug("WS client disconnected, total=%d", len(self._clients))

    async def broadcast(self, data: dict) -> None:
        dead: set[WebSocket] = set()
        for ws in list(self._clients):
            try:
                await ws.send_json(data)
            except Exception:
                dead.add(ws)
        self._clients -= dead

    @property
    def client_count(self) -> int:
        return len(self._clients)


registry = BroadcastRegistry()
