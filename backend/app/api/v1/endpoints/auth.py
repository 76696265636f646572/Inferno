"""Optional OIDC authentication. Implemented in Phase 5."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Authentication"])
