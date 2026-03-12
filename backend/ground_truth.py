"""Ground truth labels for evaluation purposes.
Categories are NOT included in production tickets but stored here
for measuring clustering quality.
"""

TICKET_CATEGORIES = {
    "OPS-004": "Review Comments",
    "OPS-005": "Review Comments",
    "OPS-006": "Review Comments",
    "OPS-007": "Review Recommendation",
    "OPS-008": "Review Recommendation",
    "OPS-009": "Review Recommendation",
    "SE-012": "File handling",
    "SE-013": "File handling",
    "SE-014": "File handling",
    "SE-015": "Draft management",
    "SE-016": "Draft management",
    "SE-017": "Draft management",
    "SE-018": "Email service",
    "SE-019": "Email service",
    "SE-020": "Email service",
    "SE-021": "Session management",
    "SE-022": "Session management",
    "SE-023": "Data integrity",
    "SE-024": "Data integrity",
    "SE-025": "Performance",
    "SE-026": "Performance",
    "SE-027": "Performance",
    "SE-028": "Access control",
    "SE-029": "Access control",
    "SE-030": "Access control",
    "SE-031": "Status tracking",
    "SE-032": "Status tracking",
    "SE-033": "Status tracking",
    "SE-034": "Validation",
    "SE-035": "Validation",
    "SE-036": "UI Preferences",
    "SE-037": "Static content",
}

ALL_CATEGORIES = [
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


def get_category(ticket_id: str) -> str:
    return TICKET_CATEGORIES.get(ticket_id, "unknown")


def get_all_categories() -> list:
    return ALL_CATEGORIES.copy()
