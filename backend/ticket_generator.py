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
