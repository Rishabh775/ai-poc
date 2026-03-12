"""Parameter tuning script for clustering optimization.
Tests different DBSCAN configurations to find optimal settings.
"""

import numpy as np
from typing import List, Dict, Tuple
from sklearn.metrics import (
    silhouette_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)

from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
from ground_truth import get_category
import config


def test_configuration(
    eps: float,
    min_samples: int,
    text_weight: float,
    category_weight: float,
    severity_weight: float,
) -> Dict:
    """Test a specific configuration and return metrics."""
    original_eps = config.DBSCAN_EPS
    original_min = config.MIN_SAMPLES
    original_text = config.HYBRID_WEIGHT_TEXT
    original_cat = config.HYBRID_WEIGHT_CATEGORY
    original_sev = config.HYBRID_WEIGHT_SEVERITY

    config.DBSCAN_EPS = eps
    config.MIN_SAMPLES = min_samples
    config.HYBRID_WEIGHT_TEXT = text_weight
    config.HYBRID_WEIGHT_CATEGORY = category_weight
    config.HYBRID_WEIGHT_SEVERITY = severity_weight

    try:
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

        unclustered_rate = len(unclustered) / len(tickets)

        silhouette = None
        if len(set(predicted_labels)) > 1:
            try:
                silhouette = silhouette_score(
                    processor.embeddings, predicted_labels, metric="cosine"
                )
            except:
                pass

        ari = adjusted_rand_score(true_labels, predicted_labels)
        nmi = normalized_mutual_info_score(true_labels, predicted_labels)

        purity_scores = []
        for cluster in clusters:
            cluster_ticket_ids = [t["id"] for t in cluster.get("all_tickets", [])]
            categories_in_cluster = []
            for t in tickets:
                if t["id"] in cluster_ticket_ids:
                    categories_in_cluster.append(get_category(t.get("id", "")))
            if categories_in_cluster:
                from collections import Counter

                cat_counter = Counter(categories_in_cluster)
                dominant = cat_counter.most_common(1)[0]
                purity = dominant[1] / len(categories_in_cluster)
                purity_scores.append(purity)

        avg_purity = np.mean(purity_scores) if purity_scores else 0

        return {
            "eps": eps,
            "min_samples": min_samples,
            "weights": f"{text_weight}/{category_weight}/{severity_weight}",
            "cluster_count": len(clusters),
            "unclustered_rate": unclustered_rate,
            "silhouette": silhouette,
            "ari": ari,
            "nmi": nmi,
            "avg_purity": avg_purity,
            "score": (
                ari * 0.4 + nmi * 0.3 + avg_purity * 0.2 - unclustered_rate * 0.1
            ),
        }
    finally:
        config.DBSCAN_EPS = original_eps
        config.MIN_SAMPLES = original_min
        config.HYBRID_WEIGHT_TEXT = original_text
        config.HYBRID_WEIGHT_CATEGORY = original_cat
        config.HYBRID_WEIGHT_SEVERITY = original_sev


def tune_parameters():
    """Test multiple configurations and find optimal settings."""
    print("=" * 80)
    print("PARAMETER TUNING - Finding Optimal Configuration")
    print("=" * 80)

    eps_values = [0.50, 0.55, 0.58, 0.60, 0.63]
    min_samples_values = [2, 3]
    weight_configs = [
        (0.85, 0.10, 0.05),
        (0.80, 0.15, 0.05),
        (0.75, 0.20, 0.05),
    ]

    results = []

    print("\nTesting configurations...")
    print("-" * 80)

    for eps in eps_values:
        for min_samples in min_samples_values:
            for text_w, cat_w, sev_w in weight_configs:
                result = test_configuration(eps, min_samples, text_w, cat_w, sev_w)
                results.append(result)

                print(
                    f"EPS={eps:.2f}, min={min_samples}, weights={text_w:.2f}/{cat_w:.2f}/{sev_w:.2f}"
                )
                print(
                    f"  Clusters: {result['cluster_count']}, Unclustered: {result['unclustered_rate'] * 100:.1f}%"
                )
                sil_str = (
                    f"{result['silhouette']:.3f}"
                    if result["silhouette"] is not None
                    else "N/A"
                )
                print(
                    f"  Silhouette: {sil_str}, "
                    f"ARI: {result['ari']:.3f}, NMI: {result['nmi']:.3f}, Purity: {result['avg_purity']:.1%}"
                )
                print(f"  Combined Score: {result['score']:.3f}")
                print()

    results.sort(key=lambda x: x["score"], reverse=True)

    print("=" * 80)
    print("TOP 5 CONFIGURATIONS")
    print("=" * 80)

    for i, r in enumerate(results[:5], 1):
        print(f"\n#{i} - Score: {r['score']:.3f}")
        print(f"  EPS: {r['eps']:.2f}, Min Samples: {r['min_samples']}")
        print(f"  Weights (text/category/severity): {r['weights']}")
        print(
            f"  Clusters: {r['cluster_count']}, Unclustered: {r['unclustered_rate'] * 100:.1f}%"
        )
        sil_str = f"{r['silhouette']:.3f}" if r["silhouette"] is not None else "N/A"
        print(
            f"  Silhouette: {sil_str}, "
            f"ARI: {r['ari']:.3f}, NMI: {r['nmi']:.3f}, Purity: {r['avg_purity']:.1%}"
        )

    best = results[0]
    print("\n" + "=" * 80)
    print("RECOMMENDED CONFIGURATION")
    print("=" * 80)
    print(f"DBSCAN_EPS = {best['eps']:.2f}")
    print(f"MIN_SAMPLES = {best['min_samples']}")
    print(f"HYBRID_WEIGHT_TEXT = {best['weights'].split('/')[0]}")
    print(f"HYBRID_WEIGHT_CATEGORY = {best['weights'].split('/')[1]}")
    print(f"HYBRID_WEIGHT_SEVERITY = {best['weights'].split('/')[2]}")
    print("=" * 80)

    return results


if __name__ == "__main__":
    tune_parameters()
