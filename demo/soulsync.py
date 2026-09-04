"""
VYNTARA Public Demonstration — SoulSync

SoulSync is represented here as a longitudinal monitoring demonstration.
The public classifier is intentionally transparent and is not a medical
diagnostic system.
"""

from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


@dataclass
class SoulSyncResult:
    """Monitoring result returned by the public demonstration."""

    category: str
    confidence: float


CATEGORIES = (
    "Calm",
    "Mild Stress",
    "Moderate Stress",
    "High Stress",
)


def _training_data() -> tuple[np.ndarray, np.ndarray]:
    """Create deterministic demonstration training examples."""
    rng = np.random.default_rng(7)

    calm = np.column_stack(
        [
            rng.normal(65, 4, 80),
            rng.normal(52, 7, 80),
            rng.normal(58, 8, 80),
        ]
    )

    mild = np.column_stack(
        [
            rng.normal(72, 4, 80),
            rng.normal(43, 6, 80),
            rng.normal(50, 7, 80),
        ]
    )

    moderate = np.column_stack(
        [
            rng.normal(80, 5, 80),
            rng.normal(33, 5, 80),
            rng.normal(42, 6, 80),
        ]
    )

    high = np.column_stack(
        [
            rng.normal(90, 5, 80),
            rng.normal(24, 4, 80),
            rng.normal(34, 5, 80),
        ]
    )

    x = np.vstack([calm, mild, moderate, high])
    y = np.repeat(CATEGORIES, 80)
    return x, y


def build_model() -> Pipeline:
    """Build the public demonstration classifier."""
    x, y = _training_data()

    model = Pipeline(
        [
            ("scaler", StandardScaler()),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    multi_class="auto",
                    random_state=11,
                ),
            ),
        ]
    )
    model.fit(x, y)
    return model


def classify(
    heart_rate_bpm: float,
    rmssd_ms: float,
    sdnn_ms: float,
) -> SoulSyncResult:
    """Classify one feature vector into a monitoring category."""
    if not all(np.isfinite([heart_rate_bpm, rmssd_ms, sdnn_ms])):
        return SoulSyncResult("Insufficient Data", 0.0)

    model = build_model()
    x = np.array([[heart_rate_bpm, rmssd_ms, sdnn_ms]])
    probabilities = model.predict_proba(x)[0]
    index = int(np.argmax(probabilities))

    return SoulSyncResult(
        category=str(model.classes_[index]),
        confidence=float(probabilities[index]),
    )


def monitoring_message(result: SoulSyncResult) -> str:
    """Return a neutral user-facing monitoring message."""
    if result.category == "Insufficient Data":
        return "Additional physiological data are required for this session."

    return (
        f"SoulSync monitoring state: {result.category} "
        f"({result.confidence * 100:.1f}% demonstration confidence)."
    )
