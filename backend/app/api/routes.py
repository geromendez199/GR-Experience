"""REST API routes for the GR Experience backend."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List

from fastapi import APIRouter, HTTPException

from ..schemas.analytics import EventAnalytics, LapComparison, StrategyRecommendation
from ..services.analytics import (
    compute_event_analytics,
    compute_lap_comparison,
    recommend_strategy,
)

router = APIRouter()


@router.get("/health", tags=["system"])
def healthcheck() -> Dict[str, str]:
    """Return a simple health status payload."""

    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/events/{event_id}/analytics", response_model=EventAnalytics, tags=["analytics"])
def get_event_analytics(event_id: str) -> EventAnalytics:
    """Return aggregate statistics for the selected event."""

    analytics = compute_event_analytics(event_id)
    if analytics is None:
        raise HTTPException(status_code=404, detail="Event not found")
    return analytics


@router.get(
    "/events/{event_id}/drivers/{driver_id}/lap-comparison",
    response_model=LapComparison,
    tags=["analytics"],
)
def compare_driver_laps(event_id: str, driver_id: str, reference_lap: int, target_lap: int) -> LapComparison:
    """Compare two laps using a simplified Dynamic Time Warping approach."""

    comparison = compute_lap_comparison(event_id, driver_id, reference_lap, target_lap)
    if comparison is None:
        raise HTTPException(status_code=404, detail="Lap comparison unavailable")
    return comparison


@router.get(
    "/events/{event_id}/strategy",
    response_model=List[StrategyRecommendation],
    tags=["strategy"],
)
def get_strategy(event_id: str, current_lap: int) -> List[StrategyRecommendation]:
    """Provide strategy guidance for the specified event and lap."""

    return recommend_strategy(event_id, current_lap)
