"""Download job HTTP surface. Implemented in Phase 2."""

from fastapi import APIRouter

router = APIRouter(prefix="/downloads", tags=["Downloads"])
