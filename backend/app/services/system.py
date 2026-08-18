"""System health and readiness checks. Keep I/O out of route handlers."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app import __version__
from app.core.config import Settings
from app.schemas.system import HealthResponse, ReadinessCheck, ReadinessResponse, SystemInfoResponse


class SystemService:
    def __init__(
        self,
        settings: Settings,
        session_factory: async_sessionmaker[AsyncSession],
    ) -> None:
        self._settings = settings
        self._session_factory = session_factory

    def liveness(self) -> HealthResponse:
        return HealthResponse(
            status="ok",
            service=self._settings.app_name,
            time=datetime.now(UTC),
        )

    async def readiness(self) -> ReadinessResponse:
        checks = [await self._database_check(), self._storage_check()]
        healthy = all(check.healthy for check in checks)
        return ReadinessResponse(
            status="ok" if healthy else "degraded",
            service=self._settings.app_name,
            checks=checks,
        )

    def info(self) -> SystemInfoResponse:
        return SystemInfoResponse(
            name=self._settings.app_name,
            version=__version__,
            environment=self._settings.environment,
            auth_enabled=self._settings.auth_enabled,
            oidc_enabled=self._settings.oidc_enabled,
            model_storage_path=str(self._settings.model_storage_path),
        )

    async def _database_check(self) -> ReadinessCheck:
        try:
            async with self._session_factory() as session:
                await session.execute(text("SELECT 1"))
        except Exception as exc:
            return ReadinessCheck(name="database", healthy=False, detail=str(exc.__class__.__name__))
        return ReadinessCheck(name="database", healthy=True)

    def _storage_check(self) -> ReadinessCheck:
        path = Path(self._settings.model_storage_path)
        try:
            path.mkdir(parents=True, exist_ok=True)
            if not path.exists() or not path.is_dir():
                return ReadinessCheck(name="storage", healthy=False, detail="not a directory")
        except OSError as exc:
            return ReadinessCheck(name="storage", healthy=False, detail=exc.__class__.__name__)
        return ReadinessCheck(name="storage", healthy=True)
