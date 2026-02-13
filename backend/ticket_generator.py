import random
from datetime import datetime, timedelta
from typing import List, Dict

class TicketGenerator:
    ISSUE_PATTERNS = {
        "reviewer_assignment": {
            "titles": [
                "Reviewer auto-assignment failing for new submissions",
                "Cannot assign reviewer to manuscript ID {id}",
                "Reviewer assignment timeout after {time} seconds",
                "Assignment algorithm not distributing load evenly",
                "Reviewer preferences ignored during assignment"
            ],
            "descriptions": [
                "The automatic reviewer assignment system is failing intermittently. Manuscripts are stuck in 'pending assignment' state. Error logs show timeout exceptions.",
                "Users report that reviewer assignments are not being created. Database shows NULL values in reviewer_id field despite successful API calls.",
                "Assignment process times out after waiting for consensus algorithm. This happens more frequently during peak hours (9-11 AM EST).",
                "Load balancer appears to ignore reviewer capacity settings. Some reviewers receiving 10+ assignments while others have zero.",
                "System assigns reviewers who have explicitly declined similar topics. Preference matching logic may be broken."
            ],
            "workflow": "reviewer_assignment",
            "severities": ["high", "critical", "medium"]
        },
        "submission_workflow": {
            "titles": [
                "Submission workflow stuck at validation step",
                "File upload fails with 500 error",
                "Metadata validation rejecting valid DOI formats",
                "Workflow state machine entering invalid state",
                "Submission cannot progress past ethics approval"
            ],
            "descriptions": [
                "Submissions are getting stuck at the validation checkpoint. The workflow engine logs show 'state transition failed' errors repeatedly.",
                "Users uploading supplementary files receive HTTP 500. Server logs indicate S3 connection timeout after 30s.",
                "DOI validation regex is rejecting valid Crossref DOIs with new format (10.XXXXX/prefix.suffix.v2). Needs pattern update.",
                "State machine occasionally enters an invalid state where status='approved' but progress_stage='pending_review'. This causes UI confusion.",
                "Ethics approval checkbox is checked and saved, but workflow refuses to advance. Database trigger may be misconfigured."
            ],
            "workflow": "submission",
            "severities": ["critical", "high", "medium"]
        },
        "dashboard_performance": {
            "titles": [
                "Dashboard load time exceeds {time} seconds",
                "Analytics queries causing database CPU spike",
                "Real-time metrics widget timing out",
                "Chart rendering freezes browser on large datasets",
                "Export to CSV fails with memory error"
            ],
            "descriptions": [
                "Main dashboard takes 15-20 seconds to load for users with >100 submissions. Database query plans show full table scans.",
                "Analytics endpoint (GET /api/analytics/summary) spikes DB CPU to 90%. Query is missing index on created_at + status columns.",
                "Real-time metrics websocket disconnects after 60s when processing large event streams. Backend memory usage grows unbounded.",
                "Rendering 500+ data points in line charts causes browser tab to freeze. Need virtualization or data aggregation.",
                "CSV export for annual report fails with 'Out of Memory' error. Dataset is 50MB+ and being loaded entirely into RAM."
            ],
            "workflow": "dashboard",
            "severities": ["medium", "high", "low"]
        },
        "timeout_errors": {
            "titles": [
                "API gateway timeout on {endpoint} endpoint",
                "Background job processing exceeding time limit",
                "Database connection pool exhausted",
                "Third-party API call timing out",
                "Session timeout occurring prematurely"
            ],
            "descriptions": [
                "API gateway returns 504 when calling POST /api/process-bulk. Job takes 90s but timeout is set to 60s.",
                "Background jobs for PDF generation are killed after exceeding 5-minute limit. Complex documents need longer processing time.",
                "Connection pool (max 20) gets exhausted during peak traffic. All connections stuck in 'idle in transaction' state.",
                "Integration with ORCID API times out intermittently. Their service has 99.5% SLA but causes cascading failures here.",
                "Users report being logged out after 15 minutes of activity. Session renewal logic is not firing correctly on user interaction."
            ],
            "workflow": "infrastructure",
            "severities": ["high", "critical", "medium"]
        },
        "release_regression": {
            "titles": [
                "v{version} broke search functionality",
                "Email notifications stopped after deployment",
                "Migration {id} rolled back due to constraint violation",
                "New UI causing layout issues on Safari",
                "API response format changed, breaking mobile app"
            ],
            "descriptions": [
                "After v2.4.0 release, search returns empty results for queries with special characters. Elasticsearch mapping change is suspected.",
                "Email service stopped sending after yesterday's deployment. Config shows SMTP credentials were overwritten by default values.",
                "Database migration 2024_01_15_add_constraints failed in production due to existing NULL values. Had to rollback.",
                "New dashboard UI has CSS layout issues on Safari 16. Flexbox behaving differently than Chrome. Not caught in testing.",
                "Changed API from camelCase to snake_case in v3.0.0. Mobile app (still on v2.x schema) now crashes on launch."
            ],
            "workflow": "release",
            "severities": ["critical", "high", "medium"]
        }
    }

    def __init__(self, num_tickets: int = 100):
        self.num_tickets = num_tickets
        self.base_date = datetime.now() - timedelta(days=90)

    def _generate_time_clustering(self) -> List[datetime]:
        """Generate timestamps with realistic clustering around deployment dates"""
        timestamps = []

        deployment_dates = [
            self.base_date + timedelta(days=15),
            self.base_date + timedelta(days=45),
            self.base_date + timedelta(days=75)
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
        """Generate realistic demo tickets with recurring patterns"""
        tickets = []
        timestamps = self._generate_time_clustering()

        pattern_distribution = [
            ("reviewer_assignment", 25),
            ("submission_workflow", 20),
            ("dashboard_performance", 18),
            ("timeout_errors", 22),
            ("release_regression", 15)
        ]

        pattern_pool = []
        for pattern_type, count in pattern_distribution:
            pattern_pool.extend([pattern_type] * count)

        random.shuffle(pattern_pool)

        for idx, pattern_type in enumerate(pattern_pool):
            if idx >= self.num_tickets:
                break

            pattern = self.ISSUE_PATTERNS[pattern_type]

            title_template = random.choice(pattern["titles"])
            title = title_template.format(
                id=random.randint(1000, 9999),
                time=random.choice([30, 60, 90, 120]),
                endpoint=random.choice(["/api/submissions", "/api/reviews", "/api/analytics"]),
                version=f"2.{random.randint(1, 9)}.{random.randint(0, 5)}",
            )

            description = random.choice(pattern["descriptions"])
            severity = random.choice(pattern["severities"])

            ticket = {
                "id": f"OPS-{1000 + idx}",
                "title": title,
                "description": description,
                "timestamp": timestamps[idx].isoformat(),
                "workflow_type": pattern["workflow"],
                "severity": severity
            }

            tickets.append(ticket)

        return tickets
