import { X } from "lucide-react";
import { JiraDraft } from "../services/api";

interface JiraModalProps {
  draft: JiraDraft["draft"] | null;
  onClose: () => void;
}

export function JiraModal({ draft, onClose }: JiraModalProps) {
  if (!draft) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-zinc-900/50 backdrop-blur-sm overflow-y-auto">
      <div className="my-8 flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden rounded-xl border border-zinc-200 bg-white shadow-2xl">
        <div className="flex items-center justify-between border-b border-zinc-200 px-6 py-4 shrink-0">
          <h2 className="text-lg font-semibold text-zinc-900">
            Jira draft preview
          </h2>
          <button
            onClick={onClose}
            className="rounded-lg p-2 text-zinc-500 transition-colors hover:bg-zinc-100 hover:text-zinc-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 space-y-5 overflow-y-auto p-6">
          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Summary
            </label>
            <p className="mt-1 font-medium text-zinc-900">{draft.summary}</p>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Priority
              </label>
              <p className="mt-1">
                <span className="inline-flex rounded px-2 py-1 text-sm font-semibold bg-amber-100 text-amber-800">
                  {draft.priority}
                </span>
              </p>
            </div>
            <div>
              <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
                Owner team
              </label>
              <p className="mt-1 text-zinc-900">{draft.owner_team}</p>
            </div>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Impact explanation
            </label>
            <p className="mt-1 text-sm text-zinc-700">
              {draft.impact_explanation}
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Cluster summary
            </label>
            <p className="mt-1 text-sm text-zinc-700">{draft.cluster_summary}</p>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Recommended action
            </label>
            <p className="mt-1 font-medium text-zinc-900">
              {draft.recommended_action}
            </p>
          </div>

          <div>
            <label className="text-xs font-semibold uppercase tracking-wider text-zinc-500">
              Example tickets
            </label>
            <div className="mt-2 space-y-2">
              {draft.example_tickets.map((ticket) => (
                <div
                  key={ticket.id}
                  className="flex items-start justify-between gap-3 rounded-lg bg-zinc-50 p-3"
                >
                  <div>
                    <p className="font-mono text-xs text-zinc-500">{ticket.id}</p>
                    <p className="mt-0.5 text-sm text-zinc-900">{ticket.title}</p>
                  </div>
                  <span
                    className={`shrink-0 rounded px-2 py-1 text-xs font-medium ${
                      ticket.severity === "critical"
                        ? "bg-red-100 text-red-800"
                        : ticket.severity === "high"
                        ? "bg-orange-100 text-orange-800"
                        : "bg-amber-100 text-amber-800"
                    }`}
                  >
                    {ticket.severity}
                  </span>
                </div>
              ))}
            </div>
          </div>

          <div className="flex justify-between border-t border-zinc-200 pt-4 text-sm text-zinc-500">
            <span>{draft.incident_count} incidents</span>
            <span>Impact: {draft.impact_score}</span>
            <span className="capitalize">{draft.urgency_tag}</span>
          </div>
        </div>

        <div className="flex justify-end gap-3 border-t border-zinc-200 bg-zinc-50 px-6 py-4">
          <button
            onClick={onClose}
            className="rounded-lg px-4 py-2 text-sm font-medium text-zinc-700 transition-colors hover:bg-zinc-200"
          >
            Close
          </button>
          <button
            onClick={() =>
              alert("Jira integration not configured. Draft ready for copy.")
            }
            className="rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white transition-colors hover:bg-sky-700"
          >
            Copy to Jira
          </button>
        </div>
      </div>
    </div>
  );
}
