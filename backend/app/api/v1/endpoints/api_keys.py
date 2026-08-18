"""API key management. Implemented in Phase 3."""

from fastapi import APIRouter

router = APIRouter(prefix="/api-keys", tags=["API Keys"])
