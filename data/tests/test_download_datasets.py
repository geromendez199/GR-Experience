"""Unit tests for :mod:`data.scripts.download_datasets`."""
from __future__ import annotations

import io
import tarfile
import zipfile
from pathlib import Path

import pytest

from data.scripts.download_datasets import (
    DatasetDefinition,
    clean_directory,
    extract_archive,
)


@pytest.fixture()
def temporary_directory(tmp_path: Path) -> Path:
    """Return a clean temporary directory."""

    return tmp_path / "artifacts"


def test_extract_zip_archive(tmp_path: Path) -> None:
    target_dir = tmp_path / "unzipped"
    definition = DatasetDefinition(
        name="example",
        url="https://example.com/archive.zip",
        archive_type="zip",
        target_dir=target_dir,
    )

    archive_path = tmp_path / "archive.zip"
    with zipfile.ZipFile(archive_path, "w") as archive:
        archive.writestr("data/file.txt", "payload")

    extracted_path = extract_archive(definition, archive_path)

    assert extracted_path == target_dir
    assert (target_dir / "data" / "file.txt").read_text() == "payload"


def test_extract_tar_archive(tmp_path: Path) -> None:
    target_dir = tmp_path / "untarred"
    definition = DatasetDefinition(
        name="example",
        url="https://example.com/archive.tar.gz",
        archive_type="tar",
        target_dir=target_dir,
    )

    archive_path = tmp_path / "archive.tar.gz"
    with tarfile.open(archive_path, "w:gz") as archive:
        info = tarfile.TarInfo(name="data/file.txt")
        payload = b"payload"
        info.size = len(payload)
        archive.addfile(info, io.BytesIO(payload))

    extracted_path = extract_archive(definition, archive_path)

    assert extracted_path == target_dir
    assert (target_dir / "data" / "file.txt").read_text() == "payload"


def test_clean_directory_removes_existing(tmp_path: Path) -> None:
    directory = tmp_path / "to-delete"
    directory.mkdir()
    (directory / "file.txt").write_text("payload")

    clean_directory(directory)

    assert not directory.exists()
