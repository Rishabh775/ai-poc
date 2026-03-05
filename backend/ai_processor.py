"""AI pipeline for Operational Intelligence Dashboard.
Embeds tickets, clusters similar issues, detects trends, and generates actionable insights.

Features:
- Semantic duplicate detection with configurable threshold
- Hybrid clustering (semantic embeddings + metadata)
- Dynamic cluster assignment for new tickets
- Cluster confidence scoring
- Improved text normalization for better embedding quality
- Domain stopword stripping to prevent false cross-cluster merges
"""

import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from datetime import datetime, timedelta

import config


class OperationalAIProcessor:
    """AI-powered ticket clustering and analysis processor."""

    # Words that appear across ALL tickets in this system and add no cluster signal.
    # Kept minimal and surgical — only strip truly universal noise.
    # DO NOT add discriminative words like: upload, session, email, autosave,
    # comment, recommendation, permission, status, performance, validation, access.
    # Those are the actual cluster signals and must be preserved.
    DOMAIN_NOISE_WORDS = [
        # Platform/entity noise — appear in every ticket
        "manuscript", "submission", "submissions",
        "reviewer", "reviewers", "editor", "editors",
        "portal", "system", "users", "user",
        "authors", "author", "jmed",
        # UI interaction noise — appear in every ticket
        "clicking", "click", "button", "page",
        "field", "fields", "form", "forms",
        # Cross-cluster bridge words — cause false merges
        "decision", "notification",
    ]

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.embeddings: Optional[np.ndarray] = None
        self.tickets_df: Optional[pd.DataFrame] = None
        self.cluster_centroids: Dict[int, np.ndarray] = {}
        self.cluster_info: Dict[int, Dict] = {}

    def normalize_ticket_text(self, title: str, description: str, severity: str) -> str:
        """Create enriched combined text with normalization.

        Normalization steps:
        - lowercase
        - strip domain noise words (universal across all tickets, cause false merges)
        - remove emails
        - remove IDs (manuscript IDs, ticket IDs)
        - strip extra whitespace

        Note: Severity is intentionally excluded from the embedding text.
        It is already captured in metadata and including it as a prefix
        skews embeddings toward severity rather than semantic topic.
        """
        combined = f"{title}. {description}"
        combined = combined.lower()

        for word in self.DOMAIN_NOISE_WORDS:
            combined = re.sub(rf"\b{word}\b", "", combined)

        combined = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", combined
        )
        combined = re.sub(r"\b[A-Z]{2,}-[A-Z]-\d{2,}-\d{5,}\b", "", combined)
        combined = re.sub(r"OPS-\d{4,}", "", combined)
        combined = re.sub(r"\s+", " ", combined)
        combined = combined.strip()
        return combined

    def normalize_title_only(self, title: str) -> str:
        """Normalize only the title for duplicate search.

        Users may not remember workflow type or severity,
        so we search only by title text.
        """
        combined = f"{title}"
        combined = combined.lower()

        for word in self.DOMAIN_NOISE_WORDS:
            combined = re.sub(rf"\b{word}\b", "", combined)

        combined = re.sub(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "", combined
        )
        combined = re.sub(r"\b[A-Z]{2,}-[A-Z]-\d{2,}-\d{5,}\b", "", combined)
        combined = re.sub(r"OPS-\d{4,}", "", combined)
        combined = re.sub(r"\s+", " ", combined)
        combined = combined.strip()
        return combined

    def cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors."""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return float(dot_product / (norm1 * norm2))

    def compute_similarities(
        self, query_embedding: np.ndarray, embeddings: np.ndarray
    ) -> np.ndarray:
        """Compute cosine similarity between query and all embeddings."""
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        all_norms = embeddings / np.linalg.norm(embeddings, axis=1, keepdims=True)
        similarities = np.dot(all_norms, query_norm)
        return similarities

    def process_tickets(self, tickets: List[Dict]) -> Dict:
        """Main processing pipeline: embed, cluster, enrich, and compute change tracking."""
        self.tickets_df = pd.DataFrame(tickets)
        self.tickets_df["timestamp"] = pd.to_datetime(self.tickets_df["timestamp"])

        normalized_texts = [
            self.normalize_ticket_text(
                row["title"], row["description"], row["severity"]
            )
            for _, row in self.tickets_df.iterrows()
        ]
        self.embeddings = self.model.encode(normalized_texts, show_progress_bar=False)

        clusters, unclustered_tickets = self._cluster_issues_hybrid()
        clusters = self._compute_cluster_confidence(clusters)
        clusters = self._add_actionable_insights(clusters)
        self._store_cluster_centroids()
        trends = self._detect_trends()
        change_tracking = self._compute_change_tracking()
        change_tracking = self._compute_per_cluster_changes(change_tracking)
        metrics = self._calculate_metrics(clusters, change_tracking)

        return {
            "clusters": clusters,
            "unclustered_tickets": unclustered_tickets,
            "trends": trends,
            "change_tracking": change_tracking,
            "metrics": metrics,
            "total_tickets": len(tickets),
            "config": config.get_config(),
        }

    def _cluster_issues_hybrid(self) -> List[Dict]:
        """Cluster using semantic embeddings (text only)."""
        clustering = DBSCAN(
            eps=config.DBSCAN_EPS, min_samples=config.MIN_SAMPLES, metric="cosine"
        )
        labels = clustering.fit_predict(self.embeddings)
        self.tickets_df["cluster"] = labels

        # --- Diagnostic: nearest-neighbor distances per ticket ---
        # Uncomment during tuning to inspect EPS calibration.
        # from sklearn.metrics.pairwise import cosine_distances
        # dist_matrix = cosine_distances(self.embeddings)
        # for i, row in enumerate(dist_matrix):
        #     sorted_dists = sorted(row)
        #     nearest = sorted_dists[1]  # skip self (distance=0)
        #     print(f"{self.tickets_df.iloc[i]['id']:10s}  nearest_neighbor_dist={nearest:.3f}")

        clusters = []
        unique_labels = set(labels)

        for label in unique_labels:
            if label == -1:
                continue

            cluster_mask = self.tickets_df["cluster"] == label
            cluster_tickets = self.tickets_df[cluster_mask]

            severity_counts = cluster_tickets["severity"].value_counts().to_dict()
            impact_score = self._calculate_impact_score(
                cluster_tickets, severity_counts
            )

            example_tickets = cluster_tickets.head(5)[
                ["id", "title", "severity", "timestamp"]
            ].to_dict("records")
            for t in example_tickets:
                t["timestamp"] = t["timestamp"].isoformat()

            all_tickets = cluster_tickets[
                ["id", "title", "severity", "timestamp"]
            ].to_dict("records")
            for t in all_tickets:
                t["timestamp"] = t["timestamp"].isoformat()

            summary = self._generate_cluster_summary(cluster_tickets)
            top_keywords = self._extract_top_keywords(cluster_tickets)
            representative_ticket = example_tickets[0] if example_tickets else None

            clusters.append(
                {
                    "cluster_id": int(label),
                    "incident_count": len(cluster_tickets),
                    "impact_score": round(impact_score, 2),
                    "severity_distribution": severity_counts,
                    "example_tickets": example_tickets,
                    "all_tickets": all_tickets,
                    "summary": summary,
                    "first_seen": cluster_tickets["timestamp"].min().isoformat(),
                    "last_seen": cluster_tickets["timestamp"].max().isoformat(),
                    "top_keywords": top_keywords,
                    "representative_ticket": representative_ticket,
                    "semantic_cohesion_score": 0.0,
                }
            )

        clusters.sort(key=lambda x: x["impact_score"], reverse=True)

        unclustered = self.tickets_df[self.tickets_df["cluster"] == -1]
        unclustered_tickets = unclustered[
            ["id", "title", "severity", "timestamp"]
        ].to_dict("records")
        for t in unclustered_tickets:
            t["timestamp"] = t["timestamp"].isoformat()

        return clusters, unclustered_tickets

    def _compute_cluster_confidence(self, clusters: List[Dict]) -> List[Dict]:
        """Compute confidence score for each cluster based on intra/inter-cluster similarity."""
        for cluster in clusters:
            cluster_id = cluster["cluster_id"]
            cluster_mask = self.tickets_df["cluster"] == cluster_id
            cluster_indices = self.tickets_df[cluster_mask].index.tolist()

            if len(cluster_indices) < 2:
                cluster["cluster_confidence_score"] = 0.5
                cluster["semantic_cohesion_score"] = 0.5
                continue

            cluster_embeddings = self.embeddings[cluster_indices]

            intra_similarities = []
            for i in range(len(cluster_embeddings)):
                for j in range(i + 1, len(cluster_embeddings)):
                    sim = self.cosine_similarity(
                        cluster_embeddings[i], cluster_embeddings[j]
                    )
                    intra_similarities.append(sim)

            avg_intra = np.mean(intra_similarities) if intra_similarities else 0.0

            other_cluster_indices = self.tickets_df[
                (self.tickets_df["cluster"] != cluster_id)
                & (self.tickets_df["cluster"] != -1)
            ].index.tolist()

            if other_cluster_indices:
                inter_similarities = []
                sample_size = min(50, len(other_cluster_indices))
                np.random.seed(42)
                sampled_others = np.random.choice(
                    other_cluster_indices, sample_size, replace=False
                )

                for ci in cluster_indices[:10]:
                    for oi in sampled_others:
                        sim = self.cosine_similarity(
                            self.embeddings[ci], self.embeddings[oi]
                        )
                        inter_similarities.append(sim)

                avg_inter = np.mean(inter_similarities) if inter_similarities else 0.0
            else:
                avg_inter = 0.0

            confidence = (avg_intra - avg_inter + 1.0) / 2.0
            confidence = max(0.0, min(1.0, confidence))

            cluster["cluster_confidence_score"] = round(confidence, 3)
            cluster["semantic_cohesion_score"] = round(avg_intra, 3)

        return clusters

    def _store_cluster_centroids(self):
        """Store cluster centroids for dynamic assignment."""
        self.cluster_centroids = {}
        self.cluster_info = {}

        unique_labels = set(self.tickets_df["cluster"])

        for label in unique_labels:
            if label == -1:
                continue
            cluster_mask = self.tickets_df["cluster"] == label
            cluster_indices = self.tickets_df[cluster_mask].index.tolist()

            centroid = np.mean(self.embeddings[cluster_indices], axis=0)
            self.cluster_centroids[label] = centroid

            cluster_tickets = self.tickets_df[cluster_mask]
            self.cluster_info[label] = {
                "severity_distribution": cluster_tickets["severity"]
                .value_counts()
                .to_dict(),
                "incident_count": len(cluster_tickets),
            }

    def check_duplicate(
        self,
        title: str,
        description: str = "",
        severity: str = "",
        title_only: bool = False,
    ) -> Dict:
        """Check if a new ticket is a duplicate of existing clusters.

        Args:
            title: Ticket title (required)
            description: Ticket description (optional)
            severity: Severity level (optional, used if title_only=False)
            title_only: If True, search only by title

        Returns:
            is_duplicate: Whether similarity exceeds threshold
            confidence_score: Maximum similarity score
            matched_cluster_id: ID of most similar cluster
            similar_tickets: Example tickets from matched cluster
        """
        if self.embeddings is None or self.tickets_df is None:
            return {
                "is_duplicate": False,
                "confidence_score": 0.0,
                "matched_cluster_id": None,
                "similar_tickets": [],
                "message": "No tickets processed yet",
            }

        if title_only:
            normalized_text = self.normalize_title_only(title)
        else:
            normalized_text = self.normalize_ticket_text(title, description, severity)

        query_embedding = self.model.encode([normalized_text], show_progress_bar=False)[0]

        similarities = self.compute_similarities(query_embedding, self.embeddings)
        best_match_idx = np.argmax(similarities)
        best_similarity = similarities[best_match_idx]

        if best_similarity >= config.SIMILARITY_THRESHOLD:
            matched_cluster_id = int(self.tickets_df.iloc[best_match_idx]["cluster"])

            cluster_mask = self.tickets_df["cluster"] == matched_cluster_id
            cluster_tickets = self.tickets_df[cluster_mask]

            similar_tickets = cluster_tickets.head(5)[
                ["id", "title", "severity", "timestamp"]
            ].to_dict("records")
            for t in similar_tickets:
                t["timestamp"] = t["timestamp"].isoformat()

            return {
                "is_duplicate": True,
                "confidence_score": round(float(best_similarity), 3),
                "matched_cluster_id": matched_cluster_id,
                "similar_tickets": similar_tickets,
                "message": f"Ticket matches cluster {matched_cluster_id}",
            }
        else:
            return {
                "is_duplicate": False,
                "confidence_score": round(float(best_similarity), 3),
                "matched_cluster_id": None,
                "similar_tickets": [],
                "message": "No matching cluster found",
            }

    def assign_to_cluster(self, title: str, description: str, severity: str) -> Dict:
        """Dynamically assign a new ticket to existing cluster or create new cluster.

        Uses centroid-based assignment with configurable threshold.
        """
        if not self.cluster_centroids:
            return {
                "assigned_cluster_id": -1,
                "created_new_cluster": True,
                "similarity_score": 0.0,
                "message": "No existing clusters - new cluster will be created",
            }

        normalized_text = self.normalize_ticket_text(title, description, severity)
        query_embedding = self.model.encode([normalized_text], show_progress_bar=False)[0]

        best_cluster_id = -1
        best_similarity = 0.0

        for cluster_id, centroid in self.cluster_centroids.items():
            similarity = self.cosine_similarity(query_embedding, centroid)
            if similarity > best_similarity:
                best_similarity = similarity
                best_cluster_id = cluster_id

        if best_similarity >= config.SIMILARITY_THRESHOLD:
            return {
                "assigned_cluster_id": best_cluster_id,
                "created_new_cluster": False,
                "similarity_score": round(best_similarity, 3),
                "message": f"Assigned to existing cluster {best_cluster_id}",
            }
        else:
            return {
                "assigned_cluster_id": -1,
                "created_new_cluster": True,
                "similarity_score": round(best_similarity, 3),
                "message": "No matching cluster - new cluster will be created",
            }

    def _add_actionable_insights(self, clusters: List[Dict]) -> List[Dict]:
        """Extend clusters with recommended_action, priority_level, etc."""
        for c in clusters:
            impact = c["impact_score"]
            severity_counts = c.get("severity_distribution", {})
            incident_count = c["incident_count"]
            confidence = c.get("cluster_confidence_score", 0.5)

            summary = c.get("summary", "")

            if summary:
                c["recommended_action"] = summary
            else:
                c["recommended_action"] = "Investigate root cause and implement fix"

            risk_score = min(
                (
                    incident_count * 2
                    + (severity_counts.get("critical", 0) * 10)
                    + (severity_counts.get("high", 0) * 5)
                ),
                100,
            )
            c["risk_score"] = round(risk_score, 1)

            time_span = (
                pd.Timestamp(c["last_seen"]) - pd.Timestamp(c["first_seen"])
            ).days
            recurrence_signal = (
                "recurring"
                if time_span >= 7 and incident_count >= 3
                else "spike"
                if incident_count >= 5
                else "intermittent"
            )
            c["recurrence_signal"] = recurrence_signal

            if impact >= 50 or severity_counts.get("critical", 0) >= 2:
                priority_level = "P1"
                urgency_tag = "immediate"
                business_impact = (
                    "Critical: Blocks core workflows and affects multiple users."
                )
            elif impact >= 30 or severity_counts.get("high", 0) >= 3:
                priority_level = "P2"
                urgency_tag = "high"
                business_impact = (
                    "High: Significant user impact; requires prompt resolution."
                )
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

            if confidence >= 0.7:
                c["confidence_label"] = "high"
            elif confidence >= 0.4:
                c["confidence_label"] = "medium"
            else:
                c["confidence_label"] = "low"

        return clusters

    def _calculate_impact_score(
        self, cluster_tickets: pd.DataFrame, severity_counts: Dict
    ) -> float:
        """Impact = frequency + severity + recurrence."""
        frequency_score = len(cluster_tickets) * 2
        severity_score = sum(
            severity_counts.get(sev, 0) * weight
            for sev, weight in config.SEVERITY_WEIGHTS.items()
        )
        time_span = (
            cluster_tickets["timestamp"].max() - cluster_tickets["timestamp"].min()
        ).days
        recurrence_score = min(time_span / 7, 10) if time_span > 0 else 0
        return frequency_score + severity_score + recurrence_score

    def _generate_cluster_summary(self, cluster_tickets: pd.DataFrame) -> str:
        """Human-readable summary of cluster."""
        count = len(cluster_tickets)
        severity_mode = cluster_tickets["severity"].mode()[0]
        common_terms = self._extract_common_terms(cluster_tickets)
        time_span = (
            cluster_tickets["timestamp"].max() - cluster_tickets["timestamp"].min()
        ).days

        summary = f"Recurring {severity_mode} severity issue. "
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
        """Extract most common terms from cluster tickets."""
        stop = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "to", "from", "up", "out", "about", "into", "through",
            "during", "before", "after", "above", "below", "between", "under",
            "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "now",
        }
        all_titles = " ".join(cluster_tickets["title"].tolist()).lower()
        words = [w for w in all_titles.split() if w not in stop and len(w) > 3]
        common = Counter(words).most_common(5)
        return [w for w, cnt in common if cnt > 1]

    def _extract_top_keywords(self, cluster_tickets: pd.DataFrame) -> List[str]:
        """Extract top keywords for cluster explainability."""
        all_text = " ".join(
            cluster_tickets["title"].tolist() + cluster_tickets["description"].tolist()
        ).lower()

        stop = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
            "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
            "have", "has", "had", "do", "does", "did", "will", "would", "could",
            "should", "may", "might", "must", "shall", "can", "need", "dare",
            "ought", "used", "from", "up", "out", "about", "into", "through",
            "during", "before", "after", "above", "below", "between", "under",
            "again", "further", "then", "once", "here", "there", "when", "where",
            "why", "how", "all", "each", "few", "more", "most", "other", "some",
            "such", "no", "nor", "not", "only", "own", "same", "so", "than", "too",
            "very", "just", "now", "this", "that", "these", "those", "it", "its",
            "we", "our", "they", "their", "them", "you", "your", "he", "she", "him",
            "her", "his", "i", "me", "my", "which", "what", "who", "whom", "whose",
        }

        words = [w for w in re.findall(r"\b[a-z]{4,}\b", all_text) if w not in stop]
        common = Counter(words).most_common(8)
        return [w for w, _ in common[:8]]

    def _detect_trends(self) -> Dict:
        """Daily incidents, severity over time."""
        self.tickets_df["date"] = self.tickets_df["timestamp"].dt.date
        daily = self.tickets_df.groupby("date").size().reset_index(name="count")
        daily["date"] = daily["date"].astype(str)

        severity_over_time = (
            self.tickets_df.groupby([self.tickets_df["timestamp"].dt.date, "severity"])
            .size()
            .reset_index(name="count")
        )
        severity_over_time.columns = ["date", "severity", "count"]
        severity_over_time["date"] = severity_over_time["date"].astype(str)

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
            len(self.tickets_df[self.tickets_df["severity"] == "critical"]) * 10
        ) + (len(self.tickets_df[self.tickets_df["severity"] == "high"]) * 5)
        risk_score = min((risk / total) * 10, 100) if total > 0 else 0

        if len(previous_7d) > 0:
            ratio = len(recent_7d) / len(previous_7d)
            stability_index = max(0, min(100, 100 - (ratio * 50)))
        else:
            stability_index = 50.0

        return {
            "trend_direction": trend_direction,
            "delta_percent": delta_percent,
            "new_clusters": 0,
            "resolved_clusters": 0,
            "stability_index": round(stability_index, 1),
            "cluster_changes": [],
        }

    def _compute_per_cluster_changes(self, change_tracking: Dict) -> Dict:
        """Compute change tracking for each cluster (last 7 days vs previous 7 days)."""
        recent_7d = self.tickets_df[
            self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=7))
        ]
        previous_7d = self.tickets_df[
            (self.tickets_df["timestamp"] > (datetime.now() - timedelta(days=14)))
            & (self.tickets_df["timestamp"] <= (datetime.now() - timedelta(days=7)))
        ]

        cluster_changes = []

        for cluster_id in self.cluster_centroids.keys():
            recent_count = len(recent_7d[recent_7d["cluster"] == cluster_id])
            previous_count = len(previous_7d[previous_7d["cluster"] == cluster_id])

            if previous_count == 0 and recent_count > 0:
                trend = "new"
            elif previous_count > 0 and recent_count == 0:
                trend = "resolved"
            elif recent_count > previous_count:
                trend = "increasing"
            elif recent_count < previous_count:
                trend = "decreasing"
            else:
                trend = "stable"

            cluster_changes.append(
                {
                    "cluster_id": cluster_id,
                    "previous_7d_count": previous_count,
                    "recent_7d_count": recent_count,
                    "trend": trend,
                }
            )

        change_tracking["cluster_changes"] = cluster_changes
        return change_tracking

    def _calculate_metrics(self, clusters: List[Dict], change_tracking: Dict) -> Dict:
        """High-level metrics for dashboard."""
        total = len(self.tickets_df)
        critical_count = len(self.tickets_df[self.tickets_df["severity"] == "critical"])
        high_count = len(self.tickets_df[self.tickets_df["severity"] == "high"])

        risk_score = (
            min(((critical_count * 10 + high_count * 5) / total) * 10, 100)
            if total > 0
            else 0
        )

        top_cluster = clusters[0] if clusters else None
        top_issue = (
            top_cluster["summary"][:120] + "..."
            if (top_cluster and len(top_cluster["summary"]) > 120)
            else (
                top_cluster["summary"]
                if top_cluster
                else "No recurring patterns detected"
            )
        )

        avg_confidence = (
            np.mean([c.get("cluster_confidence_score", 0) for c in clusters])
            if clusters
            else 0
        )

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
            "average_cluster_confidence": round(avg_confidence, 3),
        }