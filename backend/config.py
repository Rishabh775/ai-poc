"""Configuration module for Operational Intelligence Dashboard.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.65"))
DBSCAN_EPS: float = float(os.getenv("DBSCAN_EPS", "0.32"))
MIN_SAMPLES: int = int(os.getenv("MIN_SAMPLES", "2"))
USE_HDBSCAN: bool = os.getenv("USE_HDBSCAN", "true").lower() == "true"
HDBSCAN_MIN_CLUSTER_SIZE: int = int(os.getenv("HDBSCAN_MIN_CLUSTER_SIZE", "3"))
HDBSCAN_MIN_SAMPLES: int = int(os.getenv("HDBSCAN_MIN_SAMPLES", "2"))
HDBSCAN_CLUSTER_SELECTION_EPSILON: float = float(
    os.getenv("HDBSCAN_CLUSTER_SELECTION_EPSILON", "0.12")
)
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-mpnet-base-v2")
HYBRID_WEIGHT_TEXT: float = float(os.getenv("HYBRID_WEIGHT_TEXT", "0.75"))
HYBRID_WEIGHT_CATEGORY: float = float(os.getenv("HYBRID_WEIGHT_CATEGORY", "0.20"))
HYBRID_WEIGHT_SEVERITY: float = float(os.getenv("HYBRID_WEIGHT_SEVERITY", "0.05"))

USE_PCA: bool = os.getenv("USE_PCA", "true").lower() == "true"
PCA_COMPONENTS: int = int(os.getenv("PCA_COMPONENTS", "128"))

SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 10.0,
    "high": 6.0,
    "medium": 3.0,
    "low": 1.0,
}

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-1.5-flash")
CLASSIFIER_ENABLED: bool = os.getenv("CLASSIFIER_ENABLED", "false").lower() == "true"

CATEGORY_LIST: List[str] = [
    "Review Comments",
    "Review Recommendation",
    "File handling",
    "Draft management",
    "Email service",
    "Session management",
    "Data integrity",
    "Performance",
    "Access control",
    "Status tracking",
    "Validation",
    "UI Preferences",
    "Static content",
]


def get_config() -> Dict:
    """Return configuration dictionary for runtime access."""
    return {
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "dbscan_eps": DBSCAN_EPS,
        "min_samples": MIN_SAMPLES,
        "use_hdbscan": USE_HDBSCAN,
        "hdbscan_min_cluster_size": HDBSCAN_MIN_CLUSTER_SIZE,
        "hdbscan_min_samples": HDBSCAN_MIN_SAMPLES,
        "hdbscan_cluster_selection_epsilon": HDBSCAN_CLUSTER_SELECTION_EPSILON,
        "embedding_model": EMBEDDING_MODEL,
        "hybrid_weights": {
            "text": HYBRID_WEIGHT_TEXT,
            "category": HYBRID_WEIGHT_CATEGORY,
            "severity": HYBRID_WEIGHT_SEVERITY,
        },
        "use_pca": USE_PCA,
        "pca_components": PCA_COMPONENTS,
        "severity_weights": SEVERITY_WEIGHTS,
        "classifier": {
            "enabled": CLASSIFIER_ENABLED,
            "model": LLM_MODEL,
            "categories": CATEGORY_LIST,
        },
    }
