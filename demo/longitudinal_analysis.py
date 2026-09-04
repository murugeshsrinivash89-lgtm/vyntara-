"""
VYNTARA Public Demonstration — Longitudinal Physiological Analysis
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
import pandas as pd


@dataclass
class LongitudinalSummary:
    """Summary of repeated physiological sessions."""

    session_count: int
    mean_hr_bpm: float
    mean_rmssd_ms: float
    mean_sdnn_ms: float
    hr_trend: float
    rmssd_trend: float


def build_session_table(
    sessions: list[dict[str, float | str]],
) -> pd.DataFrame:
    """Convert repeated feature dictionaries into a DataFrame."""
    if not sessions:
        return pd.DataFrame(
            columns=["session", "heart_rate_bpm", "rmssd_ms", "sdnn_ms"]
        )

    frame = pd.DataFrame(sessions)

    required = ["heart_rate_bpm", "rmssd_ms", "sdnn_ms"]
    for column in required:
        if column not in frame:
            frame[column] = np.nan

    if "session" not in frame:
        frame["session"] = np.arange(1, len(frame) + 1)

    return frame[["session", *required]]


def _linear_trend(values: np.ndarray) -> float:
    """Return the slope of a simple session-index trend."""
    values = np.asarray(values, dtype=float)
    valid = np.isfinite(values)

    if np.sum(valid) < 2:
        return 0.0

    x = np.arange(len(values), dtype=float)[valid]
    y = values[valid]
    return float(np.polyfit(x, y, 1)[0])


def summarize_longitudinal(
    table: pd.DataFrame,
) -> LongitudinalSummary:
    """Calculate descriptive longitudinal statistics."""
    return LongitudinalSummary(
        session_count=len(table),
        mean_hr_bpm=float(table["heart_rate_bpm"].mean()),
        mean_rmssd_ms=float(table["rmssd_ms"].mean()),
        mean_sdnn_ms=float(table["sdnn_ms"].mean()),
        hr_trend=_linear_trend(table["heart_rate_bpm"].to_numpy()),
        rmssd_trend=_linear_trend(table["rmssd_ms"].to_numpy()),
    )


def create_demo_history(
    base_hr: float = 72.0,
    sessions: int = 14,
    seed: int = 2026,
) -> pd.DataFrame:
    """Create a reproducible longitudinal feature history for the demo."""
    rng = np.random.default_rng(seed)
    index = np.arange(sessions)

    # Smooth variation plus modest session-to-session noise.
    hr = base_hr + 2.2 * np.sin(index / 2.2) + rng.normal(0, 1.2, sessions)
    rmssd = 42.0 - 0.7 * index + 4.0 * np.cos(index / 2.7)
    rmssd += rng.normal(0, 1.8, sessions)
    sdnn = 48.0 - 0.4 * index + 3.5 * np.sin(index / 3.0)
    sdnn += rng.normal(0, 1.5, sessions)

    return pd.DataFrame(
        {
            "session": index + 1,
            "heart_rate_bpm": hr,
            "rmssd_ms": np.clip(rmssd, 15, None),
            "sdnn_ms": np.clip(sdnn, 20, None),
        }
    )
