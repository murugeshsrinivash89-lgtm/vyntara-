"""
VYNTARA Public Demonstration — Signal Preprocessing

Provides transparent, non-proprietary preprocessing operations used by the
public demonstration pipeline.
"""

from __future__ import annotations

import numpy as np
from scipy import signal


def moving_average(x: np.ndarray, window: int = 5) -> np.ndarray:
    """Apply centered moving-average smoothing."""
    x = np.asarray(x, dtype=float)

    if window < 1:
        raise ValueError("window must be >= 1.")
    if window == 1:
        return x.copy()

    kernel = np.ones(window, dtype=float) / window
    return np.convolve(x, kernel, mode="same")


def detrend_signal(x: np.ndarray) -> np.ndarray:
    """Remove a linear trend from a signal."""
    return signal.detrend(np.asarray(x, dtype=float))


def normalize_signal(x: np.ndarray) -> np.ndarray:
    """Standardize a signal to approximately zero mean and unit variance."""
    x = np.asarray(x, dtype=float)
    mean = np.mean(x)
    std = np.std(x)

    if std < 1e-12:
        return np.zeros_like(x)

    return (x - mean) / std


def bandpass_filter(
    x: np.ndarray,
    sampling_rate: float,
    low_hz: float = 0.5,
    high_hz: float = 20.0,
    order: int = 3,
) -> np.ndarray:
    """Apply a zero-phase Butterworth band-pass filter."""
    if not 0 < low_hz < high_hz < sampling_rate / 2:
        raise ValueError("Filter frequencies must lie below Nyquist.")

    sos = signal.butter(
        order,
        [low_hz, high_hz],
        btype="bandpass",
        fs=sampling_rate,
        output="sos",
    )
    return signal.sosfiltfilt(sos, np.asarray(x, dtype=float))


def preprocess_ecg(
    ecg: np.ndarray,
    sampling_rate: float,
    smoothing_window: int = 5,
) -> np.ndarray:
    """Run the public ECG preprocessing chain."""
    smoothed = moving_average(ecg, smoothing_window)
    detrended = detrend_signal(smoothed)
    return bandpass_filter(detrended, sampling_rate, 0.5, 20.0)


def preprocess_ppg(
    ppg: np.ndarray,
    sampling_rate: float,
    smoothing_window: int = 7,
) -> np.ndarray:
    """Run the public PPG preprocessing chain."""
    smoothed = moving_average(ppg, smoothing_window)
    detrended = detrend_signal(smoothed)
    return bandpass_filter(detrended, sampling_rate, 0.3, 8.0)


def preprocess_pair(
    ecg: np.ndarray,
    ppg: np.ndarray,
    sampling_rate: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Preprocess ECG and PPG using the public demonstration settings."""
    return (
        preprocess_ecg(ecg, sampling_rate),
        preprocess_ppg(ppg, sampling_rate),
    )
