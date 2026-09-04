"""
VYNTARA Public Demonstration — End-to-End Runner

Run from the demo directory:

    python run_demo.py

The runner demonstrates:
1. Synthetic ECG/PPG generation
2. Public preprocessing
3. Signal-quality assessment
4. Cardiac feature extraction
5. Longitudinal physiological analysis
6. SoulSync monitoring classification
7. Wearable/AION interaction context
8. Visualization output

This is a software demonstration and is not a medical device.
"""

from __future__ import annotations

from pathlib import Path
import sys

import numpy as np

# Allow direct execution from the demo directory.
DEMO_DIR = Path(__file__).resolve().parent
if str(DEMO_DIR) not in sys.path:
    sys.path.insert(0, str(DEMO_DIR))

from signal_generator import generate_recording
from cardiac_engine import CardiacEngine, summarize
from longitudinal_analysis import create_demo_history, summarize_longitudinal
from soulsync import classify, monitoring_message
from interaction import build_aion_context, build_wearable_state, render_console
from visualizations import (
    plot_ecg_processing,
    plot_longitudinal,
    plot_signals,
)


def main() -> None:
    """Execute the complete public demonstration."""
    output_dir = DEMO_DIR / "outputs"
    output_dir.mkdir(exist_ok=True)

    print("\n" + "=" * 64)
    print("VYNTARA — PUBLIC ENGINEERING DEMONSTRATION")
    print("=" * 64)

    recording = generate_recording(
        duration=30.0,
        heart_rate_bpm=72.0,
        variability=0.025,
        noise_level=0.025,
        artifact_strength=0.08,
        seed=42,
    )

    print("\n[1] Signal acquisition")
    print(f"ECG samples: {len(recording.ecg)}")
    print(f"Sampling rate: {recording.sampling_rate:.0f} Hz")
    print(f"Nominal HR: {recording.nominal_heart_rate_bpm:.1f} BPM")

    engine = CardiacEngine(recording.sampling_rate)
    result = engine.run(
        recording.ecg,
        reference=recording.clean_ecg,
    )

    values = summarize(result)

    print("\n[2] Cardiac Engine")
    print(f"Signal accepted: {values['accepted']}")
    print(f"Quality before: {values['quality_before']:.1f}/100")
    print(f"Quality after:  {values['quality_after']:.1f}/100")
    print(f"Pattern similarity: {values['pattern_similarity']:.3f}")
    print(f"Heart rate: {values['heart_rate_bpm']:.1f} BPM")
    print(f"Mean RR: {values['mean_rr_ms']:.1f} ms")
    print(f"RMSSD: {values['rmssd_ms']:.1f} ms")
    print(f"SDNN: {values['sdnn_ms']:.1f} ms")

    soul = classify(
        float(values["heart_rate_bpm"]),
        float(values["rmssd_ms"]),
        float(values["sdnn_ms"]),
    )

    print("\n[3] SoulSync")
    print(monitoring_message(soul))

    state = build_wearable_state(
        heart_rate_bpm=float(values["heart_rate_bpm"]),
        rmssd_ms=float(values["rmssd_ms"]),
        sdnn_ms=float(values["sdnn_ms"]),
        quality_index=float(values["quality_after"]),
        monitoring_state=soul.category,
    )
    render_console(state)

    print("\n[AION CONTEXT]")
    print(build_aion_context(state))

    history = create_demo_history()
    summary = summarize_longitudinal(history)

    print("\n[4] Longitudinal Analysis")
    print(f"Sessions: {summary.session_count}")
    print(f"Mean HR: {summary.mean_hr_bpm:.1f} BPM")
    print(f"Mean RMSSD: {summary.mean_rmssd_ms:.1f} ms")
    print(f"Mean SDNN: {summary.mean_sdnn_ms:.1f} ms")
    print(f"HR trend/session: {summary.hr_trend:+.2f}")
    print(f"RMSSD trend/session: {summary.rmssd_trend:+.2f}")

    plot_signals(
        recording.time,
        recording.ecg,
        recording.ppg,
        str(output_dir / "vyntara_signals.png"),
    )

    plot_ecg_processing(
        recording.time,
        recording.ecg,
        result.processed_ecg,
        result.features.beat_indices,
        recording.sampling_rate,
        str(output_dir / "vyntara_ecg_processing.png"),
    )

    plot_longitudinal(
        history,
        str(output_dir / "vyntara_longitudinal_trends.png"),
    )

    print("\n[5] Outputs")
    print(f"Saved demonstration plots to: {output_dir}")
    print("\nDemonstration complete.")
    print("Note: Synthetic data only; not for clinical decision-making.")


if __name__ == "__main__":
    main()
