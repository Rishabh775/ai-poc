import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.metrics.pairwise import cosine_similarity
from typing import List, Dict, Tuple
from collections import Counter
from datetime import datetime, timedelta

class OperationalAIProcessor:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.embeddings = None
        self.tickets_df = None

    def process_tickets(self, tickets: List[Dict]) -> Dict:
        """Main processing pipeline"""
        self.tickets_df = pd.DataFrame(tickets)
        self.tickets_df['timestamp'] = pd.to_datetime(self.tickets_df['timestamp'])

        combined_text = self.tickets_df.apply(
            lambda x: f"{x['title']} {x['description']}", axis=1
        ).tolist()

        self.embeddings = self.model.encode(combined_text, show_progress_bar=False)

        clusters = self._cluster_issues()
        trends = self._detect_trends()
        metrics = self._calculate_metrics(clusters)

        return {
            "clusters": clusters,
            "trends": trends,
            "metrics": metrics,
            "total_tickets": len(tickets)
        }

    def _cluster_issues(self) -> List[Dict]:
        """Cluster similar issues using DBSCAN"""
        clustering = DBSCAN(eps=0.3, min_samples=2, metric='cosine')
        labels = clustering.fit_predict(self.embeddings)

        self.tickets_df['cluster'] = labels

        clusters = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                continue

            cluster_mask = self.tickets_df['cluster'] == label
            cluster_tickets = self.tickets_df[cluster_mask]

            severity_counts = cluster_tickets['severity'].value_counts().to_dict()
            impact_score = self._calculate_impact_score(
                cluster_tickets,
                severity_counts
            )

            example_tickets = cluster_tickets.head(3)[
                ['id', 'title', 'severity', 'timestamp']
            ].to_dict('records')

            for ticket in example_tickets:
                ticket['timestamp'] = ticket['timestamp'].isoformat()

            summary = self._generate_cluster_summary(cluster_tickets)

            clusters.append({
                "cluster_id": int(label),
                "incident_count": len(cluster_tickets),
                "impact_score": round(impact_score, 2),
                "severity_distribution": severity_counts,
                "workflow_type": cluster_tickets['workflow_type'].mode()[0] if len(cluster_tickets) > 0 else "unknown",
                "example_tickets": example_tickets,
                "summary": summary,
                "first_seen": cluster_tickets['timestamp'].min().isoformat(),
                "last_seen": cluster_tickets['timestamp'].max().isoformat()
            })

        clusters.sort(key=lambda x: x['impact_score'], reverse=True)

        return clusters

    def _calculate_impact_score(self, cluster_tickets: pd.DataFrame, severity_counts: Dict) -> float:
        """Calculate impact score based on frequency, recurrence, and severity"""
        frequency_score = len(cluster_tickets) * 2

        severity_weights = {"critical": 10, "high": 6, "medium": 3, "low": 1}
        severity_score = sum(
            severity_counts.get(sev, 0) * weight
            for sev, weight in severity_weights.items()
        )

        time_span = (
            cluster_tickets['timestamp'].max() - cluster_tickets['timestamp'].min()
        ).days
        recurrence_score = min(time_span / 7, 10) if time_span > 0 else 0

        impact_score = frequency_score + severity_score + recurrence_score

        return impact_score

    def _generate_cluster_summary(self, cluster_tickets: pd.DataFrame) -> str:
        """Generate human-readable summary of cluster"""
        workflow = cluster_tickets['workflow_type'].mode()[0]
        count = len(cluster_tickets)
        severity_mode = cluster_tickets['severity'].mode()[0]

        common_terms = self._extract_common_terms(cluster_tickets)

        time_span = (
            cluster_tickets['timestamp'].max() - cluster_tickets['timestamp'].min()
        ).days

        summary = f"Recurring {severity_mode} severity issue in {workflow} workflow. "
        summary += f"{count} incidents detected over {time_span} days. "
        summary += f"Common patterns: {', '.join(common_terms[:3])}. "

        if time_span < 7:
            summary += "Recent spike detected - requires immediate attention."
        elif count > 10:
            summary += "High frequency pattern - suggests systematic problem."
        else:
            summary += "Intermittent pattern - monitor for escalation."

        return summary

    def _extract_common_terms(self, cluster_tickets: pd.DataFrame) -> List[str]:
        """Extract common terms from ticket titles"""
        all_titles = ' '.join(cluster_tickets['title'].tolist()).lower()

        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}

        words = [w for w in all_titles.split() if w not in stop_words and len(w) > 3]

        common = Counter(words).most_common(5)

        return [word for word, count in common if count > 1]

    def _detect_trends(self) -> Dict:
        """Detect trends over time"""
        self.tickets_df['date'] = self.tickets_df['timestamp'].dt.date

        daily_counts = self.tickets_df.groupby('date').size().reset_index(name='count')
        daily_counts['date'] = daily_counts['date'].astype(str)

        severity_over_time = self.tickets_df.groupby(
            [self.tickets_df['timestamp'].dt.date, 'severity']
        ).size().reset_index(name='count')
        severity_over_time.columns = ['date', 'severity', 'count']
        severity_over_time['date'] = severity_over_time['date'].astype(str)

        workflow_distribution = self.tickets_df['workflow_type'].value_counts().to_dict()

        recent_7d = self.tickets_df[
            self.tickets_df['timestamp'] > (datetime.now() - timedelta(days=7))
        ]
        previous_7d = self.tickets_df[
            (self.tickets_df['timestamp'] > (datetime.now() - timedelta(days=14))) &
            (self.tickets_df['timestamp'] <= (datetime.now() - timedelta(days=7)))
        ]

        trend_direction = "stable"
        if len(previous_7d) > 0:
            change_pct = ((len(recent_7d) - len(previous_7d)) / len(previous_7d)) * 100
            if change_pct > 20:
                trend_direction = "increasing"
            elif change_pct < -20:
                trend_direction = "decreasing"

        return {
            "daily_incidents": daily_counts.to_dict('records'),
            "severity_over_time": severity_over_time.to_dict('records'),
            "workflow_distribution": workflow_distribution,
            "trend_direction": trend_direction,
            "recent_7d_count": len(recent_7d),
            "previous_7d_count": len(previous_7d)
        }

    def _calculate_metrics(self, clusters: List[Dict]) -> Dict:
        """Calculate high-level metrics"""
        total_incidents = len(self.tickets_df)

        critical_count = len(self.tickets_df[self.tickets_df['severity'] == 'critical'])
        high_count = len(self.tickets_df[self.tickets_df['severity'] == 'high'])

        risk_score = min(((critical_count * 10 + high_count * 5) / total_incidents) * 10, 100)

        recent_7d = self.tickets_df[
            self.tickets_df['timestamp'] > (datetime.now() - timedelta(days=7))
        ]
        previous_7d = self.tickets_df[
            (self.tickets_df['timestamp'] > (datetime.now() - timedelta(days=14))) &
            (self.tickets_df['timestamp'] <= (datetime.now() - timedelta(days=7)))
        ]

        if len(previous_7d) > 0:
            stability_index = max(0, 100 - ((len(recent_7d) / len(previous_7d)) * 100))
        else:
            stability_index = 50

        top_cluster = clusters[0] if clusters else None
        top_recurring_issue = top_cluster['summary'] if top_cluster else "No recurring patterns detected"

        return {
            "total_incidents": total_incidents,
            "risk_score": round(risk_score, 1),
            "stability_index": round(stability_index, 1),
            "top_recurring_issue": top_recurring_issue,
            "critical_incidents": critical_count,
            "high_priority_incidents": high_count,
            "cluster_count": len(clusters)
        }
