"""Seed script to ingest a demo session for the GR-Experience dashboard."""
from __future__ import annotations

from pathlib import Path

from backend.app.cli import ingest
from backend.app.config import get_settings
from scripts.prepare_sample_archive import prepare_sample_archive

DEFAULT_SESSION_ID = "demo_barber_2025"
DEFAULT_SAMPLE = "barber-motorsports-park"


def main() -> None:
    settings = get_settings()
    archive_path = prepare_sample_archive(DEFAULT_SAMPLE, Path(settings.data_dir))
    ingest(archive_path, session_id=DEFAULT_SESSION_ID)


if __name__ == "__main__":
    main()
