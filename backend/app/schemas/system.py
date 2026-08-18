from datetime import datetime

from pydantic import BaseModel, Field


class HealthResponse(BaseModel):
    status: str = Field(examples=["ok"])
    service: str
    time: datetime


class ReadinessCheck(BaseModel):
    name: str
    healthy: bool
    detail: str | None = None


class ReadinessResponse(BaseModel):
    status: str = Field(examples=["ok", "degraded"])
    service: str
    checks: list[ReadinessCheck]


class SystemInfoResponse(BaseModel):
    name: str
    version: str
    environment: str
    auth_enabled: bool
    oidc_enabled: bool
    model_storage_path: str
