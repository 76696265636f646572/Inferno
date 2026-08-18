"""Typed process configuration loaded from environment variables."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Literal, Self

from pydantic import AliasChoices, Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Infrastructure configuration. Secrets are never included in `safe_dump`."""

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_name: str = "Inferno"
    environment: Literal["development", "production", "test"] = "development"

    database_url: str = "sqlite+aiosqlite:///./inferno.db"
    database_auto_migrate: bool = True

    model_storage_path: Path = Path("./models")

    llama_cpp_binary: Path = Path("/usr/local/bin/llama-server")

    hf_token: SecretStr | None = None

    auth_enabled: bool = False
    oidc_enabled: bool = False
    oidc_issuer_url: str | None = None
    oidc_client_id: str | None = None
    oidc_client_secret: SecretStr | None = None

    cors_origins: str = "http://localhost:3000"

    host: str = "0.0.0.0"
    port: int = Field(default=8000, ge=1, le=65535)

    log_level: str = "INFO"
    log_json: bool = Field(
        default=True,
        validation_alias=AliasChoices("LOG_JSON", "log_json"),
    )

    request_timeout_seconds: float = 60.0
    max_request_bytes: int = 10 * 1024 * 1024

    @field_validator("hf_token", "oidc_client_secret", "oidc_issuer_url", "oidc_client_id", mode="before")
    @classmethod
    def empty_string_to_none(cls, value: object) -> object:
        if value == "":
            return None
        return value

    @field_validator("log_level")
    @classmethod
    def normalize_log_level(cls, value: str) -> str:
        return value.upper()

    @model_validator(mode="after")
    def oidc_requires_auth_fields(self) -> Self:
        if self.oidc_enabled and not self.auth_enabled:
            msg = "OIDC_ENABLED=true requires AUTH_ENABLED=true"
            raise ValueError(msg)
        if self.oidc_enabled and not (self.oidc_issuer_url and self.oidc_client_id):
            msg = "OIDC_ENABLED=true requires OIDC_ISSUER_URL and OIDC_CLIENT_ID"
            raise ValueError(msg)
        return self

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")

    def ensure_storage_dir(self) -> Path:
        self.model_storage_path.mkdir(parents=True, exist_ok=True)
        return self.model_storage_path

    def safe_dump(self) -> dict[str, object]:
        """Serialize settings without secrets for diagnostics."""
        return {
            "app_name": self.app_name,
            "environment": self.environment,
            "database_url": redact_database_url(self.database_url),
            "database_auto_migrate": self.database_auto_migrate,
            "model_storage_path": str(self.model_storage_path),
            "llama_cpp_binary": str(self.llama_cpp_binary),
            "hf_token_configured": self.hf_token is not None,
            "auth_enabled": self.auth_enabled,
            "oidc_enabled": self.oidc_enabled,
            "oidc_issuer_url": self.oidc_issuer_url,
            "oidc_client_id": self.oidc_client_id,
            "oidc_client_secret_configured": self.oidc_client_secret is not None,
            "cors_origins": self.cors_origin_list,
            "host": self.host,
            "port": self.port,
            "log_level": self.log_level,
            "log_json": self.log_json,
        }


def redact_database_url(url: str) -> str:
    """Strip credentials from a SQLAlchemy URL for logs."""
    if "://" not in url:
        return url
    scheme, rest = url.split("://", 1)
    if "@" not in rest:
        return url
    _creds, host = rest.split("@", 1)
    return f"{scheme}://***@{host}"


@lru_cache
def get_settings() -> Settings:
    return Settings()
