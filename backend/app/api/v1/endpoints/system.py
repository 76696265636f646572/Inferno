from fastapi import APIRouter, Depends

from app.api.deps import get_system_service
from app.schemas.errors import ErrorResponse
from app.schemas.system import HealthResponse, ReadinessResponse, SystemInfoResponse
from app.services.system import SystemService

router = APIRouter(prefix="/system", tags=["System"])


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Liveness probe",
)
async def health(service: SystemService = Depends(get_system_service)) -> HealthResponse:
    return service.liveness()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={503: {"model": ErrorResponse}},
    summary="Readiness probe",
)
async def ready(service: SystemService = Depends(get_system_service)) -> ReadinessResponse:
    return await service.readiness()


@router.get(
    "/info",
    response_model=SystemInfoResponse,
    summary="Public system information",
)
async def info(service: SystemService = Depends(get_system_service)) -> SystemInfoResponse:
    return service.info()
