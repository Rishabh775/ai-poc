"""AI pipeline for Operational Intelligence Dashboard.
Embeds tickets, clusters similar issues, detects trends, and generates actionable insights.
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from typing import List, Dict, Any
from collections import Counter
from datetime import datetime, timedelta

# Ownership mapping: workflow_type -> team
WORKFLOW_TO_TEAM = {
    "submission": "Backend Team",
    "review": "Platform Team",
    "dashboard": "Frontend Team",
    "release": "Release Engineering",
    "infra": "DevOps",
}

# Action templates by workflow and severity
ACTION_TEMPLATES = {
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

class OperationalAIProcessor:
    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings = None
        self.tickets_df = None

    def process_tickets(self, tickets: List[Dict]) -> Dict:
        """Main processing pipeline: embed, cluster, enrich, and compute change tracking."""
        self.tickets_df = pd.DataFrame(tickets)
        self.tickets_df["timestamp"] = pd.to_datetime(self.tickets_df["timestamp"])

        combined_text = self.tickets_df.apply(
            lambda x: f"{x['title']} {x['description']}", axis=1
        ).tolist()
        self.embeddings = self.model.encode(combined_text, show_progress_bar=False)

        clusters = self._cluster_issues()
        clusters = self._add_actionable_insights(clusters)
        trends = self._detect_trends()
        change_tracking = self._compute_change_tracking()
        metrics = self._calculate_metrics(clusters, change_tracking)

        return {
            "clusters": clusters,
            "trends": trends,
            "change_tracking": change_tracking,
            "metrics": metrics,
            "total_tickets": len(tickets),
        }

    def _cluster_issues(self) -> List[Dict]:
        """Cluster similar issues using DBSCAN."""
        clustering = DBSCAN(eps=0.35, min_samples=2, metric="cosine")
        labels = clustering.fit_predict(self.embeddings)
        self.tickets_df["cluster"] = labels

        clusters = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                continue

            cluster_mask = self.tickets_df["cluster"] == label
            cluster_tickets = self.tickets_df[cluster_mask]

            severity_counts = cluster_tickets["severity"].value_counts().to_dict()
            impact_score = self._calculate_impact_score(cluster_tickets, severity_counts)

            example_tickets = (
                cluster_tickets.head(5)[["id", "title", "severity", "timestamp"]]
                .to_dict("records")
            )
            for t in example_tickets:
                t["timestamp"] = t["timestamp"].isoformat()

            summary = self._generate_cluster_summary(cluster_tickets)
            workflow = (
                cluster_tickets["workflow_type"].mode()[0]
                if len(cluster_tickets) > 0
                else "unknown"
            )

            clusters.append({
                "cluster_id": int(label),
                "incident_count": len(cluster_tickets),
                "impact_score": round(impact_score, 2),
                "severity_distribution": severity_counts,
                "workflow_type": workflow,
                "example_tickets": example_tickets,
                "summary": summary,
                "first_seen": cluster_tickets["timestamp"].min().isoformat(),
                "last_seen": cluster_tickets["timestamp"].max().isoformat(),
            })

        clusters.sort(key=lambda x: x["impact_score"], reverse=True)
        return clusters

    def _add_actionable_insights(self, clusters: List[Dict]) -> List[Dict]:
        """Extend clusters with recommended_action, priority_level, owner_team, etc."""
        for c in clusters:
            workflow = c["workflow_type"]
            impact = c["impact_score"]
            severity_counts = c.get("severity_distribution", {})
            incident_count = c["incident_count"]

            owner_team = WORKFLOW_TO_TEAM.get(workflow, "Platform Team")
            c["owner_team"] = owner_team

            actions = ACTION_TEMPLATES.get(workflow, ["Investigate root cause and implement fix"])
            c["recommended_action"] = actions[0] if actions else "Investigate and remediate"

            risk_score = min(
                (incident_count * 2 + (severity_counts.get("critical", 0) * 10) + (severity_counts.get("high", 0) * 5)),
                100,
            )
            c["risk_score"] = round(risk_score, 1)

            time_span = (
                pd.Timestamp(c["last_seen"]) - pd.Timestamp(c["first_seen"])
            ).days
            recurrence_signal = "recurring" if time_span >= 7 and incident_count >= 3 else "spike" if incident_count >= 5 else "intermittent"
            c["recurrence_signal"] = recurrence_signal

            if impact >= 50 or severity_counts.get("critical", 0) >= 2:
                priority_level = "P1"
                urgency_tag = "immediate"
                business_impact = "Critical: Blocks core workflows and affects multiple users."
            elif impact >= 30 or severity_counts.get("high", 0) >= 3:
                priority_level = "P2"
                urgency_tag = "high"
                business_impact = "High: Significant user impact; requires prompt resolution."
            elif impact >= 15 or incident_count >= 5:
                priority_level = "P3"
                urgency_tag = "elevated"
                business_impact = "Moderate: Recurring pattern; address within sprint."
            else:
                priority_level = "P4"
                urgency_tag = "monitor"
                business_impact = "Low: Monitor; escalate if frequency increases."

            c["priority_level"] = priority_level
            c["urgency_tag"] = urgency_tag
            c["business_impact"] = business_impact

        return clusters

    def _calculate_impact_score(self, cluster_tickets: pd.DataFrame, severity_counts: Dict) -> float:
        """Impact = frequency + severity + recurrence."""
        frequency_score = len(cluster_tickets) * 2
        severity_weights = {"critical": 10, "high": 6, "medium": 3, "low": 1}
        severity_score = sum(
            severity_counts.get(sev, 0) * weight
            for sev, weight in severity_weights.items()
        )
        time_span = (
            cluster_tickets["timestamp"].max() - cluster_tickets["timestamp"].min()
        ).days
        recurrence_score = min(time_span / 7, 10) if time_span > 0 else 0
        return frequency_score + severity_score + recurrence_score

    def _generate_cluster_summary(self, cluster_tickets: pd.DataFrame) -> str:
        """Human-readable summary of cluster."""
        workflow = cluster_tickets["workflow_type"].mode()[0]
        count = len(cluster_tickets)
        severity_mode = cluster_tickets["severity"].mode()[0]
        common_terms = self._extract_common_terms(cluster_tickets)
        time_span = (
            cluster_tickets["timestamp"].max() - cluster_tickets["timestamp"].min()
        ).days

        summary = f"Recurring {severity_mode} severity issue in {workflow} workflow. "
        summary += f"{count} incidents over {time_span} days. "
        if common_terms:
            summary += f"Common patterns: {', '.join(common_terms[:3])}. "
        if time_span < 7:
            summary += "Recent spike - requires immediate attention."
        elif count > 10:
            summary += "High frequency - suggests systematic problem."
        else:
            summary += "Intermittent pattern - monitor for escalation."
        return summary

    def _extract_common_terms(self, cluster_tickets: pd.DataFrame) -> List[str]:
        stop = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        all_titles = " ".join(cluster_tickets["title"].tolist()).lower()
        words = [w for w in all_titles.split() if w not in stop and len(w) > 3]
        common = Counter(words).most_common(5)
        return [w for w, cnt in common if cnt > 1]

    def _detect_trends(self) -> Dict:
        """Daily incidents, severity over time, workflow distribution."""
        self.tickets_df["date"] = self.tickets_df["timestamp"].dt.date
        daily = self.tickets_df.groupby("date").size().reset_index(name="count")
        daily["date"] = daily["date"].astype(str)

        severity_over_time = (
            self.tickets_df.groupby(
                [self.tickets_df["timestamp"].dt.date, "severity"]
            )
            .size()
            .reset_index(name="count")
        )
        severity_over_time.columns = ["date", "severity", "count"]
        severity_over_time["date"] = severity_over_time["date"].astype(str)

        workflow_dist = self.tickets_df["workflow_type"].value_counts().to_dict()

        recent_7d = self.tickets_df[
            self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=7))
        ]
        previous_7d = self.tickets_df[
            (self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=14)))
            & (self.tickets_df["timestamp"] <= (datetime.now() - timedelta(days=7)))
        ]

        trend_direction = "stable"
        if len(previous_7d) > 0:
            change_pct = ((len(recent_7d) - len(previous_7d)) / len(previous_7d)) * 100
            if change_pct > 20:
                trend_direction = "increasing"
            elif change_pct < -20:
                trend_direction = "decreasing"

        return {
            "daily_incidents": daily.to_dict("records"),
            "severity_over_time": severity_over_time.to_dict("records"),
            "workflow_distribution": workflow_dist,
            "trend_direction": trend_direction,
            "recent_7d_count": len(recent_7d),
            "previous_7d_count": len(previous_7d),
        }

    def _compute_change_tracking(self) -> Dict:
        """Compare last 7 days vs previous 7 days."""
        recent_7d = self.tickets_df[
            self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=7))
        ]
        previous_7d = self.tickets_df[
            (self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=14)))
            & (self.tickets_df["timestamp"] <= (datetime.now() - timedelta(days=7)))
        ]

        if len(previous_7d) > 0:
            delta_percent = round(
                ((len(recent_7d) - len(previous_7d)) / len(previous_7d)) * 100, 1
            )
        else:
            delta_percent = 100.0 if len(recent_7d) > 0 else 0.0

        trend_direction = "stable"
        if len(previous_7d) > 0:
            change = (len(recent_7d) - len(previous_7d)) / len(previous_7d)
            if change > 0.2:
                trend_direction = "increasing"
            elif change < -0.2:
                trend_direction = "decreasing"

        total = len(self.tickets_df)
        risk = (
            (len(self.tickets_df[self.tickets_df["severity"] == "critical"]) * 10)
            + (len(self.tickets_df[self.tickets_df["severity"] == "high"]) * 5)
        )
        risk_score = min((risk / total) * 10, 100) if total > 0 else 0

        if len(previous_7d) > 0:
            ratio = len(recent_7d) / len(previous_7d)
            stability_index = max(0, min(100, 100 - (ratio * 50)))
        else:
            stability_index = 50.0

        return {
            "trend_direction": trend_direction,
            "delta_percent": delta_percent,
            "new_clusters": 0,  # Simulated - would require historical comparison
            "resolved_clusters": 0,
            "stability_index": round(stability_index, 1),
        }

    def _calculate_metrics(self, clusters: List[Dict], change_tracking: Dict) -> Dict:
        """High-level metrics for dashboard."""
        total = len(self.tickets_df)
        critical_count = len(self.tickets_df[self.tickets_df["severity"] == "critical"])
        high_count = len(self.tickets_df[self.tickets_df["severity"] == "high"])

        risk_score = min(
            ((critical_count * 10 + high_count * 5) / total) * 10, 100
        ) if total > 0 else 0

        top_cluster = clusters[0] if clusters else None
        top_issue = top_cluster["summary"][:120] + "..." if (top_cluster and len(top_cluster["summary"]) > 120) else (top_cluster["summary"] if top_cluster else "No recurring patterns detected")

        return {
            "total_incidents": total,
            "top_issue": top_issue,
            "risk_score": round(risk_score, 1),
            "stability_index": change_tracking.get("stability_index", 50),
            "trend_direction": change_tracking.get("trend_direction", "stable"),
            "top_recurring_issue": top_issue,
            "critical_incidents": critical_count,
            "high_priority_incidents": high_count,
            "cluster_count": len(clusters),
        }

