import { describe, it, expect } from "vitest";
import { sortClusters, sortClustersByConfidence } from "../utils/sorting";
import { Cluster } from "../services/api";

const mockClusters: Cluster[] = [
  {
    cluster_id: 1,
    incident_count: 10,
    impact_score: 0.8,
    severity_distribution: { critical: 5, high: 3, medium: 2 },
    example_tickets: [],
    all_tickets: [],
    summary: "Test cluster 1",
    first_seen: "2024-01-01",
    last_seen: "2024-01-10",
    priority_level: "P1",
    recurrence_signal: "recurring",
    cluster_confidence_score: 0.9,
  },
  {
    cluster_id: 2,
    incident_count: 5,
    impact_score: 0.5,
    severity_distribution: { high: 3, medium: 2 },
    example_tickets: [],
    all_tickets: [],
    summary: "Test cluster 2",
    first_seen: "2024-01-02",
    last_seen: "2024-01-09",
    priority_level: "P3",
    recurrence_signal: "stable",
    cluster_confidence_score: 0.4,
  },
  {
    cluster_id: 3,
    incident_count: 20,
    impact_score: 0.6,
    severity_distribution: { medium: 15, low: 5 },
    example_tickets: [],
    all_tickets: [],
    summary: "Test cluster 3",
    first_seen: "2024-01-01",
    last_seen: "2024-01-15",
    priority_level: "P2",
    recurrence_signal: "spike",
    cluster_confidence_score: 0.7,
  },
];

describe("Sorting Utilities", () => {
  describe("sortClusters", () => {
    it("should sort by frequency", () => {
      const sorted = sortClusters(mockClusters, "frequency");
      expect(sorted[0].cluster_id).toBe(3); // 20 incidents
      expect(sorted[1].cluster_id).toBe(1); // 10 incidents
      expect(sorted[2].cluster_id).toBe(2); // 5 incidents
    });

    it("should sort by impact", () => {
      const sorted = sortClusters(mockClusters, "impact");
      expect(sorted[0].cluster_id).toBe(1); // 0.8 impact
      expect(sorted[1].cluster_id).toBe(3); // 0.6 impact
      expect(sorted[2].cluster_id).toBe(2); // 0.5 impact
    });

    it("should sort by priority", () => {
      const sorted = sortClusters(mockClusters, "priority");
      expect(sorted[0].cluster_id).toBe(1); // P1
      expect(sorted[1].cluster_id).toBe(3); // P2
      expect(sorted[2].cluster_id).toBe(2); // P3
    });

    it("should sort by recurrence", () => {
      const sorted = sortClusters(mockClusters, "recurrence");
      expect(sorted[0].cluster_id).toBe(1); // recurring
      expect(sorted[1].cluster_id).toBe(3); // spike
      expect(sorted[2].cluster_id).toBe(2); // stable
    });

    it("should sort by severity (max severity in cluster)", () => {
      const sorted = sortClusters(mockClusters, "severity");
      expect(sorted[0].cluster_id).toBe(1); // has critical (max severity)
      expect(sorted[1].cluster_id).toBe(2); // has high (second max)
      expect(sorted[2].cluster_id).toBe(3); // max is medium
    });

    it("should not mutate original array", () => {
      const original = [...mockClusters];
      sortClusters(mockClusters, "frequency");
      expect(mockClusters).toEqual(original);
    });
  });

  describe("sortClustersByConfidence", () => {
    it("should sort by confidence score descending", () => {
      const sorted = sortClustersByConfidence(mockClusters);
      expect(sorted[0].cluster_confidence_score).toBe(0.9);
      expect(sorted[1].cluster_confidence_score).toBe(0.7);
      expect(sorted[2].cluster_confidence_score).toBe(0.4);
    });

    it("should not mutate original array", () => {
      const original = [...mockClusters];
      sortClustersByConfidence(mockClusters);
      expect(mockClusters).toEqual(original);
    });

    it("should handle missing confidence scores", () => {
      const clustersWithoutConfidence = [
        { ...mockClusters[0], cluster_confidence_score: undefined },
        mockClusters[1],
      ];
      const sorted = sortClustersByConfidence(clustersWithoutConfidence);
      expect(sorted[0].cluster_id).toBe(2); // 0.4 score
      expect(sorted[1].cluster_id).toBe(1); // undefined = 0
    });
  });
});
