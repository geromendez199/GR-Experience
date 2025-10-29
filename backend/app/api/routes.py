"""Additional analytics and event-focused API routes."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from .. import schemas
from ..deps import get_parquet_store
from ..models import StrategyContext, StrategyEngine, compute_dtw_alignment

router = APIRouter(prefix="/api", tags=["events"])


@router.get("/health", tags=["health"])
async def health() -> dict[str, str]:
    """Return a simple healthcheck payload."""
    return {"status": "ok"}


@router.get("/events/{event_id}/analytics")
async def event_analytics(event_id: str, store=Depends(get_parquet_store)) -> dict[str, Any]:
    """Return aggregate analytics for a given event/session."""

    df = store.read_session(event_id)
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    track = None
    if "track" in df.columns and not df["track"].isna().all():
        track = str(df["track"].iloc[0])

    # Filter laps with a reasonable lap time to avoid outliers from pits or invalid data.
    valid_laps = df[df["lap_time_s"].between(20, 300, inclusive="both")]
    fastest = (
        valid_laps.groupby("car_id")["lap_time_s"].min().dropna().to_dict()
        if not valid_laps.empty
        else {}
    )

    stint_summary: list[dict[str, Any]] = []
    if {"car_id", "tire_set"}.issubset(df.columns):
        grouped = df.groupby(["car_id", "tire_set"])
        for (car_id, tire_set), stint_df in grouped:
            if stint_df.empty:
                continue
            stint_summary.append(
                {
                    "car_id": str(car_id),
                    "tire_set": str(tire_set),
                    "start_lap": int(stint_df["lap"].min()),
                    "end_lap": int(stint_df["lap"].max()),
                    "avg_pace_s": float(stint_df["lap_time_s"].mean()),
                }
            )

    summary = {
        "fastest_lap": {str(car): float(time) for car, time in fastest.items()},
        "valid_laps": int(valid_laps["lap"].nunique()) if not valid_laps.empty else 0,
        "stints": stint_summary,
    }

    return {"event_id": event_id, "track": track, "summary": summary}


@router.get("/events/{event_id}/drivers/{driver_id}/lap-comparison")
async def compare_driver_lap(
    event_id: str,
    driver_id: str,
    *,
    lap: int = Query(..., ge=1, description="Lap number to analyse"),
    reference_driver_id: str = Query(
        ..., description="Driver identifier to compare against"
    ),
    metric: str = Query(
        "speed_kph", description="Telemetry metric column to align using DTW"
    ),
    store=Depends(get_parquet_store),
) -> dict[str, Any]:
    """Compare two drivers on a specific lap using Dynamic Time Warping."""

    df = store.read_session(event_id)
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    required_columns = {"car_id", "lap", metric}
    missing = required_columns.difference(df.columns)
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Missing telemetry columns: {', '.join(sorted(missing))}",
        )

    driver_lap = df[(df["car_id"] == driver_id) & (df["lap"] == lap)]
    if driver_lap.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver lap not found",
        )

    reference_lap = df[(df["car_id"] == reference_driver_id) & (df["lap"] == lap)]
    if reference_lap.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reference driver lap not found",
        )

    comparison = compute_dtw_alignment(driver_lap, reference_lap, value_column=metric)

    return {
        "event_id": event_id,
        "driver_id": driver_id,
        "reference_driver_id": reference_driver_id,
        "lap": lap,
        "metric": metric,
        **comparison,
    }


@router.post("/events/{event_id}/strategy", response_model=schemas.StrategyResponse)
async def event_strategy(
    event_id: str,
    payload: schemas.StrategyRequest,
    store=Depends(get_parquet_store),
) -> schemas.StrategyResponse:
    """Simulate a pit strategy for an event/session."""

    session_id = payload.session_id
    if session_id != event_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Body session_id must match the requested event",
        )

    df = store.read_session(session_id)
    if df.empty:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Event not found"
        )

    engine = StrategyEngine()
    context = StrategyContext(
        session_id=session_id,
        target_position=payload.target_position,
        data=df,
    )
    result = engine.simulate(context)
    result["expected_gain_s"] = float(
        max(min(result["expected_gain_s"], 60.0), -60.0)
    )
    return schemas.StrategyResponse(**result)
