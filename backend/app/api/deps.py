"""FastAPI dependencies. Handlers should only orchestrate services."""

from __future__ import annotations

from fastapi import Request

from app.core.config import Settings
from app.services.system import SystemService


def get_settings_dep(request: Request) -> Settings:
    return request.app.state.settings


def get_system_service(request: Request) -> SystemService:
    return request.app.state.system_service
