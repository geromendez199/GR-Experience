"""Lightweight data structures for analytics payloads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class LapMetric:
    lap_number: int
    lap_time_seconds: float
    average_speed_kmh: float
    throttle_usage_pct: float
    brake_usage_pct: float


@dataclass
class EventAnalytics:
    event_id: str
    fastest_lap_seconds: float
    slowest_lap_seconds: float
    average_lap_seconds: float
    laps: List[LapMetric]


@dataclass
class SectorDelta:
    sector: str
    delta_seconds: float


@dataclass
class LapComparison:
    event_id: str
    driver_id: str
    reference_lap: int
    target_lap: int
    total_delta_seconds: float
    sector_deltas: List[SectorDelta]


@dataclass
class StrategyRecommendation:
    lap: int
    action: str
    expected_position: int
    confidence: float
