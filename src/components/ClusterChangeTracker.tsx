import { TrendingUp, TrendingDown, Minus, AlertCircle, CheckCircle2, Sparkles } from "lucide-react";
import { ClusterChange } from "../services/api";

interface ClusterChangeTrackerProps {
  clusterChanges: ClusterChange[];
  clusters: Array<{
    cluster_id: number;
    summary: string;
    priority_level?: string;
  }>;
  onClusterClick?: (clusterId: number) => void;
}

export function ClusterChangeTracker({ clusterChanges, clusters, onClusterClick }: ClusterChangeTrackerProps) {
  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case "new":
        return <Sparkles className="h-4 w-4 text-sky-600" />;
      case "increasing":
        return <TrendingUp className="h-4 w-4 text-red-600" />;
      case "decreasing":
        return <TrendingDown className="h-4 w-4 text-emerald-600" />;
      case "resolved":
        return <CheckCircle2 className="h-4 w-4 text-emerald-600" />;
      default:
        return <Minus className="h-4 w-4 text-zinc-400" />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case "new":
        return "bg-sky-50 border-sky-200";
      case "increasing":
        return "bg-red-50 border-red-200";
      case "decreasing":
        return "bg-emerald-50 border-emerald-200";
      case "resolved":
        return "bg-emerald-50 border-emerald-200";
      default:
        return "bg-zinc-50 border-zinc-200";
    }
  };

  const getTrendBadge = (trend: string) => {
    switch (trend) {
      case "new":
        return "bg-sky-100 text-sky-700";
      case "increasing":
        return "bg-red-100 text-red-700";
      case "decreasing":
        return "bg-emerald-100 text-emerald-700";
      case "resolved":
        return "bg-emerald-100 text-emerald-700";
      default:
        return "bg-zinc-100 text-zinc-600";
    }
  };

  const getClusterInfo = (clusterId: number) => {
    return clusters.find(c => c.cluster_id === clusterId);
  };

  const sortedChanges = [...clusterChanges].sort((a, b) => {
    const priority = { new: 0, increasing: 1, decreasing: 2, stable: 3, resolved: 4 };
    return priority[a.trend] - priority[b.trend];
  });

  const newClusters = clusterChanges.filter(c => c.trend === "new");
  const increasingClusters = clusterChanges.filter(c => c.trend === "increasing");
  const decreasingClusters = clusterChanges.filter(c => c.trend === "decreasing");

  return (
    <div className="rounded-xl border border-zinc-200 bg-white shadow-card">
      <div className="border-b border-zinc-100 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-violet-100">
            <TrendingUp className="h-5 w-5 text-violet-600" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-zinc-900">
              Cluster Change Tracker
            </h2>
            <p className="text-sm text-zinc-500">
              Last 7 days vs previous 7 days
            </p>
          </div>
        </div>
      </div>

      <div className="p-5">
        <div className="mb-4 grid grid-cols-3 gap-3">
          <div className="rounded-lg bg-sky-50 p-3 text-center">
            <div className="text-2xl font-bold text-sky-600">{newClusters.length}</div>
            <div className="text-xs font-medium text-sky-700">New</div>
          </div>
          <div className="rounded-lg bg-red-50 p-3 text-center">
            <div className="text-2xl font-bold text-red-600">{increasingClusters.length}</div>
            <div className="text-xs font-medium text-red-700">Increasing</div>
          </div>
          <div className="rounded-lg bg-emerald-50 p-3 text-center">
            <div className="text-2xl font-bold text-emerald-600">{decreasingClusters.length}</div>
            <div className="text-xs font-medium text-emerald-700">Decreasing</div>
          </div>
        </div>

        {clusterChanges.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-8 text-center">
            <AlertCircle className="mb-2 h-8 w-8 text-zinc-400" />
            <p className="text-sm text-zinc-500">No cluster change data available</p>
          </div>
        ) : (
          <div className="space-y-2">
            {sortedChanges.slice(0, 6).map((change) => {
              const clusterInfo = getClusterInfo(change.cluster_id);
              return (
                <div
                  key={change.cluster_id}
                  className={`flex items-center gap-3 rounded-lg border p-3 ${getTrendColor(change.trend)} ${
                    onClusterClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""
                  }`}
                  onClick={() => onClusterClick?.(change.cluster_id)}
                >
                  {getTrendIcon(change.trend)}
                  <div className="min-w-0 flex-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-zinc-900">
                        Cluster #{change.cluster_id}
                      </span>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getTrendBadge(change.trend)}`}>
                        {change.trend}
                      </span>
                    </div>
                    {clusterInfo && (
                      <p className="mt-0.5 truncate text-xs text-zinc-600">
                        {clusterInfo.priority_level}
                      </p>
                    )}
                  </div>
                  <div className="text-right">
                    <div className="text-sm font-semibold text-zinc-900">
                      {change.recent_7d_count}
                    </div>
                    <div className="text-xs text-zinc-500">
                      was {change.previous_7d_count}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {clusterChanges.length > 6 && (
          <p className="mt-3 text-center text-xs text-zinc-500">
            + {clusterChanges.length - 6} more clusters
          </p>
        )}
      </div>
    </div>
  );
}
