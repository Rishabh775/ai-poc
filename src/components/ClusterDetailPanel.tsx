import {
  X,
  Calendar,
  AlertTriangle,
  Target,
  TrendingUp,
  Users,
  Gauge,
  Tag,
} from "lucide-react";
import { Cluster } from "../services/api";

interface ClusterDetailPanelProps {
  cluster: Cluster;
  onClose: () => void;
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

export function ClusterDetailPanel({ cluster, onClose }: ClusterDetailPanelProps) {
  const severityEntries = Object.entries(cluster.severity_distribution || {});
  const priority = cluster.priority_level || "P3";

  return (
    <div className="absolute right-0 top-0 min-h-screen w-full max-w-lg flex-col border-l border-zinc-200 bg-white shadow-xl">
      <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 shrink-0">
        <h2 className="text-lg font-semibold text-zinc-900">
          Cluster #{cluster.cluster_id}
        </h2>
        <button
          onClick={onClose}
          className="rounded-lg p-2 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700"
        >
          <X className="h-5 w-5" />
        </button>
      </div>

      <div className="flex-1 space-y-6 overflow-y-auto p-6">
        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`rounded px-2.5 py-1 text-sm font-semibold ${
              priorityStyles[priority] ?? priorityStyles.P3
            }`}
          >
            {priority}
          </span>
          <span className="text-sm capitalize text-zinc-600">
            {cluster.urgency_tag || "elevated"}
          </span>
          <span className="text-sm text-zinc-600">
            {cluster.owner_team || "Platform Team"}
          </span>
        </div>

        <div>
          <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            <AlertTriangle className="h-4 w-4" />
            Summary
          </h3>
          <p className="text-sm leading-relaxed text-zinc-900">
            {cluster.summary}
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-lg bg-zinc-50 p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
              Incidents
            </p>
            <p className="mt-1 text-2xl font-bold text-zinc-900">
              {cluster.incident_count}
            </p>
          </div>
          <div className="rounded-lg bg-zinc-50 p-4">
            <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
              Impact score
            </p>
            <p className="mt-1 text-2xl font-bold text-zinc-900">
              {cluster.impact_score}
            </p>
          </div>
          {cluster.risk_score != null && (
            <div className="col-span-2 rounded-lg bg-zinc-50 p-4">
              <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
                Risk score
              </p>
              <p className="mt-1 text-2xl font-bold text-zinc-900">
                {cluster.risk_score}
              </p>
            </div>
          )}
          
          {cluster.cluster_confidence_score != null && (
            <div className="col-span-2 rounded-lg bg-amber-50 p-4 border border-amber-200">
              <div className="flex items-center justify-between">
                <p className="text-xs font-medium uppercase tracking-wider text-amber-700">
                  <Gauge className="mr-1 inline h-3 w-3" />
                  AI Confidence
                </p>
                <span className={`text-lg font-bold ${
                  cluster.cluster_confidence_score >= 0.7 ? 'text-emerald-600' :
                  cluster.cluster_confidence_score >= 0.4 ? 'text-amber-600' : 'text-red-600'
                }`}>
                  {Math.round(cluster.cluster_confidence_score * 100)}%
                </span>
              </div>
              <p className="mt-1 text-xs text-amber-600">
                {cluster.cluster_confidence_score >= 0.7 ? 'High confidence - tickets are well grouped' :
                 cluster.cluster_confidence_score >= 0.4 ? 'Medium confidence - some variation in tickets' :
                 'Low confidence - tickets may need reclassification'}
              </p>
            </div>
          )}
        </div>

        <div>
          <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            <Calendar className="h-4 w-4" />
            Timeline
          </h3>
          <p className="text-sm text-zinc-700">
            {new Date(cluster.first_seen).toLocaleDateString(undefined, {
              dateStyle: "medium",
            })}{" "}
            –{" "}
            {new Date(cluster.last_seen).toLocaleDateString(undefined, {
              dateStyle: "medium",
            })}
          </p>
        </div>

        <div>
          <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            Severity distribution
          </h3>
          <div className="flex flex-wrap gap-2">
            {severityEntries.map(([sev, count]) => (
              <span
                key={sev}
                className={`rounded px-2 py-1 text-sm font-medium ${
                  severityColors[sev] ?? severityColors.medium
                }`}
              >
                {sev}: {count}
              </span>
            ))}
          </div>
        </div>

        {cluster.business_impact && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
              <Target className="h-4 w-4" />
              Business impact
            </h3>
            <p className="text-sm text-zinc-700">{cluster.business_impact}</p>
          </div>
        )}

        {cluster.recommended_action && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
              <TrendingUp className="h-4 w-4" />
              Recommended action
            </h3>
            <p className="font-medium text-zinc-900">
              {cluster.recommended_action}
            </p>
          </div>
        )}

        {cluster.recurrence_signal && (
          <div>
            <h3 className="mb-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Recurrence
            </h3>
            <p className="capitalize text-zinc-700">
              {cluster.recurrence_signal}
            </p>
          </div>
        )}

        {cluster.top_keywords && cluster.top_keywords.length > 0 && (
          <div>
            <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
              <Tag className="h-4 w-4" />
              Top Keywords
            </h3>
            <div className="flex flex-wrap gap-1.5">
              {cluster.top_keywords.map((keyword, idx) => (
                <span
                  key={idx}
                  className="rounded-full bg-sky-50 border border-sky-200 px-2.5 py-1 text-xs font-medium text-sky-700"
                >
                  {keyword}
                </span>
              ))}
            </div>
          </div>
        )}

        <div>
          <h3 className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-wider text-zinc-500">
            <Users className="h-4 w-4" />
            Example tickets
          </h3>
          <div className="space-y-2">
            {cluster.example_tickets.map((ticket) => (
              <div
                key={ticket.id}
                className="flex items-start justify-between gap-3 rounded-lg bg-zinc-50 p-3"
              >
                <div className="min-w-0 flex-1">
                  <p className="font-mono text-xs text-zinc-500">{ticket.id}</p>
                  <p className="mt-0.5 text-sm text-zinc-900 line-clamp-2">
                    {ticket.title}
                  </p>
                  <p className="mt-1 text-xs text-zinc-500">
                    {new Date(ticket.timestamp).toLocaleDateString()}
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
        </div>
      </div>
    </div>
  );
}
