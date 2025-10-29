from __future__ import annotations

import numpy as np
import pandas as pd

from backend.app.models import StrategyContext, StrategyEngine


def _build_dataset() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    t_ms = 0
    for lap in range(1, 21):
        tire_set = "S1" if lap <= 10 else "S2"
        lap_time = 90 + 0.25 * lap
        for sector in range(1, 4):
            sector_time = lap_time / 3 + float(rng.uniform(-0.1, 0.1))
            t_ms += int(sector_time * 1000)
            rows.append(
                {
                    "session_id": "strat_session",
                    "track": "Barber Motorsports Park",
                    "event_date": "2025-04-20",
                    "car_id": "GR21",
                    "lap": lap,
                    "sector": sector,
                    "t_ms": t_ms,
                    "lap_time_s": lap_time,
                    "speed_kph": 180 - 0.5 * lap + float(rng.uniform(-2, 2)),
                    "throttle": 95 - 0.5 * lap,
                    "brake": 5 + 0.2 * lap,
                    "gear": 6,
                    "tire_set": tire_set,
                    "track_temp_c": 35.0,
                    "air_temp_c": 28.0,
                    "flag_state": "green",
                }
            )
    return pd.DataFrame(rows)


def test_strategy_engine_simulation() -> None:
    df = _build_dataset()
    engine = StrategyEngine()
    context = StrategyContext(session_id="strat_session", target_position=2, data=df)
    result = engine.simulate(context)
    assert "pit_window" in result
    assert 0 <= result["confidence"] <= 1
    assert result["stint_summary"], "Expected multiple window evaluations"
    assert isinstance(result["notes"], list)
