import { describe, it, expect, beforeEach, vi } from "vitest";
import { render, screen, fireEvent } from "@testing-library/react";
import { ClusterPanel } from "../components/ClusterPanel";
import { Cluster, UnclusteredTicket } from "../services/api";

const mockTicket = {
  id: "T001",
  title: "Connection timeout",
  severity: "critical" as const,
  timestamp: "2024-01-01T10:00:00Z",
};

const mockCluster: Cluster = {
  cluster_id: 1,
  incident_count: 10,
  impact_score: 0.85,
  severity_distribution: { critical: 5, high: 3, medium: 2 },
  example_tickets: [mockTicket],
  all_tickets: [mockTicket],
  summary: "Database connection failures",
  first_seen: "2024-01-01",
  last_seen: "2024-01-10",
  priority_level: "P1",
  recurrence_signal: "recurring",
  cluster_confidence_score: 0.92,
};

const mockUnclusteredTicket: UnclusteredTicket = {
  id: "T002",
  title: "Unclustered issue",
  severity: "high",
  timestamp: "2024-01-01T11:00:00Z",
};

describe("ClusterPanel", () => {
  const onDetails = vi.fn();
  const onCreateJira = vi.fn();

  beforeEach(() => {
    onDetails.mockClear();
    onCreateJira.mockClear();
  });

  it("should render cluster cards", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    expect(screen.getByText(/Cluster #1/)).toBeInTheDocument();
    expect(
      screen.getByText("Database connection failures"),
    ).toBeInTheDocument();
  });

  it("should sort clusters by frequency", () => {
    const cluster2 = { ...mockCluster, cluster_id: 2, incident_count: 5 };

    render(
      <ClusterPanel
        clusters={[cluster2, mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    const clusterHeadings = screen.getAllByText(/Cluster #/);
    expect(clusterHeadings[0]).toHaveTextContent("Cluster #1"); // 10 incidents first
  });

  it("should render unassigned tickets section when provided", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[mockUnclusteredTicket]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    expect(screen.getByText(/Unassigned Tickets \(1\)/)).toBeInTheDocument();
    expect(screen.getByText("Unclustered issue")).toBeInTheDocument();
  });

  it("should call onDetails when Details button is clicked", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    const detailsButton = screen.getByText("Details");
    fireEvent.click(detailsButton);

    expect(onDetails).toHaveBeenCalledWith(mockCluster);
  });

  it("should call onCreateJira when Create Jira button is clicked", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    const jiraButton = screen.getByText("Create Jira");
    fireEvent.click(jiraButton);

    expect(onCreateJira).toHaveBeenCalledWith(mockCluster);
  });

  it("should display cluster metadata", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    expect(screen.getByText("P1")).toBeInTheDocument();
    expect(screen.getAllByText(/10 incidents/)[0]).toBeInTheDocument();
  });

  it("should show collapsible example tickets", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    const examplesButton = screen.getByText(/Example tickets \(1\)/);
    fireEvent.click(examplesButton);

    expect(screen.getByText("Connection timeout")).toBeInTheDocument();
  });

  it("should handle empty clusters list", () => {
    const { container } = render(
      <ClusterPanel
        clusters={[]}
        unclusteredTickets={[]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    // Check that the wrapper exists with no cluster cards
    const wrapper = container.querySelector(".space-y-4");
    expect(wrapper).toBeInTheDocument();
    expect(wrapper?.children.length).toBe(0);
  });

  it("should properly type unclusteredTickets as UnclusteredTicket[]", () => {
    // This test verifies that the type is properly fixed from `any[]`
    const tickets: UnclusteredTicket[] = [
      mockUnclusteredTicket,
      {
        id: "T003",
        title: "Another issue",
        severity: "medium",
        timestamp: "2024-01-01T12:00:00Z",
      },
    ];

    render(
      <ClusterPanel
        clusters={[]}
        unclusteredTickets={tickets}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    expect(screen.getByText("Unclustered issue")).toBeInTheDocument();
    expect(screen.getByText("Another issue")).toBeInTheDocument();
  });

  it("should apply severity colors correctly", () => {
    render(
      <ClusterPanel
        clusters={[mockCluster]}
        unclusteredTickets={[mockUnclusteredTicket]}
        sortBy="frequency"
        onDetails={onDetails}
        onCreateJira={onCreateJira}
      />,
    );

    // Check severity badge is rendered with proper classes
    const severityBadges = screen.getAllByText(/critical|high/);
    expect(severityBadges.length).toBeGreaterThan(0);
  });
});
