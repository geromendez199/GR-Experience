from __future__ import annotations

import zipfile
from pathlib import Path

from backend.app.dataio import compute_session_metrics, extract_zip, normalize_files
from backend.app.dataio.parquet_store import ParquetStore


def test_ingestion_pipeline(tmp_path: Path) -> None:
    csv_path = Path("data/samples/barber-motorsports-park.csv").resolve()
    zip_path = tmp_path / "barber-motorsports-park.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.write(csv_path, arcname="telemetry.csv")
    assert zip_path.exists()
    staging_dir = tmp_path / "staging"
    files = extract_zip(zip_path, staging_dir)
    assert files, "Extraction must yield files"
    df = normalize_files(files, session_id="unit_session", track="Barber Motorsports Park")
    assert set(df.columns) >= {
        "session_id",
        "track",
        "car_id",
        "lap",
        "sector",
        "lap_time_s",
    }
    assert df["lap_time_s"].between(20, 300).all()
    metrics = compute_session_metrics(df)
    assert "fastest_lap" in metrics

    store = ParquetStore(root=tmp_path / "parquet", partition_cols=["session_id", "track"])
    store.write_session(df)
    reloaded = store.read_session("unit_session")
    assert not reloaded.empty
    assert reloaded["car_id"].nunique() == df["car_id"].nunique()
