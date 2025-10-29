"""Utility class for persisting normalized telemetry to Parquet."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.dataset as ds
import pyarrow.parquet as pq
import structlog

logger = structlog.get_logger(__name__)


@dataclass
class ParquetStore:
    root: Path
    partition_cols: list[str]

    def __post_init__(self) -> None:
        self.root = self.root.expanduser().resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def write_session(self, df: pd.DataFrame) -> None:
        if df.empty:
            raise ValueError("Cannot write empty dataframe")
        table = pa.Table.from_pandas(df, preserve_index=False)
        pq.write_to_dataset(
            table,
            root_path=str(self.root),
            partition_cols=self.partition_cols,
            existing_data_behavior="overwrite_or_ignore",
        )
        logger.info(
            "parquet.write",
            partitions=self.partition_cols,
            rows=len(df),
            root=str(self.root),
        )

    def read_session(
        self,
        session_id: str,
        track: str | None = None,
        columns: list[str] | None = None,
        filters: list[tuple[str, str, object]] | None = None,
    ) -> pd.DataFrame:
        if not any(self.root.glob("**/*.parquet")):
            return pd.DataFrame()
        dataset = ds.dataset(self.root, format="parquet")
        filter_exprs: list[ds.Expression] = [ds.field("session_id") == session_id]
        if track:
            filter_exprs.append(ds.field("track") == track)
        if filters:
            for column, op, value in filters:
                filter_exprs.append(getattr(ds.field(column), op)(value))
        combined = filter_exprs[0]
        for expr in filter_exprs[1:]:
            combined = combined & expr
        table = dataset.to_table(filter=combined, columns=columns)
        return table.to_pandas()

    def scan_laps(
        self,
        session_id: str,
        car_id: str | None = None,
        offset: int = 0,
        limit: int = 500,
        track: str | None = None,
    ) -> pd.DataFrame:
        filters = [("session_id", "eq", session_id)]
        if car_id:
            filters.append(("car_id", "eq", car_id))
        if track:
            filters.append(("track", "eq", track))
        if not any(self.root.glob("**/*.parquet")):
            return pd.DataFrame()
        dataset = ds.dataset(self.root, format="parquet")
        expr = None
        for column, op, value in filters:
            column_expr = getattr(ds.field(column), op)(value)
            expr = column_expr if expr is None else expr & column_expr
        if expr is None:
            raise ValueError("No filters applied")
        table = dataset.scan(columns=None, filter=expr).to_table()
        df = table.to_pandas()
        df = df.sort_values(["car_id", "lap", "sector", "t_ms"])
        return df.iloc[offset : offset + limit]
