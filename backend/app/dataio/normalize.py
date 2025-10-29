"""Normalization utilities for raw telemetry data."""
from __future__ import annotations

from pathlib import Path
from typing import Iterable, Mapping

import pandas as pd
import structlog

logger = structlog.get_logger(__name__)

CANONICAL_COLUMNS = [
    "session_id",
    "track",
    "event_date",
    "car_id",
    "lap",
    "sector",
    "t_ms",
    "lap_time_s",
    "speed_kph",
    "throttle",
    "brake",
    "gear",
    "tire_set",
    "track_temp_c",
    "air_temp_c",
    "flag_state",
]

COLUMN_ALIASES: Mapping[str, str] = {
    "session": "session_id",
    "track_name": "track",
    "event": "event_date",
    "car": "car_id",
    "car_number": "car_id",
    "lap_number": "lap",
    "lap_idx": "lap",
    "sector_number": "sector",
    "time_ms": "t_ms",
    "timestamp_ms": "t_ms",
    "timestamp": "t_ms",
    "delta_ms": "lap_time_s",
    "lap_time_ms": "lap_time_s",
    "velocity": "speed_kph",
    "speed": "speed_kph",
    "throttle_pct": "throttle",
    "brake_pct": "brake",
    "gear_idx": "gear",
    "tyre_set": "tire_set",
    "tyre": "tire_set",
    "track_temp": "track_temp_c",
    "air_temp": "air_temp_c",
    "flag": "flag_state",
}

NUMERIC_BOUNDS: Mapping[str, tuple[float | int | None, float | int | None]] = {
    "lap_time_s": (20, 500),
    "speed_kph": (0, 360),
    "throttle": (0, 100),
    "brake": (0, 100),
    "gear": (0, 10),
    "track_temp_c": (-10, 80),
    "air_temp_c": (-20, 60),
}


class NormalizationError(RuntimeError):
    pass


def _read_raw_file(path: Path) -> pd.DataFrame:
    if path.suffix.lower() in {".csv", ".txt"}:
        df = pd.read_csv(path)
    elif path.suffix.lower() == ".json":
        df = pd.read_json(path)
    else:
        raise NormalizationError(f"Unsupported file format: {path.suffix}")
    if df.empty:
        raise NormalizationError(f"File {path} is empty")
    df.columns = [col.strip() for col in df.columns]
    return df


def _normalize_timestamp(df: pd.DataFrame) -> pd.DataFrame:
    # Prefer ECU timestamp column over derived lap times when available.
    if "t_ms" in df:
        return df
    if "timestamp_ms" in df.columns:
        ts = pd.to_numeric(df["timestamp_ms"], errors="coerce")
        if ts.notna().any():
            df["t_ms"] = ts.round().astype("Int64")
            df = df.drop(columns=["timestamp_ms"])
            return df
    if "time_ms" in df.columns:
        ts = pd.to_numeric(df["time_ms"], errors="coerce")
        if ts.notna().any():
            df["t_ms"] = ts.round().astype("Int64")
            df = df.drop(columns=["time_ms"])
            return df
    if "timestamp" in df.columns:
        ts = pd.to_datetime(df["timestamp"], utc=True, errors="coerce")
        if ts.notna().any():
            df["t_ms"] = (ts.view("int64") // 1_000_000).astype("Int64")
            return df
    if "time" in df.columns:
        ts = pd.to_datetime(df["time"], utc=True, errors="coerce")
        if ts.notna().any():
            df["t_ms"] = (ts.view("int64") // 1_000_000).astype("Int64")
            return df
    if "meta_time" in df.columns:
        df["t_ms"] = (df["meta_time"].astype(float) * 1000).round().astype("Int64")
    elif "lap_time_s" in df.columns:
        df["t_ms"] = (df["lap_time_s"].cumsum() * 1000).round().astype("Int64")
    else:
        # Some of our sample telemetry sets do not expose any timestamp information.
        # When that happens, synthesize a monotonic timeline based on surrogate
        # columns so downstream processing can continue.
        if "index" in df.columns:
            index_values = pd.to_numeric(df["index"], errors="coerce")
            if index_values.notna().any():
                df["t_ms"] = (index_values.fillna(method="ffill").fillna(0) * 1000).round().astype(
                    "Int64"
                )
                return df
        if "lap" in df.columns:
            laps = pd.to_numeric(df["lap"], errors="coerce").fillna(method="ffill").fillna(0)
            positions = df.groupby(laps).cumcount()
            df["t_ms"] = (
                (laps.astype(int) * 60_000) + (positions * 1000)
            ).astype("Int64")
            return df
        synthetic = pd.Series(pd.RangeIndex(len(df)), index=df.index)
        df["t_ms"] = (synthetic * 1000).astype("Int64")
    return df


def _coerce_columns(df: pd.DataFrame) -> pd.DataFrame:
    rename_map = {col: COLUMN_ALIASES.get(col, col) for col in df.columns}
    had_lap_time_ms = "lap_time_ms" in df.columns and rename_map.get("lap_time_ms") == "lap_time_s"
    df = df.rename(columns=rename_map)
    if had_lap_time_ms and "lap_time_s" in df.columns:
        df["lap_time_s"] = pd.to_numeric(df["lap_time_s"], errors="coerce") / 1000.0
    for column in CANONICAL_COLUMNS:
        if column not in df.columns:
            df[column] = pd.NA
    return df[CANONICAL_COLUMNS]


def _clean_types(df: pd.DataFrame) -> pd.DataFrame:
    df["session_id"] = df["session_id"].astype(str)
    df["track"] = df["track"].astype(str)
    df["car_id"] = df["car_id"].astype(str)
    df["lap"] = df["lap"].astype("Int64")
    df["sector"] = df["sector"].astype("Int64")
    df["t_ms"] = pd.to_numeric(df["t_ms"], errors="coerce").astype(float)
    df["lap_time_s"] = df["lap_time_s"].astype(float)
    for col in ["speed_kph", "throttle", "brake", "track_temp_c", "air_temp_c"]:
        df[col] = df[col].astype(float)
    df["gear"] = df["gear"].astype("Int64")
    df["tire_set"] = df["tire_set"].fillna("unknown").astype(str)
    df["flag_state"] = df["flag_state"].fillna("green").str.lower()
    return df


def _interpolate_numeric(df: pd.DataFrame) -> pd.DataFrame:
    numeric_cols = [
        "lap_time_s",
        "speed_kph",
        "throttle",
        "brake",
        "gear",
        "track_temp_c",
        "air_temp_c",
    ]
    df = df.sort_values(["car_id", "lap", "sector", "t_ms"])
    for car_id, car_df in df.groupby("car_id", group_keys=False):
        df.loc[car_df.index, numeric_cols] = (
            car_df[numeric_cols]
            .apply(pd.to_numeric, errors="coerce")
            .interpolate(limit_direction="both")
            .fillna(method="bfill")
            .fillna(method="ffill")
        )
    return df


def _enforce_bounds(df: pd.DataFrame) -> pd.DataFrame:
    for column, (lower, upper) in NUMERIC_BOUNDS.items():
        if lower is not None:
            df.loc[df[column] < lower, column] = lower
        if upper is not None:
            df.loc[df[column] > upper, column] = upper
    return df


def _derive_missing_lap_times(df: pd.DataFrame) -> pd.DataFrame:
    needs_lap_time = df["lap_time_s"].isna() | (df["lap_time_s"] <= 0)
    if needs_lap_time.any():
        df = df.sort_values(["car_id", "lap", "sector", "t_ms"])
        df["lap_time_s"] = df.groupby(["car_id", "lap"])["t_ms"].transform(
            lambda s: (s - s.min()) / 1000.0
        )
    return df


def _derive_event_date(df: pd.DataFrame) -> pd.DataFrame:
    if df["event_date"].notna().any():
        try:
            df["event_date"] = pd.to_datetime(df["event_date"], errors="coerce").dt.date
            return df
        except Exception as exc:  # noqa: BLE001
            logger.warning("normalize.event_date_parse_failed", error=str(exc))
    # fallback: use timestamp minimum
    ts_min = pd.to_datetime(df["t_ms"], unit="ms", utc=True).min()
    df["event_date"] = ts_min.tz_convert("UTC").date() if ts_min.tzinfo else ts_min.date()
    return df


def normalize_files(
    files: Iterable[Path],
    session_id: str,
    track: str,
) -> pd.DataFrame:
    """Normalize raw telemetry files into the canonical schema."""

    frames: list[pd.DataFrame] = []
    for path in files:
        raw = _read_raw_file(path)
        raw = _normalize_timestamp(raw)
        raw = _coerce_columns(raw)
        raw["session_id"] = session_id
        raw["track"] = track
        frames.append(raw)
        logger.debug("normalize.file", path=str(path), rows=len(raw))

    if not frames:
        raise NormalizationError("No telemetry data found in archive")

    df = pd.concat(frames, ignore_index=True)
    df = _clean_types(df)
    df = _derive_missing_lap_times(df)
    df = _interpolate_numeric(df)
    df = _enforce_bounds(df)
    df = _derive_event_date(df)

    mandatory = ["session_id", "track", "car_id", "lap", "sector", "t_ms", "lap_time_s"]
    if df[mandatory].isnull().any().any():
        missing_cols = [col for col in mandatory if df[col].isnull().any()]
        raise NormalizationError(f"Missing critical values after normalization: {missing_cols}")

    df = df.sort_values(["car_id", "lap", "sector", "t_ms"]).reset_index(drop=True)
    logger.info(
        "normalize.complete",
        session_id=session_id,
        track=track,
        rows=len(df),
        cars=df["car_id"].nunique(),
        laps=df["lap"].max(),
    )
    return df


def compute_session_metrics(df: pd.DataFrame) -> dict:
    """Compute basic metrics for ingestion response."""

    valid_laps = df[df["lap_time_s"].between(20, 300)]
    fastest = (
        valid_laps.groupby("car_id")["lap_time_s"].min().sort_values().head(1).to_dict()
    )
    stints: list[dict] = []
    for car_id, car_df in df.groupby("car_id"):
        for tire_set, stint_df in car_df.groupby("tire_set"):
            if stint_df.empty:
                continue
            stints.append(
                {
                    "car_id": car_id,
                    "tire_set": tire_set,
                    "start_lap": int(stint_df["lap"].min()),
                    "end_lap": int(stint_df["lap"].max()),
                    "avg_pace_s": float(stint_df["lap_time_s"].mean()),
                }
            )
    return {
        "fastest_lap": fastest,
        "valid_laps": int(valid_laps["lap"].nunique()),
        "stints": stints,
    }
