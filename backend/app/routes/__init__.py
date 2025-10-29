"""API router registration."""
from fastapi import APIRouter

from . import sessions, strategy, telemetry, ws

api_router = APIRouter()
api_router.include_router(sessions.router)
api_router.include_router(telemetry.router)
api_router.include_router(strategy.router)
api_router.include_router(ws.router)

__all__ = ["api_router"]
