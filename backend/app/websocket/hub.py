"""In-memory WebSocket fan-out. Typed events only — no ad-hoc dicts."""

from __future__ import annotations

import logging
from collections.abc import Iterable

from fastapi import WebSocket

from app.schemas.ws import WebSocketEvent

logger = logging.getLogger(__name__)


class WebSocketHub:
    def __init__(self) -> None:
        self._connections: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._connections.discard(websocket)

    async def send(self, websocket: WebSocket, event: WebSocketEvent) -> None:
        await websocket.send_json(event.model_dump(mode="json"))

    async def broadcast(self, event: WebSocketEvent, *, skip: Iterable[WebSocket] = ()) -> None:
        skipped = set(skip)
        stale: list[WebSocket] = []
        payload = event.model_dump(mode="json")
        for connection in list(self._connections):
            if connection in skipped:
                continue
            try:
                await connection.send_json(payload)
            except Exception:
                logger.debug("dropping stale websocket", exc_info=True)
                stale.append(connection)
        for connection in stale:
            self.disconnect(connection)
