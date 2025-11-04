"""WebSocket streaming for live telemetry."""
from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect

from ..deps import get_parquet_store
from ..schemas import WebSocketFrame

router = APIRouter()


@router.websocket("/ws/{session_id}")
async def session_stream(
    websocket: WebSocket,
    session_id: str,
    store=Depends(get_parquet_store),
) -> None:
    await websocket.accept()
    try:
        df = store.read_session(session_id)
        if df.empty:
            await websocket.send_json({"error": "session not found"})
            await websocket.close()
            return
        df = df.sort_values(["t_ms"])
        best_lap = df.groupby("car_id")["lap_time_s"].min().to_dict()
        for _, row in df.iterrows():
            delta = (
                float(row["lap_time_s"] - best_lap[str(row["car_id"])])
                if row["car_id"] in best_lap
                else 0.0
            )
            frame = WebSocketFrame(
                t=int(row["t_ms"]),
                car_id=str(row["car_id"]),
                lap=int(row["lap"]),
                delta_s=delta,
                flag=str(row.get("flag_state", "green")),
            )
            await websocket.send_json(frame.dict(by_alias=True))
            await asyncio.sleep(0.01)
    except WebSocketDisconnect:
        return
