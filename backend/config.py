"""Configuration module for Operational Intelligence Dashboard.
Loads settings from environment variables with sensible defaults.
"""

import os
from typing import Dict

SIMILARITY_THRESHOLD: float = float(os.getenv("SIMILARITY_THRESHOLD", "0.80"))
DBSCAN_EPS: float = float(os.getenv("DBSCAN_EPS", "0.5"))
MIN_SAMPLES: int = int(os.getenv("MIN_SAMPLES", "2"))

SEVERITY_WEIGHTS: Dict[str, float] = {
    "critical": 10.0,
    "high": 6.0,
    "medium": 3.0,
    "low": 1.0,
}

WORKFLOW_ENCODINGS: Dict[str, list] = {
    "": [0.0, 0.0, 0.0, 0.0, 0.0],
    "submission": [1.0, 0.0, 0.0, 0.0, 0.0],
    "review": [0.0, 1.0, 0.0, 0.0, 0.0],
    "dashboard": [0.0, 0.0, 1.0, 0.0, 0.0],
    "release": [0.0, 0.0, 0.0, 1.0, 0.0],
    "infra": [0.0, 0.0, 0.0, 0.0, 1.0],
}

WORKFLOW_TO_TEAM: Dict[str, str] = {
    "": "Unassigned",
    "submission": "Backend Team",
    "review": "Platform Team",
    "dashboard": "Frontend Team",
    "release": "Release Engineering",
    "infra": "DevOps",
}

ACTION_TEMPLATES: Dict[str, list] = {
    "submission": [
        "Audit workflow state machine and fix invalid transition paths",
        "Add retry logic and dead-letter queue for stuck validations",
        "Review validation rules and DOI regex patterns",
    ],
    "review": [
        "Investigate reviewer assignment algorithm and load distribution",
        "Add capacity-based routing and preference matching fixes",
        "Implement queue depth alerts and auto-scaling for backlog",
    ],
    "dashboard": [
        "Optimize analytics queries and add missing indexes",
        "Implement chart virtualization and data aggregation",
        "Add caching layer for real-time metrics endpoint",
    ],
    "release": [
        "Add pre-deployment regression test suite for critical paths",
        "Implement feature flag rollout with canary deployment",
        "Review migration scripts for NULL handling before production",
    ],
    "infra": [
        "Scale connection pools and tune timeout settings",
        "Review autoscaling policies and resource limits",
        "Implement circuit breakers for third-party API calls",
    ],
}


def get_config() -> Dict:
    """Return configuration dictionary for runtime access."""
    return {
        "similarity_threshold": SIMILARITY_THRESHOLD,
        "dbscan_eps": DBSCAN_EPS,
        "min_samples": MIN_SAMPLES,
        "severity_weights": SEVERITY_WEIGHTS,
        "workflow_encodings": WORKFLOW_ENCODINGS,
    }
