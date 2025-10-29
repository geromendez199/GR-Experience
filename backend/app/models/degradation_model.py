"""Tire degradation modeling utilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression

from .features import build_lap_features


@dataclass
class DegradationResult:
    coefficients: dict[str, float]
    variance: float
    predictions: pd.DataFrame


class DegradationModel:
    def __init__(self) -> None:
        self.model = LinearRegression()
        self.fitted = False
        self.feature_columns = ["stint_lap", "tire_age", "track_temp_c", "air_temp_c"]
        self.variance_: float | None = None

    def fit(self, df: pd.DataFrame) -> DegradationResult:
        feature_set = build_lap_features(df)
        X = feature_set.features[self.feature_columns]
        y = feature_set.target
        self.model.fit(X, y)
        preds = self.model.predict(X)
        variance = float(np.var(y - preds))
        self.fitted = True
        self.variance_ = variance
        coefficients = {
            col: float(coef) for col, coef in zip(self.feature_columns, self.model.coef_)
        }
        predictions = pd.DataFrame({
            "lap": df["lap"].values,
            "predicted_lap_time_s": preds,
            "actual_lap_time_s": y.values,
        })
        return DegradationResult(coefficients=coefficients, variance=variance, predictions=predictions)

    def project(self, stint_laps: np.ndarray, context: dict[str, float]) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("Model must be fitted before projection")
        inputs = np.column_stack(
            [
                stint_laps,
                stint_laps - 1,
                np.full_like(stint_laps, context.get("track_temp_c", 30.0), dtype=float),
                np.full_like(stint_laps, context.get("air_temp_c", 25.0), dtype=float),
            ]
        )
        return self.model.predict(inputs)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "fitted": self.fitted}, path)

    @classmethod
    def load(cls, path: Path) -> "DegradationModel":
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.fitted = data.get("fitted", True)
        return instance
