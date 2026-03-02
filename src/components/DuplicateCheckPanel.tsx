import { useState, useEffect } from "react";
import { Search, CheckCircle, XCircle, AlertTriangle, Loader2 } from "lucide-react";
import { api, DuplicateCheckResponse } from "../services/api";

interface DuplicateCheckPanelProps {
  onClusterClick?: (clusterId: number) => void;
}

interface TicketSuggestion {
  id: string;
  title: string;
  severity: string;
  workflow_type: string;
}

export function DuplicateCheckPanel({ onClusterClick }: DuplicateCheckPanelProps) {
  const [title, setTitle] = useState("");
  const [result, setResult] = useState<DuplicateCheckResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [suggestions, setSuggestions] = useState<TicketSuggestion[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);

  useEffect(() => {
    if (title.length < 2) {
      setSuggestions([]);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        const response = await api.searchTickets(title);
        setSuggestions(response.tickets);
        setShowSuggestions(true);
      } catch (err) {
        // Silent fail
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [title]);

  useEffect(() => {
    if (title.length < 3) {
      setResult(null);
      return;
    }

    const timer = setTimeout(async () => {
      setChecking(true);
      try {
        const response = await api.checkDuplicate({
          title: title,
          title_only: true,
        });
        setResult(response);
      } catch (err) {
        // Silent fail
      } finally {
        setChecking(false);
      }
    }, 500);

    return () => clearTimeout(timer);
  }, [title]);

  const handleSelectSuggestion = (ticket: TicketSuggestion) => {
    setTitle(ticket.title);
    setShowSuggestions(false);
    setSuggestions([]);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!title.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await api.checkDuplicate({
        title: title,
        title_only: true,
      });
      setResult(response);
    } catch (err) {
      setError("Failed to check. Make sure backend is running.");
    } finally {
      setLoading(false);
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 0.80) return "text-emerald-600";
    if (score >= 0.60) return "text-amber-600";
    return "text-red-600";
  };

  const getConfidenceBg = (score: number) => {
    if (score >= 0.80) return "bg-emerald-50 border-emerald-200";
    if (score >= 0.60) return "bg-amber-50 border-amber-200";
    return "bg-red-50 border-red-200";
  };

  return (
    <div className="rounded-xl border border-zinc-200 bg-white shadow-card">
      <div className="border-b border-zinc-100 px-5 py-4">
        <div className="flex items-center gap-3">
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-sky-100">
            <Search className="h-5 w-5 text-sky-600" />
          </div>
          <div>
            <h2 className="text-base font-semibold text-zinc-900">
              Check Duplicate
            </h2>
            <p className="text-sm text-zinc-500">
              Find similar existing tickets
            </p>
          </div>
        </div>
      </div>

      <form onSubmit={handleSubmit} className="p-5">
        <div className="space-y-4">
          <div>
            <label className="mb-1.5 block text-sm font-medium text-zinc-700">
              Ticket Title
            </label>
            <div className="relative">
              <input
                type="text"
                value={title}
                onChange={(e) => setTitle(e.target.value)}
                onFocus={() => suggestions.length > 0 && setShowSuggestions(true)}
                onBlur={() => setTimeout(() => setShowSuggestions(false), 200)}
                placeholder="e.g., Reviewer status not updating"
                className="w-full rounded-lg border border-zinc-300 px-3 py-2.5 text-sm shadow-card focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
              />
              {checking && (
                <div className="absolute right-3 top-1/2 -translate-y-1/2">
                  <Loader2 className="h-4 w-4 animate-spin text-sky-600" />
                </div>
              )}
              {showSuggestions && suggestions.length > 0 && (
                <div className="absolute z-10 mt-1 w-full rounded-lg border border-zinc-200 bg-white shadow-lg">
                  {suggestions.map((ticket) => (
                    <button
                      key={ticket.id}
                      type="button"
                      onClick={() => handleSelectSuggestion(ticket)}
                      className="w-full px-3 py-2 text-left hover:bg-sky-50"
                    >
                      <div className="flex items-center gap-2">
                        <span className="font-mono text-xs text-zinc-500">{ticket.id}</span>
                        <span className={`rounded px-1.5 py-0.5 text-xs ${
                          ticket.severity === "critical" ? "bg-red-100 text-red-700" :
                          ticket.severity === "high" ? "bg-orange-100 text-orange-700" :
                          "bg-zinc-100 text-zinc-600"
                        }`}>
                          {ticket.severity}
                        </span>
                      </div>
                      <p className="mt-1 truncate text-sm text-zinc-700">{ticket.title}</p>
                    </button>
                  ))}
                </div>
              )}
            </div>
          </div>

          <p className="text-xs text-zinc-500">
            Searches by title only - you don't need to know the workflow type or severity
          </p>

          <button
            type="submit"
            disabled={loading || !title.trim()}
            className="flex w-full items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-2.5 text-sm font-medium text-white shadow-card hover:bg-sky-700 disabled:opacity-50"
          >
            {loading ? (
              <>
                <Loader2 className="h-4 w-4 animate-spin" />
                Checking...
              </>
            ) : (
              <>
                <Search className="h-4 w-4" />
                Check for Duplicates
              </>
            )}
          </button>
        </div>
      </form>

      {error && (
        <div className="mx-5 mb-5 rounded-lg border border-red-200 bg-red-50 p-4">
          <div className="flex items-center gap-2 text-red-700">
            <AlertTriangle className="h-4 w-4" />
            <p className="text-sm">{error}</p>
          </div>
        </div>
      )}

      {result && (
        <div className="border-t border-zinc-100 p-5 pt-0">
          <div className={`mt-4 rounded-lg border p-4 ${getConfidenceBg(result.confidence_score)}`}>
            <div className="flex items-start gap-3">
              {result.is_duplicate ? (
                <CheckCircle className="h-5 w-5 text-emerald-600" />
              ) : (
                <XCircle className="h-5 w-5 text-red-600" />
              )}
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h3 className="font-semibold text-zinc-900">
                    {result.is_duplicate ? "Similar Ticket Found!" : "No Similar Ticket"}
                  </h3>
                  <span className={`text-lg font-bold ${getConfidenceColor(result.confidence_score)}`}>
                    {Math.round(result.confidence_score * 100)}%
                  </span>
                </div>
                <p className="mt-1 text-sm text-zinc-600">
                  {result.is_duplicate 
                    ? `Matches cluster #${result.matched_cluster_id}` 
                    : "No match above 80% threshold"}
                </p>
              </div>
            </div>
          </div>

          {result.is_duplicate && result.matched_cluster_id !== null && result.similar_tickets.length > 0 && (
            <div className="mt-4">
              <div className="mb-3 flex items-center justify-between">
                <h4 className="text-sm font-medium text-zinc-700">
                  Similar Tickets
                </h4>
                {onClusterClick && (
                  <button
                    onClick={() => onClusterClick(result.matched_cluster_id!)}
                    className="text-sm font-medium text-sky-600"
                  >
                    View Cluster →
                  </button>
                )}
              </div>
              
              <div className="space-y-2">
                {result.similar_tickets.slice(0, 3).map((ticket) => (
                  <div
                    key={ticket.id}
                    className="rounded-lg border border-zinc-200 bg-zinc-50 p-3"
                  >
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-medium text-zinc-500">
                        {ticket.id}
                      </span>
                      <span className={`rounded-full px-2 py-0.5 text-xs font-medium ${
                        ticket.severity === "critical" ? "bg-red-100 text-red-700" :
                        ticket.severity === "high" ? "bg-orange-100 text-orange-700" :
                        "bg-zinc-100 text-zinc-600"
                      }`}>
                        {ticket.severity}
                      </span>
                    </div>
                    <p className="mt-1 text-sm text-zinc-700 line-clamp-2">
                      {ticket.title}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
