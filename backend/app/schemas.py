"""Pydantic schemas for API requests and responses."""
from __future__ import annotations

from typing import Any, Dict, List, Tuple

from pydantic import BaseModel, Field, validator


class TelemetryFrame(BaseModel):
    t_ms: int
    car_id: str
    lap: int
    sector: int
    speed_kph: float
    throttle: float
    brake: float
    gear: int
    lap_time_s: float | None = None
    track_temp_c: float | None = None
    air_temp_c: float | None = None
    flag_state: str | None = None


class IngestRequest(BaseModel):
    zip_path: str = Field(..., description="Absolute or relative path to the telemetry zip")

    @validator("zip_path")
    def validate_zip_path(cls, value: str) -> str:
        if not value.endswith(".zip"):
            raise ValueError("zip_path must point to a .zip archive")
        return value


class StrategyRequest(BaseModel):
    session_id: str
    target_position: int | None = None


class StrategyResponse(BaseModel):
    pit_window: Tuple[int, int]
    expected_gain_s: float = Field(ge=-60, le=60)
    confidence: float = Field(ge=0, le=1)
    stint_summary: List[Dict[str, Any]]
    notes: List[str] = []


class LapResponse(BaseModel):
    session_id: str
    track: str
    data: List[TelemetryFrame]
    total: int
    offset: int
    limit: int


class TrainingComparisonRequest(BaseModel):
    session_id: str
    ideal_car_id: str
    reference_car_id: str
    lap: int
    metric: str = Field("speed_kph", description="Telemetry column to align using DTW")


class TrainingComparisonResponse(BaseModel):
    distance: float
    path: List[Tuple[int, int]]
    recommendations: List[str]


class SessionIngestResponse(BaseModel):
    session_id: str
    track: str
    metrics: Dict[str, Any]


class WebSocketFrame(BaseModel):
    t: int = Field(..., alias="t_ms")
    car_id: str
    lap: int
    delta_s: float
    flag: str

    class Config:
        allow_population_by_field_name = True
