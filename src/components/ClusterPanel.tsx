import { useState } from "react";
import {
  AlertCircle,
  ChevronDown,
  ChevronRight,
  Calendar,
  FileEdit,
  ExternalLink,
} from "lucide-react";
import { Cluster, UnclusteredTicket } from "../services/api";
import { SEVERITY_COLORS, PRIORITY_STYLES } from "../constants/styles";
import { sortClusters, SortOption } from "../utils/sorting";

interface ClusterPanelProps {
  clusters: Cluster[];
  unclusteredTickets: UnclusteredTicket[];
  sortBy: SortOption;
  onDetails: (cluster: Cluster) => void;
  onCreateJira: (cluster: Cluster) => void;
}

export function ClusterPanel({
  clusters,
  unclusteredTickets,
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
          onDetails={onDetails}
          onCreateJira={onCreateJira}
        />
      ))}

      {unclusteredTickets.length > 0 && (
        <div className="rounded-lg border-2 border-dashed border-zinc-300 p-4">
          <h3 className="mb-3 text-sm font-semibold text-zinc-700">
            Unassigned Tickets ({unclusteredTickets.length})
          </h3>
          <div className="space-y-2">
            {unclusteredTickets.map((ticket: UnclusteredTicket) => (
              <div
                key={ticket.id}
                className="flex items-start justify-between gap-3 rounded-lg bg-zinc-50 p-3"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-xs text-zinc-500">{ticket.id}</p>
                  <p className="mt-0.5 text-sm text-zinc-800 line-clamp-2">
                    {ticket.title}
                  </p>
                </div>
                <span
                  className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                    SEVERITY_COLORS[
                      ticket.severity as keyof typeof SEVERITY_COLORS
                    ] ?? SEVERITY_COLORS.medium
                  }`}
                >
                  {ticket.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ClusterCard({
  cluster,
  onDetails,
  onCreateJira,
}: {
  cluster: Cluster;
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
              <AlertCircle className="h-5 w-5 text-sky-600" strokeWidth={2} />
            </div>
            <div>
              <div className="flex flex-wrap items-center gap-2">
                <span
                  className={`rounded px-2 py-0.5 text-xs font-semibold ${
                    PRIORITY_STYLES[
                      (cluster.priority_level ||
                        "P3") as keyof typeof PRIORITY_STYLES
                    ] ?? PRIORITY_STYLES.P3
                  }`}
                >
                  {cluster.priority_level || "P3"}
                </span>
                <span className="text-xs text-zinc-500">
                  {cluster.incident_count} incidents
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
                  {new Date(cluster.first_seen).toLocaleDateString()}–
                  {new Date(cluster.last_seen).toLocaleDateString()}
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
                      SEVERITY_COLORS[
                        ticket.severity as keyof typeof SEVERITY_COLORS
                      ] ?? SEVERITY_COLORS.medium
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
