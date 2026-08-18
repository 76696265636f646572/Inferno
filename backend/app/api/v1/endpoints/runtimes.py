"""Runtime manager HTTP surface. Implemented in Phase 1."""

from fastapi import APIRouter

router = APIRouter(prefix="/runtimes", tags=["Runtimes"])
