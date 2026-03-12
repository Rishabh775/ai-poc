import { describe, it, expect } from "vitest";
import {
  getConfidenceColor,
  getConfidenceBgColor,
  getConfidenceTextColor,
  confidenceLevelToBgColor,
  getDuplicateConfidenceColor,
  getDuplicateConfidenceBgColor,
  getConfidenceStats,
} from "../utils/formatting";
import {
  CONFIDENCE_THRESHOLDS,
  DUPLICATE_CHECK_THRESHOLDS,
} from "../constants/confidence";

describe("Formatting Utilities", () => {
  describe("getConfidenceColor", () => {
    it("should return emerald for high confidence", () => {
      expect(getConfidenceColor(0.8)).toBe("text-emerald-600");
      expect(getConfidenceColor(0.9)).toBe("text-emerald-600");
      expect(getConfidenceColor(1.0)).toBe("text-emerald-600");
    });

    it("should return amber for medium confidence", () => {
      expect(getConfidenceColor(0.5)).toBe("text-amber-600");
      expect(getConfidenceColor(0.6)).toBe("text-amber-600");
    });

    it("should return red for low confidence", () => {
      expect(getConfidenceColor(0.2)).toBe("text-red-600");
      expect(getConfidenceColor(0.0)).toBe("text-red-600");
    });
  });

  describe("getConfidenceBgColor", () => {
    it("should return emerald background for high confidence", () => {
      expect(getConfidenceBgColor(0.8)).toBe(
        "bg-emerald-50 border-emerald-200",
      );
      expect(getConfidenceBgColor(0.95)).toBe(
        "bg-emerald-50 border-emerald-200",
      );
    });

    it("should return amber background for medium confidence", () => {
      expect(getConfidenceBgColor(0.5)).toBe("bg-amber-50 border-amber-200");
    });

    it("should return red background for low confidence", () => {
      expect(getConfidenceBgColor(0.3)).toBe("bg-red-50 border-red-200");
      expect(getConfidenceBgColor(0.0)).toBe("bg-red-50 border-red-200");
    });
  });

  describe("getConfidenceTextColor", () => {
    it("should return emerald text for high confidence", () => {
      expect(getConfidenceTextColor(0.8)).toBe("text-emerald-700");
    });

    it("should return amber text for medium confidence", () => {
      expect(getConfidenceTextColor(0.5)).toBe("text-amber-700");
    });

    it("should return red text for low confidence", () => {
      expect(getConfidenceTextColor(0.2)).toBe("text-red-700");
    });
  });

  describe("confidenceLevelToBgColor", () => {
    it("should return emerald for high", () => {
      expect(confidenceLevelToBgColor("high")).toBe(
        "bg-emerald-100 text-emerald-700",
      );
    });

    it("should return amber for medium", () => {
      expect(confidenceLevelToBgColor("medium")).toBe(
        "bg-amber-100 text-amber-700",
      );
    });

    it("should return red for low", () => {
      expect(confidenceLevelToBgColor("low")).toBe("bg-red-100 text-red-700");
    });

    it("should return zinc for unknown", () => {
      expect(confidenceLevelToBgColor("unknown")).toBe(
        "bg-zinc-100 text-zinc-600",
      );
      expect(confidenceLevelToBgColor(undefined)).toBe(
        "bg-zinc-100 text-zinc-600",
      );
    });
  });

  describe("getDuplicateConfidenceColor", () => {
    it("should return emerald for high duplicate confidence", () => {
      expect(getDuplicateConfidenceColor(0.85)).toBe("text-emerald-600");
    });

    it("should return amber for medium duplicate confidence", () => {
      expect(getDuplicateConfidenceColor(0.65)).toBe("text-amber-600");
    });

    it("should return red for low duplicate confidence", () => {
      expect(getDuplicateConfidenceColor(0.5)).toBe("text-red-600");
    });
  });

  describe("getDuplicateConfidenceBgColor", () => {
    it("should return emerald background for high", () => {
      expect(getDuplicateConfidenceBgColor(0.85)).toBe(
        "bg-emerald-50 border-emerald-200",
      );
    });

    it("should return amber background for medium", () => {
      expect(getDuplicateConfidenceBgColor(0.65)).toBe(
        "bg-amber-50 border-amber-200",
      );
    });

    it("should return red background for low", () => {
      expect(getDuplicateConfidenceBgColor(0.5)).toBe(
        "bg-red-50 border-red-200",
      );
    });
  });

  describe("getConfidenceStats", () => {
    it("should count high, medium, and low confidence scores", () => {
      const scores = [0.9, 0.8, 0.6, 0.5, 0.3, 0.2, 0.1];
      const stats = getConfidenceStats([], scores);

      expect(stats.high).toBe(2); // 0.9, 0.8
      expect(stats.medium).toBe(2); // 0.6, 0.5
      expect(stats.low).toBe(3); // 0.3, 0.2, 0.1
    });

    it("should handle empty scores", () => {
      const stats = getConfidenceStats([], []);
      expect(stats.high).toBe(0);
      expect(stats.medium).toBe(0);
      expect(stats.low).toBe(0);
    });

    it("should classify exact threshold values correctly", () => {
      const scores = [CONFIDENCE_THRESHOLDS.HIGH, CONFIDENCE_THRESHOLDS.MEDIUM];
      const stats = getConfidenceStats([], scores);

      expect(stats.high).toBe(1);
      expect(stats.medium).toBe(1);
      expect(stats.low).toBe(0);
    });
  });

  describe("Threshold consistency", () => {
    it("should use correct confidence thresholds", () => {
      expect(CONFIDENCE_THRESHOLDS.HIGH).toBe(0.7);
      expect(CONFIDENCE_THRESHOLDS.MEDIUM).toBe(0.4);
      expect(CONFIDENCE_THRESHOLDS.LOW).toBe(0.0);
    });

    it("should use correct duplicate check thresholds", () => {
      expect(DUPLICATE_CHECK_THRESHOLDS.HIGH).toBe(0.8);
      expect(DUPLICATE_CHECK_THRESHOLDS.MEDIUM).toBe(0.6);
      expect(DUPLICATE_CHECK_THRESHOLDS.LOW).toBe(0.0);
    });
  });
});
