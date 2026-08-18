"""Shared test fixtures. Each test gets an isolated SQLite file and storage dir."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app.core.config import Settings, get_settings


@pytest.fixture
def tmp_settings(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Settings:
    db_path = tmp_path / "inferno.db"
    storage = tmp_path / "models"
    storage.mkdir()
    monkeypatch.setenv("APP_NAME", "Inferno")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.setenv("DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    monkeypatch.setenv("DATABASE_AUTO_MIGRATE", "true")
    monkeypatch.setenv("MODEL_STORAGE_PATH", str(storage))
    monkeypatch.setenv("LOG_JSON", "false")
    monkeypatch.setenv("LOG_LEVEL", "WARNING")
    monkeypatch.setenv("AUTH_ENABLED", "false")
    monkeypatch.setenv("OIDC_ENABLED", "false")
    get_settings.cache_clear()
    settings = Settings()
    yield settings
    get_settings.cache_clear()


@pytest.fixture
def client(tmp_settings: Settings) -> Iterator[TestClient]:
    from app.main import create_app

    application = create_app(tmp_settings)
    with TestClient(application) as test_client:
        yield test_client
