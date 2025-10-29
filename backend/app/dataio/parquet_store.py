"""Filesystem-backed Parquet store used by the telemetry API."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import pandas as pd
import structlog

logger = structlog.get_logger(__name__)


def _ensure_directory(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _iter_parquet_files(root: Path) -> Iterable[Path]:
    yield from root.rglob("*.parquet")


@dataclass
class ParquetStore:
    """Persist normalized telemetry data as partitioned Parquet files."""

    root: Path
    partition_cols: list[str]

    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()
        _ensure_directory(self.root)

    def _partition_path(self, df: pd.DataFrame) -> Path:
        target = self.root
        for column in self.partition_cols:
            if column not in df.columns:
                raise KeyError(f"Partition column '{column}' missing from dataframe")
            value = str(df[column].iloc[0])
            target = target / f"{column}={value}"
        return target

    def _load_dataset(self) -> pd.DataFrame:
        files = list(_iter_parquet_files(self.root))
        if not files:
            return pd.DataFrame()
        frames = [pd.read_parquet(path) for path in files]
        return pd.concat(frames, ignore_index=True)

    def write_session(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Cannot write empty dataframe")
        target_dir = self._partition_path(df)
        _ensure_directory(target_dir)
        file_path = target_dir / "data.parquet"
        df.to_parquet(file_path, index=False)
        logger.info(
            "parquet.write",
            partitions=self.partition_cols,
            rows=len(df),
            root=str(self.root),
            file=str(file_path),
        )

    def read_session(
        self,
        session_id: str,
        track: str | None = None,
        columns: list[str] | None = None,
        filters: list[tuple[str, str, object]] | None = None,
    ) -> pd.DataFrame:
        df = self._load_dataset()
        if df.empty:
            return df
        mask = df["session_id"] == session_id
        if track:
            mask &= df["track"] == track
        if filters:
            for column, op, value in filters:
                if op == "eq":
                    mask &= df[column] == value
                elif op == "ne":
                    mask &= df[column] != value
                elif op == "lt":
                    mask &= df[column] < value
                elif op == "le":
                    mask &= df[column] <= value
                elif op == "gt":
                    mask &= df[column] > value
                elif op == "ge":
                    mask &= df[column] >= value
                else:
                    raise ValueError(f"Unsupported filter operator: {op}")
        filtered = df.loc[mask].copy()
        if columns:
            missing = set(columns) - set(filtered.columns)
            if missing:
                raise KeyError(f"Requested columns {missing} are not available")
            filtered = filtered[columns]
        return filtered.reset_index(drop=True)

    def scan_laps(
        self,
        session_id: str,
        car_id: str | None = None,
        offset: int = 0,
        limit: int = 500,
        track: str | None = None,
    ) -> pd.DataFrame:
        df = self._load_dataset()
        if df.empty:
            return df
        mask = df["session_id"] == session_id
        if car_id:
            mask &= df["car_id"] == car_id
        if track:
            mask &= df["track"] == track
        filtered = df.loc[mask].copy()
        filtered = filtered.sort_values(["car_id", "lap", "sector", "t_ms"])
        return filtered.iloc[offset : offset + limit].reset_index(drop=True)
