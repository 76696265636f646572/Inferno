from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.core.config import Settings, redact_database_url


def test_safe_dump_excludes_secrets() -> None:
    settings = Settings(
        hf_token="hf_super_secret",  # noqa: S106
        oidc_client_secret="oidc-secret",  # noqa: S106
        database_url="postgresql+asyncpg://inferno:password@db:5432/inferno",
    )
    dumped = settings.safe_dump()
    serialized = str(dumped)
    assert "hf_super_secret" not in serialized
    assert "oidc-secret" not in serialized
    assert "password" not in serialized
    assert dumped["hf_token_configured"] is True
    assert dumped["oidc_client_secret_configured"] is True
    assert dumped["database_url"] == "postgresql+asyncpg://***@db:5432/inferno"


def test_redact_database_url_without_credentials() -> None:
    url = "sqlite+aiosqlite:///./inferno.db"
    assert redact_database_url(url) == url


def test_empty_secrets_become_none() -> None:
    settings = Settings(hf_token="", oidc_client_secret="")
    assert settings.hf_token is None
    assert settings.oidc_client_secret is None


def test_cors_origin_list_splits_csv() -> None:
    settings = Settings(cors_origins="http://localhost:3000, http://127.0.0.1:3000")
    assert settings.cors_origin_list == ["http://localhost:3000", "http://127.0.0.1:3000"]


def test_oidc_requires_auth() -> None:
    with pytest.raises(ValidationError):
        Settings(auth_enabled=False, oidc_enabled=True, oidc_issuer_url="https://idp.example", oidc_client_id="app")
