import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { ExecutiveSummary } from "../components/ExecutiveSummary";
import { Metrics, Trends, ChangeTracking } from "../services/api";

const mockMetrics: Metrics = {
  total_incidents: 152,
  cluster_count: 8,
  critical_incidents: 5,
  high_priority_incidents: 12,
  top_issue: "Database connection failures",
  top_recommended_action: "Review database connection pool settings",
  risk_score: 0.75,
  stability_index: 0.6,
  trend_direction: "increasing",
  top_recurring_issue: "Timeout errors",
  average_cluster_confidence: 0.78,
};

const mockTrends: Trends = {
  daily_incidents: [],
  severity_over_time: [],
  trend_direction: "increasing",
  recent_7d_count: 45,
  previous_7d_count: 35,
};

const mockChangeTracking: ChangeTracking = {
  trend_direction: "increasing",
  delta_percent: 28.6,
  new_clusters: 1,
  resolved_clusters: 0,
  stability_index: 0.6,
  cluster_changes: [],
};

describe("ExecutiveSummary", () => {
  it("should render executive summary section", () => {
    render(<ExecutiveSummary metrics={mockMetrics} trends={mockTrends} />);

    expect(screen.getByText("Executive summary")).toBeInTheDocument();
  });

  it("should display total incidents and cluster count", () => {
    render(<ExecutiveSummary metrics={mockMetrics} trends={mockTrends} />);

    expect(screen.getByText(/152 incidents/)).toBeInTheDocument();
    expect(screen.getByText(/8[\s\S]*recurring patterns/)).toBeInTheDocument();
  });

  it("should display critical and high priority incidents", () => {
    render(<ExecutiveSummary metrics={mockMetrics} trends={mockTrends} />);

    expect(screen.getByText("5 critical")).toBeInTheDocument();
    expect(screen.getByText("12 high")).toBeInTheDocument();
  });

  it("should show trend information", () => {
    render(<ExecutiveSummary metrics={mockMetrics} trends={mockTrends} />);

    expect(screen.getByText(/Incidents increasing/)).toBeInTheDocument();
    expect(screen.getByText(/45 last 7d vs 35 prior/)).toBeInTheDocument();
  });

  it("should display change tracking delta when provided", () => {
    render(
      <ExecutiveSummary
        metrics={mockMetrics}
        trends={mockTrends}
        changeTracking={mockChangeTracking}
      />,
    );

    expect(screen.getByText(/Δ 28.6%/)).toBeInTheDocument();
  });

  it("should display recommended action", () => {
    render(<ExecutiveSummary metrics={mockMetrics} trends={mockTrends} />);

    expect(
      screen.getByText("Review database connection pool settings"),
    ).toBeInTheDocument();
  });

  it("should show default recommended action if not provided", () => {
    const metricsWithoutAction = {
      ...mockMetrics,
      top_recommended_action: undefined,
    };

    render(
      <ExecutiveSummary metrics={metricsWithoutAction} trends={mockTrends} />,
    );

    expect(
      screen.getByText(/Monitor and analyze top patterns/),
    ).toBeInTheDocument();
  });

  it("should display decreasing trend with proper styling", () => {
    const decreasingTrends = { ...mockTrends, trend_direction: "decreasing" };

    render(
      <ExecutiveSummary metrics={mockMetrics} trends={decreasingTrends} />,
    );

    expect(screen.getByText(/Incidents decreasing/)).toBeInTheDocument();
  });

  it("should display stable trend", () => {
    const stableTrends = { ...mockTrends, trend_direction: "stable" };

    render(<ExecutiveSummary metrics={mockMetrics} trends={stableTrends} />);

    expect(screen.getByText(/Incidents stable/)).toBeInTheDocument();
  });
});
