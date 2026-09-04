"""
VYNTARA Public Demonstration — Interaction Layer
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class InteractionState:
    """State prepared for wearable and AION-facing demonstrations."""

    display_title: str
    display_lines: list[str]
    vibration: str
    physiological_context: dict[str, float | str]


def build_wearable_state(
    heart_rate_bpm: float,
    rmssd_ms: float,
    sdnn_ms: float,
    quality_index: float,
    monitoring_state: str,
) -> InteractionState:
    """Convert physiological output into simple wearable feedback."""
    if quality_index < 50:
        vibration = "signal_check"
    elif monitoring_state in {"Moderate Stress", "High Stress"}:
        vibration = "gentle_attention"
    else:
        vibration = "none"

    lines = [
        f"HR   {heart_rate_bpm:.0f} BPM",
        f"RMSSD {rmssd_ms:.1f} ms",
        f"SDNN  {sdnn_ms:.1f} ms",
        f"State {monitoring_state}",
        f"SQI   {quality_index:.0f}/100",
    ]

    context = {
        "heart_rate_bpm": float(heart_rate_bpm),
        "rmssd_ms": float(rmssd_ms),
        "sdnn_ms": float(sdnn_ms),
        "signal_quality": float(quality_index),
        "monitoring_state": monitoring_state,
    }

    return InteractionState(
        display_title="VYNTARA",
        display_lines=lines,
        vibration=vibration,
        physiological_context=context,
    )


def build_aion_context(state: InteractionState) -> str:
    """Create a compact context payload for the public AION demonstration."""
    context = state.physiological_context

    return (
        "VYNTARA physiological context | "
        f"HR={context['heart_rate_bpm']:.1f} BPM | "
        f"RMSSD={context['rmssd_ms']:.1f} ms | "
        f"SDNN={context['sdnn_ms']:.1f} ms | "
        f"SQI={context['signal_quality']:.1f}/100 | "
        f"State={context['monitoring_state']}"
    )


def render_console(state: InteractionState) -> None:
    """Print the wearable-style state to a terminal."""
    print("\n[VYNTARA DISPLAY]")
    print("=" * 28)
    print(state.display_title)

    for line in state.display_lines:
        print(line)

    print(f"Vibration: {state.vibration}")
    print("=" * 28)
