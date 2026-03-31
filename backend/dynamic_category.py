"""Dynamic category generation based on ticket topic and symptom.

Produces labels that adapt to the incident text instead of forcing every
ticket into a small fixed taxonomy. We still allow the broad taxonomy to
exist separately for evaluation and fallback.
"""

from typing import Dict, List, Tuple

import symptom_classifier


TOPIC_RULES: List[Tuple[str, List[str]]] = [
    ("Upload", ["upload", "uploaded", "attachment", "supplementary file"]),
    ("Download", ["download", "export", "pdf format"]),
    ("Review Workflow", ["review", "reviewer", "comments", "reply"]),
    ("Access Journey", ["access", "permission", "forbidden", "invitation link"]),
    ("Session", ["session", "logged out", "keep-alive"]),
    ("Draft/Autosave", ["draft", "autosave", "saved state", "cover letter"]),
    ("Email Delivery", ["email", "smtp", "notification", "reminder"]),
    ("Status Flow", ["status", "workflow", "with editor", "deadline"]),
    ("Validation", ["validation", "invalid", "required field", "format"]),
    ("Performance", ["slow", "latency", "timeout", "spinner"]),
    ("Preferences", ["dark mode", "theme", "preference"]),
    ("Static Content", ["homepage", "label", "impact factor", "static content"]),
]


def infer_topic(ticket: Dict) -> str:
    """Infer the main functional area from title and description."""
    text = f"{ticket.get('title', '')}. {ticket.get('description', '')}".lower()

    for topic, phrases in TOPIC_RULES:
        if any(phrase in text for phrase in phrases):
            return topic

    return "General Workflow"


def build_dynamic_category(ticket: Dict) -> str:
    """Build a dynamic category label from topic and symptom."""
    topic = infer_topic(ticket)
    symptom = ticket.get("symptom") or symptom_classifier.classify_ticket(ticket)

    if symptom in {"General failure", "Upload failure", "Download failure"}:
        return f"{topic} - Failure"
    return f"{topic} - {symptom}"


def enrich_tickets_with_dynamic_categories(tickets: List[Dict]) -> List[Dict]:
    """Add a dynamic category while preserving any existing broad taxonomy."""
    enriched = []
    for ticket in tickets:
        ticket_copy = ticket.copy()
        if "taxonomy_category" not in ticket_copy and "category" in ticket_copy:
            ticket_copy["taxonomy_category"] = ticket_copy["category"]
        ticket_copy["category"] = build_dynamic_category(ticket_copy)
        enriched.append(ticket_copy)
    return enriched
