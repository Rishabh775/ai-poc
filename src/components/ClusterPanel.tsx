import { useState } from "react";
import {
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Calendar,
  FileEdit,
  ExternalLink,
} from "lucide-react";
import { Cluster } from "../services/api";

interface ClusterPanelProps {
  clusters: Cluster[];
  sortBy: "frequency" | "severity" | "impact" | "recurrence" | "priority";
  onDetails: (cluster: Cluster) => void;
  onCreateJira: (cluster: Cluster) => void;
}

const severityColors: Record<string, string> = {
  critical: "bg-red-100 text-red-800",
  high: "bg-orange-100 text-orange-800",
  medium: "bg-amber-100 text-amber-800",
  low: "bg-emerald-100 text-emerald-800",
};

const priorityStyles: Record<string, string> = {
  P1: "bg-red-600 text-white",
  P2: "bg-orange-600 text-white",
  P3: "bg-amber-500 text-white",
  P4: "bg-zinc-500 text-white",
};

function sortClusters(
  clusters: Cluster[],
  sortBy: ClusterPanelProps["sortBy"]
): Cluster[] {
  const sorted = [...clusters];
  switch (sortBy) {
    case "frequency":
      sorted.sort((a, b) => b.incident_count - a.incident_count);
      break;
    case "severity": {
      const sevOrder = { critical: 4, high: 3, medium: 2, low: 1 };
      sorted.sort((a, b) => {
        const aMax = Math.max(
          ...Object.keys(a.severity_distribution || {}).map(
            (s) => sevOrder[s as keyof typeof sevOrder] || 0
          ),
          0
        );
        const bMax = Math.max(
          ...Object.keys(b.severity_distribution || {}).map(
            (s) => sevOrder[s as keyof typeof sevOrder] || 0
          ),
          0
        );
        return bMax - aMax;
      });
      break;
    }
    case "impact":
      sorted.sort((a, b) => b.impact_score - a.impact_score);
      break;
    case "recurrence": {
      const recScore = (c: Cluster) =>
        c.recurrence_signal === "recurring"
          ? 3
          : c.recurrence_signal === "spike"
          ? 2
          : 1;
      sorted.sort((a, b) => recScore(b) - recScore(a));
      break;
    }
    case "priority": {
      const pOrder = { P1: 4, P2: 3, P3: 2, P4: 1 };
      sorted.sort(
        (a, b) =>
          (pOrder[(b.priority_level || "P4") as keyof typeof pOrder] ?? 0) -
          (pOrder[(a.priority_level || "P4") as keyof typeof pOrder] ?? 0)
      );
      break;
    }
    default:
      break;
  }
  return sorted;
}

export function ClusterPanel({
  clusters,
  sortBy,
  onDetails,
  onCreateJira,
}: ClusterPanelProps) {
  const displayed = sortClusters(clusters, sortBy);

  return (
    <div className="space-y-4">
      {displayed.map((cluster) => (
        <ClusterCard
          key={cluster.cluster_id}
          cluster={cluster}
          severityColors={severityColors}
          priorityStyles={priorityStyles}
          onDetails={onDetails}
          onCreateJira={onCreateJira}
        />
      ))}
    </div>
  );
}

function ClusterCard({
  cluster,
  severityColors,
  priorityStyles,
  onDetails,
  onCreateJira,
}: {
  cluster: Cluster;
  severityColors: Record<string, string>;
  priorityStyles: Record<string, string>;
  onDetails: (c: Cluster) => void;
  onCreateJira: (c: Cluster) => void;
}) {
  const [showExamples, setShowExamples] = useState(false);

  return (
    <div className="rounded-xl border border-zinc-200 bg-white shadow-card transition-shadow hover:shadow-card-hover">
      <div className="p-5">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div className="flex gap-4">
            <div className="rounded-lg bg-sky-100 p-2">
              <AlertCircle
                className="h-5 w-5 text-sky-600"
                strokeWidth={2}
              />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs font-semibold ${
                    priorityStyles[cluster.priority_level || "P3"] ??
                    priorityStyles.P3
                  }`}
                >
                  {cluster.priority_level || "P3"}
                </span>
                <span className="text-xs text-zinc-500">
                  {cluster.owner_team || "Platform Team"}
                </span>
                <span className="rounded bg-zinc-100 px-2 py-0.5 text-xs text-zinc-600">
                  {cluster.workflow_type.replace(/_/g, " ")}
                </span>
              </div>
              <h4 className="mt-2 font-semibold text-zinc-900">
                Cluster #{cluster.cluster_id}
              </h4>
              <p className="mt-1 text-sm leading-relaxed text-zinc-600">
                {cluster.summary}
              </p>
              {cluster.recommended_action && (
                <p className="mt-2 text-sm font-medium text-sky-700">
                  → {cluster.recommended_action}
                </p>
              )}
              <div className="mt-3 flex flex-wrap items-center gap-3 text-xs text-zinc-500">
                <span>{cluster.incident_count} incidents</span>
                <span className="flex items-center gap-1">
                  <Calendar className="h-3.5 w-3.5" />
                  {new Date(cluster.first_seen).toLocaleDateString()}–{new Date(cluster.last_seen).toLocaleDateString()}
                </span>
                {cluster.risk_score != null && (
                  <span>Risk {cluster.risk_score}</span>
                )}
                <span className="font-medium text-zinc-700">
                  Impact {cluster.impact_score}
                </span>
              </div>
            </div>
          </div>
          <div className="flex shrink-0 gap-2 sm:flex-col">
            <button
              onClick={() => onDetails(cluster)}
              className="inline-flex items-center justify-center gap-1.5 rounded-lg border border-zinc-300 bg-white px-3 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-50"
            >
              <FileEdit className="h-4 w-4" />
              Details
            </button>
            <button
              onClick={() => onCreateJira(cluster)}
              className="inline-flex items-center justify-center gap-1.5 rounded-lg bg-sky-600 px-3 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-700"
            >
              <ExternalLink className="h-4 w-4" />
              Create Jira
            </button>
          </div>
        </div>

        {/* Collapsible examples */}
        <div className="mt-4 border-t border-zinc-100 pt-4">
          <button
            onClick={() => setShowExamples(!showExamples)}
            className="flex items-center gap-1 text-xs font-medium text-zinc-600 hover:text-zinc-900"
          >
            {showExamples ? (
              <ChevronDown className="h-4 w-4" />
            ) : (
              <ChevronRight className="h-4 w-4" />
            )}
            Example tickets ({cluster.example_tickets.length})
          </button>
          {showExamples && (
            <div className="mt-3 space-y-2">
              {cluster.example_tickets.slice(0, 3).map((ticket) => (
                <div
                  key={ticket.id}
                  className="flex items-start justify-between gap-3 rounded-lg bg-zinc-50 p-3"
                >
                  <div className="min-w-0 flex-1">
                    <p className="font-mono text-xs text-zinc-500">
                      {ticket.id}
                    </p>
                    <p className="mt-0.5 text-sm text-zinc-800 line-clamp-2">
                      {ticket.title}
                    </p>
                  </div>
                  <span
                    className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                      severityColors[ticket.severity] ?? severityColors.medium
                    }`}
                  >
                    {ticket.severity}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
