"""Entry point for the FastAPI application."""
from __future__ import annotations

from fastapi import FastAPI, WebSocket

from .api.routes import router as api_router

app = FastAPI(title="GR Experience API", version="0.1.0")
app.include_router(api_router, prefix="/api")


@app.websocket("/ws/live-telemetry")
async def websocket_endpoint(websocket: WebSocket) -> None:
    """Minimal WebSocket endpoint used for streaming telemetry frames.

    The implementation currently performs a simple echo to demonstrate the
    integration between the backend and the frontend. Real telemetry
    broadcasting can be plugged into this function later.
    """

    await websocket.accept()
    try:
        while True:
            message = await websocket.receive_text()
            await websocket.send_json({"type": "echo", "payload": message})
    except Exception:
        await websocket.close()
