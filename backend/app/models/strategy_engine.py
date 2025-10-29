"""Race strategy simulation utilities."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .degradation_model import DegradationModel
from .lap_time_model import LapTimeModel


@dataclass
class StrategyContext:
    session_id: str
    target_position: int | None
    data: pd.DataFrame


class StrategyEngine:
    def __init__(
        self,
        lap_model: LapTimeModel | None = None,
        degradation_model: DegradationModel | None = None,
    ) -> None:
        self.lap_model = lap_model or LapTimeModel()
        self.degradation_model = degradation_model or DegradationModel()

    def prepare(self, df: pd.DataFrame) -> None:
        if not self.lap_model.fitted:
            self.lap_model.fit(df)
        if not self.degradation_model.fitted:
            self.degradation_model.fit(df)

    def simulate(self, context: StrategyContext) -> dict:
        df = context.data.copy()
        df = df.sort_values(["car_id", "lap", "sector", "t_ms"])
        self.prepare(df)

        baseline = df.groupby("lap")["lap_time_s"].mean().sort_index()
        temps = {
            "track_temp_c": float(df["track_temp_c"].mean()),
            "air_temp_c": float(df["air_temp_c"].mean()),
        }
        projections = self._evaluate_windows(baseline, temps)
        best = max(projections, key=lambda item: item["expected_gain_s"])
        return {
            "pit_window": best["pit_window"],
            "expected_gain_s": float(best["expected_gain_s"]),
            "confidence": float(best["confidence"]),
            "stint_summary": projections,
            "notes": best["notes"],
        }

    def _evaluate_windows(self, baseline: pd.Series, temps: dict[str, float]) -> list[dict]:
        laps = baseline.index.to_numpy()
        min_lap, max_lap = int(laps.min()), int(laps.max())
        window_width = max(3, int((max_lap - min_lap) * 0.2))
        candidate_windows = [
            (lap, min(lap + window_width, max_lap))
            for lap in range(min_lap + 3, max_lap - window_width + 1)
        ]
        if not candidate_windows:
            candidate_windows = [(min_lap + 1, max_lap - 1)]
        results: list[dict] = []
        variance = self.degradation_model.variance_ or 0.5
        for start, end in candidate_windows:
            stint_length = end - start + 1
            stay_out = baseline.loc[start:end]
            projected = self.degradation_model.project(
                np.arange(1, stint_length + 1, dtype=float), temps
            )
            expected_gain = float(stay_out.sum() - projected.sum())
            avg_pace = max(stay_out.mean(), 1e-6)
            confidence = float(np.clip(1.0 - np.sqrt(variance) / avg_pace, 0.0, 1.0))
            notes = [
                f"Undercut delta {expected_gain:.2f}s over laps {start}-{end}",
                f"Average projected lap {projected.mean():.3f}s vs current {stay_out.mean():.3f}s",
            ]
            if confidence < 0.4:
                notes.append("Confidence limited by high variance in degradation fit")
            results.append(
                {
                    "pit_window": (int(start), int(end)),
                    "expected_gain_s": expected_gain,
                    "confidence": confidence,
                    "notes": notes,
                }
            )
        return results
