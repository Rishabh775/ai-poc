import { Cluster } from "../services/api";
import {
  SEVERITY_ORDER,
  PRIORITY_ORDER,
  Severity,
  Priority,
} from "../constants/styles";

export type SortOption =
  | "frequency"
  | "severity"
  | "impact"
  | "recurrence"
  | "priority";

export function sortClusters(
  clusters: Cluster[],
  sortBy: SortOption,
): Cluster[] {
  const sorted = [...clusters];

  switch (sortBy) {
    case "frequency":
      sorted.sort((a, b) => b.incident_count - a.incident_count);
      break;

    case "severity": {
      sorted.sort((a, b) => {
        const aMax = Math.max(
          ...Object.keys(a.severity_distribution || {}).map(
            (s) => SEVERITY_ORDER[s as Severity] || 0,
          ),
          0,
        );
        const bMax = Math.max(
          ...Object.keys(b.severity_distribution || {}).map(
            (s) => SEVERITY_ORDER[s as Severity] || 0,
          ),
          0,
        );
        return bMax - aMax;
      });
      break;
    }

    case "impact":
      sorted.sort((a, b) => b.impact_score - a.impact_score);
      break;

    case "recurrence": {
      const recScore = (c: Cluster) =>
        c.recurrence_signal === "recurring"
          ? 3
          : c.recurrence_signal === "spike"
            ? 2
            : 1;
      sorted.sort((a, b) => recScore(b) - recScore(a));
      break;
    }

    case "priority": {
      sorted.sort(
        (a, b) =>
          (PRIORITY_ORDER[(b.priority_level || "P4") as Priority] ?? 0) -
          (PRIORITY_ORDER[(a.priority_level || "P4") as Priority] ?? 0),
      );
      break;
    }

    default:
      break;
  }

  return sorted;
}

export function sortClustersByConfidence(clusters: Cluster[]): Cluster[] {
  return [...clusters].sort(
    (a, b) =>
      (b.cluster_confidence_score || 0) - (a.cluster_confidence_score || 0),
  );
}
