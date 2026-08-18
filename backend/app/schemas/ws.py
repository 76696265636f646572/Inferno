from datetime import UTC, datetime
from typing import Any, Literal

from pydantic import BaseModel, Field


class WebSocketEvent(BaseModel):
    """Typed envelope for every `/ws` message."""

    type: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class SystemStatusData(BaseModel):
    status: Literal["healthy", "degraded", "unknown"]
    service: str
