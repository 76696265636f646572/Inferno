"""Model registry HTTP surface. Implemented in Phase 1."""

from fastapi import APIRouter

router = APIRouter(prefix="/models", tags=["Models"])
