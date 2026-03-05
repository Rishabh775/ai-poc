import { Gauge, Info, CheckCircle2, AlertTriangle, XCircle } from "lucide-react";
import { Cluster } from "../services/api";

interface ClusterConfidencePanelProps {
  clusters: Cluster[];
  averageConfidence: number;
  onClusterClick?: (cluster: Cluster) => void;
}

export function ClusterConfidencePanel({ clusters, averageConfidence, onClusterClick }: ClusterConfidencePanelProps) {
  const getConfidenceIcon = (score: number) => {
    if (score >= 0.7) return <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
    if (score >= 0.4) return <AlertTriangle className="h-5 w-5 text-amber-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.7) return "bg-emerald-50 border-emerald-200";
    if (score >= 0.4) return "bg-amber-50 border-amber-200";
    return "bg-red-50 border-red-200";
  };

  const getConfidenceText = (score: number) => {
    if (score >= 0.7) return "text-emerald-700";
    if (score >= 0.4) return "text-amber-700";
    return "text-red-700";
  };

  const getConfidenceLabel = (label: string | undefined) => {
    switch (label) {
      case "high": return "bg-emerald-100 text-emerald-700";
      case "medium": return "bg-amber-100 text-amber-700";
      case "low": return "bg-red-100 text-red-700";
      default: return "bg-zinc-100 text-zinc-600";
    }
  };

  const sortedByConfidence = [...clusters].sort(
    (a, b) => (b.cluster_confidence_score || 0) - (a.cluster_confidence_score || 0)
  );

  const highConfidence = clusters.filter(c => (c.cluster_confidence_score || 0) >= 0.7).length;
  const mediumConfidence = clusters.filter(c => {
    const score = c.cluster_confidence_score || 0;
    return score >= 0.4 && score < 0.7;
  }).length;
  const lowConfidence = clusters.filter(c => (c.cluster_confidence_score || 0) < 0.4).length;

  return (
    <div className="rounded-xl border border-zinc-200 bg-white shadow-card">
      <div className="border-b border-zinc-100 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-amber-100">
            <Gauge className="h-5 w-5 text-amber-600" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-zinc-900">
              Cluster Confidence
            </h2>
            <p className="text-sm text-zinc-500">
              AI confidence in cluster groupings
            </p>
          </div>
        </div>
      </div>

      <div className="p-5">
        <div className="mb-4 rounded-lg bg-gradient-to-r from-slate-800 to-slate-700 p-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-300">Average Confidence</p>
              <p className="text-3xl font-bold text-white">
                {Math.round(averageConfidence * 100)}%
              </p>
            </div>
            <div className="text-right">
              <Gauge className="mx-auto h-12 w-12 text-sky-400" />
            </div>
          </div>
          <div className="mt-3 flex gap-2">
            <span className="rounded-full bg-emerald-500/20 px-2 py-0.5 text-xs font-medium text-emerald-400">
              {highConfidence} high
            </span>
            <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-xs font-medium text-amber-400">
              {mediumConfidence} medium
            </span>
            <span className="rounded-full bg-red-500/20 px-2 py-0.5 text-xs font-medium text-red-400">
              {lowConfidence} low
            </span>
          </div>
        </div>

        <div className="mb-4 flex items-start gap-2 rounded-lg border border-blue-200 bg-blue-50 p-3">
          <Info className="mt-0.5 h-4 w-4 flex-shrink-0 text-blue-600" />
          <p className="text-xs text-blue-700">
            Confidence measures how well tickets within a cluster are related to each other 
            vs. tickets in other clusters. Higher confidence = better semantic grouping.
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-medium text-zinc-700">Cluster Confidence Scores</h3>
          {sortedByConfidence.slice(0, 5).map((cluster) => (
            <div
              key={cluster.cluster_id}
              className={`flex items-center gap-3 rounded-lg border p-3 ${
                onClusterClick ? "cursor-pointer hover:shadow-md transition-shadow" : ""
              } ${getConfidenceColor(cluster.cluster_confidence_score || 0)}`}
              onClick={() => onClusterClick?.(cluster)}
            >
              {getConfidenceIcon(cluster.cluster_confidence_score || 0)}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-zinc-900">
                    Cluster #{cluster.cluster_id}
                  </span>
                  <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${getConfidenceLabel(cluster.confidence_label)}`}>
                    {cluster.confidence_label || "unknown"}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-xs text-zinc-600">
                  {cluster.incident_count} tickets
                </p>
              </div>
              <div className="text-right">
                <span className={`text-lg font-bold ${getConfidenceText(cluster.cluster_confidence_score || 0)}`}>
                  {Math.round((cluster.cluster_confidence_score || 0) * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {clusters.length > 5 && (
          <p className="mt-3 text-center text-xs text-zinc-500">
            + {clusters.length - 5} more clusters
          </p>
        )}
      </div>
    </div>
  );
}
