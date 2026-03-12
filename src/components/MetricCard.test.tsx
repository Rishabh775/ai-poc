import { describe, it, expect } from "vitest";
import { render, screen } from "@testing-library/react";
import { Activity } from "lucide-react";
import { MetricCard } from "../components/MetricCard";

describe("MetricCard", () => {
  it("should render standard card with title and value", () => {
    render(<MetricCard title="Total Incidents" value={152} icon={Activity} />);

    expect(screen.getByText(/TOTAL INCIDENTS/i)).toBeInTheDocument();
    expect(screen.getByText("152")).toBeInTheDocument();
  });

  it("should render with trend text", () => {
    render(
      <MetricCard
        title="Incidents"
        value={152}
        icon={Activity}
        trend="↑ 15% vs last week"
      />,
    );

    expect(screen.getByText("↑ 15% vs last week")).toBeInTheDocument();
  });

  it("should render hero variant with gradient background", () => {
    const { container } = render(
      <MetricCard
        title="Critical Issues"
        value={8}
        icon={Activity}
        hero={true}
      />,
    );

    const heroCard = container.querySelector(".bg-gradient-to-br");
    expect(heroCard).toBeInTheDocument();
    expect(heroCard).toHaveClass("from-zinc-900");
    expect(heroCard).toHaveClass("text-white");
  });

  it("should apply custom icon color", () => {
    const { container } = render(
      <MetricCard
        title="High Priority"
        value={24}
        icon={Activity}
        iconColor="text-red-600"
      />,
    );

    const iconContainer = container.querySelector(".text-red-600");
    expect(iconContainer).toBeInTheDocument();
  });

  it("should render icon from lucide-react", () => {
    const { container } = render(
      <MetricCard title="Test" value={42} icon={Activity} />,
    );

    // SVG should be rendered
    const svg = container.querySelector("svg");
    expect(svg).toBeInTheDocument();
  });

  it("should handle string and number values", () => {
    const { rerender } = render(
      <MetricCard title="Test" value="Active" icon={Activity} />,
    );

    expect(screen.getByText("Active")).toBeInTheDocument();

    rerender(<MetricCard title="Test" value={100} icon={Activity} />);

    expect(screen.getByText("100")).toBeInTheDocument();
  });
});
