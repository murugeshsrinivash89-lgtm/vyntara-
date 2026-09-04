"""
VYNTARA Public Demonstration — Visualization Utilities
"""

from __future__ import annotations

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


def plot_signals(
    time: np.ndarray,
    ecg: np.ndarray,
    ppg: np.ndarray,
    output_path: str = "vyntara_signals.png",
) -> None:
    """Plot the public demonstration ECG and PPG signals."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    axes[0].plot(time, ecg, linewidth=1.0)
    axes[0].set_title("VYNTARA Synthetic ECG")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(alpha=0.25)

    axes[1].plot(time, ppg, linewidth=1.0)
    axes[1].set_title("VYNTARA Synthetic PPG")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_ecg_processing(
    time: np.ndarray,
    raw_ecg: np.ndarray,
    processed_ecg: np.ndarray,
    peaks: np.ndarray,
    sampling_rate: float,
    output_path: str = "vyntara_ecg_processing.png",
) -> None:
    """Plot raw ECG, processed ECG and detected beat locations."""
    fig, axes = plt.subplots(2, 1, figsize=(12, 7), sharex=True)

    axes[0].plot(time, raw_ecg, linewidth=0.8)
    axes[0].set_title("Raw Synthetic ECG")
    axes[0].set_ylabel("Amplitude")
    axes[0].grid(alpha=0.25)

    axes[1].plot(time, processed_ecg, linewidth=0.9)
    if len(peaks):
        axes[1].scatter(
            peaks / sampling_rate,
            processed_ecg[peaks],
            s=18,
            label="Detected beats",
        )
        axes[1].legend()
    axes[1].set_title("Processed ECG and Beat Detection")
    axes[1].set_xlabel("Time (s)")
    axes[1].set_ylabel("Amplitude")
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)


def plot_longitudinal(
    history: pd.DataFrame,
    output_path: str = "vyntara_longitudinal_trends.png",
) -> None:
    """Plot repeated HR and HRV measurements."""
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)

    axes[0].plot(
        history["session"],
        history["heart_rate_bpm"],
        marker="o",
        linewidth=1.4,
    )
    axes[0].set_title("Longitudinal Heart Rate")
    axes[0].set_ylabel("BPM")
    axes[0].grid(alpha=0.25)

    axes[1].plot(
        history["session"],
        history["rmssd_ms"],
        marker="o",
        linewidth=1.4,
        label="RMSSD",
    )
    axes[1].plot(
        history["session"],
        history["sdnn_ms"],
        marker="o",
        linewidth=1.4,
        label="SDNN",
    )
    axes[1].set_title("Longitudinal HRV Features")
    axes[1].set_xlabel("Session")
    axes[1].set_ylabel("Milliseconds")
    axes[1].legend()
    axes[1].grid(alpha=0.25)

    fig.tight_layout()
    fig.savefig(output_path, dpi=160, bbox_inches="tight")
    plt.close(fig)
