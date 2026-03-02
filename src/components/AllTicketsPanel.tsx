import { useEffect, useState, useMemo } from "react";
import { Search, AlertCircle, Plus, X, Loader2, Users } from "lucide-react";
import { api, TicketWithCluster, Cluster } from "../services/api";

interface AllTicketsPanelProps {
  onClusterClick?: (clusterId: number) => void;
  onClusterAssigned?: () => void;
}

const WORKFLOWS = ["all", "submission", "review", "dashboard", "release", "infra"];
const SEVERITIES = ["all", "critical", "high", "medium", "low"];
const SORT_OPTIONS = [
  { value: "timestamp", label: "Date" },
  { value: "cluster_id", label: "Cluster" },
  { value: "severity", label: "Severity" },
];

const WORKFLOW_TYPES = ["submission", "review", "dashboard", "release", "infra"];
const SEVERITY_LEVELS = ["critical", "high", "medium", "low"];

export function AllTicketsPanel({ onClusterClick, onClusterAssigned }: AllTicketsPanelProps) {
  const [tickets, setTickets] = useState<TicketWithCluster[]>([]);
  const [clusters, setClusters] = useState<Cluster[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showAddForm, setShowAddForm] = useState(false);
  const [adding, setAdding] = useState(false);
  
  const [newTicket, setNewTicket] = useState({
    title: "",
    description: "",
    workflow_type: "",
    severity: "medium",
  });

  const [searchQuery, setSearchQuery] = useState("");
  const [workflowFilter, setWorkflowFilter] = useState("all");
  const [severityFilter, setSeverityFilter] = useState("all");
  const [clusterFilter, setClusterFilter] = useState<number | "all">("all");
  const [sortBy, setSortBy] = useState("timestamp");
  const [assigningTicket, setAssigningTicket] = useState<string | null>(null);
  const [assigning, setAssigning] = useState(false);
  const [selectedTickets, setSelectedTickets] = useState<Set<string>>(new Set());

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await api.getTicketsWithClusters();
      setTickets(data.tickets);
      setClusters(data.clusters);
      setError(null);
    } catch (err) {
      setError("Failed to load tickets");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleAddTicket = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTicket.title.trim()) return;

    setAdding(true);
    try {
      await api.createTicket(newTicket);
      setNewTicket({ title: "", description: "", workflow_type: "review", severity: "medium" });
      setShowAddForm(false);
      await fetchData();
    } catch (err) {
      console.error("Failed to add ticket:", err);
    } finally {
      setAdding(false);
    }
  };

  const filteredTickets = useMemo(() => {
    let result = [...tickets];

    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      result = result.filter(
        (t) =>
          t.title.toLowerCase().includes(query) ||
          t.description.toLowerCase().includes(query) ||
          t.id.toLowerCase().includes(query)
      );
    }

    if (workflowFilter !== "all") {
      result = result.filter((t) => t.workflow_type === workflowFilter);
    }

    if (severityFilter !== "all") {
      result = result.filter((t) => t.severity === severityFilter);
    }

    if (clusterFilter !== "all") {
      result = result.filter((t) => t.cluster_id === clusterFilter);
    }

    result.sort((a, b) => {
      if (sortBy === "timestamp") {
        return new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime();
      }
      if (sortBy === "cluster_id") {
        return (a.cluster_id || 999) - (b.cluster_id || 999);
      }
      if (sortBy === "severity") {
        const severityOrder: Record<string, number> = { critical: 0, high: 1, medium: 2, low: 3 };
        return (severityOrder[a.severity] ?? 4) - (severityOrder[b.severity] ?? 4);
      }
      return 0;
    });

    return result;
  }, [tickets, searchQuery, workflowFilter, severityFilter, clusterFilter, sortBy]);

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case "critical": return "bg-red-100 text-red-700 border-red-200";
      case "high": return "bg-orange-100 text-orange-700 border-orange-200";
      case "medium": return "bg-amber-100 text-amber-700 border-amber-200";
      case "low": return "bg-zinc-100 text-zinc-600 border-zinc-200";
      default: return "bg-zinc-100 text-zinc-600";
    }
  };

  const getClusterBadge = (clusterId: number | null) => {
    if (clusterId === null) {
      return "bg-zinc-200 text-zinc-500";
    }
    const cluster = clusters.find((c) => c.cluster_id === clusterId);
    if (!cluster) return "bg-zinc-200 text-zinc-500";
    
    switch (cluster.priority_level) {
      case "P1": return "bg-red-100 text-red-700 border-red-200";
      case "P2": return "bg-orange-100 text-orange-700 border-orange-200";
      case "P3": return "bg-amber-100 text-amber-700 border-amber-200";
      default: return "bg-zinc-100 text-zinc-600 border-zinc-200";
    }
  };

  const uniqueClusters = useMemo(() => {
    const clusterIds = [...new Set(tickets.map((t) => t.cluster_id).filter((c) => c !== null))];
    return clusterIds.map((id) => clusters.find((c) => c.cluster_id === id)).filter(Boolean) as Cluster[];
  }, [tickets, clusters]);

  if (loading) {
    return (
      <div className="flex items-center justify-center p-8">
        <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-300 border-t-sky-600" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-lg border border-red-200 bg-red-50 p-4">
        <div className="flex items-center gap-2 text-red-700">
          <AlertCircle className="h-4 w-4" />
          <p>{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="rounded-xl border border-zinc-200 bg-white p-4 shadow-card">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-zinc-400" />
            <input
              type="text"
              placeholder="Search tickets..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full rounded-lg border border-zinc-300 py-2 pl-10 pr-4 text-sm focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20"
            />
          </div>

          <button
            onClick={() => {
              const csv = [
                ["ID", "Title", "Description", "Severity", "Workflow", "Cluster", "Timestamp"].join(","),
                ...tickets.map(t => [
                  t.id,
                  `"${t.title.replace(/"/g, '""')}"`,
                  `"${(t.description || "").replace(/"/g, '""')}"`,
                  t.severity,
                  t.workflow_type || "",
                  t.cluster_id ?? "",
                  t.timestamp
                ].join(","))
              ].join("\n");
              const blob = new Blob([csv], { type: "text/csv" });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = `tickets-${new Date().toISOString().split("T")[0]}.csv`;
              a.click();
            }}
            className="flex items-center gap-2 rounded-lg border border-zinc-300 px-4 py-2 text-sm font-medium text-zinc-700 hover:bg-zinc-50"
          >
            Export CSV
          </button>

          <button
            onClick={() => setShowAddForm(!showAddForm)}
            className="flex items-center gap-2 rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700"
          >
            <Plus className="h-4 w-4" />
            Add Ticket
          </button>
        </div>

        {showAddForm && (
          <div className="mt-4 rounded-lg border border-sky-200 bg-sky-50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <h3 className="font-medium text-zinc-900">Add New Ticket</h3>
              <button
                onClick={() => setShowAddForm(false)}
                className="text-zinc-500 hover:text-zinc-700"
              >
                <X className="h-4 w-4" />
              </button>
            </div>
            <form onSubmit={handleAddTicket} className="space-y-3">
              <div>
                <input
                  type="text"
                  placeholder="Ticket title"
                  value={newTicket.title}
                  onChange={(e) => setNewTicket({ ...newTicket, title: e.target.value })}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
                  required
                />
              </div>
              <div>
                <textarea
                  placeholder="Description"
                  value={newTicket.description}
                  onChange={(e) => setNewTicket({ ...newTicket, description: e.target.value })}
                  className="w-full rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
                  rows={2}
                />
              </div>
              <div className="grid grid-cols-2 gap-3">
                <select
                  value={newTicket.workflow_type}
                  onChange={(e) => setNewTicket({ ...newTicket, workflow_type: e.target.value })}
                  className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
                >
                  <option value="">Select workflow (optional)</option>
                  {WORKFLOW_TYPES.map((w) => (
                    <option key={w} value={w}>
                      {w.charAt(0).toUpperCase() + w.slice(1)}
                    </option>
                  ))}
                </select>
                <select
                  value={newTicket.severity}
                  onChange={(e) => setNewTicket({ ...newTicket, severity: e.target.value })}
                  className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
                >
                  {SEVERITY_LEVELS.map((s) => (
                    <option key={s} value={s}>
                      {s.charAt(0).toUpperCase() + s.slice(1)}
                    </option>
                  ))}
                </select>
              </div>
              <button
                type="submit"
                disabled={adding || !newTicket.title.trim()}
                className="flex w-full items-center justify-center gap-2 rounded-lg bg-sky-600 px-4 py-2 text-sm font-medium text-white hover:bg-sky-700 disabled:opacity-50"
              >
                {adding ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Plus className="h-4 w-4" />
                    Add Ticket
                  </>
                )}
              </button>
            </form>
          </div>
        )}

        <div className="mt-4 flex flex-wrap gap-2">
          <select
            value={workflowFilter}
            onChange={(e) => setWorkflowFilter(e.target.value)}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
          >
            {WORKFLOWS.map((w) => (
              <option key={w} value={w}>
                {w === "all" ? "All Workflows" : w.charAt(0).toUpperCase() + w.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
          >
            {SEVERITIES.map((s) => (
              <option key={s} value={s}>
                {s === "all" ? "All Severities" : s.charAt(0).toUpperCase() + s.slice(1)}
              </option>
            ))}
          </select>

          <select
            value={clusterFilter === "all" ? "all" : clusterFilter === -1 ? "unclustered" : clusterFilter}
            onChange={(e) => {
              if (e.target.value === "all") setClusterFilter("all");
              else if (e.target.value === "unclustered") setClusterFilter(-1);
              else setClusterFilter(Number(e.target.value));
            }}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
          >
            <option value="all">All Clusters</option>
            <option value="unclustered">Unclustered</option>
            {uniqueClusters.map((c) => (
              <option key={c.cluster_id} value={c.cluster_id}>
                Cluster {c.cluster_id} ({c.workflow_type})
              </option>
            ))}
          </select>

          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="rounded-lg border border-zinc-300 px-3 py-2 text-sm focus:border-sky-500 focus:outline-none"
          >
            {SORT_OPTIONS.map((s) => (
              <option key={s.value} value={s.value}>
                Sort by {s.label}
              </option>
            ))}
          </select>
        </div>

        <div className="mt-3 text-sm text-zinc-500">
          Showing {filteredTickets.length} of {tickets.length} tickets
        </div>

        {selectedTickets.size > 0 && (
          <div className="sticky bottom-4 z-10 mt-3 flex items-center justify-between rounded-lg border border-sky-200 bg-sky-50 p-3 shadow-lg">
            <span className="text-sm font-medium text-sky-700">
              {selectedTickets.size} ticket(s) selected
            </span>
            <div className="flex gap-2">
              <select
                onChange={async (e) => {
                  if (e.target.value) {
                    setAssigning(true);
                    try {
                      await api.bulkAssignTickets(Array.from(selectedTickets), Number(e.target.value));
                      setSelectedTickets(new Set());
                      await fetchData();
                      onClusterAssigned?.();
                    } catch (err) {
                      console.error(err);
                    } finally {
                      setAssigning(false);
                    }
                  }
                }}
                className="rounded border border-sky-300 px-2 py-1 text-sm"
              >
                <option value="">Assign to cluster...</option>
                {clusters.map((c) => (
                  <option key={c.cluster_id} value={c.cluster_id}>
                    Cluster {c.cluster_id} - {c.workflow_type}
                  </option>
                ))}
              </select>
              <button
                onClick={() => setSelectedTickets(new Set())}
                className="rounded border border-sky-300 px-2 py-1 text-sm text-sky-700 hover:bg-sky-100"
              >
                Clear
              </button>
            </div>
          </div>
        )}
      </div>

      <div className="space-y-2">
        {filteredTickets.map((ticket) => (
          <div
            key={ticket.id}
            className="group rounded-lg border border-zinc-200 bg-white p-4 shadow-card transition-shadow hover:shadow-md"
          >
            <div className="flex items-start gap-3">
              <input
                type="checkbox"
                checked={selectedTickets.has(ticket.id)}
                onChange={(e) => {
                  const newSelected = new Set(selectedTickets);
                  if (e.target.checked) {
                    newSelected.add(ticket.id);
                  } else {
                    newSelected.delete(ticket.id);
                  }
                  setSelectedTickets(newSelected);
                }}
                className="mt-1 h-4 w-4 rounded border-zinc-300"
              />
              <div className="flex-1">
                <div className="flex items-start justify-between gap-4">
                  <div className="min-w-0 flex-1">
                    <div className="flex flex-wrap items-center gap-2">
                      <span className="font-mono text-sm font-medium text-zinc-600">
                        {ticket.id}
                      </span>
                      <span className={`rounded-full border px-2 py-0.5 text-xs font-medium ${getSeverityColor(ticket.severity)}`}>
                        {ticket.severity}
                      </span>
                      {ticket.workflow_type && (
                        <span className="rounded-full bg-zinc-100 px-2 py-0.5 text-xs font-medium text-zinc-600">
                          {ticket.workflow_type}
                        </span>
                      )}
                      {ticket.category && (
                        <span className="rounded-full bg-sky-50 border border-sky-200 px-2 py-0.5 text-xs font-medium text-sky-700">
                          {ticket.category}
                        </span>
                      )}
                      {ticket.cluster_id !== null && (
                        <button
                          onClick={() => onClusterClick?.(ticket.cluster_id!)}
                          className={`rounded-full border px-2 py-0.5 text-xs font-medium transition-colors hover:opacity-80 ${getClusterBadge(ticket.cluster_id)}`}
                        >
                          Cluster #{ticket.cluster_id}
                        </button>
                      )}
                      {ticket.cluster_id === null && (
                        <div className="relative">
                          <button
                            onClick={() => setAssigningTicket(assigningTicket === ticket.id ? null : ticket.id)}
                            className="flex items-center gap-1 rounded-full border border-sky-200 bg-sky-50 px-2 py-0.5 text-xs font-medium text-sky-700 hover:bg-sky-100"
                          >
                            <Users className="h-3 w-3" />
                            Assign
                          </button>
                          {assigningTicket === ticket.id && (
                            <div className="absolute left-0 top-6 z-10 w-48 rounded-lg border border-zinc-200 bg-white py-1 shadow-lg">
                              {clusters.map((c) => (
                                <button
                                  key={c.cluster_id}
                                  onClick={async () => {
                                    setAssigning(true);
                                    try {
                                      await api.manuallyAssignCluster(ticket.id, c.cluster_id);
                                      await fetchData();
                                      setAssigningTicket(null);
                                      onClusterAssigned?.();
                                    } catch (err) {
                                      console.error(err);
                                    } finally {
                                      setAssigning(false);
                                    }
                                  }}
                                  disabled={assigning}
                                  className="w-full px-3 py-2 text-left text-xs hover:bg-zinc-50"
                                >
                                  Cluster {c.cluster_id} - {c.workflow_type}
                                </button>
                              ))}
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                    <h3 className="mt-2 text-sm font-medium text-zinc-900 line-clamp-2">
                      {ticket.title}
                    </h3>
                    <p className="mt-1 text-xs text-zinc-500 line-clamp-2">
                      {ticket.description}
                    </p>
                    <div className="mt-2 flex items-center gap-4 text-xs text-zinc-400">
                      <span>{new Date(ticket.timestamp).toLocaleString()}</span>
                      {ticket.cluster_priority && (
                        <span className="text-zinc-500">
                          Priority: {ticket.cluster_priority}
                        </span>
                      )}
                      {ticket.cluster_impact && (
                        <span className="text-zinc-500">
                          Impact: {ticket.cluster_impact}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {filteredTickets.length === 0 && (
        <div className="py-8 text-center text-zinc-500">
          No tickets match your filters
        </div>
      )}
    </div>
  );
}
