"""Utilities for extracting telemetry archives."""
from __future__ import annotations

import shutil
import zipfile
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


def _verify_zip_integrity(zip_path: Path) -> None:
    with zipfile.ZipFile(zip_path) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            if info.file_size <= 0:
                raise ValueError(f"Archive member {info.filename} is empty")
            # ZipFile will raise a BadZipFile on CRC mismatch when read. We proactively check.
            with zf.open(info.filename) as member:
                data = member.read()
            computed = zipfile.crc32(data) & 0xFFFFFFFF
            if computed != info.CRC:
                raise ValueError(
                    f"CRC mismatch for {info.filename}: expected {info.CRC}, got {computed}"
                )


def extract_zip(input_zip: Path, out_dir: Path) -> list[Path]:
    """Extract a telemetry archive ensuring integrity.

    Parameters
    ----------
    input_zip:
        Path to the telemetry archive. Must end with ``.zip``.
    out_dir:
        Destination directory for extracted files. It will be created if missing.

    Returns
    -------
    list[Path]
        List of extracted file paths.
    """

    input_zip = input_zip.expanduser().resolve()
    if not input_zip.exists():
        raise FileNotFoundError(f"Telemetry archive not found: {input_zip}")
    if input_zip.suffix.lower() != ".zip":
        raise ValueError("Only .zip archives are supported")

    logger.info("extract.start", archive=str(input_zip))
    out_dir = out_dir.expanduser().resolve()
    if out_dir.exists():
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    _verify_zip_integrity(input_zip)

    extracted: list[Path] = []
    with zipfile.ZipFile(input_zip) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            target_path = out_dir / info.filename
            target_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(info.filename) as source, open(target_path, "wb") as dest:
                shutil.copyfileobj(source, dest)
            extracted.append(target_path)
            logger.debug(
                "extract.member", filename=info.filename, size=info.file_size, dest=str(target_path)
            )

    logger.info("extract.complete", archive=str(input_zip), files=len(extracted))
    return extracted
