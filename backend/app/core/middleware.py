"""ASGI middleware for request IDs, timing, and request-size limits."""

from __future__ import annotations

import json
import logging
import time
import uuid
from collections.abc import Awaitable, Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.errors import error_payload
from app.core.logging import request_id_ctx

logger = logging.getLogger(__name__)

REQUEST_ID_HEADER = "X-Request-ID"


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        incoming = request.headers.get(REQUEST_ID_HEADER)
        request_id = incoming.strip() if incoming else str(uuid.uuid4())
        token = request_id_ctx.set(request_id)
        started = time.perf_counter()
        try:
            response = await call_next(request)
        except Exception:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.exception(
                "unhandled_request_error",
                extra={"duration_ms": duration_ms, "status_code": 500},
            )
            raise
        else:
            duration_ms = round((time.perf_counter() - started) * 1000, 2)
            logger.info(
                "%s %s",
                request.method,
                request.url.path,
                extra={"duration_ms": duration_ms, "status_code": response.status_code},
            )
            response.headers[REQUEST_ID_HEADER] = request_id
            return response
        finally:
            request_id_ctx.reset(token)


class MaxBodySizeMiddleware:
    """Reject requests whose Content-Length exceeds the configured limit."""

    def __init__(self, app: ASGIApp, max_bytes: int) -> None:
        self.app = app
        self.max_bytes = max_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] == "http":
            headers = {k.decode("latin-1").lower(): v.decode("latin-1") for k, v in scope.get("headers", [])}
            length = headers.get("content-length")
            if length is not None:
                try:
                    size = int(length)
                except ValueError:
                    size = 0
                if size > self.max_bytes:
                    body = error_payload(
                        "REQUEST_TOO_LARGE",
                        "The request body exceeds the allowed size.",
                    )
                    response = Response(
                        content=json.dumps(body),
                        status_code=413,
                        media_type="application/json",
                    )
                    await response(scope, receive, send)
                    return
        await self.app(scope, receive, send)
