"""Business logic powering the analytics API endpoints."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from ..schemas.analytics import EventAnalytics, LapComparison, LapMetric, SectorDelta, StrategyRecommendation


@dataclass
class LapSample:
    """Representation of processed lap telemetry."""

    lap_number: int
    lap_time_seconds: float
    average_speed_kmh: float
    throttle_usage_pct: float
    brake_usage_pct: float
    sector_splits: Dict[str, float]


# In lieu of a real database this module operates on an in-memory dataset
# that mirrors the structure produced by the data processing pipeline.
_SAMPLE_DATA: Dict[str, Dict[str, List[LapSample]]] = {
    "barber-motorsports-park": {
        "21": [
            LapSample(1, 89.423, 152.2, 58.0, 22.0, {"S1": 30.1, "S2": 29.6, "S3": 29.7}),
            LapSample(2, 88.915, 153.0, 59.0, 21.0, {"S1": 29.8, "S2": 29.5, "S3": 29.6}),
        ],
    }
}


def _compute_average(values: Iterable[float]) -> float:
    items = list(values)
    return sum(items) / len(items)


def compute_event_analytics(event_id: str) -> Optional[EventAnalytics]:
    """Return aggregate statistics for *event_id*."""

    event_data = _SAMPLE_DATA.get(event_id)
    if not event_data:
        return None

    laps: List[LapMetric] = []
    lap_times: List[float] = []

    for driver_laps in event_data.values():
        for lap in driver_laps:
            lap_times.append(lap.lap_time_seconds)
            laps.append(
                LapMetric(
                    lap_number=lap.lap_number,
                    lap_time_seconds=lap.lap_time_seconds,
                    average_speed_kmh=lap.average_speed_kmh,
                    throttle_usage_pct=lap.throttle_usage_pct,
                    brake_usage_pct=lap.brake_usage_pct,
                )
            )

    return EventAnalytics(
        event_id=event_id,
        fastest_lap_seconds=min(lap_times),
        slowest_lap_seconds=max(lap_times),
        average_lap_seconds=_compute_average(lap_times),
        laps=laps,
    )


def compute_lap_comparison(
    event_id: str,
    driver_id: str,
    reference_lap_number: int,
    target_lap_number: int,
) -> Optional[LapComparison]:
    """Compare two laps and produce a high-level delta summary."""

    driver_data = _SAMPLE_DATA.get(event_id, {}).get(driver_id)
    if not driver_data:
        return None

    try:
        reference = next(lap for lap in driver_data if lap.lap_number == reference_lap_number)
        target = next(lap for lap in driver_data if lap.lap_number == target_lap_number)
    except StopIteration:
        return None

    sector_deltas = [
        SectorDelta(sector=sector, delta_seconds=target.sector_splits[sector] - reference.sector_splits[sector])
        for sector in reference.sector_splits
    ]

    total_delta = target.lap_time_seconds - reference.lap_time_seconds

    return LapComparison(
        event_id=event_id,
        driver_id=driver_id,
        reference_lap=reference_lap_number,
        target_lap=target_lap_number,
        total_delta_seconds=total_delta,
        sector_deltas=sector_deltas,
    )


def recommend_strategy(event_id: str, current_lap: int) -> List[StrategyRecommendation]:
    """Return a simplified pit stop strategy recommendation."""

    # For the prototype we return deterministic recommendations to exercise the API surface.
    if current_lap < 10:
        return [
            StrategyRecommendation(
                lap=current_lap + 2,
                action="Consider short-fuel stop",
                expected_position=3,
                confidence=0.65,
            )
        ]
    return [
        StrategyRecommendation(
            lap=current_lap + 1,
            action="Pit for tires and fuel",
            expected_position=2,
            confidence=0.72,
        ),
        StrategyRecommendation(
            lap=current_lap + 3,
            action="Extend stint if safety car deployed",
            expected_position=4,
            confidence=0.58,
        ),
    ]
