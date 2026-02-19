"""Demo ticket generator for Operational Intelligence Dashboard.
Generates 80-120 Jira-style tickets with recurring operational patterns.
"""

import random
from datetime import datetime, timedelta
from typing import List, Dict

# Ownership mapping: workflow_type -> team
WORKFLOW_TO_TEAM = {
    "submission": "Backend Team",
    "review": "Platform Team",
    "dashboard": "Frontend Team",
    "release": "Release Engineering",
    "infra": "DevOps",
}


class TicketGenerator:
    """Generates realistic Jira-style tickets simulating operational noise."""

    ISSUE_PATTERNS = {
        "reviewer_assignment": {
            "titles": [
                "Reviewer auto-assignment failing for new submissions",
                "Cannot assign reviewer to manuscript ID {id}",
                "Reviewer assignment timeout after {time} seconds",
                "Assignment algorithm not distributing load evenly",
                "Reviewer preferences ignored during assignment",
                "Review queue stuck - no reviewers being assigned",
                "Assigned reviewer never receives notification",
            ],
            "descriptions": [
                "The automatic reviewer assignment system is failing intermittently. Manuscripts are stuck in 'pending assignment' state.",
                "Users report that reviewer assignments are not being created. Database shows NULL values in reviewer_id field.",
                "Assignment process times out after waiting for consensus algorithm. Happens more during peak hours (9-11 AM EST).",
                "Load balancer appears to ignore reviewer capacity settings. Some reviewers receiving 10+ assignments while others have zero.",
                "System assigns reviewers who have explicitly declined similar topics. Preference matching logic may be broken.",
            ],
            "workflow_type": "review",
            "severities": ["high", "critical", "medium"],
        },
        "submission_workflow": {
            "titles": [
                "Submission workflow stuck at validation step",
                "File upload fails with 500 error",
                "Metadata validation rejecting valid DOI formats",
                "Workflow state machine entering invalid state",
                "Submission cannot progress past ethics approval",
                "Upload progress bar freezes at 90%",
                "Duplicate submission created when user retries",
            ],
            "descriptions": [
                "Submissions are getting stuck at the validation checkpoint. Workflow engine logs show 'state transition failed' errors.",
                "Users uploading supplementary files receive HTTP 500. Server logs indicate S3 connection timeout after 30s.",
                "DOI validation regex is rejecting valid Crossref DOIs with new format (10.XXXXX/prefix.suffix.v2). Needs pattern update.",
                "State machine occasionally enters invalid state where status='approved' but progress_stage='pending_review'.",
                "Ethics approval checkbox is checked and saved, but workflow refuses to advance. Database trigger may be misconfigured.",
            ],
            "workflow_type": "submission",
            "severities": ["critical", "high", "medium"],
        },
        "dashboard_performance": {
            "titles": [
                "Dashboard load time exceeds {time} seconds",
                "Analytics queries causing database CPU spike",
                "Real-time metrics widget timing out",
                "Chart rendering freezes browser on large datasets",
                "Export to CSV fails with memory error",
                "Dashboard shows stale data after overnight batch run",
                "Metrics cards fail to load on first page visit",
            ],
            "descriptions": [
                "Main dashboard takes 15-20 seconds to load for users with >100 submissions. Database query plans show full table scans.",
                "Analytics endpoint spikes DB CPU to 90%. Query is missing index on created_at + status columns.",
                "Real-time metrics websocket disconnects after 60s when processing large event streams.",
                "Rendering 500+ data points in line charts causes browser tab to freeze. Need virtualization.",
                "CSV export for annual report fails with 'Out of Memory' error. Dataset is 50MB+.",
            ],
            "workflow_type": "dashboard",
            "severities": ["medium", "high", "low"],
        },
        "timeout_errors": {
            "titles": [
                "API gateway timeout on bulk processing endpoint",
                "Background job processing exceeding time limit",
                "Database connection pool exhausted",
                "Third-party API call timing out",
                "Session timeout occurring prematurely",
                "Health check endpoint returning 504 under load",
                "Webhook delivery timing out to external systems",
            ],
            "descriptions": [
                "API gateway returns 504 when calling POST /api/process-bulk. Job takes 90s but timeout is set to 60s.",
                "Background jobs for PDF generation are killed after exceeding 5-minute limit. Complex documents need longer.",
                "Connection pool (max 20) gets exhausted during peak traffic. Connections stuck in 'idle in transaction'.",
                "Integration with ORCID API times out intermittently. Cascading failures when downstream services slow.",
                "Users report being logged out after 15 minutes of activity. Session renewal logic not firing correctly.",
            ],
            "workflow_type": "infra",
            "severities": ["high", "critical", "medium"],
        },
        "release_regression": {
            "titles": [
                "v{version} broke search functionality",
                "Email notifications stopped after deployment",
                "Migration rolled back due to constraint violation",
                "New UI causing layout issues on Safari",
                "API response format changed, breaking mobile app",
                "Feature flag not toggling correctly in production",
                "Deployment left orphaned background jobs",
            ],
            "descriptions": [
                "After v2.4.0 release, search returns empty results for queries with special characters. Elasticsearch mapping change suspected.",
                "Email service stopped sending after yesterday's deployment. Config shows SMTP credentials overwritten by default values.",
                "Database migration failed in production due to existing NULL values. Had to rollback.",
                "New dashboard UI has CSS layout issues on Safari 16. Flexbox behaving differently than Chrome.",
                "Changed API from camelCase to snake_case in v3.0.0. Mobile app (v2.x schema) now crashes on launch.",
            ],
            "workflow_type": "release",
            "severities": ["critical", "high", "medium"],
        },
        "infra_instability": {
            "titles": [
                "Kubernetes pod evictions during node pressure",
                "Redis cache cluster failover taking 5+ minutes",
                "Message queue backlog growing unbounded",
                "CDN cache invalidation delays affecting users",
                "Certificate renewal failed - manual intervention needed",
                "Disk space critical on analytics node",
            ],
            "descriptions": [
                "Pods being evicted due to memory pressure. OOMKilled events in logs. Node autoscaling not responsive.",
                "Redis sentinel failover takes 5+ minutes during primary failure. Client connection pool exhausts.",
                "RabbitMQ queue depth growing 1000+ messages/hour. Consumer scaling not keeping up.",
                "CDN purge requests taking 30+ minutes to propagate. Users seeing stale assets globally.",
                "Let's Encrypt certificate renewal failed. TLS handshake errors in production.",
            ],
            "workflow_type": "infra",
            "severities": ["critical", "high", "medium"],
        },
        "backlog_spike": {
            "titles": [
                "Review queue backlog increased 3x overnight",
                "Support ticket volume spike after announcement",
                "Pending approvals exceeding SLA threshold",
                "Escalation queue backing up - triage needed",
                "Unprocessed events accumulating in pipeline",
            ],
            "descriptions": [
                "Review queue went from 50 to 150 items overnight. No new submissions - appears to be processing stall.",
                "Support ticket volume 3x normal after product announcement. Auto-routing overwhelmed.",
                "Approvals pending > 72 hours. 23 items waiting for stakeholder sign-off.",
                "Escalation queue has 45 items. Normal load is 5-10. Triage team understaffed.",
            ],
            "workflow_type": "review",
            "severities": ["high", "medium", "low"],
        },
    }

    def __init__(self, num_tickets: int = None):
        """Initialize with 80-120 tickets (random within range if not specified)."""
        self.num_tickets = num_tickets or random.randint(80, 120)
        self.base_date = datetime.now() - timedelta(days=90)

    def _safe_format(self, template: str, **kwargs) -> str:
        """Format template with only the placeholders that exist."""
        try:
            return template.format(**kwargs)
        except KeyError:
            for key, val in kwargs.items():
                template = template.replace("{" + key + "}", str(val))
            return template

    def _generate_timestamps(self) -> List[datetime]:
        """Generate timestamps with clustering around deployment dates."""
        timestamps = []
        deployment_dates = [
            self.base_date + timedelta(days=15),
            self.base_date + timedelta(days=45),
            self.base_date + timedelta(days=75),
        ]

        for _ in range(self.num_tickets):
            if random.random() < 0.4:
                deployment = random.choice(deployment_dates)
                offset_hours = random.randint(0, 72)
                ts = deployment + timedelta(hours=offset_hours)
            else:
                random_days = random.randint(0, 90)
                random_hours = random.randint(0, 23)
                ts = self.base_date + timedelta(days=random_days, hours=random_hours)
            timestamps.append(ts)

        return sorted(timestamps)

    def generate_tickets(self) -> List[Dict]:
        """Generate 80-120 realistic demo tickets with recurring patterns."""
        tickets = []
        timestamps = self._generate_timestamps()

        pattern_distribution = [
            ("reviewer_assignment", 18),
            ("submission_workflow", 16),
            ("dashboard_performance", 14),
            ("timeout_errors", 15),
            ("release_regression", 12),
            ("infra_instability", 14),
            ("backlog_spike", 11),
        ]

        pattern_pool = []
        for pattern_type, count in pattern_distribution:
            pattern_pool.extend([pattern_type] * count)
        random.shuffle(pattern_pool)

        placeholders = {
            "id": random.randint(1000, 9999),
            "time": random.choice([30, 60, 90, 120]),
            "endpoint": random.choice(["/api/submissions", "/api/reviews", "/api/analytics"]),
            "version": f"2.{random.randint(1, 9)}.{random.randint(0, 5)}",
        }

        for idx, pattern_type in enumerate(pattern_pool[: self.num_tickets]):
            pattern = self.ISSUE_PATTERNS[pattern_type]
            title_template = random.choice(pattern["titles"])
            title = self._safe_format(title_template, **placeholders)
            description = random.choice(pattern["descriptions"])
            severity = random.choice(pattern["severities"])

            ticket = {
                "id": f"OPS-{1000 + idx}",
                "title": title,
                "description": description,
                "timestamp": timestamps[idx].isoformat(),
                "workflow_type": pattern["workflow_type"],
                "severity": severity,
            }
            tickets.append(ticket)
            placeholders["id"] = random.randint(1000, 9999)

        return tickets
