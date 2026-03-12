// Severity color mappings
export const SEVERITY_COLORS = {
  critical: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-amber-100 text-amber-800",
  low: "bg-emerald-100 text-emerald-800",
} as const;

// Priority level styles
export const PRIORITY_STYLES = {
  P1: "bg-red-600 text-white",
  P2: "bg-orange-600 text-white",
  P3: "bg-amber-500 text-white",
  P4: "bg-zinc-500 text-white",
} as const;

// Severity order for sorting
export const SEVERITY_ORDER = {
  critical: 4,
  high: 3,
  medium: 2,
  low: 1,
} as const;

// Priority order for sorting
export const PRIORITY_ORDER = {
  P1: 4,
  P2: 3,
  P3: 2,
  P4: 1,
} as const;

export type Severity = keyof typeof SEVERITY_COLORS;
export type Priority = keyof typeof PRIORITY_STYLES;
