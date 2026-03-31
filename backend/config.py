"""Configuration module for Operational Intelligence Dashboard.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.70"))
DBSCAN_EPS: float = float(os.getenv("DBSCAN_EPS", "0.35"))
MIN_SAMPLES: int = int(os.getenv("MIN_SAMPLES", "2"))  
USE_HDBSCAN: bool = os.getenv("USE_HDBSCAN", "false").lower() == "true"
HDBSCAN_MIN_CLUSTER_SIZE: int = int(os.getenv("HDBSCAN_MIN_CLUSTER_SIZE", "2"))
HDBSCAN_MIN_SAMPLES: int = int(os.getenv("HDBSCAN_MIN_SAMPLES", "1"))
HDBSCAN_CLUSTER_SELECTION_EPSILON: float = float(
    os.getenv("HDBSCAN_CLUSTER_SELECTION_EPSILON", "0.05")
)
# paraphrase-mpnet-base-v2 is trained specifically for paraphrase detection —
# sentences that mean the same thing but are worded differently get similar
# vectors even without any LLM rewriting step. This is a free upgrade over
# all-mpnet-base-v2 for the "same problem, different description" use case.
EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "paraphrase-mpnet-base-v2")
HYBRID_WEIGHT_TEXT: float = float(os.getenv("HYBRID_WEIGHT_TEXT", "0.85"))
HYBRID_WEIGHT_CATEGORY: float = float(os.getenv("HYBRID_WEIGHT_CATEGORY", "0.05"))
HYBRID_WEIGHT_SEVERITY: float = float(os.getenv("HYBRID_WEIGHT_SEVERITY", "0.05"))
HYBRID_WEIGHT_SYMPTOM: float = float(os.getenv("HYBRID_WEIGHT_SYMPTOM", "0.05"))

USE_PCA: bool = os.getenv("USE_PCA", "true").lower() == "true"
PCA_COMPONENTS: int = int(os.getenv("PCA_COMPONENTS", "12"))  # Tighter clustering

SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 10.0,
    "high": 6.0,
    "medium": 3.0,
    "low": 1.0,
}

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
CLASSIFIER_ENABLED: bool = os.getenv("CLASSIFIER_ENABLED", "false").lower() == "true"
CATEGORY_MODE: str = os.getenv("CATEGORY_MODE", "dynamic").lower()

# ── Normalization mode ────────────────────────────────────────────────────
# Three mutually exclusive modes (checked in order of priority):
#
#  USE_LLM_NORMALIZATION=true   → Gemini API (best quality, needs API key)
#  USE_LOCAL_NORMALIZATION=true → FLAN-T5 local model (good quality, no key,
#                                 downloads ~300 MB once, runs on CPU)
#  neither                      → standard regex normalization (always works)
#
# In both LLM and local modes the system rewrites every ticket into a single
# canonical problem sentence before embedding, so "comment reply missing for
# reviewer" and "author's reply not appearing in panel" produce near-identical
# vectors and cluster together correctly.
USE_LLM_NORMALIZATION: bool = os.getenv("USE_LLM_NORMALIZATION", "false").lower() == "true"
LLM_NORMALIZATION_BATCH_SIZE: int = int(os.getenv("LLM_NORMALIZATION_BATCH_SIZE", "10"))

USE_LOCAL_NORMALIZATION: bool = os.getenv("USE_LOCAL_NORMALIZATION", "false").lower() == "true"
LOCAL_NORMALIZATION_MODEL: str = os.getenv("LOCAL_NORMALIZATION_MODEL", "google/flan-t5-base")

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
            "symptom": HYBRID_WEIGHT_SYMPTOM,
        },
        "use_pca": USE_PCA,
        "pca_components": PCA_COMPONENTS,
        "severity_weights": SEVERITY_WEIGHTS,
        "classifier": {
            "enabled": CLASSIFIER_ENABLED,
            "model": LLM_MODEL,
            "categories": CATEGORY_LIST,
            "mode": CATEGORY_MODE,
        },
        "llm_normalization": {
            "enabled": USE_LLM_NORMALIZATION,
            "batch_size": LLM_NORMALIZATION_BATCH_SIZE,
        },
        "local_normalization": {
            "enabled": USE_LOCAL_NORMALIZATION,
            "model": LOCAL_NORMALIZATION_MODEL,
        },
    }
