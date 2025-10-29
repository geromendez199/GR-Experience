"""RandomForest baseline for lap time estimation."""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split

from .features import build_lap_features


class LapTimeModel:
    def __init__(self, n_estimators: int = 200, random_state: int = 42) -> None:
        self.model = RandomForestRegressor(
            n_estimators=n_estimators,
            random_state=random_state,
            n_jobs=-1,
        )
        self.fitted = False
        self.mae_: float | None = None

    def fit(self, df) -> "LapTimeModel":
        feature_set = build_lap_features(df)
        X_train, X_valid, y_train, y_valid = train_test_split(
            feature_set.features,
            feature_set.target,
            test_size=0.2,
            random_state=42,
        )
        self.model.fit(X_train, y_train)
        preds = self.model.predict(X_valid)
        self.mae_ = float(mean_absolute_error(y_valid, preds))
        self.fitted = True
        return self

    def predict(self, df) -> np.ndarray:
        if not self.fitted:
            raise RuntimeError("Model must be fitted before predicting")
        feature_set = build_lap_features(df)
        return self.model.predict(feature_set.features)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        joblib.dump({"model": self.model, "mae": self.mae_}, path)

    @classmethod
    def load(cls, path: Path) -> "LapTimeModel":
        data = joblib.load(path)
        instance = cls()
        instance.model = data["model"]
        instance.mae_ = data.get("mae")
        instance.fitted = True
        return instance
