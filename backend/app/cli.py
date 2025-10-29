"""Command line utilities for the GR-Experience backend."""
from __future__ import annotations

import argparse
from pathlib import Path

from .config import get_settings
from .dataio import compute_session_metrics, extract_zip, normalize_files
from .deps import get_parquet_store


def ingest(zip_path: Path, session_id: str) -> None:
    settings = get_settings()
    store = get_parquet_store()
    staging = settings.data_dir / "staging" / session_id
    files = extract_zip(zip_path, staging)
    track = zip_path.stem.replace('-', ' ').replace('_', ' ').title()
    normalized = normalize_files(files, session_id=session_id, track=track)
    store.write_session(normalized)
    metrics = compute_session_metrics(normalized)
    print(f"Ingested session {session_id} ({track})")
    print(f"Fastest lap: {metrics['fastest_lap']}")
    print(f"Valid laps: {metrics['valid_laps']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="GR-Experience CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    ingest_parser = sub.add_parser("ingest", help="Ingest a telemetry archive")
    ingest_parser.add_argument("session_id", help="Normalized session identifier")
    ingest_parser.add_argument("zip_path", type=Path, help="Path to telemetry ZIP archive")

    args = parser.parse_args()
    if args.command == "ingest":
        ingest(args.zip_path, args.session_id)


if __name__ == "__main__":
    main()
