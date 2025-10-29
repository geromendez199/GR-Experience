"""Feature engineering utilities for telemetry models."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class FeatureSet:
    features: pd.DataFrame
    target: pd.Series


def build_lap_features(df: pd.DataFrame) -> FeatureSet:
    """Construct lap-level features for modeling."""

    df = df.sort_values(["car_id", "lap", "sector", "t_ms"]).copy()
    df["stint_id"] = df.groupby(["car_id", "tire_set"]).ngroup()
    df["stint_lap"] = (
        df.groupby(["car_id", "tire_set"])["lap"].rank(method="dense").astype(int)
    )
    df["prev_lap_time"] = df.groupby("car_id")["lap_time_s"].shift(1)
    df["prev_lap_time"].fillna(df["lap_time_s"], inplace=True)

    stint_avg = df.groupby(["car_id", "tire_set"])["lap_time_s"].transform("mean")
    df["avg_stint_pace"] = stint_avg
    df["tire_age"] = df["stint_lap"] - 1
    df["is_under_flag"] = df["flag_state"].isin({"yellow", "sc"}).astype(int)

    df = _derive_sector_metrics(df)
    feature_cols = [
        "stint_id",
        "stint_lap",
        "prev_lap_time",
        "avg_stint_pace",
        "tire_age",
        "is_under_flag",
        "sector_delta_s",
        "sector_time_s",
        "speed_kph",
        "throttle",
        "brake",
        "gear",
        "track_temp_c",
        "air_temp_c",
    ]
    features = df[feature_cols]
    target = df["lap_time_s"]
    features = features.fillna(method="ffill").fillna(method="bfill")
    return FeatureSet(features=features, target=target)


def _derive_sector_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["t_ms"] = pd.to_numeric(df["t_ms"], errors="coerce")
    df["lap_time_s"] = pd.to_numeric(df["lap_time_s"], errors="coerce")

    df["sector_time_s"] = (
        df.groupby(["car_id", "lap"])["t_ms"].diff().fillna(df["lap_time_s"])
    ) / 1000.0
    global_sector = df.groupby(["track", "sector"])['sector_time_s'].transform('median')
    df["sector_delta_s"] = df["sector_time_s"] - global_sector
    return df


def compute_dtw_alignment(
    ideal_lap: pd.DataFrame,
    reference_lap: pd.DataFrame,
    value_column: str = "speed_kph",
) -> dict:
    """Align two laps using Dynamic Time Warping and emit recommendations."""

    ideal = ideal_lap.sort_values("t_ms")[value_column].to_numpy(dtype=float)
    ref = reference_lap.sort_values("t_ms")[value_column].to_numpy(dtype=float)
    if ideal.size == 0 or ref.size == 0:
        raise ValueError("Both laps must contain telemetry samples")

    distance, path = _dtw(ideal, ref)
    if not path:
        return {"distance": float(distance), "path": [], "recommendations": []}
    sector_breaks = np.linspace(0, len(path) - 1, num=4, dtype=int)
    recommendations: list[str] = []
    for i in range(len(sector_breaks) - 1):
        seg = path[sector_breaks[i] : sector_breaks[i + 1]]
        ideal_vals = ideal[[p[0] for p in seg]]
        ref_vals = ref[[p[1] for p in seg]]
        delta = np.mean(ideal_vals - ref_vals)
        if delta > 2:
            recommendations.append(
                f"Sector {i+1}: increase minimum speed, average delta {delta:.2f} kph"
            )
        elif delta < -2:
            recommendations.append(
                f"Sector {i+1}: car is over-rotating, scrub {abs(delta):.2f} kph for stability"
            )
        else:
            recommendations.append(f"Sector {i+1}: pace aligned within ±2 kph")

    return {
        "distance": float(distance),
        "path": path,
        "recommendations": recommendations,
    }


def _dtw(a: np.ndarray, b: np.ndarray) -> tuple[float, list[tuple[int, int]]]:
    n, m = len(a), len(b)
    cost = np.full((n + 1, m + 1), np.inf)
    cost[0, 0] = 0.0

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            dist = abs(a[i - 1] - b[j - 1])
            cost[i, j] = dist + min(cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1])

    i, j = n, m
    path: list[tuple[int, int]] = []
    while i > 0 and j > 0:
        path.append((i - 1, j - 1))
        choices = [cost[i - 1, j], cost[i, j - 1], cost[i - 1, j - 1]]
        arg = int(np.argmin(choices))
        if arg == 0:
            i -= 1
        elif arg == 1:
            j -= 1
        else:
            i -= 1
            j -= 1
    path.reverse()
    return cost[n, m], path
