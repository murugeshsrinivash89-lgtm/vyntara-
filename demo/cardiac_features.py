"""
VYNTARA Public Demonstration — Cardiac Feature Extraction
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class CardiacFeatures:
    """Physiological features derived from detected beat locations."""

    heart_rate_bpm: float
    mean_rr_ms: float
    rmssd_ms: float
    sdnn_ms: float
    rr_intervals_ms: np.ndarray
    beat_indices: np.ndarray


def detect_r_peaks(
    ecg: np.ndarray,
    sampling_rate: float,
    minimum_distance_s: float = 0.45,
    prominence_fraction: float = 0.35,
) -> np.ndarray:
    """Detect candidate ECG peaks using a transparent prominence rule."""
    from scipy.signal import find_peaks

    x = np.asarray(ecg, dtype=float)
    prominence = max(np.std(x) * prominence_fraction, 0.05)
    distance = max(1, int(minimum_distance_s * sampling_rate))

    peaks, _ = find_peaks(
        x,
        distance=distance,
        prominence=prominence,
    )
    return peaks


def rr_intervals_from_peaks(
    peaks: np.ndarray,
    sampling_rate: float,
) -> np.ndarray:
    """Convert peak indices into RR intervals in milliseconds."""
    peaks = np.asarray(peaks, dtype=int)

    if len(peaks) < 2:
        return np.asarray([], dtype=float)

    return np.diff(peaks) / sampling_rate * 1000.0


def compute_hrv(
    rr_intervals_ms: np.ndarray,
    peaks: np.ndarray | None = None,
) -> CardiacFeatures:
    """Compute HR, mean RR, RMSSD and SDNN from RR intervals."""
    rr = np.asarray(rr_intervals_ms, dtype=float)

    if len(rr) == 0:
        return CardiacFeatures(
            np.nan, np.nan, np.nan, np.nan, rr, np.asarray([], dtype=int)
        )

    mean_rr = float(np.mean(rr))
    heart_rate = 60000.0 / mean_rr if mean_rr > 0 else np.nan

    if len(rr) >= 2:
        successive = np.diff(rr)
        rmssd = float(np.sqrt(np.mean(successive ** 2)))
    else:
        rmssd = np.nan

    sdnn = float(np.std(rr, ddof=1)) if len(rr) >= 2 else np.nan

    return CardiacFeatures(
        heart_rate_bpm=float(heart_rate),
        mean_rr_ms=mean_rr,
        rmssd_ms=rmssd,
        sdnn_ms=sdnn,
        rr_intervals_ms=rr,
        beat_indices=np.asarray(peaks if peaks is not None else [], dtype=int),
    )


def extract_cardiac_features(
    ecg: np.ndarray,
    sampling_rate: float,
) -> CardiacFeatures:
    """Run peak detection and HRV feature extraction."""
    peaks = detect_r_peaks(ecg, sampling_rate)
    rr = rr_intervals_from_peaks(peaks, sampling_rate)
    return compute_hrv(rr, peaks)
