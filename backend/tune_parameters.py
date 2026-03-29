"""Parameter tuning script for clustering optimization.
Tests different HDBSCAN/DBSCAN configurations to find optimal settings.
Now includes PCA dimensionality reduction option.

Usage:
    python tune_parameters.py [--quick] [--output results.json]
"""

import argparse
import json
import numpy as np
from datetime import datetime
from typing import List, Dict, Tuple
from sklearn.metrics import (
    silhouette_score,
    adjusted_rand_score,
    normalized_mutual_info_score,
)
from sklearn.decomposition import PCA
from collections import Counter

try:
    import hdbscan

    HDBSCAN_AVAILABLE = True
except ImportError:
    HDBSCAN_AVAILABLE = False
    print("WARNING: hdbscan not installed. Install with: pip install hdbscan")

from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
from ground_truth import get_category
import config


def test_configuration(
    min_cluster_size: int,
    min_samples: int,
    cluster_selection_epsilon: float,
    text_weight: float,
    category_weight: float,
    severity_weight: float,
    use_pca: bool = False,
    pca_components: int = 128,
) -> Dict:
    """Test a specific configuration and return metrics."""
    original_min_cluster_size = config.HDBSCAN_MIN_CLUSTER_SIZE
    original_min_samples = config.HDBSCAN_MIN_SAMPLES
    original_epsilon = config.HDBSCAN_CLUSTER_SELECTION_EPSILON
    original_text = config.HYBRID_WEIGHT_TEXT
    original_cat = config.HYBRID_WEIGHT_CATEGORY
    original_sev = config.HYBRID_WEIGHT_SEVERITY
    original_use_pca = config.USE_PCA
    original_pca_components = config.PCA_COMPONENTS

    config.HDBSCAN_MIN_CLUSTER_SIZE = min_cluster_size
    config.HDBSCAN_MIN_SAMPLES = min_samples
    config.HDBSCAN_CLUSTER_SELECTION_EPSILON = cluster_selection_epsilon
    config.HYBRID_WEIGHT_TEXT = text_weight
    config.HYBRID_WEIGHT_CATEGORY = category_weight
    config.HYBRID_WEIGHT_SEVERITY = severity_weight
    config.USE_PCA = use_pca
    config.PCA_COMPONENTS = pca_components

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
                cat_counter = Counter(categories_in_cluster)
                dominant = cat_counter.most_common(1)[0]
                purity = dominant[1] / len(categories_in_cluster)
                purity_scores.append(purity)

        avg_purity = np.mean(purity_scores) if purity_scores else 0

        return {
            "min_cluster_size": min_cluster_size,
            "min_samples": min_samples,
            "cluster_selection_epsilon": cluster_selection_epsilon,
            "weights": f"{text_weight}/{category_weight}/{severity_weight}",
            "use_pca": use_pca,
            "pca_components": pca_components,
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
        config.HDBSCAN_MIN_CLUSTER_SIZE = original_min_cluster_size
        config.HDBSCAN_MIN_SAMPLES = original_min_samples
        config.HDBSCAN_CLUSTER_SELECTION_EPSILON = original_epsilon
        config.HYBRID_WEIGHT_TEXT = original_text
        config.HYBRID_WEIGHT_CATEGORY = original_cat
        config.HYBRID_WEIGHT_SEVERITY = original_sev
        config.USE_PCA = original_use_pca
        config.PCA_COMPONENTS = original_pca_components


def tune_parameters(quick_mode: bool = False, use_pca: bool = True) -> List[Dict]:
    """Test multiple configurations and find optimal settings."""
    print("=" * 80)
    print("PARAMETER TUNING - Finding Optimal Configuration")
    print("=" * 80)
    print(f"HDBSCAN available: {HDBSCAN_AVAILABLE}")
    print(f"Embedding model: {config.EMBEDDING_MODEL}")
    print("-" * 80)

    if quick_mode:
        min_cluster_sizes = [2, 3]
        min_samples_values = [1, 2]
        epsilon_values = [0.08, 0.12]
        weight_configs = [
            (0.75, 0.20, 0.05),
            (0.80, 0.15, 0.05),
        ]
        pca_configs = [(False, 128)] if not use_pca else [(True, 128), (False, 768)]
    else:
        min_cluster_sizes = [2, 3, 4]
        min_samples_values = [1, 2, 3]
        epsilon_values = [0.0, 0.08, 0.12, 0.15]
        weight_configs = [
            (0.70, 0.25, 0.05),
            (0.75, 0.20, 0.05),
            (0.80, 0.15, 0.05),
            (0.85, 0.10, 0.05),
        ]
        pca_configs = [(True, 128), (True, 64), (False, 768)]

    results = []

    print("\nTesting configurations...")
    print("-" * 80)

    total_combos = (
        len(min_cluster_sizes)
        * len(min_samples_values)
        * len(epsilon_values)
        * len(weight_configs)
        * len(pca_configs)
    )
    current = 0

    for min_cluster_size in min_cluster_sizes:
        for min_samples in min_samples_values:
            for epsilon in epsilon_values:
                for text_w, cat_w, sev_w in weight_configs:
                    for pca_flag, pca_comp in pca_configs:
                        current += 1

                        if current % 5 == 0:
                            print(f"  Progress: {current}/{total_combos}")

                        result = test_configuration(
                            min_cluster_size=min_cluster_size,
                            min_samples=min_samples,
                            cluster_selection_epsilon=epsilon,
                            text_weight=text_w,
                            category_weight=cat_w,
                            severity_weight=sev_w,
                            use_pca=pca_flag,
                            pca_components=pca_comp,
                        )
                        results.append(result)

                        pca_str = f"PCA{pca_comp}" if pca_flag else "NoPCA"
                        print(
                            f"  min_cluster={min_cluster_size}, min_samples={min_samples}, "
                            f"eps={epsilon:.2f}, weights={text_w:.2f}/{cat_w:.2f}, {pca_str}"
                        )
                        sil_str = (
                            f"{result['silhouette']:.3f}"
                            if result["silhouette"] is not None
                            else "N/A"
                        )
                        print(
                            f"    Clusters: {result['cluster_count']}, "
                            f"Unclustered: {result['unclustered_rate'] * 100:.1f}%, "
                            f"Sil: {sil_str}"
                        )
                        print(
                            f"    ARI: {result['ari']:.3f}, "
                            f"NMI: {result['nmi']:.3f}, "
                            f"Purity: {result['avg_purity']:.1%}, "
                            f"Score: {result['score']:.3f}"
                        )

    results.sort(key=lambda x: x["score"], reverse=True)

    print("\n" + "=" * 80)
    print("TOP 5 CONFIGURATIONS")
    print("=" * 80)

    for i, r in enumerate(results[:5], 1):
        print(f"\n#{i} - Score: {r['score']:.3f}")
        print(
            f"  Min Cluster Size: {r['min_cluster_size']}, Min Samples: {r['min_samples']}"
        )
        print(f"  Epsilon: {r['cluster_selection_epsilon']:.2f}")
        print(f"  Weights (text/category/severity): {r['weights']}")
        pca_str = f"PCA {r['pca_components']}" if r["use_pca"] else "No PCA"
        print(f"  Dimensionality: {pca_str}")
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
    print(f"HDBSCAN_MIN_CLUSTER_SIZE = {best['min_cluster_size']}")
    print(f"HDBSCAN_MIN_SAMPLES = {best['min_samples']}")
    print(f"HDBSCAN_CLUSTER_SELECTION_EPSILON = {best['cluster_selection_epsilon']}")
    weights = best["weights"].split("/")
    print(f"HYBRID_WEIGHT_TEXT = {weights[0]}")
    print(f"HYBRID_WEIGHT_CATEGORY = {weights[1]}")
    print(f"HYBRID_WEIGHT_SEVERITY = {weights[2]}")
    print(f"USE_PCA = {'True' if best['use_pca'] else 'False'}")
    if best["use_pca"]:
        print(f"PCA_COMPONENTS = {best['pca_components']}")
    print("-" * 80)
    print(
        f"Expected silhouette score: {best['silhouette']:.3f}"
        if best["silhouette"]
        else "Expected silhouette score: N/A"
    )
    print(f"Expected ARI: {best['ari']:.3f}")
    print(f"Expected NMI: {best['nmi']:.3f}")
    print("=" * 80)

    return results


def main():
    parser = argparse.ArgumentParser(description="Tune clustering parameters")
    parser.add_argument(
        "--quick", action="store_true", help="Quick mode with fewer combinations"
    )
    parser.add_argument(
        "--output", type=str, default="tuning_results.json", help="Output file"
    )
    parser.add_argument("--no-pca", action="store_true", help="Disable PCA in tuning")
    args = parser.parse_args()

    results = tune_parameters(quick_mode=args.quick, use_pca=not args.no_pca)

    output_data = {
        "timestamp": datetime.now().isoformat(),
        "best_config": results[0] if results else None,
        "top_5": results[:5],
    }

    with open(args.output, "w") as f:
        json.dump(output_data, f, indent=2, default=str)

    print(f"\nResults saved to {args.output}")
