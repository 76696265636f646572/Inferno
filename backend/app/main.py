"""Inferno API entrypoint."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app import __version__
from app.api.v1.router import api_router
from app.core.config import Settings, get_settings
from app.core.errors import register_exception_handlers
from app.core.logging import configure_logging
from app.core.middleware import MaxBodySizeMiddleware, RequestContextMiddleware
from app.db.migrate import run_migrations
from app.db.session import create_engine, create_session_factory
from app.schemas.system import HealthResponse
from app.services.system import SystemService
from app.websocket.hub import WebSocketHub
from app.websocket.router import router as ws_router

logger = logging.getLogger(__name__)

OPENAPI_TAGS = [
    {"name": "Models", "description": "Local model registry."},
    {"name": "Downloads", "description": "Background model downloads and verification."},
    {"name": "Runtimes", "description": "Inference runtime lifecycle (llama.cpp first)."},
    {"name": "Inference", "description": "OpenAI-compatible chat and completions gateway."},
    {"name": "Analytics", "description": "Request, token, and performance metrics."},
    {"name": "Authentication", "description": "Optional OIDC login and sessions."},
    {"name": "API Keys", "description": "Gateway credentials for inference clients."},
    {"name": "System", "description": "Health, readiness, and control-plane status."},
]


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging(level=settings.log_level, json_logs=settings.log_json)

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        logger.info("starting", extra={"environment": settings.environment})
        settings.ensure_storage_dir()
        engine = create_engine(settings)
        session_factory = create_session_factory(engine)
        app.state.settings = settings
        app.state.engine = engine
        app.state.session_factory = session_factory
        app.state.ws_hub = WebSocketHub()
        app.state.system_service = SystemService(settings, session_factory)
        if settings.database_auto_migrate:
            await run_migrations(settings.database_url)
        yield
        await engine.dispose()
        logger.info("stopped")

    application = FastAPI(
        title=settings.app_name,
        description="Your local AI control plane.",
        version=__version__,
        openapi_tags=OPENAPI_TAGS,
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
    )
    application.state.settings = settings

    application.add_middleware(RequestContextMiddleware)
    application.add_middleware(MaxBodySizeMiddleware, max_bytes=settings.max_request_bytes)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origin_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    register_exception_handlers(application)
    application.include_router(api_router, prefix="/api/v1")
    application.include_router(ws_router)

    @application.get("/health", response_model=HealthResponse, tags=["System"], summary="Process liveness")
    async def root_health(request: Request) -> HealthResponse:
        service: SystemService = request.app.state.system_service
        return service.liveness()

    @application.get("/ready", response_model=HealthResponse, tags=["System"], include_in_schema=False)
    async def root_ready(request: Request) -> JSONResponse:
        service: SystemService = request.app.state.system_service
        result = await service.readiness()
        status_code = 200 if result.status == "ok" else 503
        return JSONResponse(status_code=status_code, content=result.model_dump(mode="json"))

    return application


app = create_app()
