import { useEffect, useState } from "react";
import {
  Activity,
  AlertTriangle,
  TrendingUp,
  Shield,
  ChevronDown,
} from "lucide-react";
import { api, InsightsResponse, Cluster, JiraDraft } from "./services/api";
import { MetricCard } from "./components/MetricCard";
import { TopIssueCard } from "./components/TopIssueCard";
import { TrendChart } from "./components/TrendChart";
import { SeverityChart } from "./components/SeverityChart";
import { WorkflowChart } from "./components/WorkflowChart";
import { ClusterDistributionChart } from "./components/ClusterDistributionChart";
import { ClusterPanel } from "./components/ClusterPanel";
import { ExecutiveSummary } from "./components/ExecutiveSummary";
import { ClusterDetailPanel } from "./components/ClusterDetailPanel";
import { JiraModal } from "./components/JiraModal";
import { DuplicateCheckPanel } from "./components/DuplicateCheckPanel";
import { ClusterChangeTracker } from "./components/ClusterChangeTracker";
import { ClusterConfidencePanel } from "./components/ClusterConfidencePanel";
import { AllTicketsPanel } from "./components/AllTicketsPanel";

type SortOption =
  | "frequency"
  | "severity"
  | "impact"
  | "recurrence"
  | "priority";

type TabType = "overview" | "duplicate" | "changes" | "confidence" | "tickets";

const SORT_OPTIONS: { value: SortOption; label: string }[] = [
  { value: "frequency", label: "Frequency" },
  { value: "severity", label: "Severity" },
  { value: "impact", label: "Impact" },
  { value: "recurrence", label: "Recurrence" },
  { value: "priority", label: "Priority" },
];

function App() {
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCluster, setSelectedCluster] = useState<Cluster | null>(null);
  const [jiraDraft, setJiraDraft] = useState<JiraDraft["draft"] | null>(null);
  const [sortBy, setSortBy] = useState<SortOption>("priority");
  const [activeTab, setActiveTab] = useState<TabType>("overview");

  const fetchInsights = async () => {
    try {
      setLoading(true);
      const data = await api.getInsights();
      setInsights(data);
      setError(null);
    } catch (err) {
      console.error("Failed to fetch insights:", err);
      setError(
        "Failed to load insights. Make sure the backend is running on http://localhost:8000"
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInsights();
  }, []);

  const handleDetails = (cluster: Cluster) => {
    setSelectedCluster(cluster);
  };

  const handleCreateJira = async (cluster: Cluster) => {
    try {
      const res = await api.createJiraDraft(cluster.cluster_id);
      setJiraDraft(res.draft);
    } catch (err) {
      console.error("Failed to create Jira draft:", err);
      alert("Failed to generate Jira draft.");
    }
  };

  const handleClusterClick = (clusterId: number) => {
    if (insights) {
      const cluster = insights.clusters.find(c => c.cluster_id === clusterId);
      if (cluster) {
        setSelectedCluster(cluster);
      }
    }
  };

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-100">
        <div className="text-center">
          <div className="mx-auto mb-4 h-12 w-12 animate-spin rounded-full border-2 border-zinc-300 border-t-sky-600" />
          <p className="font-medium text-zinc-700">Processing operational data</p>
          <p className="mt-1 text-sm text-zinc-500">
            AI is analyzing incident patterns
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-zinc-100">
        <div className="w-full max-w-md rounded-xl border border-zinc-200 bg-white p-8 shadow-card">
          <div className="mb-4 flex items-center gap-3">
            <div className="rounded-lg bg-red-100 p-2">
              <AlertTriangle className="h-6 w-6 text-red-600" />
            </div>
            <h2 className="text-lg font-semibold text-zinc-900">Connection error</h2>
          </div>
          <p className="mb-4 text-zinc-600">{error}</p>
          <div className="rounded-lg bg-zinc-50 p-4">
            <p className="mb-2 text-sm font-medium text-zinc-900">
              To start the backend:
            </p>
            <code className="block rounded bg-zinc-900 px-2 py-1.5 text-xs text-white">
              cd backend && python main.py
            </code>
          </div>
        </div>
      </div>
    );
  }

  if (!insights) return null;

  const { metrics, trends, change_tracking } = insights;
  const trendDir = change_tracking?.trend_direction ?? "stable";

  const severityData = insights.clusters.reduce(
    (acc, cluster) => {
      Object.entries(cluster.severity_distribution || {}).forEach(
        ([severity, count]) => {
          acc[severity] = (acc[severity] || 0) + count;
        }
      );
      return acc;
    },
    {} as Record<string, number>
  );

  return (
    <div className="flex min-h-screen flex-col bg-zinc-100">
      <header className="border-b border-zinc-200 bg-zinc-900 shrink-0">
        <div className="mx-auto max-w-7xl px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-sky-500">
                <Activity className="h-5 w-5 text-white" strokeWidth={2} />
              </div>
              <div>
                <h1 className="text-lg font-bold text-white">
                  Operational Intelligence
                </h1>
                <p className="text-sm text-zinc-400">
                  AI-powered operational triage engine
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-zinc-500">Last updated</p>
              <p className="text-sm font-medium text-white">
                {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto max-w-7xl px-6 py-8">
        <div className="mb-6 flex gap-2 border-b border-zinc-200">
          <button
            onClick={() => setActiveTab("overview")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "overview"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab("duplicate")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "duplicate"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            Check Duplicate
          </button>
          <button
            onClick={() => setActiveTab("changes")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "changes"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            Cluster Changes
          </button>
          <button
            onClick={() => setActiveTab("confidence")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "confidence"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            Cluster Confidence
          </button>
          <button
            onClick={() => setActiveTab("tickets")}
            className={`px-4 py-2 text-sm font-medium transition-colors ${
              activeTab === "tickets"
                ? "border-b-2 border-sky-600 text-sky-600"
                : "text-zinc-500 hover:text-zinc-700"
            }`}
          >
            All Tickets
          </button>
        </div>

        {activeTab === "overview" && (
          <>
            <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-4">
              <div className="lg:col-span-1">
                <MetricCard
                  title="Risk score"
                  value={metrics.risk_score}
                  icon={AlertTriangle}
                  trend={`${metrics.critical_incidents} critical · ${metrics.high_priority_incidents} high`}
                  hero
                />
              </div>
              <div className="grid grid-cols-2 gap-4 lg:col-span-3 lg:grid-cols-4">
                <MetricCard
                  title="Total incidents"
                  value={metrics.total_incidents}
                  icon={Activity}
                  trend={`${trends.recent_7d_count} in last 7d`}
                  iconColor="text-sky-600"
                />
                <MetricCard
                  title="Stability"
                  value={change_tracking?.stability_index ?? metrics.stability_index}
                  icon={Shield}
                  trend={trendDir}
                  iconColor="text-emerald-600"
                />
                <MetricCard
                  title="Trend"
                  value={`${(change_tracking?.delta_percent ?? 0) > 0 ? "+" : ""}${change_tracking?.delta_percent ?? 0}%`}
                  icon={TrendingUp}
                  trend={`vs prev 7d · ${trendDir}`}
                  iconColor={
                    trendDir === "increasing"
                      ? "text-red-600"
                      : trendDir === "decreasing"
                      ? "text-emerald-600"
                      : "text-zinc-500"
                  }
                />
                <MetricCard
                  title="Clusters"
                  value={metrics.cluster_count}
                  icon={Activity}
                  trend="patterns detected"
                  iconColor="text-violet-600"
                />
              </div>
            </div>

            <div className="mb-8">
              <TopIssueCard
                summary={
                  metrics.top_issue ||
                  metrics.top_recurring_issue ||
                  "No recurring patterns detected"
                }
                criticalCount={metrics.critical_incidents}
                highCount={metrics.high_priority_incidents}
              />
            </div>

            <div className="mb-8">
              <ExecutiveSummary
                metrics={metrics}
                trends={trends}
                changeTracking={change_tracking}
              />
            </div>

            <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
              <TrendChart data={trends.daily_incidents} />
              <WorkflowChart data={trends.workflow_distribution} />
            </div>

            <div className="mb-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
              <SeverityChart data={severityData} />
              <ClusterDistributionChart clusters={insights.clusters} />
            </div>

            <div className="mb-4 flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
              <h2 className="text-lg font-semibold text-zinc-900">
                Issue clusters
              </h2>
              <div className="relative">
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as SortOption)}
                  className="w-full appearance-none rounded-lg border border-zinc-300 bg-white py-2 pl-4 pr-10 text-sm font-medium text-zinc-700 shadow-card focus:border-sky-500 focus:outline-none focus:ring-2 focus:ring-sky-500/20 sm:w-auto"
                >
                  {SORT_OPTIONS.map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      Sort by {opt.label}
                    </option>
                  ))}
                </select>
                <ChevronDown className="pointer-events-none absolute right-3 top-1/2 h-5 w-5 -translate-y-1/2 text-zinc-500" />
              </div>
            </div>

            <ClusterPanel
              clusters={insights.clusters}
              sortBy={sortBy}
              onDetails={handleDetails}
              onCreateJira={handleCreateJira}
            />
          </>
        )}

        {activeTab === "duplicate" && (
          <div className="mx-auto max-w-2xl">
            <DuplicateCheckPanel onClusterClick={handleClusterClick} />
          </div>
        )}

        {activeTab === "changes" && (
          <div className="mx-auto max-w-2xl">
            <ClusterChangeTracker
              clusterChanges={change_tracking?.cluster_changes || []}
              clusters={insights.clusters}
              onClusterClick={handleClusterClick}
            />
          </div>
        )}

        {activeTab === "confidence" && (
          <div className="mx-auto max-w-2xl">
            <ClusterConfidencePanel
              clusters={insights.clusters}
              averageConfidence={metrics.average_cluster_confidence}
              onClusterClick={(cluster) => setSelectedCluster(cluster)}
            />
          </div>
        )}

        {activeTab === "tickets" && (
          <AllTicketsPanel onClusterClick={handleClusterClick} onClusterAssigned={fetchInsights} />
        )}
      </main>

      {selectedCluster && (
        <div className="fixed inset-0 z-40 bg-black/30" onClick={() => setSelectedCluster(null)}>
          <div className="absolute inset-0 overflow-y-auto" onClick={(e) => e.stopPropagation()}>
            <ClusterDetailPanel
              cluster={selectedCluster}
              allClusters={insights?.clusters || []}
              onClose={() => setSelectedCluster(null)}
              onMerge={async (sourceId, targetId) => {
                await api.mergeClusters(sourceId, targetId);
                fetchInsights();
              }}
              onNameUpdate={fetchInsights}
            />
          </div>
        </div>
      )}

      {jiraDraft && (
        <JiraModal draft={jiraDraft} onClose={() => setJiraDraft(null)} />
      )}

      <footer className="mt-auto border-t border-zinc-200 bg-white py-6 shrink-0">
        <p className="text-center text-sm text-zinc-500">
          Operational Intelligence — AI analysis → prioritization → action
        </p>
      </footer>
    </div>
  );
}

export default App;
