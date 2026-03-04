"""Demo ticket generator for Operational Intelligence Dashboard.
Generates realistic Jira-style tickets with specific test scenarios.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict


WORKFLOW_TO_TEAM = {
    "submission": "Backend Team",
    "review": "Platform Team",
    "dashboard": "Frontend Team",
    "release": "Release Engineering",
    "infra": "DevOps",
}


class TicketGenerator:
    """Generates realistic test tickets for operational intelligence testing."""

    TEST_TICKETS: List[Dict] = [
        {
            "id": "OPS-001",
            "title": "Reviewer unable to add comments in R1 round",
            "description": "The reviewer is unable to add comments in the R1 round. The comment box appears active but typed content does not persist. This issue is occurring in the peer review workflow for manuscript ID JMED-D-25-00412.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Comments",
        },
        {
            "id": "OPS-002",
            "title": "Reviewer cannot add recommendation in initial round",
            "description": "During the review process, the reviewer completed their assessment but was unable to save or submit the final recommendation (Accept / Minor Revision / Reject). After selecting a recommendation and clicking Save, the selection resets to blank.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Recommendation",
        },
        {
            "id": "OPS-003",
            "title": "Reviewer comments disappear after submission attempt",
            "description": "Multiple reviewers have reported that after entering detailed comments for authors and editors, the system throws a timeout error and clears the input fields. This prevents them from completing the review. The problem started after the latest deployment affecting the review module.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Comments",
        },
        {
    "id": "SE-002",
    "title": "File upload fails for large documents",
    "description": "Users receive an error when uploading files larger than 10MB during submission.",
    "workflow_type": "submission",
    "severity": "high",
    "category": "File handling"
},
{
    "id": "SE-003",
    "title": "Form validation not triggering on required fields",
    "description": "Mandatory fields are not showing validation errors when left empty.",
    "workflow_type": "submission",
    "severity": "medium",
    "category": "Validation"
},
{
    "id": "SE-004",
    "title": "Autosave not persisting draft data",
    "description": "Draft responses are lost after page refresh despite autosave being enabled.",
    "workflow_type": "submission",
    "severity": "high",
    "category": "Draft management"
},
{
    "id": "SE-005",
    "title": "Incorrect error message on payment failure",
    "description": "Users see a generic technical error instead of a payment declined message.",
    "workflow_type": "payment",
    "severity": "medium",
    "category": "Payment processing"
},
{
    "id": "SE-006",
    "title": "Slow loading on dashboard overview",
    "description": "Dashboard takes more than 15 seconds to load user submission summaries.",
    "workflow_type": "dashboard",
    "severity": "high",
    "category": "Performance"
},
{
    "id": "SE-007",
    "title": "Email notification not triggered after submission",
    "description": "Users do not receive confirmation emails after successfully submitting the form.",
    "workflow_type": "notification",
    "severity": "critical",
    "category": "Email service"
},
{
    "id": "SE-008",
    "title": "Session timeout without warning",
    "description": "Users are logged out abruptly without prior timeout warning during long submissions.",
    "workflow_type": "authentication",
    "severity": "high",
    "category": "Session management"
},
{
    "id": "SE-009",
    "title": "Incorrect status displayed in submission history",
    "description": "Completed submissions are incorrectly marked as pending in the history view.",
    "workflow_type": "submission",
    "severity": "medium",
    "category": "Status tracking"
},
{
    "id": "SE-010",
    "title": "Search filter not applying correctly",
    "description": "Filtering submissions by date range returns inconsistent or incomplete results.",
    "workflow_type": "dashboard",
    "severity": "low",
    "category": "Search & filter"
},
{
    "id": "SE-011",
    "title": "Duplicate submissions created on retry",
    "description": "Retrying submission after network failure creates multiple duplicate entries.",
    "workflow_type": "submission",
    "severity": "critical",
    "category": "Data integrity"
}
    ]

    def __init__(self, num_tickets: int = None, include_test_cases: bool = True):
        self.num_tickets = num_tickets or len(self.TEST_TICKETS)
        self.base_date = datetime.now() - timedelta(days=90)
        self.include_test_cases = include_test_cases

    def generate_tickets(self) -> List[Dict]:
        """Generate test tickets."""
        tickets = []

        for idx, ticket_template in enumerate(self.TEST_TICKETS):
            days_offset = idx * 2
            timestamp = self.base_date + timedelta(
                days=days_offset, hours=random.randint(0, 23)
            )

            ticket = {
                "id": ticket_template["id"],
                "title": ticket_template["title"],
                "description": ticket_template["description"],
                "timestamp": timestamp.isoformat(),
                "workflow_type": ticket_template["workflow_type"],
                "severity": ticket_template["severity"],
                "category": ticket_template["category"],
            }
            tickets.append(ticket)

        return tickets
