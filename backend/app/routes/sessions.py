"""Session ingestion and telemetry routes."""
from __future__ import annotations

from pathlib import Path

import orjson
from fastapi import APIRouter, Depends, HTTPException, Query
from starlette import status

from .. import schemas
from ..config import Settings
from ..dataio import compute_session_metrics, extract_zip, normalize_files
from ..deps import get_parquet_store, get_redis, get_settings_dependency

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.post("/{session_id}/ingest", response_model=schemas.SessionIngestResponse)
async def ingest_session(
    session_id: str,
    payload: schemas.IngestRequest,
    settings: Settings = Depends(get_settings_dependency),
    store=Depends(get_parquet_store),
    redis=Depends(get_redis),
) -> schemas.SessionIngestResponse:
    zip_path = _resolve_zip_path(payload.zip_path, settings)
    staging_dir = settings.data_dir / "staging" / session_id
    extracted_files = extract_zip(zip_path, staging_dir)
    track = _infer_track(zip_path)
    normalized = normalize_files(extracted_files, session_id=session_id, track=track)
    store.write_session(normalized)
    metrics = compute_session_metrics(normalized)
    cache_key = f"session:{session_id}:metrics"
    await redis.set(
        cache_key,
        orjson.dumps(metrics).decode("utf-8"),
        ex=settings.redis_cache_ttl_seconds,
    )
    return schemas.SessionIngestResponse(session_id=session_id, track=track, metrics=metrics)


@router.get("/{session_id}/laps", response_model=schemas.LapResponse)
async def get_laps(
    session_id: str,
    car_id: str | None = Query(None),
    offset: int = Query(0, ge=0),
    limit: int = Query(500, ge=1, le=5000),
    settings: Settings = Depends(get_settings_dependency),
    store=Depends(get_parquet_store),
    redis=Depends(get_redis),
) -> schemas.LapResponse:
    cache_key = f"session:{session_id}:laps:{car_id}:{offset}:{limit}"
    cached = await redis.get(cache_key)
    if cached:
        payload = orjson.loads(cached)
        return schemas.LapResponse(**payload)

    df = store.scan_laps(session_id=session_id, car_id=car_id, offset=offset, limit=limit)
    if df.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No telemetry data found")
    track = df["track"].iloc[0]
    frames = []
    for row in df.to_dict("records"):
        payload = {field: row[field] for field in schemas.TelemetryFrame.__fields__ if field in row}
        frames.append(schemas.TelemetryFrame(**payload))
    response = schemas.LapResponse(
        session_id=session_id,
        track=track,
        data=frames,
        total=len(df),
        offset=offset,
        limit=limit,
    )
    await redis.set(cache_key, response.json(), ex=settings.redis_cache_ttl_seconds)
    return response


def _resolve_zip_path(path_str: str, settings: Settings) -> Path:
    path = Path(path_str)
    if not path.is_absolute():
        path = (settings.data_dir / path).resolve()
    if not path.exists():
        candidate = settings.data_dir / "input" / path.name
        if candidate.exists():
            path = candidate.resolve()
    if settings.data_dir not in path.parents and path != settings.data_dir:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="zip_path must reside inside DATA_DIR",
        )
    return path


def _infer_track(zip_path: Path) -> str:
    stem = zip_path.stem
    return stem.replace("-", " ").replace("_", " ").title()
