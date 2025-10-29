"""Telemetry analytics endpoints."""
from __future__ import annotations

import orjson
from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from .. import schemas
from ..config import Settings
from ..dataio import compute_session_metrics
from ..deps import get_parquet_store, get_redis, get_settings_dependency
from ..models import compute_dtw_alignment

router = APIRouter(prefix="/api", tags=["telemetry"])


@router.get("/sessions/{session_id}/summary")
async def get_session_summary(
    session_id: str,
    store=Depends(get_parquet_store),
    redis=Depends(get_redis),
    settings: Settings = Depends(get_settings_dependency),
):
    cache_key = f"session:{session_id}:metrics"
    cached = await redis.get(cache_key)
    if cached:
        return orjson.loads(cached)

    df = store.read_session(session_id=session_id)
    if df.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    metrics = compute_session_metrics(df)
    await redis.set(
        cache_key,
        orjson.dumps(metrics).decode("utf-8"),
        ex=settings.redis_cache_ttl_seconds,
    )
    return metrics


@router.post("/training/compare-lap", response_model=schemas.TrainingComparisonResponse)
async def compare_lap(
    payload: schemas.TrainingComparisonRequest,
    store=Depends(get_parquet_store),
) -> schemas.TrainingComparisonResponse:
    filters = [("lap", "eq", payload.lap)]
    ideal_df = store.read_session(payload.session_id, filters=filters + [("car_id", "eq", payload.ideal_car_id)])
    ref_df = store.read_session(payload.session_id, filters=filters + [("car_id", "eq", payload.reference_car_id)])
    if ideal_df.empty or ref_df.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lap data unavailable for comparison")
    dtw_result = compute_dtw_alignment(ideal_df, ref_df, value_column=payload.metric)
    return schemas.TrainingComparisonResponse(**dtw_result)
