import {
  CONFIDENCE_THRESHOLDS,
  DUPLICATE_CHECK_THRESHOLDS,
} from "../constants/confidence";

export function getConfidenceColor(score: number): string {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH) return "text-emerald-600";
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return "text-amber-600";
  return "text-red-600";
}

export function getConfidenceBgColor(score: number): string {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH)
    return "bg-emerald-50 border-emerald-200";
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM)
    return "bg-amber-50 border-amber-200";
  return "bg-red-50 border-red-200";
}

export function getConfidenceTextColor(score: number): string {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH) return "text-emerald-700";
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return "text-amber-700";
  return "text-red-700";
}

export function confidenceLevelToBgColor(label: string | undefined): string {
  switch (label) {
    case "high":
      return "bg-emerald-100 text-emerald-700";
    case "medium":
      return "bg-amber-100 text-amber-700";
    case "low":
      return "bg-red-100 text-red-700";
    default:
      return "bg-zinc-100 text-zinc-600";
  }
}

export function getDuplicateConfidenceColor(score: number): string {
  if (score >= DUPLICATE_CHECK_THRESHOLDS.HIGH) return "text-emerald-600";
  if (score >= DUPLICATE_CHECK_THRESHOLDS.MEDIUM) return "text-amber-600";
  return "text-red-600";
}

export function getDuplicateConfidenceBgColor(score: number): string {
  if (score >= DUPLICATE_CHECK_THRESHOLDS.HIGH)
    return "bg-emerald-50 border-emerald-200";
  if (score >= DUPLICATE_CHECK_THRESHOLDS.MEDIUM)
    return "bg-amber-50 border-amber-200";
  return "bg-red-50 border-red-200";
}

// Utility to get confidence stats
export function getConfidenceStats(_clusters: Cluster[], scores: number[]) {
  const getConfidenceLevel = (score: number): "high" | "medium" | "low" => {
    if (score >= CONFIDENCE_THRESHOLDS.HIGH) return "high";
    if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return "medium";
    return "low";
  };

  const high = scores.filter((s) => getConfidenceLevel(s) === "high").length;
  const medium = scores.filter(
    (s) => getConfidenceLevel(s) === "medium",
  ).length;
  const low = scores.filter((s) => getConfidenceLevel(s) === "low").length;

  return { high, medium, low };
}

interface Cluster {
  cluster_confidence_score?: number;
}
