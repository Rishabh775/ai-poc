"""Unit tests for clustering pipeline quality.
Verifies that silhouette score meets minimum threshold.

Usage:
    python test_clustering.py
    python -m pytest test_clustering.py -v
"""

import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import numpy as np
from ticket_generator import TicketGenerator
from ai_processor import OperationalAIProcessor
import config


class TestClusteringQuality(unittest.TestCase):
    """Test clustering quality metrics."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.generator = TicketGenerator()
        cls.tickets = cls.generator.generate_tickets()
        cls.processor = OperationalAIProcessor()
        cls.insights = cls.processor.process_tickets(cls.tickets)

    def test_silhouette_score_threshold(self):
        """Test that silhouette score meets minimum threshold (0.05 for real operational data)."""
        quality = self.insights.get("quality", {})
        silhouette = quality.get("silhouette_score")

        # Note: Realistic silhouette for operational data with overlapping categories
        # is typically 0.05-0.15. Higher values (0.5+) are only achievable
        # with well-separated synthetic data.
        self.assertIsNotNone(silhouette, "Silhouette score should not be None")
        self.assertGreaterEqual(
            silhouette,
            0.05,
            f"Silhouette score ({silhouette:.3f}) should be >= 0.05. "
            f"Note: Real operational data typically has silhouette 0.05-0.15.",
        )
        print(f"\n✓ Silhouette score: {silhouette:.3f} (threshold: 0.05)")

    def test_cluster_count_reasonable(self):
        """Test that number of clusters is reasonable."""
        clusters = self.insights.get("clusters", [])
        num_clusters = len(clusters)
        num_tickets = len(self.tickets)

        self.assertGreater(num_clusters, 0, "Should have at least 1 cluster")
        self.assertLess(
            num_clusters, num_tickets, "Should have fewer clusters than tickets"
        )
        self.assertLess(
            num_clusters,
            num_tickets * 0.5,
            "Should not have more clusters than 50% of tickets",
        )
        print(f"\n✓ Cluster count: {num_clusters} (tickets: {num_tickets})")

    def test_unclustered_rate_acceptable(self):
        """Test that unclustered ticket rate is acceptable (< 30%)."""
        unclustered = self.insights.get("unclustered_tickets", [])
        num_unclustered = len(unclustered)
        num_tickets = len(self.tickets)
        unclustered_rate = num_unclustered / num_tickets if num_tickets > 0 else 0

        self.assertLess(
            unclustered_rate,
            0.30,
            f"Unclustered rate ({unclustered_rate:.1%}) should be < 30%",
        )
        print(f"\n✓ Unclustered rate: {unclustered_rate:.1%} (threshold: 30%)")

    def test_cluster_confidence_scores(self):
        """Test that cluster confidence scores are computed."""
        clusters = self.insights.get("clusters", [])

        for cluster in clusters:
            confidence = cluster.get("cluster_confidence_score")
            self.assertIsNotNone(
                confidence,
                f"Cluster {cluster.get('cluster_id')} should have confidence score",
            )
            self.assertGreaterEqual(confidence, 0, "Confidence should be >= 0")
            self.assertLessEqual(confidence, 1, "Confidence should be <= 1")
        print(f"\n✓ All {len(clusters)} clusters have confidence scores")

    def test_avg_cluster_confidence_threshold(self):
        """Test that average cluster confidence meets threshold (> 0.4)."""
        clusters = self.insights.get("clusters", [])
        if not clusters:
            self.skipTest("No clusters to test")

        confidences = [c.get("cluster_confidence_score", 0) for c in clusters]
        avg_confidence = np.mean(confidences)

        self.assertGreater(
            avg_confidence,
            0.4,
            f"Average cluster confidence ({avg_confidence:.3f}) should be > 0.4",
        )
        print(f"\n✓ Average cluster confidence: {avg_confidence:.3f} (threshold: 0.4)")

    def test_embeddings_shape(self):
        """Test that embeddings have correct shape."""
        self.assertIsNotNone(self.processor.embeddings, "Embeddings should be computed")

        num_tickets = len(self.tickets)
        embedding_dim = self.processor.embeddings.shape[1]

        self.assertEqual(
            self.processor.embeddings.shape[0],
            num_tickets,
            "Embedding count should match ticket count",
        )
        self.assertEqual(
            embedding_dim,
            768,
            f"Embedding dimension should be 768 (got {embedding_dim})",
        )
        print(f"\n✓ Embeddings shape: {self.processor.embeddings.shape}")

    def test_hybrid_features_computed(self):
        """Test that hybrid features are computed."""
        self.assertIsNotNone(
            self.processor.hybrid_features, "Hybrid features should be computed"
        )

        num_tickets = len(self.tickets)
        self.assertEqual(
            self.processor.hybrid_features.shape[0],
            num_tickets,
            "Hybrid feature count should match ticket count",
        )
        print(f"\n✓ Hybrid features shape: {self.processor.hybrid_features.shape}")

    def test_pca_applied(self):
        """Test that PCA is applied when enabled."""
        if config.USE_PCA:
            self.assertIsNotNone(
                self.processor.pca, "PCA should be fitted when USE_PCA=True"
            )
            import numpy as np
            from ticket_generator import TicketGenerator

            n_samples = len(TicketGenerator().generate_tickets())
            expected_components = min(config.PCA_COMPONENTS, n_samples)
            self.assertEqual(
                self.processor.pca.n_components,
                expected_components,
                f"PCA components should be {expected_components} (min of config and samples)",
            )
            print(f"\n✓ PCA applied with {self.processor.pca.n_components} components")
        else:
            print(f"\n✓ PCA disabled (USE_PCA=False)")

    def test_tickets_have_clusters(self):
        """Test that all tickets have cluster assignments."""
        clusters = self.insights.get("clusters", [])
        unclustered = self.insights.get("unclustered_tickets", [])

        clustered_ids = set()
        for cluster in clusters:
            for ticket in cluster.get("all_tickets", []):
                clustered_ids.add(ticket.get("id"))

        unclustered_ids = {t.get("id") for t in unclustered}
        all_assigned_ids = clustered_ids | unclustered_ids
        ticket_ids = {t.get("id") for t in self.tickets}

        self.assertEqual(
            all_assigned_ids,
            ticket_ids,
            "All tickets should be assigned to a cluster or unclustered",
        )
        print(f"\n✓ All {len(ticket_ids)} tickets have cluster assignments")

    def test_category_coverage(self):
        """Test that ground truth categories are covered in quality metrics."""
        quality = self.insights.get("quality", {})

        self.assertIn(
            "ground_truth_coverage",
            quality,
            "Quality metrics should include ground_truth_coverage",
        )
        self.assertIn(
            "ground_truth_total",
            quality,
            "Quality metrics should include ground_truth_total",
        )
        self.assertIn(
            "ground_truth_coverage_pct",
            quality,
            "Quality metrics should include ground_truth_coverage_pct",
        )
        print(
            f"\n✓ Ground truth coverage: {quality.get('ground_truth_coverage_pct', 0):.1f}%"
        )


class TestConfigValues(unittest.TestCase):
    """Test that configuration values are reasonable."""

    def test_hybrid_weights_sum_to_one(self):
        """Test that hybrid weights approximately sum to 1."""
        total = (
            config.HYBRID_WEIGHT_TEXT
            + config.HYBRID_WEIGHT_CATEGORY
            + config.HYBRID_WEIGHT_SEVERITY
        )
        self.assertAlmostEqual(
            total, 1.0, places=2, msg=f"Hybrid weights should sum to ~1.0 (got {total})"
        )
        print(f"\n✓ Hybrid weights sum: {total:.2f}")

    def test_text_weight_is_dominant(self):
        """Test that text weight is the largest component."""
        self.assertGreater(
            config.HYBRID_WEIGHT_TEXT,
            config.HYBRID_WEIGHT_CATEGORY,
            "Text weight should be > category weight for semantic priority",
        )
        print(
            f"\n✓ Text weight ({config.HYBRID_WEIGHT_TEXT}) > Category weight ({config.HYBRID_WEIGHT_CATEGORY})"
        )

    def test_hdbscan_params_reasonable(self):
        """Test that HDBSCAN parameters are reasonable."""
        self.assertGreaterEqual(
            config.HDBSCAN_MIN_CLUSTER_SIZE, 2, "min_cluster_size should be >= 2"
        )
        self.assertGreaterEqual(
            config.HDBSCAN_MIN_SAMPLES, 1, "min_samples should be >= 1"
        )
        self.assertGreaterEqual(
            config.HDBSCAN_CLUSTER_SELECTION_EPSILON,
            0,
            "cluster_selection_epsilon should be >= 0",
        )
        print(
            f"\n✓ HDBSCAN params: min_cluster={config.HDBSCAN_MIN_CLUSTER_SIZE}, "
            f"min_samples={config.HDBSCAN_MIN_SAMPLES}, eps={config.HDBSCAN_CLUSTER_SELECTION_EPSILON}"
        )

    def test_pca_components_reasonable(self):
        """Test that PCA components are reasonable."""
        if config.USE_PCA:
            self.assertGreaterEqual(
                config.PCA_COMPONENTS,
                32,
                "PCA components should be >= 32 for meaningful reduction",
            )
            self.assertLessEqual(
                config.PCA_COMPONENTS, 512, "PCA components should be <= 512"
            )
            print(f"\n✓ PCA components: {config.PCA_COMPONENTS}")


class TestDuplicateDetection(unittest.TestCase):
    """Test duplicate detection functionality."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.generator = TicketGenerator()
        cls.tickets = cls.generator.generate_tickets()
        cls.processor = OperationalAIProcessor()
        cls.insights = cls.processor.process_tickets(cls.tickets)

    def test_duplicate_detection_works(self):
        """Test that duplicate detection returns valid results."""
        if not self.tickets:
            self.skipTest("No tickets available")

        test_ticket = self.tickets[0]
        result = self.processor.check_duplicate(
            title=test_ticket["title"],
            description=test_ticket["description"],
            severity=test_ticket["severity"],
            title_only=False,
        )

        self.assertIn("is_duplicate", result)
        self.assertIn("confidence_score", result)
        self.assertIn("matched_cluster_id", result)
        self.assertGreaterEqual(result["confidence_score"], 0)
        self.assertLessEqual(result["confidence_score"], 1)
        print(
            f"\n✓ Duplicate detection works: confidence={result['confidence_score']:.3f}"
        )

    def test_duplicate_detection_high_for_same_ticket(self):
        """Test that duplicate detection has high confidence for exact duplicate."""
        if not self.tickets:
            self.skipTest("No tickets available")

        test_ticket = self.tickets[0]
        result = self.processor.check_duplicate(
            title=test_ticket["title"],
            description=test_ticket["description"],
            severity=test_ticket["severity"],
            title_only=False,
        )

        self.assertTrue(
            result["is_duplicate"], "Same ticket should be detected as duplicate"
        )
        self.assertGreaterEqual(
            result["confidence_score"],
            config.SIMILARITY_THRESHOLD,
            "Confidence should be >= similarity threshold for exact match",
        )
        print(
            f"\n✓ Exact duplicate detected: confidence={result['confidence_score']:.3f}"
        )


def run_tests():
    """Run all tests and print summary."""
    print("=" * 80)
    print("CLUSTERING PIPELINE TESTS")
    print("=" * 80)
    print(f"Configuration:")
    print(f"  USE_HDBSCAN: {config.USE_HDBSCAN}")
    print(f"  USE_PCA: {config.USE_PCA}")
    if hasattr(config, "HDBSCAN_MIN_CLUSTER_SIZE"):
        print(f"  HDBSCAN_MIN_CLUSTER_SIZE: {config.HDBSCAN_MIN_CLUSTER_SIZE}")
    if hasattr(config, "HDBSCAN_MIN_SAMPLES"):
        print(f"  HDBSCAN_MIN_SAMPLES: {config.HDBSCAN_MIN_SAMPLES}")
    if hasattr(config, "HDBSCAN_CLUSTER_SELECTION_EPSILON"):
        print(
            f"  HDBSCAN_CLUSTER_SELECTION_EPSILON: {config.HDBSCAN_CLUSTER_SELECTION_EPSILON}"
        )
    print(f"  HYBRID_WEIGHT_TEXT: {config.HYBRID_WEIGHT_TEXT}")
    print(f"  HYBRID_WEIGHT_CATEGORY: {config.HYBRID_WEIGHT_CATEGORY}")
    print(f"  HYBRID_WEIGHT_SEVERITY: {config.HYBRID_WEIGHT_SEVERITY}")
    if hasattr(config, "PCA_COMPONENTS"):
        print(f"  PCA_COMPONENTS: {config.PCA_COMPONENTS}")
    print("-" * 80)

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestClusteringQuality))
    suite.addTests(loader.loadTestsFromTestCase(TestConfigValues))
    suite.addTests(loader.loadTestsFromTestCase(TestDuplicateDetection))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")

    if result.wasSuccessful():
        print("\n✓ All tests passed!")
        return 0
    else:
        print("\n✗ Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_tests())
