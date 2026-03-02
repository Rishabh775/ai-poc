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
        # Category A: Reviewer Status / Workflow State Mismatch
        {
            "id": "OPS-A001",
            "title": "Review completion state not updating",
            "description": "The manuscript NIMG-D-25-01472 still appears under 'Partially Saved' despite the reviewer confirming final submission. Please update the status to completed. Editor escalated this.",
            "workflow_type": "review",
            "severity": "high",
            "category": "Reviewer Status",
        },
        {
            "id": "OPS-A002",
            "title": "Reviewer stuck in incomplete state",
            "description": "Reviewer Dr. S. Banerjee submitted feedback yesterday, but system still reflects 'Draft Saved'. Backend may not be syncing review state.",
            "workflow_type": "review",
            "severity": "high",
            "category": "Reviewer Status",
        },
        {
            "id": "OPS-A003",
            "title": "Incorrect reviewer status in backend",
            "description": "Request to change review flag from 'Partial Review Saved' to 'Completed Review' for submission ID JCP-D-26-00117. Editorial office needs this corrected before decision letter.",
            "workflow_type": "review",
            "severity": "critical",
            "category": "Reviewer Status",
        },
        {
            "id": "OPS-A004",
            "title": "Status mismatch",
            "description": "Editor says review done but UI shows partial. ID: PRJ-D-25-9981",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Reviewer Status",
        },
        {
            "id": "OPS-A005",
            "title": "Review marked done but not reflecting",
            "description": "Issue created from Slack. Reviewer: Liang Wu. Email: liangwu@gmail.com. Review marked done but dashboard not reflecting change.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Reviewer Status",
        },
        # Category B: Dashboard Performance / Slowness
        {
            "id": "OPS-B001",
            "title": "Analytics dashboard timing out",
            "description": "Operational metrics page takes >40 seconds to load when filtering by workflow type. Happens intermittently during peak hours.",
            "workflow_type": "dashboard",
            "severity": "high",
            "category": "Dashboard Performance",
        },
        {
            "id": "OPS-B002",
            "title": "Performance degradation on metrics screen",
            "description": "Query response time increased significantly after last deployment. Cluster distribution graph not rendering until refresh.",
            "workflow_type": "dashboard",
            "severity": "high",
            "category": "Dashboard Performance",
        },
        {
            "id": "OPS-B003",
            "title": "Dashboard slow",
            "description": "Very slow when opening cluster insights.",
            "workflow_type": "dashboard",
            "severity": "medium",
            "category": "Dashboard Performance",
        },
        {
            "id": "OPS-B004",
            "title": "UI lag and graph rendering issue",
            "description": "Users report freezing when switching tabs between 'Trend Analysis' and 'Severity Breakdown'. Also occasionally throws timeout error.",
            "workflow_type": "dashboard",
            "severity": "medium",
            "category": "Dashboard Performance",
        },
        # Category C: Timeout / System Errors
        {
            "id": "OPS-C001",
            "title": "Backend 504 error during submission",
            "description": "Authors encountering gateway timeout while submitting revised manuscripts. Possibly related to file upload validation.",
            "workflow_type": "infra",
            "severity": "critical",
            "category": "Timeout",
        },
        {
            "id": "OPS-C002",
            "title": "Submission request failing intermittently",
            "description": "HTTP 504 observed for some manuscripts during final confirmation step. Logs show long-running DB transaction.",
            "workflow_type": "infra",
            "severity": "high",
            "category": "Timeout",
        },
        {
            "id": "OPS-C003",
            "title": "Review submission fails after 30s",
            "description": "Reviewer clicks submit, spinner runs, then system shows 'Request timed out'.",
            "workflow_type": "infra",
            "severity": "high",
            "category": "Timeout",
        },
        {
            "id": "OPS-C004",
            "title": "Timeout on save",
            "description": "Saving review results in timeout.",
            "workflow_type": "infra",
            "severity": "medium",
            "category": "Timeout",
        },
        # Category D: Release Regression
        {
            "id": "OPS-D001",
            "title": "Feature working before deployment, now broken",
            "description": "After release v3.4.2, reviewer assignment automation no longer triggers. Previously auto-assigned based on specialty.",
            "workflow_type": "release",
            "severity": "critical",
            "category": "Release Regression",
        },
        {
            "id": "OPS-D002",
            "title": "Post-deploy regression in assignment workflow",
            "description": "Automatic reviewer mapping logic not executing since last patch. Manual assignment required.",
            "workflow_type": "release",
            "severity": "high",
            "category": "Release Regression",
        },
        {
            "id": "OPS-D003",
            "title": "Regression: email notification not firing",
            "description": "Notification service stopped sending confirmation emails after latest production update.",
            "workflow_type": "release",
            "severity": "high",
            "category": "Release Regression",
        },
        # Category E: Duplicate Classification Edge Case
        {
            "id": "OPS-E001",
            "title": "Editorial request to finalize review state",
            "description": "Please finalize reviewer progress flag to indicate completion for manuscript AJO-D-25-00219.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Completion",
        },
        {
            "id": "OPS-E002",
            "title": "Backend adjustment required",
            "description": "Manuscript review phase incorrectly marked as in-progress though review submitted 2 days ago.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Completion",
        },
        {
            "id": "OPS-E003",
            "title": "Review phase inconsistency",
            "description": "Mismatch between reviewer submission timestamp and displayed workflow state.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Review Completion",
        },
        # Category F: Noise / Non-Issue
        {
            "id": "OPS-F001",
            "title": "Add new journal template",
            "description": "Request to configure new manuscript template for Pediatric Cardiology.",
            "workflow_type": "submission",
            "severity": "low",
            "category": "Configuration",
        },
        {
            "id": "OPS-F002",
            "title": "Change editor phone number",
            "description": "Please update contact information for Dr. Elena Ruiz in the admin panel.",
            "workflow_type": "dashboard",
            "severity": "low",
            "category": "Configuration",
        },
        {
            "id": "OPS-F003",
            "title": "Question about login",
            "description": "User forgot password and cannot reset.",
            "workflow_type": "infra",
            "severity": "low",
            "category": "Support",
        },
        # Category G: Extremely Hard Case (Mixed Intent)
        {
            "id": "OPS-G001",
            "title": "Review marked complete but submission timed out",
            "description": "Reviewer claims completion but encountered timeout during final step. Status unclear if saved or not.",
            "workflow_type": "review",
            "severity": "high",
            "category": "Mixed",
        },
        # Category H: Minimal Context
        {
            "id": "OPS-H001",
            "title": "Please fix ASAP",
            "description": "Workflow broken.",
            "workflow_type": "review",
            "severity": "high",
            "category": "Unknown",
        },
        {
            "id": "OPS-H002",
            "title": "Not working",
            "description": "Review stuck.",
            "workflow_type": "review",
            "severity": "medium",
            "category": "Unknown",
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
