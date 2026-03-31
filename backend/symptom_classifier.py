"""Lightweight symptom classifier for finer-grained ticket context.

Adds a cross-category "what actually went wrong" label so broad categories
like File handling can still be separated into timeout vs corruption vs
validation vs stuck-progress style issues.
"""

from typing import Dict, List, Tuple
import re


SYMPTOM_RULES: List[Tuple[str, List[str]]] = [
    (
        "Missing UI action",
        [
            "missing",
            "not visible",
            "reply button",
            "option unavailable",
            "lacks the button",
            "only sees",
        ],
    ),
    (
        "Access error",
        [
            "permission denied",
            "forbidden",
            "unauthorized",
            "can't show this page",
            "cannot access",
            "access error",
            "invitation link",
        ],
    ),
    (
        "Timeout",
        [
            "timeout",
            "times out",
            "timed out",
            "connection reset",
            "reset by peer",
        ],
    ),
    (
        "Stuck progress",
        [
            "stuck",
            "hangs at",
            "99%",
            "pending indefinitely",
            "never completes",
            "keeps loading",
            "progress bar",
        ],
    ),
    (
        "Validation rejection",
        [
            "format not supported",
            "unsupported file format",
            "validation",
            "required field",
            "reject",
            "rejected",
            "quota exceeded",
        ],
    ),
    (
        "Data corruption",
        [
            "corrupted",
            "altered during transfer",
            "cannot be opened",
            "broken file",
            "hash shows",
        ],
    ),
    (
        "Download failure",
        [
            "download fails",
            "unable to download",
            "download button",
            "download link",
            "download opens blank page",
            "export",
        ],
    ),
    (
        "Browser/client issue",
        [
            "browser freezes",
            "freezes",
            "safari",
            "popup error",
            "across browsers",
        ],
    ),
    (
        "Server/internal error",
        [
            "server error",
            "error 500",
            "internal error",
            "fails silently",
            "returns error",
        ],
    ),
]


def classify_ticket(ticket: Dict) -> str:
    """Infer the main symptom pattern from the ticket text."""
    text = f"{ticket.get('title', '')}. {ticket.get('description', '')}".lower()
    text = re.sub(r"\s+", " ", text)

    for symptom, phrases in SYMPTOM_RULES:
        if any(phrase in text for phrase in phrases):
            return symptom

    if "upload" in text:
        return "Upload failure"
    if "download" in text:
        return "Download failure"
    if "comment" in text or "reply" in text:
        return "Comment workflow issue"
    return "General failure"


def classify_tickets_batch(tickets: List[Dict]) -> Dict[str, str]:
    """Classify multiple tickets into symptom patterns."""
    return {
        ticket.get("id", f"unknown_{idx}"): classify_ticket(ticket)
        for idx, ticket in enumerate(tickets)
    }


def enrich_tickets_with_symptoms(tickets: List[Dict]) -> List[Dict]:
    """Add a symptom field to each ticket."""
    symptoms_map = classify_tickets_batch(tickets)
    enriched = []
    for ticket in tickets:
        ticket_copy = ticket.copy()
        ticket_copy["symptom"] = symptoms_map.get(ticket.get("id", ""), "General failure")
        enriched.append(ticket_copy)
    return enriched
