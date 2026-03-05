"""Configuration module for Operational Intelligence Dashboard.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Dict

SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.55"))
DBSCAN_EPS: float = float(os.getenv("DBSCAN_EPS", "0.48"))
MIN_SAMPLES: int = int(os.getenv("MIN_SAMPLES", "2"))

SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 10.0,
    "high": 6.0,
    "medium": 3.0,
    "low": 1.0,
}


def get_config() -> Dict:
    """Return configuration dictionary for runtime access."""
    return {
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "dbscan_eps": DBSCAN_EPS,
        "min_samples": MIN_SAMPLES,
        "severity_weights": SEVERITY_WEIGHTS,
    }