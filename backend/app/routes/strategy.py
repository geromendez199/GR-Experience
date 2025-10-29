"""Race strategy endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from starlette import status

from .. import schemas
from ..deps import get_parquet_store
from ..models import StrategyContext, StrategyEngine

router = APIRouter(prefix="/api/strategy", tags=["strategy"])


@router.post("/simulate", response_model=schemas.StrategyResponse)
async def simulate_strategy(
    payload: schemas.StrategyRequest,
    store=Depends(get_parquet_store),
) -> schemas.StrategyResponse:
    df = store.read_session(payload.session_id)
    if df.empty:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session not found")
    engine = StrategyEngine()
    context = StrategyContext(
        session_id=payload.session_id,
        target_position=payload.target_position,
        data=df,
    )
    result = engine.simulate(context)
    result["expected_gain_s"] = float(max(min(result["expected_gain_s"], 60.0), -60.0))
    return schemas.StrategyResponse(**result)
