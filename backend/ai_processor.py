"""AI pipeline for Operational Intelligence Dashboard.
Embeds tickets, clusters similar issues, detects trends, and generates actionable insights.

Features:
- Semantic duplicate detection with configurable threshold
- Hybrid clustering (semantic embeddings + metadata: category + severity)
- Dynamic cluster assignment for new tickets
- Cluster confidence scoring with silhouette analysis
- Improved text normalization for better embedding quality
- Category-aware clustering when metadata available
- HDBSCAN support for better clustering on small datasets
"""

import re
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.cluster import DBSCAN
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_samples
from typing import List, Dict, Any, Tuple, Optional
from collections import Counter
from datetime import datetime, timedelta

try:
    import hdbscan

    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False

import config
import category_classifier
import ground_truth


STOP_WORDS = {
    "the",
    "a",
    "an",
    "and",
    "or",
    "but",
    "in",
    "on",
    "at",
    "to",
    "for",
    "of",
    "with",
    "by",
    "is",
    "are",
    "was",
    "were",
    "be",
    "been",
    "being",
    "have",
    "has",
    "had",
    "do",
    "does",
    "did",
    "will",
    "would",
    "could",
    "should",
    "may",
    "might",
    "must",
    "shall",
    "can",
    "need",
    "dare",
    "ought",
    "used",
    "from",
    "up",
    "out",
    "about",
    "into",
    "through",
    "during",
    "before",
    "after",
    "above",
    "below",
    "between",
    "under",
    "again",
    "further",
    "then",
    "once",
    "here",
    "there",
    "when",
    "where",
    "why",
    "how",
    "all",
    "each",
    "few",
    "more",
    "most",
    "other",
    "some",
    "such",
    "no",
    "nor",
    "not",
    "only",
    "own",
    "same",
    "so",
    "than",
    "too",
    "very",
    "just",
    "now",
    "this",
    "that",
    "these",
    "those",
    "it",
    "its",
    "we",
    "our",
    "they",
    "their",
    "them",
    "you",
    "your",
    "he",
    "she",
    "him",
    "her",
    "his",
    "i",
    "me",
    "my",
    "which",
    "what",
    "who",
    "whom",
    "whose",
}


class OperationalAIProcessor:
    """AI-powered ticket clustering and analysis processor."""

    DOMAIN_NOISE_WORDS = [
        "clicking",
        "click",
        "button",
    ]

    DOMAIN_SYNONYMS = {
        "cannot": "can't",
        "does not": "doesn't",
        "is not": "isn't",
        "are not": "aren't",
        "will not": "won't",
        "not working": "broken",
        "not loading": "broken",
        "failing": "broken",
        "fails": "broken",
        "error": "broken",
        "timeout": "timeout",
        "time out": "timeout",
    }

    # FIX 1: CATEGORY_SIMILARITY_BOOST is now actually wired in.
    # Applied during hybrid feature construction to pull related categories
    # closer together in feature space before clustering.
    # Format: (category_a, category_b) -> similarity boost added to
    # the dot product of their one-hot encoded vectors.
    CATEGORY_SIMILARITY_BOOST = {
        # Only kept pairs where a single ticket can genuinely straddle both
        # categories (e.g. "reviewer can't submit score" touches both review
        # comments and recommendation).  All other pairs were removed because
        # they linked distinct problem types (upload failure ≠ autosave broken,
        # session timeout ≠ permission denied, slow page ≠ data not saving)
        # and caused unrelated tickets to merge into the same cluster.
        ("Review Comments", "Review Recommendation"): 0.08,
    }

    def __init__(self):
        self.model = SentenceTransformer(config.EMBEDDING_MODEL)
        self.embeddings: Optional[np.ndarray] = None
        self.hybrid_features: Optional[np.ndarray] = None
        self.tickets_df: Optional[pd.DataFrame] = None
        self.cluster_centroids: Dict[int, np.ndarray] = {}
        self.cluster_info: Dict[int, Dict] = {}
        self.category_encoder: Optional[OneHotEncoder] = None
        self.severity_encoder: Optional[StandardScaler] = None
        self.scaler: Optional[StandardScaler] = None
        self.pca: Optional[PCA] = None
        self.pca_components: int = config.PCA_COMPONENTS if config.USE_PCA else None

    def normalize_ticket_text(self, title: str, description: str, severity: str) -> str:
        """Create enriched combined text with normalization.

        Normalization steps:
        - lowercase
        - normalize synonyms (e.g., "cannot" -> "can't")
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

        for src, tgt in self.DOMAIN_SYNONYMS.items():
            combined = combined.replace(src, tgt)

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

    def normalize_tickets_with_llm(self, tickets: List[Dict]) -> List[str]:
        """Use Gemini to rewrite each ticket into a canonical one-sentence problem statement.

        This is the key fix for "same problem, different wording" clustering failures.
        When ops staff describe the same issue differently each time (e.g. "comment reply
        missing for reviewer" vs "author's reply not appearing in review panel"), standard
        embedding picks up surface differences and may not cluster them together.
        Gemini strips the noise and extracts the core symptom, so both become nearly
        identical vectors and land in the same cluster.

        Tickets are processed in batches (LLM_NORMALIZATION_BATCH_SIZE) to minimise
        API round-trips.  Any batch that fails falls back to standard normalization
        for those tickets so the pipeline never stalls.

        Returns a list of normalized text strings in the same order as `tickets`.
        """
        results = [""] * len(tickets)

        # Pre-fill with standard normalization as fallback
        for i, ticket in enumerate(tickets):
            results[i] = self.normalize_ticket_text(
                str(ticket.get("title", "")),
                str(ticket.get("description", "")),
                str(ticket.get("severity", "")),
            )

        if not config.USE_LLM_NORMALIZATION or not config.GEMINI_API_KEY:
            return results

        try:
            from google import genai
            from google.genai import types as genai_types

            client = genai.Client(api_key=config.GEMINI_API_KEY)
        except Exception:
            return results

        batch_size = config.LLM_NORMALIZATION_BATCH_SIZE
        total = len(tickets)

        for batch_start in range(0, total, batch_size):
            batch = tickets[batch_start : batch_start + batch_size]
            batch_lines = []
            for j, t in enumerate(batch, start=1):
                title = str(t.get("title", "")).strip()
                desc = str(t.get("description", "")).strip()
                # Truncate very long descriptions to keep prompt size manageable
                if len(desc) > 300:
                    desc = desc[:300] + "..."
                batch_lines.append(f"{j}. Title: {title} | Description: {desc}")

            prompt = (
                "For each support ticket below, write ONE concise sentence (max 12 words) "
                "that captures the core technical problem.\n"
                "Rules:\n"
                "- Focus on WHAT is broken and WHAT symptom the user sees.\n"
                "- Do NOT mention names, dates, ticket IDs, or workarounds.\n"
                "- Do NOT start with 'The user' or 'A user'.\n"
                "- Return ONLY a numbered list matching the input order, nothing else.\n\n"
                "Tickets:\n"
                + "\n".join(batch_lines)
                + "\n\nProblem statements:"
            )

            try:
                response = client.models.generate_content(
                    model=config.LLM_MODEL,
                    contents=prompt,
                    config=genai_types.GenerateContentConfig(
                        temperature=0,
                        max_output_tokens=300,
                    ),
                )
                raw = response.text.strip()
                lines = [l.strip() for l in raw.splitlines() if l.strip()]

                for j, line in enumerate(lines):
                    # Strip leading "1. " / "1) " numbering if present
                    clean = re.sub(r"^\d+[\.\)]\s*", "", line).strip()
                    global_idx = batch_start + j
                    if global_idx < total and clean:
                        results[global_idx] = clean

            except Exception as e:
                print(
                    f"LLM normalization failed for batch {batch_start}-"
                    f"{batch_start + len(batch)}: {e}. Using standard normalization."
                )
                # fallback already set above — continue to next batch

        print(
            f"LLM normalization complete: {total} tickets processed "
            f"(batch_size={batch_size})"
        )
        return results

    def normalize_tickets_locally(self, tickets: List[Dict]) -> List[str]:
        """Use a local FLAN-T5 model to normalize tickets — no API key needed.

        Downloads google/flan-t5-base (~300 MB) on first run and caches it
        locally.  Subsequent runs are instant.  Runs on CPU so no GPU required.

        Same goal as normalize_tickets_with_llm: rewrite each ticket into a
        short canonical problem statement so that tickets describing the same
        issue with different words produce similar embeddings and cluster
        together.

        Falls back to standard normalization per-ticket if the model cannot
        be loaded (e.g. transformers not installed).
        """
        # Pre-fill with standard normalization as fallback
        results = [
            self.normalize_ticket_text(
                str(t.get("title", "")),
                str(t.get("description", "")),
                str(t.get("severity", "")),
            )
            for t in tickets
        ]

        if not config.USE_LOCAL_NORMALIZATION:
            return results

        try:
            from transformers import pipeline as hf_pipeline

            print(
                f"Loading local normalization model: {config.LOCAL_NORMALIZATION_MODEL} "
                f"(downloads once then cached)"
            )
            summarizer = hf_pipeline(
                "text2text-generation",
                model=config.LOCAL_NORMALIZATION_MODEL,
                device=-1,          # CPU — change to 0 for GPU
                max_new_tokens=40,
            )
        except Exception as e:
            print(
                f"Local normalization model could not be loaded: {e}\n"
                f"Tip: run  pip install transformers torch --break-system-packages\n"
                f"Falling back to standard normalization."
            )
            return results

        prompt_template = (
            "Summarize this support ticket in one sentence of at most 12 words. "
            "Focus only on what is broken and the symptom. "
            "Remove names, dates, IDs, and workarounds.\n\n"
            "Title: {title}\nDescription: {desc}"
        )

        for i, ticket in enumerate(tickets):
            title = str(ticket.get("title", "")).strip()
            desc = str(ticket.get("description", "")).strip()
            if len(desc) > 300:
                desc = desc[:300] + "..."

            prompt = prompt_template.format(title=title, desc=desc)
            try:
                output = summarizer(prompt)[0]["generated_text"].strip()
                if output:
                    results[i] = output
            except Exception as e:
                print(f"Local normalization failed for ticket {ticket.get('id','?')}: {e}")
                # fallback already set

        print(f"Local normalization complete: {len(tickets)} tickets processed")
        return results

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
        """Main processing pipeline: classify, embed, cluster, enrich, and compute change tracking."""
        if not tickets:
            return {
                "clusters": [],
                "unclustered_tickets": [],
                "trends": {
                    "daily_incidents": [],
                    "severity_over_time": [],
                    "trend_direction": "stable",
                },
                "change_tracking": {
                    "trend_direction": "stable",
                    "delta_percent": 0,
                    "cluster_changes": [],
                },
                "metrics": {"total_incidents": 0, "risk_score": 0},
                "total_tickets": 0,
                "config": config.get_config(),
            }

        if "category" not in tickets[0]:
            tickets = category_classifier.enrich_tickets_with_categories(
                tickets, model=self.model
            )

        self.tickets_df = pd.DataFrame(tickets)
        self.tickets_df["timestamp"] = pd.to_datetime(self.tickets_df["timestamp"])

        if config.USE_LLM_NORMALIZATION and config.GEMINI_API_KEY:
            # Option 1: Gemini API — best quality, needs GEMINI_API_KEY in .env
            normalized_texts = self.normalize_tickets_with_llm(tickets)
        elif config.USE_LOCAL_NORMALIZATION:
            # Option 2: Local FLAN-T5 — good quality, no API key needed.
            # Downloads google/flan-t5-base (~300 MB) once then uses cache.
            # Set USE_LOCAL_NORMALIZATION=true in .env to enable.
            normalized_texts = self.normalize_tickets_locally(tickets)
        else:
            # Option 3: Standard regex normalization — always available, no deps.
            # Works well with the paraphrase-mpnet-base-v2 embedding model which
            # handles same-meaning different-wording naturally.
            normalized_texts = [
                self.normalize_ticket_text(
                    str(row["title"]), str(row["description"]), str(row["severity"])
                )
                for _, row in self.tickets_df.iterrows()
            ]
        self.embeddings = np.array(
            self.model.encode(normalized_texts, show_progress_bar=False)
        )

        self._build_hybrid_features()

        clusters, unclustered_tickets = self._cluster_issues_hybrid()
        clusters = self._compute_cluster_confidence(clusters)
        clusters = self._add_actionable_insights(clusters)
        self._store_cluster_centroids()
        trends = self._detect_trends()
        change_tracking = self._compute_change_tracking()
        change_tracking = self._compute_per_cluster_changes(change_tracking)
        metrics = self._calculate_metrics(clusters, change_tracking)

        quality_metrics = self._compute_quality_metrics(clusters, unclustered_tickets)

        return {
            "clusters": clusters,
            "unclustered_tickets": unclustered_tickets,
            "trends": trends,
            "change_tracking": change_tracking,
            "metrics": metrics,
            "quality": quality_metrics,
            "total_tickets": len(tickets),
            "config": config.get_config(),
        }

    def _build_hybrid_features(self):
        """Build hybrid feature vector combining text embeddings with metadata.

        FIX 1: CATEGORY_SIMILARITY_BOOST is now applied here.
        After one-hot encoding, we add the boost value to the dot product
        between tickets that belong to related category pairs, pulling them
        closer in feature space before clustering runs.

        FIX 5: Optional PCA dimensionality reduction to reduce noise in
        high-dimensional embeddings (768 -> 128 dimensions).
        """
        text_weight = config.HYBRID_WEIGHT_TEXT
        category_weight = config.HYBRID_WEIGHT_CATEGORY
        severity_weight = config.HYBRID_WEIGHT_SEVERITY

        embeddings_to_use = self.embeddings.copy()

        n_samples = embeddings_to_use.shape[0]
        n_features = embeddings_to_use.shape[1]
        max_components = min(n_samples, n_features)

        if config.USE_PCA:
            target_components = min(config.PCA_COMPONENTS, max_components)
            if embeddings_to_use.shape[1] > target_components:
                self.pca = PCA(n_components=target_components)
                embeddings_to_use = self.pca.fit_transform(embeddings_to_use)

        text_features = embeddings_to_use * text_weight

        has_category = "category" in self.tickets_df.columns
        has_severity = "severity" in self.tickets_df.columns

        metadata_features = np.zeros((len(self.tickets_df), 0))

        category_encoded = None
        if has_category and category_weight > 0:
            categories = (
                self.tickets_df["category"].fillna("unknown").values.reshape(-1, 1)
            )
            self.category_encoder = OneHotEncoder(
                sparse_output=False, handle_unknown="ignore"
            )
            category_encoded = self.category_encoder.fit_transform(categories)

            # Apply CATEGORY_SIMILARITY_BOOST: for each pair of related categories,
            # find tickets in each and add the boost to their category vectors'
            # cross-component, effectively shrinking their distance in feature space.
            category_list = [
                cat[len("x0_") :] if cat.startswith("x0_") else cat
                for cat in self.category_encoder.get_feature_names_out()
            ]
            ticket_categories = self.tickets_df["category"].fillna("unknown").tolist()

            for (cat_a, cat_b), boost in self.CATEGORY_SIMILARITY_BOOST.items():
                if cat_a in category_list and cat_b in category_list:
                    idx_a = category_list.index(cat_a)
                    idx_b = category_list.index(cat_b)
                    # For tickets in cat_a, boost their cat_b component and vice versa
                    for i, tc in enumerate(ticket_categories):
                        if tc == cat_a:
                            category_encoded[i, idx_b] += boost
                        elif tc == cat_b:
                            category_encoded[i, idx_a] += boost

            category_scaled = category_encoded * category_weight
            metadata_features = np.hstack([metadata_features, category_scaled])

        if has_severity and severity_weight > 0:
            severities = (
                self.tickets_df["severity"].fillna("medium").values.reshape(-1, 1)
            )
            severity_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
            severity_numeric = np.array(
                [severity_order.get(s.lower(), 2) for s in severities.flatten()]
            ).reshape(-1, 1)
            self.severity_encoder = StandardScaler()
            severity_scaled = (
                self.severity_encoder.fit_transform(severity_numeric) * severity_weight
            )
            metadata_features = np.hstack([metadata_features, severity_scaled])

        if metadata_features.shape[1] > 0:
            self.hybrid_features = np.hstack([text_features, metadata_features])
        else:
            self.hybrid_features = text_features

    def _cluster_issues_hybrid(self) -> Tuple[List[Dict], List[Dict]]:
        """Cluster using hybrid features (text + metadata)."""
        features_to_use = (
            self.hybrid_features
            if self.hybrid_features is not None
            else self.embeddings
        )

        if config.USE_HDBSCAN and HDBSCAN_AVAILABLE:
            norms = np.linalg.norm(features_to_use, axis=1, keepdims=True)
            norms[norms == 0] = 1
            normalized_features = features_to_use / norms
            clustering = hdbscan.HDBSCAN(
                min_cluster_size=config.HDBSCAN_MIN_CLUSTER_SIZE,
                min_samples=config.HDBSCAN_MIN_SAMPLES,
                metric="euclidean",
                cluster_selection_method="eom",
                cluster_selection_epsilon=config.HDBSCAN_CLUSTER_SELECTION_EPSILON,
                prediction_data=True,
            )
            labels = clustering.fit_predict(normalized_features)
        else:
            clustering = DBSCAN(
                eps=config.DBSCAN_EPS, min_samples=config.MIN_SAMPLES, metric="cosine"
            )
            labels = clustering.fit_predict(features_to_use)

        self.tickets_df["cluster"] = labels

        if len(set(labels)) > 1:
            try:
                silhouette_vals = silhouette_samples(
                    features_to_use, labels, metric="cosine"
                )
                self.tickets_df["silhouette_score"] = silhouette_vals
            except ValueError:
                self.tickets_df["silhouette_score"] = 0.0
        else:
            self.tickets_df["silhouette_score"] = 0.0

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

            # FIX 2: summary is now topic-aware, not a generic template
            summary = self._generate_cluster_summary(cluster_tickets)
            top_keywords = self._extract_top_keywords(cluster_tickets)
            representative_ticket = example_tickets[0] if example_tickets else None

            category_dist = {}
            if "category" in cluster_tickets.columns:
                category_dist = cluster_tickets["category"].value_counts().to_dict()

            avg_silhouette = cluster_tickets["silhouette_score"].mean()

            clusters.append(
                {
                    "cluster_id": int(label),
                    "incident_count": len(cluster_tickets),
                    "impact_score": round(impact_score, 2),
                    "severity_distribution": severity_counts,
                    "category_distribution": category_dist,
                    "example_tickets": example_tickets,
                    "all_tickets": all_tickets,
                    "summary": summary,
                    "first_seen": cluster_tickets["timestamp"].min().isoformat(),
                    "last_seen": cluster_tickets["timestamp"].max().isoformat(),
                    "top_keywords": top_keywords,
                    "representative_ticket": representative_ticket,
                    "semantic_cohesion_score": 0.0,
                    "avg_silhouette_score": round(avg_silhouette, 3),
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
        features_to_use = (
            self.hybrid_features
            if self.hybrid_features is not None
            else self.embeddings
        )

        for cluster in clusters:
            cluster_id = cluster["cluster_id"]
            cluster_mask = self.tickets_df["cluster"] == cluster_id
            cluster_indices = self.tickets_df[cluster_mask].index.tolist()

            if len(cluster_indices) < 2:
                cluster["cluster_confidence_score"] = 0.5
                cluster["semantic_cohesion_score"] = 0.5
                continue

            cluster_features = features_to_use[cluster_indices]

            intra_similarities = []
            for i in range(len(cluster_features)):
                for j in range(i + 1, len(cluster_features)):
                    sim = self.cosine_similarity(
                        cluster_features[i], cluster_features[j]
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
                            features_to_use[ci], features_to_use[oi]
                        )
                        inter_similarities.append(sim)

                avg_inter = np.mean(inter_similarities) if inter_similarities else 0.0
            else:
                avg_inter = 0.0

            confidence = (avg_intra - avg_inter + 1.0) / 2.0
            confidence = max(0.0, min(1.0, confidence))

            silhouette = cluster.get("avg_silhouette_score", 0)
            combined_confidence = confidence * 0.6 + (silhouette + 1) / 2 * 0.4

            cluster["cluster_confidence_score"] = round(combined_confidence, 3)
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
        """Check if a new ticket is a duplicate of existing clusters."""
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

        query_embedding = self.model.encode([normalized_text], show_progress_bar=False)[
            0
        ]

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
        """Dynamically assign a new ticket to existing cluster or create new cluster."""
        if not self.cluster_centroids:
            return {
                "assigned_cluster_id": -1,
                "created_new_cluster": True,
                "similarity_score": 0.0,
                "message": "No existing clusters - new cluster will be created",
            }

        normalized_text = self.normalize_ticket_text(title, description, severity)
        query_embedding = self.model.encode([normalized_text], show_progress_bar=False)[
            0
        ]

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

            first_seen = pd.Timestamp(c["first_seen"])
            last_seen = pd.Timestamp(c["last_seen"])
            time_span = (last_seen - first_seen).days

            risk_score = min(
                (
                    incident_count * 2
                    + (severity_counts.get("critical", 0) * 10)
                    + (severity_counts.get("high", 0) * 5)
                ),
                100,
            )
            c["risk_score"] = round(risk_score, 1)

            recurrence_signal = (
                "recurring"
                if time_span >= 7 and incident_count >= 3
                else "spike"
                if incident_count >= 5
                else "intermittent"
            )
            c["recurrence_signal"] = recurrence_signal

            critical_count = severity_counts.get("critical", 0)
            high_count = severity_counts.get("high", 0)

            if recurrence_signal == "recurring" and critical_count >= 2:
                c["recommended_action"] = (
                    f"Critical recurring pattern detected. Immediately investigate root cause "
                    f"and implement permanent fix. Current rate: {incident_count} incidents over {time_span} days."
                )
            elif recurrence_signal == "spike" and critical_count >= 1:
                c["recommended_action"] = (
                    f"Urgent spike in critical incidents. Establish incident response team "
                    f"and deploy hotfix. {incident_count} incidents detected."
                )
            elif time_span <= 1 and incident_count >= 3:
                c["recommended_action"] = (
                    f"High-frequency spike detected within 24 hours. Enable detailed logging "
                    f"and monitoring. Escalate to on-call team immediately."
                )
            elif high_count >= 3 or impact >= 50:
                c["recommended_action"] = (
                    f"High-impact cluster requiring prompt attention. Review recent deployments "
                    f"and configuration changes. Schedule emergency review meeting."
                )
            elif recurrence_signal == "recurring":
                c["recommended_action"] = (
                    f"Establish preventive monitoring for this recurring pattern. Document "
                    f"workflow and implement safeguards to reduce incident frequency."
                )
            else:
                c["recommended_action"] = (
                    "Investigate and implement targeted fix to prevent future occurrences."
                )

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
        """Human-readable summary of cluster.

        FIX 2: Summary now leads with the actual topic (top keywords) rather
        than a generic severity/count template. This makes it useful in the
        dashboard overview without having to drill into individual tickets.
        """
        count = len(cluster_tickets)
        severity_mode = cluster_tickets["severity"].mode()[0]
        top_keywords = self._extract_common_terms(cluster_tickets)
        time_span = (
            cluster_tickets["timestamp"].max() - cluster_tickets["timestamp"].min()
        ).days

        # Lead with topic, not boilerplate
        if top_keywords:
            topic = ", ".join(top_keywords[:2])
            summary = f"{count} {severity_mode}-severity incidents related to {topic}. "
        else:
            summary = f"{count} {severity_mode}-severity incidents. "

        summary += f"Spanning {time_span} days. "

        # Dominant category if available
        if "category" in cluster_tickets.columns:
            dominant_category = cluster_tickets["category"].mode()[0]
            summary += f"Category: {dominant_category}. "

        if time_span < 7:
            summary += "Recent spike — requires immediate attention."
        elif count > 10:
            summary += "High frequency — suggests systematic problem."
        else:
            summary += "Intermittent pattern — monitor for escalation."

        return summary

    def _extract_common_terms(self, cluster_tickets: pd.DataFrame) -> List[str]:
        """Extract most common terms from cluster tickets."""
        all_titles = " ".join(cluster_tickets["title"].tolist()).lower()
        words = [w for w in all_titles.split() if w not in STOP_WORDS and len(w) > 3]
        common = Counter(words).most_common(5)
        return [w for w, cnt in common if cnt > 1]

    def _extract_top_keywords(self, cluster_tickets: pd.DataFrame) -> List[str]:
        """Extract top keywords for cluster explainability."""
        all_text = " ".join(
            cluster_tickets["title"].tolist() + cluster_tickets["description"].tolist()
        ).lower()

        words = [
            w for w in re.findall(r"\b[a-z]{4,}\b", all_text) if w not in STOP_WORDS
        ]
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

        top_recommended_action = (
            top_cluster.get("recommended_action", "Investigate and implement fix")
            if top_cluster
            else "No patterns to act on"
        )

        return {
            "total_incidents": total,
            "top_issue": top_issue,
            "top_recommended_action": top_recommended_action,
            "risk_score": round(risk_score, 1),
            "stability_index": change_tracking.get("stability_index", 50),
            "trend_direction": change_tracking.get("trend_direction", "stable"),
            "top_recurring_issue": top_issue,
            "critical_incidents": critical_count,
            "high_priority_incidents": high_count,
            "cluster_count": len(clusters),
            "average_cluster_confidence": round(avg_confidence, 3),
        }

    def _compute_quality_metrics(
        self, clusters: List[Dict], unclustered_tickets: List[Dict]
    ) -> Dict:
        """Compute clustering quality metrics: silhouette score and confusion matrix.

        FIX 3: Silhouette score is now read from already-computed per-ticket
        values in self.tickets_df["silhouette_score"] rather than recomputing
        from scratch. This eliminates the double-computation and ensures the
        quality score matches what individual tickets show.

        FIX 4: ground_truth_coverage is now included in the output so the
        dashboard can show how much of the dataset the quality metrics reflect.
        """
        ticket_to_cluster = {}
        for cluster in clusters:
            for t in cluster.get("all_tickets", []):
                ticket_to_cluster[t["id"]] = cluster["cluster_id"]
        for t in unclustered_tickets:
            ticket_to_cluster[t["id"]] = -1

        true_labels = []
        predicted_labels = []
        valid_indices = []

        for idx, row in self.tickets_df.iterrows():
            ticket_id = row.get("id", "")
            true_cat = ground_truth.get_category(ticket_id)
            if true_cat != "unknown":
                true_labels.append(true_cat)
                predicted_labels.append(ticket_to_cluster.get(ticket_id, -1))
                valid_indices.append(idx)

        total_tickets = len(self.tickets_df)
        covered_tickets = len(valid_indices)

        # FIX 3: Read pre-computed silhouette scores instead of recomputing.
        # Only include tickets that (a) have ground truth and (b) are in a cluster
        # (silhouette is undefined for noise points labeled -1).
        silhouette = None
        if valid_indices and len(set(predicted_labels)) > 1:
            try:
                clustered_mask = [p != -1 for p in predicted_labels]
                clustered_indices = [
                    idx for idx, m in zip(valid_indices, clustered_mask) if m
                ]
                if len(clustered_indices) > 1:
                    silhouette = float(
                        self.tickets_df.loc[
                            clustered_indices, "silhouette_score"
                        ].mean()
                    )
            except (KeyError, ValueError):
                silhouette = None

        confusion_matrix = {}
        all_categories = ground_truth.get_all_categories()

        for cat in all_categories:
            confusion_matrix[cat] = {}

        for i, row in self.tickets_df.iterrows():
            ticket_id = row.get("id", "")
            true_cat = ground_truth.get_category(ticket_id)
            if true_cat == "unknown":
                continue

            cluster_id = ticket_to_cluster.get(ticket_id, -1)
            cluster_key = f"Cluster {cluster_id}" if cluster_id != -1 else "Unclustered"

            if cluster_key not in confusion_matrix[true_cat]:
                confusion_matrix[true_cat][cluster_key] = 0
            confusion_matrix[true_cat][cluster_key] += 1

        cluster_ids = [f"Cluster {c['cluster_id']}" for c in clusters]
        cluster_ids.append("Unclustered")

        used_clusters = set()
        for row in confusion_matrix.values():
            used_clusters.update(row.keys())
        cluster_ids = [c for c in cluster_ids if c in used_clusters]

        return {
            "silhouette_score": round(silhouette, 3)
            if silhouette is not None
            else None,
            "silhouette_interpretation": self._interpret_silhouette(silhouette),
            # FIX 4: Expose coverage so dashboard can show "Quality based on X/Y tickets"
            "ground_truth_coverage": covered_tickets,
            "ground_truth_total": total_tickets,
            "ground_truth_coverage_pct": round(covered_tickets / total_tickets * 100, 1)
            if total_tickets > 0
            else 0.0,
            "confusion_matrix": confusion_matrix,
            "cluster_labels": cluster_ids,
            "ground_truth_categories": all_categories,
        }

    def _interpret_silhouette(self, score: Optional[float]) -> str:
        """Provide human-readable interpretation of silhouette score."""
        if score is None:
            return "Insufficient data"
        if score >= 0.7:
            return "Strong cluster structure"
        if score >= 0.5:
            return "Reasonable cluster structure"
        if score >= 0.25:
            return "Weak cluster structure"
        if score >= 0:
            return "No substantial structure"
        return "Artificial clustering"
