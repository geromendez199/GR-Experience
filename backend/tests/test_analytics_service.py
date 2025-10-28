"""Tests for the analytics service module."""
from __future__ import annotations

from backend.app.services.analytics import (
    compute_event_analytics,
    compute_lap_comparison,
    recommend_strategy,
)


def test_compute_event_analytics_returns_payload() -> None:
    analytics = compute_event_analytics("barber-motorsports-park")
    assert analytics is not None
    assert analytics.event_id == "barber-motorsports-park"
    assert analytics.fastest_lap_seconds <= analytics.slowest_lap_seconds
    assert len(analytics.laps) >= 1


def test_compute_lap_comparison_handles_missing_lap() -> None:
    comparison = compute_lap_comparison("barber-motorsports-park", "21", 1, 2)
    assert comparison is not None
    assert comparison.total_delta_seconds != 0


def test_recommend_strategy_varies_by_lap() -> None:
    early_strategy = recommend_strategy("barber-motorsports-park", current_lap=5)
    late_strategy = recommend_strategy("barber-motorsports-park", current_lap=15)

    assert len(early_strategy) == 1
    assert len(late_strategy) == 2
