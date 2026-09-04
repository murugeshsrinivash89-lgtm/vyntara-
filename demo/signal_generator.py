"""
VYNTARA Public Demonstration — Synthetic Physiological Signal Generator

This module generates reproducible ECG- and PPG-like signals for software
development, visualization, and pipeline testing.

The generated data are synthetic and are not intended for clinical use.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass
class SignalBundle:
    """Container for a synchronized synthetic ECG/PPG recording."""

    time: np.ndarray
    ecg: np.ndarray
    ppg: np.ndarray
    clean_ecg: np.ndarray
    clean_ppg: np.ndarray
    sampling_rate: float
    nominal_heart_rate_bpm: float


def _gaussian_pulse(
    x: np.ndarray, center: float, width: float, amplitude: float
) -> np.ndarray:
    """Create a Gaussian-shaped physiological component."""
    return amplitude * np.exp(-0.5 * ((x - center) / width) ** 2)


def _rr_series(
    duration: float,
    heart_rate_bpm: float,
    variability: float,
    rng: np.random.Generator,
) -> np.ndarray:
    """Create a gently varying sequence of RR intervals."""
    mean_rr = 60.0 / heart_rate_bpm
    count = int(duration / mean_rr) + 4

    slow = np.sin(np.linspace(0, 4 * np.pi, count)) * variability
    random_component = rng.normal(0.0, variability * 0.35, count)

    rr = mean_rr * (1.0 + slow + random_component)
    return np.clip(rr, mean_rr * 0.80, mean_rr * 1.20)


def _beat_times(duration: float, rr: np.ndarray) -> np.ndarray:
    """Convert RR intervals to beat timestamps."""
    timestamps: list[float] = []
    current = 0.45

    for interval in rr:
        if current >= duration:
            break
        timestamps.append(current)
        current += float(interval)

    return np.asarray(timestamps)


def generate_ecg(
    duration: float = 30.0,
    sampling_rate: float = 250.0,
    heart_rate_bpm: float = 72.0,
    variability: float = 0.025,
    noise_level: float = 0.025,
    artifact_strength: float = 0.0,
    seed: int = 42,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate time, clean ECG, and observed ECG signals."""
    if duration <= 0 or sampling_rate <= 0:
        raise ValueError("duration and sampling_rate must be positive.")

    rng = np.random.default_rng(seed)
    n = int(duration * sampling_rate)
    time = np.arange(n) / sampling_rate
    signal = np.zeros(n, dtype=float)

    rr = _rr_series(duration, heart_rate_bpm, variability, rng)
    beats = _beat_times(duration, rr)

    # Public demonstration morphology: P, Q, R, S and T components.
    for beat in beats:
        signal += _gaussian_pulse(time, beat - 0.18, 0.035, 0.10)
        signal += _gaussian_pulse(time, beat - 0.045, 0.012, -0.14)
        signal += _gaussian_pulse(time, beat, 0.010, 1.00)
        signal += _gaussian_pulse(time, beat + 0.040, 0.014, -0.22)
        signal += _gaussian_pulse(time, beat + 0.23, 0.075, 0.28)

    baseline = 0.035 * np.sin(2 * np.pi * 0.25 * time)
    clean = signal + baseline

    observed = clean.copy()
    observed += rng.normal(0.0, noise_level, n)

    if artifact_strength > 0:
        burst = np.zeros(n)
        start = int(0.38 * n)
        stop = min(n, start + int(0.08 * n))
        burst[start:stop] = artifact_strength * np.sin(
            np.linspace(0, 14 * np.pi, stop - start)
        )
        observed += burst

    return time, clean, observed


def generate_ppg(
    duration: float = 30.0,
    sampling_rate: float = 100.0,
    heart_rate_bpm: float = 72.0,
    variability: float = 0.025,
    noise_level: float = 0.018,
    artifact_strength: float = 0.0,
    seed: int = 43,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Generate time, clean PPG, and observed PPG signals."""
    rng = np.random.default_rng(seed)
    n = int(duration * sampling_rate)
    time = np.arange(n) / sampling_rate
    signal = np.zeros(n, dtype=float)

    rr = _rr_series(duration, heart_rate_bpm, variability, rng)
    beats = _beat_times(duration, rr)

    for beat in beats:
        # Pulse onset, main systolic peak, and a small reflected component.
        signal += _gaussian_pulse(time, beat + 0.08, 0.085, 0.75)
        signal += _gaussian_pulse(time, beat + 0.18, 0.12, 0.22)
        signal += _gaussian_pulse(time, beat + 0.42, 0.055, 0.08)

    baseline = 0.025 * np.sin(2 * np.pi * 0.18 * time)
    clean = signal + baseline

    observed = clean + rng.normal(0.0, noise_level, n)

    if artifact_strength > 0:
        start = int(0.55 * n)
        stop = min(n, start + int(0.06 * n))
        observed[start:stop] += artifact_strength * np.sin(
            np.linspace(0, 10 * np.pi, stop - start)
        )

    return time, clean, observed


def generate_recording(
    duration: float = 30.0,
    ecg_sampling_rate: float = 250.0,
    ppg_sampling_rate: float = 100.0,
    heart_rate_bpm: float = 72.0,
    variability: float = 0.025,
    noise_level: float = 0.025,
    artifact_strength: float = 0.0,
    seed: int = 42,
) -> SignalBundle:
    """Generate a synchronized synthetic ECG/PPG demonstration recording."""
    ecg_time, clean_ecg, ecg = generate_ecg(
        duration,
        ecg_sampling_rate,
        heart_rate_bpm,
        variability,
        noise_level,
        artifact_strength,
        seed,
    )

    ppg_time, clean_ppg, ppg = generate_ppg(
        duration,
        ppg_sampling_rate,
        heart_rate_bpm,
        variability,
        noise_level * 0.7,
        artifact_strength * 0.7,
        seed + 1,
    )

    # PPG is generated on its own sampling grid. For the public bundle,
    # preserve the ECG time base and interpolate PPG for synchronized plotting.
    ppg_on_ecg_grid = np.interp(ecg_time, ppg_time, ppg)
    clean_ppg_on_ecg_grid = np.interp(ecg_time, ppg_time, clean_ppg)

    return SignalBundle(
        time=ecg_time,
        ecg=ecg,
        ppg=ppg_on_ecg_grid,
        clean_ecg=clean_ecg,
        clean_ppg=clean_ppg_on_ecg_grid,
        sampling_rate=ecg_sampling_rate,
        nominal_heart_rate_bpm=heart_rate_bpm,
    )


if __name__ == "__main__":
    recording = generate_recording()
    print(f"Generated {recording.time.size} samples.")
    print(f"Sampling rate: {recording.sampling_rate:.1f} Hz")
    print(f"Nominal HR: {recording.nominal_heart_rate_bpm:.1f} BPM")
