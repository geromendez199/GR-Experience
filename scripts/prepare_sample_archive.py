"""Utilities to build demo telemetry archives without shipping binaries."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path

DEFAULT_SAMPLE = "barber-motorsports-park"


def prepare_sample_archive(name: str, data_dir: Path) -> Path:
    samples_dir = data_dir / "samples"
    csv_path = samples_dir / f"{name}.csv"
    if not csv_path.exists():
        raise FileNotFoundError(
            f"Sample CSV not found at {csv_path}. Ensure the repository data folder is available."
        )

    archive_dir = data_dir / "input"
    archive_dir.mkdir(parents=True, exist_ok=True)
    archive_path = archive_dir / f"{name}.zip"

    with zipfile.ZipFile(archive_path, "w") as zf:
        zf.write(csv_path, arcname="telemetry.csv")

    return archive_path


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare sample telemetry archives")
    parser.add_argument("name", nargs="?", default=DEFAULT_SAMPLE, help="Sample identifier (default: %(default)s)")
    parser.add_argument("--data-dir", default=Path("data"), type=Path, help="Root data directory")
    args = parser.parse_args()

    archive = prepare_sample_archive(args.name, args.data_dir.resolve())
    print(f"Created archive at {archive}")


if __name__ == "__main__":
    main()
