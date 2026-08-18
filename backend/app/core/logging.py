"""JSON-capable structured logging. Secrets are never written."""

from __future__ import annotations

import json
import logging
import re
import sys
from contextvars import ContextVar
from datetime import UTC, datetime
from typing import Any

request_id_ctx: ContextVar[str | None] = ContextVar("request_id", default=None)
runtime_id_ctx: ContextVar[str | None] = ContextVar("runtime_id", default=None)
model_id_ctx: ContextVar[str | None] = ContextVar("model_id", default=None)
download_id_ctx: ContextVar[str | None] = ContextVar("download_id", default=None)

_SECRET_KEYS = re.compile(
    r"(token|secret|password|authorization|api[_-]?key|hf_token|client_secret)",
    re.IGNORECASE,
)
_REDACTED = "***"


def redact_value(key: str, value: Any) -> Any:
    if _SECRET_KEYS.search(key):
        return _REDACTED
    return value


class ContextFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_ctx.get()
        record.runtime_id = runtime_id_ctx.get()
        record.model_id = model_id_ctx.get()
        record.download_id = download_id_ctx.get()
        return True


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        for key in ("request_id", "runtime_id", "model_id", "download_id", "duration_ms", "status_code"):
            value = getattr(record, key, None)
            if value is not None:
                payload[key] = value
        if record.exc_info:
            payload["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(payload, default=str)


class TextFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        request_id = getattr(record, "request_id", None) or "-"
        base = f"{record.levelname} {request_id} {record.name} {record.getMessage()}"
        if record.exc_info:
            return f"{base}\n{self.formatException(record.exc_info)}"
        return base


def configure_logging(*, level: str, json_logs: bool) -> None:
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if json_logs else TextFormatter())
    handler.addFilter(ContextFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(level)

    logging.getLogger("uvicorn.access").disabled = True
