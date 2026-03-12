import { Lightbulb, TrendingUp, TrendingDown, Minus } from "lucide-react";
import { Metrics, Trends, ChangeTracking } from "../services/api";

interface ExecutiveSummaryProps {
  metrics: Metrics;
  trends: Trends;
  changeTracking?: ChangeTracking;
}

export function ExecutiveSummary({
  metrics,
  trends,
  changeTracking,
}: ExecutiveSummaryProps) {
  const trendDir = changeTracking?.trend_direction ?? trends.trend_direction;

  const TrendIcon = () => {
    if (trendDir === "increasing")
      return <TrendingUp className="h-4 w-4 text-red-600" />;
    if (trendDir === "decreasing")
      return <TrendingDown className="h-4 w-4 text-emerald-600" />;
    return <Minus className="h-4 w-4 text-zinc-500" />;
  };

  const trendColor =
    trendDir === "increasing"
      ? "text-red-600"
      : trendDir === "decreasing"
        ? "text-emerald-600"
        : "text-zinc-600";

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-card">
      <div className="flex items-start gap-4">
        <div className="rounded-lg bg-sky-100 p-2.5">
          <Lightbulb className="h-5 w-5 text-sky-600" strokeWidth={2} />
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="text-base font-semibold text-zinc-900">
            Executive summary
          </h3>
          <p className="mt-2 text-sm leading-relaxed text-zinc-600">
            {metrics.total_incidents} incidents across {metrics.cluster_count}{" "}
            recurring patterns in the past 90 days.{" "}
            <span className="font-medium text-zinc-800">
              {metrics.critical_incidents} critical
            </span>{" "}
            and{" "}
            <span className="font-medium text-zinc-800">
              {metrics.high_priority_incidents} high
            </span>{" "}
            require attention.
          </p>
          <div className="mt-3 flex items-center gap-2 text-sm">
            <TrendIcon />
            <span className={trendColor}>
              Incidents {trendDir} — {trends.recent_7d_count} last 7d vs{" "}
              {trends.previous_7d_count} prior
              {changeTracking && ` (Δ ${changeTracking.delta_percent}%)`}
            </span>
          </div>
          <div className="mt-4 border-t border-zinc-100 pt-4">
            <p className="text-sm font-medium text-zinc-900 mb-2">
              Recommended action:
            </p>
            <p className="text-sm leading-relaxed text-zinc-700">
              {metrics.top_recommended_action ||
                "Monitor and analyze top patterns for continuous improvement."}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
