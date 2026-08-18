from datetime import UTC, datetime

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.schemas.ws import SystemStatusData, WebSocketEvent
from app.websocket.hub import WebSocketHub

router = APIRouter()


def _hello_event(service: str) -> WebSocketEvent:
    data = SystemStatusData(status="healthy", service=service)
    return WebSocketEvent(
        type="system.status",
        data=data.model_dump(),
        timestamp=datetime.now(UTC),
    )


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket) -> None:
    hub: WebSocketHub = websocket.app.state.ws_hub
    settings = websocket.app.state.settings
    await hub.connect(websocket)
    try:
        await hub.send(websocket, _hello_event(settings.app_name))
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        hub.disconnect(websocket)
    except Exception:
        hub.disconnect(websocket)
        raise
