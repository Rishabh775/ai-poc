// Confidence score thresholds
export const CONFIDENCE_THRESHOLDS = {
  HIGH: 0.7,
  MEDIUM: 0.4,
  LOW: 0.0,
} as const;

// Duplicate check thresholds
export const DUPLICATE_CHECK_THRESHOLDS = {
  HIGH: 0.8,
  MEDIUM: 0.6,
  LOW: 0.0,
} as const;

export const getConfidenceLevel = (
  score: number,
): "high" | "medium" | "low" => {
  if (score >= CONFIDENCE_THRESHOLDS.HIGH) return "high";
  if (score >= CONFIDENCE_THRESHOLDS.MEDIUM) return "medium";
  return "low";
};

export const getDuplicateConfidenceLevel = (
  score: number,
): "high" | "medium" | "low" => {
  if (score >= DUPLICATE_CHECK_THRESHOLDS.HIGH) return "high";
  if (score >= DUPLICATE_CHECK_THRESHOLDS.MEDIUM) return "medium";
  return "low";
};
