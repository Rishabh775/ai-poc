import { useState } from "react";
import {
  Gauge,
  Info,
  CheckCircle2,
  AlertTriangle,
  XCircle,
  ChevronDown,
  ChevronUp,
} from "lucide-react";
import { Cluster } from "../services/api";
import {
  getConfidenceBgColor,
  getConfidenceTextColor,
  confidenceLevelToBgColor,
} from "../utils/formatting";
import { CONFIDENCE_THRESHOLDS } from "../constants/confidence";
import { sortClustersByConfidence } from "../utils/sorting";

interface ClusterConfidencePanelProps {
  clusters: Cluster[];
  averageConfidence: number;
  onClusterClick?: (cluster: Cluster) => void;
}

export function ClusterConfidencePanel({
  clusters,
  averageConfidence,
  onClusterClick,
}: ClusterConfidencePanelProps) {
  const [showAll, setShowAll] = useState(false);

  const getConfidenceIcon = (score: number) => {
    if (score >= CONFIDENCE_THRESHOLDS.HIGH)
      return <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
    if (score >= CONFIDENCE_THRESHOLDS.MEDIUM)
      return <AlertTriangle className="h-5 w-5 text-amber-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const sortedByConfidence = sortClustersByConfidence(clusters);

  const highConfidence = clusters.filter(
    (c) => (c.cluster_confidence_score || 0) >= CONFIDENCE_THRESHOLDS.HIGH,
  ).length;
  const mediumConfidence = clusters.filter((c) => {
    const score = c.cluster_confidence_score || 0;
    return (
      score >= CONFIDENCE_THRESHOLDS.MEDIUM &&
      score < CONFIDENCE_THRESHOLDS.HIGH
    );
  }).length;
  const lowConfidence = clusters.filter(
    (c) => (c.cluster_confidence_score || 0) < CONFIDENCE_THRESHOLDS.MEDIUM,
  ).length;

  const displayedClusters = showAll
    ? sortedByConfidence
    : sortedByConfidence.slice(0, 5);

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
            Confidence measures how well tickets within a cluster are related to
            each other vs. tickets in other clusters. Higher confidence = better
            semantic grouping.
          </p>
        </div>

        <div className="space-y-2">
          <h3 className="text-sm font-medium text-zinc-700">
            Cluster Confidence Scores
          </h3>
          {displayedClusters.map((cluster) => (
            <div
              key={cluster.cluster_id}
              className={`flex items-center gap-3 rounded-lg border p-3 ${
                onClusterClick
                  ? "cursor-pointer hover:shadow-md transition-shadow"
                  : ""
              } ${getConfidenceBgColor(cluster.cluster_confidence_score || 0)}`}
              onClick={() => onClusterClick?.(cluster)}
            >
              {getConfidenceIcon(cluster.cluster_confidence_score || 0)}
              <div className="min-w-0 flex-1">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-zinc-900">
                    Cluster #{cluster.cluster_id}
                  </span>
                  <span
                    className={`rounded-full px-2 py-0.5 text-xs font-medium ${confidenceLevelToBgColor(cluster.confidence_label)}`}
                  >
                    {cluster.confidence_label || "unknown"}
                  </span>
                </div>
                <p className="mt-0.5 truncate text-xs text-zinc-600">
                  {cluster.incident_count} tickets
                </p>
              </div>
              <div className="text-right">
                <span
                  className={`text-lg font-bold ${getConfidenceTextColor(cluster.cluster_confidence_score || 0)}`}
                >
                  {Math.round((cluster.cluster_confidence_score || 0) * 100)}%
                </span>
              </div>
            </div>
          ))}
        </div>

        {clusters.length > 5 && (
          <button
            onClick={() => setShowAll(!showAll)}
            className="mt-3 flex w-full items-center justify-center gap-1 rounded-lg border border-zinc-200 py-2 text-xs font-medium text-zinc-600 hover:bg-zinc-50 transition-colors"
          >
            {showAll ? (
              <>
                <ChevronUp className="h-4 w-4" />
                Show less
              </>
            ) : (
              <>
                <ChevronDown className="h-4 w-4" />
                Show all {clusters.length} clusters
              </>
            )}
          </button>
        )}
      </div>
    </div>
  );
}
