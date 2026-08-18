from fastapi import APIRouter

from app.api.v1.endpoints import (
    analytics,
    api_keys,
    auth,
    downloads,
    inference,
    models,
    runtimes,
    system,
)

api_router = APIRouter()
api_router.include_router(system.router)
api_router.include_router(models.router)
api_router.include_router(downloads.router)
api_router.include_router(runtimes.router)
api_router.include_router(inference.router)
api_router.include_router(analytics.router)
api_router.include_router(auth.router)
api_router.include_router(api_keys.router)
