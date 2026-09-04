"""
VYNTARA Public Demonstration — Signal Quality Assessment

The public implementation provides transparent quality metrics for demo
purposes. It does not expose the private VYNTARA signal-quality methodology.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from scipy import signal


@dataclass
class QualityReport:
    """Summary of a signal-quality assessment."""

    quality_index: float
    variance_score: float
    periodicity_score: float
    stability_score: float
    status: str


def _clip01(value: float) -> float:
    return float(np.clip(value, 0.0, 1.0))


def normalized_variance_score(x: np.ndarray) -> float:
    """Estimate whether signal amplitude is within a useful range."""
    x = np.asarray(x, dtype=float)
    spread = np.std(x)
    if spread < 1e-8:
        return 0.0
    return _clip01(1.0 - abs(np.log10(spread + 1e-6) + 1.0) / 3.0)


def periodicity_score(x: np.ndarray) -> float:
    """Estimate repeating structure using autocorrelation."""
    x = np.asarray(x, dtype=float)
    x = x - np.mean(x)

    if np.linalg.norm(x) < 1e-10:
        return 0.0

    corr = signal.fftconvolve(x, x[::-1], mode="full")
    center = len(x) - 1
    corr = corr[center:] / max(corr[center], 1e-12)

    if len(corr) < 20:
        return 0.0

    search_end = min(len(corr), int(0.8 * len(corr)))
    peak = np.max(corr[5:search_end])
    return _clip01(float(peak))


def stability_score(x: np.ndarray, segments: int = 8) -> float:
    """Compare segment-level standard deviations for consistency."""
    x = np.asarray(x, dtype=float)

    if len(x) < segments * 2:
        return 0.0

    pieces = np.array_split(x, segments)
    spreads = np.asarray([np.std(piece) for piece in pieces])
    mean_spread = np.mean(spreads)

    if mean_spread < 1e-10:
        return 0.0

    coefficient = np.std(spreads) / mean_spread
    return _clip01(1.0 - coefficient)


def assess_signal_quality(x: np.ndarray) -> QualityReport:
    """Compute a public demonstration signal-quality index."""
    variance = normalized_variance_score(x)
    periodicity = periodicity_score(x)
    stability = stability_score(x)

    quality = 100.0 * (
        0.25 * variance + 0.45 * periodicity + 0.30 * stability
    )

    status = (
        "HIGH"
        if quality >= 75
        else "ACCEPTABLE"
        if quality >= 50
        else "LOW"
    )

    return QualityReport(
        quality_index=float(quality),
        variance_score=variance,
        periodicity_score=periodicity,
        stability_score=stability,
        status=status,
    )


def cross_correlation_similarity(
    reference: np.ndarray,
    observed: np.ndarray,
) -> float:
    """Return normalized zero-lag correlation between two equal-length signals."""
    a = np.asarray(reference, dtype=float)
    b = np.asarray(observed, dtype=float)

    n = min(len(a), len(b))
    a = a[:n] - np.mean(a[:n])
    b = b[:n] - np.mean(b[:n])

    denominator = np.linalg.norm(a) * np.linalg.norm(b)
    if denominator < 1e-12:
        return 0.0

    return float(np.dot(a, b) / denominator)
