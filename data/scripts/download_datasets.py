"""Utility functions for downloading and preparing GR Cup telemetry datasets."""
from __future__ import annotations

import concurrent.futures
import logging
import shutil
import tarfile
import urllib.request
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Optional

LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True)
class DatasetDefinition:
    """Metadata required to retrieve and unpack a telemetry dataset."""

    name: str
    url: str
    archive_type: str  # ``zip`` or ``tar``
    target_dir: Path

    def archive_path(self, download_root: Path) -> Path:
        """Return the expected archive path inside *download_root*."""

        suffix = ".zip" if self.archive_type == "zip" else ".tar.gz"
        return download_root / f"{self.name}{suffix}"


DEFAULT_DATASETS: Dict[str, DatasetDefinition] = {
    "barber-motorsports-park": DatasetDefinition(
        name="barber-motorsports-park",
        url="https://example.com/datasets/barber-motorsports-park.zip",
        archive_type="zip",
        target_dir=Path("data/raw/barber"),
    ),
    "circuit-of-the-americas": DatasetDefinition(
        name="circuit-of-the-americas",
        url="https://example.com/datasets/circuit-of-the-americas.tar.gz",
        archive_type="tar",
        target_dir=Path("data/raw/cota"),
    ),
}


def ensure_directory(path: Path) -> None:
    """Create *path* if it does not exist."""

    path.mkdir(parents=True, exist_ok=True)


def download_dataset(definition: DatasetDefinition, *, download_root: Path) -> Path:
    """Download a dataset archive to *download_root*.

    When the file already exists it is left untouched to avoid wasting bandwidth.
    """

    ensure_directory(download_root)
    archive_path = definition.archive_path(download_root)
    if archive_path.exists():
        LOGGER.info("Skipping download for %s; file already present", definition.name)
        return archive_path

    LOGGER.info("Downloading %s from %s", definition.name, definition.url)
    with urllib.request.urlopen(definition.url) as response, archive_path.open("wb") as file_obj:
        shutil.copyfileobj(response, file_obj)
    return archive_path


def extract_archive(definition: DatasetDefinition, archive_path: Path) -> Path:
    """Extract *archive_path* to the dataset's target directory."""

    ensure_directory(definition.target_dir)
    if definition.archive_type == "zip":
        with zipfile.ZipFile(archive_path) as archive:
            archive.extractall(definition.target_dir)
    elif definition.archive_type == "tar":
        with tarfile.open(archive_path) as archive:
            archive.extractall(definition.target_dir)
    else:
        raise ValueError(f"Unsupported archive type: {definition.archive_type}")
    return definition.target_dir


def clean_directory(path: Path) -> None:
    """Remove *path* if it exists."""

    if path.exists():
        shutil.rmtree(path)


def fetch_datasets(
    dataset_names: Optional[Iterable[str]] = None,
    *,
    download_root: Path = Path("data/downloads"),
    dataset_catalog: Dict[str, DatasetDefinition] = DEFAULT_DATASETS,
) -> Dict[str, Path]:
    """Download and extract the requested datasets."""

    selected = (
        dataset_catalog.items()
        if dataset_names is None
        else ((name, dataset_catalog[name]) for name in dataset_names)
    )
    results: Dict[str, Path] = {}
    with concurrent.futures.ThreadPoolExecutor() as executor:
        future_to_name = {
            executor.submit(download_dataset, definition, download_root=download_root): name
            for name, definition in selected
        }
        for future in concurrent.futures.as_completed(future_to_name):
            name = future_to_name[future]
            archive_path = future.result()
            extracted_path = extract_archive(dataset_catalog[name], archive_path)
            results[name] = extracted_path
    return results


__all__ = [
    "DatasetDefinition",
    "DEFAULT_DATASETS",
    "download_dataset",
    "extract_archive",
    "fetch_datasets",
    "clean_directory",
]
