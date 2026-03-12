"""Evaluate clustering quality against known categories.
Measures how well semantic clusters align with actual ticket categories.
"""

import numpy as np
from collections import Counter, defaultdict
from typing import List, Dict, Tuple
from sklearn.metrics import (
    silhouette_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)

from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
from ground_truth import get_category, get_all_categories, TICKET_CATEGORIES
import config


def evaluate_clustering() -> Dict:
    """Comprehensive clustering evaluation."""
    print("=" * 70)
    print("CLUSTERING EVALUATION REPORT")
    print("=" * 70)

    generator = TicketGenerator()
    tickets = generator.generate_tickets()

    processor = OperationalAIProcessor()
    insights = processor.process_tickets(tickets)

    clusters = insights["clusters"]
    unclustered = insights["unclustered_tickets"]

    true_labels = [get_category(t.get("id", "")) for t in tickets]
    predicted_labels = []

    ticket_to_cluster = {}
    for cluster in clusters:
        for t in cluster.get("all_tickets", []):
            ticket_to_cluster[t["id"]] = cluster["cluster_id"]
    for t in unclustered:
        ticket_to_cluster[t["id"]] = -1

    for t in tickets:
        predicted_labels.append(ticket_to_cluster.get(t["id"], -1))

    print(f"\nCurrent Configuration:")
    print(f"  DBSCAN_EPS: {config.DBSCAN_EPS}")
    print(f"  MIN_SAMPLES: {config.MIN_SAMPLES}")
    print(f"  SIMILARITY_THRESHOLD: {config.SIMILARITY_THRESHOLD}")

    print(f"\n--- Cluster Statistics ---")
    print(f"Total tickets: {len(tickets)}")
    print(f"Clusters formed: {len(clusters)}")
    print(
        f"Unclustered tickets: {len(unclustered)} ({len(unclustered) / len(tickets) * 100:.1f}%)"
    )

    cluster_sizes = [c["incident_count"] for c in clusters]
    if cluster_sizes:
        print(f"Avg cluster size: {np.mean(cluster_sizes):.1f}")
        print(f"Max cluster size: {max(cluster_sizes)}")
        print(f"Min cluster size: {min(cluster_sizes)}")

    print(f"\n--- Cluster Quality Metrics ---")

    if len(set(predicted_labels)) > 1:
        try:
            silhouette = silhouette_score(
                processor.embeddings, predicted_labels, metric="cosine"
            )
            print(
                f"Silhouette Score: {silhouette:.3f} (range: -1 to 1, higher is better)"
            )
        except:
            silhouette = None
            print("Silhouette Score: N/A (not enough variation)")
    else:
        silhouette = None
        print("Silhouette Score: N/A (only one cluster)")

    ari = adjusted_rand_score(true_labels, predicted_labels)
    nmi = normalized_mutual_info_score(true_labels, predicted_labels)
    print(f"Adjusted Rand Index: {ari:.3f} (range: -1 to 1, 1.0 = perfect)")
    print(f"Normalized Mutual Info: {nmi:.3f} (range: 0 to 1, 1.0 = perfect)")

    print(f"\n--- Category Distribution ---")
    category_counts = Counter(true_labels)
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  {cat}: {count} tickets")

    print(f"\n--- Cluster Purity Analysis ---")
    print("Shows how well each cluster captures a single category:\n")

    purity_scores = []
    for cluster in sorted(clusters, key=lambda x: -x["impact_score"])[:10]:
        cluster_id = cluster["cluster_id"]
        cluster_ticket_ids = [t["id"] for t in cluster.get("all_tickets", [])]

        categories_in_cluster = []
        for t in tickets:
            if t["id"] in cluster_ticket_ids:
                categories_in_cluster.append(get_category(t.get("id", "")))

        if categories_in_cluster:
            cat_counter = Counter(categories_in_cluster)
            dominant_cat = cat_counter.most_common(1)[0]
            purity = dominant_cat[1] / len(categories_in_cluster)
            purity_scores.append(purity)

            confidence = cluster.get("cluster_confidence_score", 0)
            cohesion = cluster.get("semantic_cohesion_score", 0)

            print(
                f"Cluster {cluster_id} (n={len(categories_in_cluster)}, purity={purity:.1%}):"
            )
            print(f"  Dominant: {dominant_cat[0]} ({dominant_cat[1]} tickets)")
            print(f"  Confidence: {confidence:.3f}, Cohesion: {cohesion:.3f}")
            if len(cat_counter) > 1:
                print(f"  Mixed with: {dict(cat_counter)}")
            print(f"  Keywords: {', '.join(cluster.get('top_keywords', [])[:5])}")
            print()

    avg_purity = np.mean(purity_scores) if purity_scores else 0
    print(f"Average Cluster Purity: {avg_purity:.1%}")

    print(f"\n--- Category Coverage Analysis ---")
    print("Shows how each category is distributed across clusters:\n")

    category_to_clusters = defaultdict(lambda: defaultdict(int))
    for i, t in enumerate(tickets):
        cat = get_category(t.get("id", ""))
        cluster_label = predicted_labels[i]
        category_to_clusters[cat][cluster_label] += 1

    for cat in sorted(category_to_clusters.keys()):
        cluster_dist = category_to_clusters[cat]
        total = sum(cluster_dist.values())
        unclustered_count = cluster_dist.get(-1, 0)
        clustered_count = total - unclustered_count

        print(f"{cat}:")
        print(
            f"  Total: {total}, Clustered: {clustered_count} ({clustered_count / total * 100:.0f}%), Unclustered: {unclustered_count}"
        )

        sorted_clusters = sorted(
            [(k, v) for k, v in cluster_dist.items() if k != -1], key=lambda x: -x[1]
        )[:3]
        if sorted_clusters:
            print(f"  Top clusters: {dict(sorted_clusters)}")
        print()

    print(f"\n--- Unclustered Ticket Analysis ---")
    if unclustered:
        unclustered_cats = Counter(
            [
                get_category(t.get("id", ""))
                for t in tickets
                if t["id"] in [u["id"] for u in unclustered]
            ]
        )
        print("Categories with most unclustered tickets:")
        for cat, count in unclustered_cats.most_common(5):
            print(f"  {cat}: {count}")
    else:
        print("No unclustered tickets!")

    print(f"\n--- Embedding Distance Analysis ---")
    from sklearn.metrics.pairwise import cosine_distances

    dist_matrix = cosine_distances(processor.embeddings)

    same_category_dists = []
    diff_category_dists = []

    for i in range(len(tickets)):
        for j in range(i + 1, len(tickets)):
            dist = dist_matrix[i, j]
            if true_labels[i] == true_labels[j]:
                same_category_dists.append(dist)
            else:
                diff_category_dists.append(dist)

    print(f"Same-category avg distance: {np.mean(same_category_dists):.3f}")
    print(f"Different-category avg distance: {np.mean(diff_category_dists):.3f}")
    print(
        f"Separation ratio: {np.mean(diff_category_dists) / np.mean(same_category_dists):.2f}x"
    )

    same_90th = np.percentile(same_category_dists, 90)
    diff_10th = np.percentile(diff_category_dists, 10)
    print(f"\n90th percentile same-category: {same_90th:.3f}")
    print(f"10th percentile diff-category: {diff_10th:.3f}")
    print(f"Gap: {diff_10th - same_90th:.3f} (positive = good separation)")

    print(f"\n--- Recommendations ---")

    if len(unclustered) / len(tickets) > 0.3:
        print("⚠️  High unclustered rate. Consider increasing DBSCAN_EPS.")

    if avg_purity < 0.6:
        print("⚠️  Low cluster purity. Consider decreasing DBSCAN_EPS or MIN_SAMPLES.")

    if np.mean(same_category_dists) > 0.4:
        print("⚠️  High intra-category variance. Consider better text normalization.")

    if diff_10th < same_90th:
        print("⚠️  Category overlap detected. Consider hybrid clustering with metadata.")

    optimal_eps = (
        np.mean(same_category_dists) + np.percentile(same_category_dists, 75)
    ) / 2
    print(f"\nSuggested DBSCAN_EPS: {optimal_eps:.2f} (current: {config.DBSCAN_EPS})")

    print("=" * 70)

    return {
        "silhouette": silhouette,
        "ari": ari,
        "nmi": nmi,
        "avg_purity": avg_purity,
        "unclustered_rate": len(unclustered) / len(tickets),
        "cluster_count": len(clusters),
        "avg_cluster_size": np.mean(cluster_sizes) if cluster_sizes else 0,
    }


if __name__ == "__main__":
    evaluate_clustering()
