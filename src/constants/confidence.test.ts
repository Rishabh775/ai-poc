import { describe, it, expect } from "vitest";
import {
  getConfidenceLevel,
  getDuplicateConfidenceLevel,
} from "../constants/confidence";
import {
  SEVERITY_COLORS,
  PRIORITY_STYLES,
  SEVERITY_ORDER,
  PRIORITY_ORDER,
} from "../constants/styles";

describe("Confidence Constants", () => {
  describe("getConfidenceLevel", () => {
    it("should classify high confidence", () => {
      expect(getConfidenceLevel(0.9)).toBe("high");
      expect(getConfidenceLevel(0.7)).toBe("high");
    });

    it("should classify medium confidence", () => {
      expect(getConfidenceLevel(0.6)).toBe("medium");
      expect(getConfidenceLevel(0.4)).toBe("medium");
    });

    it("should classify low confidence", () => {
      expect(getConfidenceLevel(0.3)).toBe("low");
      expect(getConfidenceLevel(0.0)).toBe("low");
    });
  });

  describe("getDuplicateConfidenceLevel", () => {
    it("should classify high duplicate confidence", () => {
      expect(getDuplicateConfidenceLevel(0.95)).toBe("high");
      expect(getDuplicateConfidenceLevel(0.8)).toBe("high");
    });

    it("should classify medium duplicate confidence", () => {
      expect(getDuplicateConfidenceLevel(0.75)).toBe("medium");
      expect(getDuplicateConfidenceLevel(0.6)).toBe("medium");
    });

    it("should classify low duplicate confidence", () => {
      expect(getDuplicateConfidenceLevel(0.5)).toBe("low");
      expect(getDuplicateConfidenceLevel(0.0)).toBe("low");
    });
  });
});

describe("Style Constants", () => {
  describe("SEVERITY_COLORS", () => {
    it("should have all severity levels", () => {
      expect(SEVERITY_COLORS.critical).toBeDefined();
      expect(SEVERITY_COLORS.high).toBeDefined();
      expect(SEVERITY_COLORS.medium).toBeDefined();
      expect(SEVERITY_COLORS.low).toBeDefined();
    });

    it("should have correct color classes", () => {
      expect(SEVERITY_COLORS.critical).toContain("red");
      expect(SEVERITY_COLORS.high).toContain("orange");
      expect(SEVERITY_COLORS.medium).toContain("amber");
      expect(SEVERITY_COLORS.low).toContain("emerald");
    });
  });

  describe("PRIORITY_STYLES", () => {
    it("should have all priority levels", () => {
      expect(PRIORITY_STYLES.P1).toBeDefined();
      expect(PRIORITY_STYLES.P2).toBeDefined();
      expect(PRIORITY_STYLES.P3).toBeDefined();
      expect(PRIORITY_STYLES.P4).toBeDefined();
    });
  });

  describe("SEVERITY_ORDER", () => {
    it("should order severity correctly", () => {
      expect(SEVERITY_ORDER.critical).toBe(4);
      expect(SEVERITY_ORDER.high).toBe(3);
      expect(SEVERITY_ORDER.medium).toBe(2);
      expect(SEVERITY_ORDER.low).toBe(1);
    });
  });

  describe("PRIORITY_ORDER", () => {
    it("should order priority correctly", () => {
      expect(PRIORITY_ORDER.P1).toBe(4);
      expect(PRIORITY_ORDER.P2).toBe(3);
      expect(PRIORITY_ORDER.P3).toBe(2);
      expect(PRIORITY_ORDER.P4).toBe(1);
    });
  });
});
