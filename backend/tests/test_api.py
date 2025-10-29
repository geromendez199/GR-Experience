from __future__ import annotations

import zipfile
from pathlib import Path

import fakeredis.aioredis
import pytest
from fastapi.testclient import TestClient

from backend.app.config import Settings
from backend.app.dataio.parquet_store import ParquetStore
from backend.app.deps import get_parquet_store, get_redis, get_settings_dependency
from backend.app.main import app


@pytest.fixture()
def client(tmp_path: Path) -> TestClient:
    data_dir = tmp_path
    (data_dir / "input").mkdir(parents=True, exist_ok=True)
    csv_path = Path("data/samples/barber-motorsports-park.csv").resolve()
    sample_zip = data_dir / "input" / "barber-motorsports-park.zip"
    with zipfile.ZipFile(sample_zip, "w") as zf:
        zf.write(csv_path, arcname="telemetry.csv")

    settings = Settings(
        api_host="0.0.0.0",
        api_port=8000,
        cors_origins="http://testserver",
        data_dir=data_dir,
        redis_url="redis://localhost:6379/0",
        next_public_api_base_url="http://testserver",
        model_dir=data_dir / "models",
    )

    store = ParquetStore(root=data_dir / "parquet", partition_cols=["session_id", "track"])

    async def _redis_override():
        client = fakeredis.aioredis.FakeRedis()
        try:
            yield client
        finally:
            await client.close()

    app.dependency_overrides[get_settings_dependency] = lambda: settings
    app.dependency_overrides[get_parquet_store] = lambda: store
    app.dependency_overrides[get_redis] = _redis_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


def test_ingest_and_query(client: TestClient) -> None:
    response = client.post(
        "/api/sessions/test_session/ingest",
        json={"zip_path": "input/barber-motorsports-park.zip"},
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["session_id"] == "test_session"
    assert "fastest_lap" in payload["metrics"]

    laps = client.get(
        "/api/sessions/test_session/laps",
        params={"car_id": "GR21", "limit": 20},
    )
    assert laps.status_code == 200
    data = laps.json()
    assert data["data"]

    summary = client.get("/api/sessions/test_session/summary")
    assert summary.status_code == 200
    strategy = client.post("/api/strategy/simulate", json={"session_id": "test_session"})
    assert strategy.status_code == 200
    strategy_payload = strategy.json()
    assert "pit_window" in strategy_payload

    training = client.post(
        "/api/training/compare-lap",
        json={
            "session_id": "test_session",
            "ideal_car_id": "GR21",
            "reference_car_id": "GR22",
            "lap": 1,
            "metric": "speed_kph",
        },
    )
    assert training.status_code == 200
    assert "recommendations" in training.json()

    with client.websocket_connect("/ws/test_session") as ws:
        frame = ws.receive_json()
        assert "car_id" in frame
