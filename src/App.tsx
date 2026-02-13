import { useEffect, useState } from 'react';
import { Activity, AlertTriangle, TrendingUp, Shield } from 'lucide-react';
import { api, InsightsResponse } from './services/api';
import { MetricCard } from './components/MetricCard';
import { TrendChart } from './components/TrendChart';
import { SeverityChart } from './components/SeverityChart';
import { WorkflowChart } from './components/WorkflowChart';
import { ClusterPanel } from './components/ClusterPanel';
import { ExecutiveSummary } from './components/ExecutiveSummary';

function App() {
  const [insights, setInsights] = useState<InsightsResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchInsights = async () => {
      try {
        setLoading(true);
        await new Promise(resolve => setTimeout(resolve, 1500));
        const data = await api.getInsights();
        setInsights(data);
        setError(null);
      } catch (err) {
        console.error('Failed to fetch insights:', err);
        setError('Failed to load insights. Make sure the backend is running on http://localhost:8000');
      } finally {
        setLoading(false);
      }
    };

    fetchInsights();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto mb-4"></div>
          <p className="text-lg font-medium text-gray-700">Processing operational data...</p>
          <p className="text-sm text-gray-500 mt-2">AI is analyzing incident patterns</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="bg-white rounded-lg shadow-lg p-8 max-w-md">
          <div className="flex items-center space-x-3 mb-4">
            <AlertTriangle className="w-8 h-8 text-red-600" />
            <h2 className="text-xl font-semibold text-gray-900">Connection Error</h2>
          </div>
          <p className="text-gray-700 mb-4">{error}</p>
          <div className="bg-gray-50 rounded p-4">
            <p className="text-sm font-medium text-gray-900 mb-2">To start the backend:</p>
            <code className="text-xs bg-gray-900 text-white p-2 rounded block">
              cd backend && python main.py
            </code>
          </div>
        </div>
      </div>
    );
  }

  if (!insights) {
    return null;
  }

  const severityData = insights.clusters.reduce((acc, cluster) => {
    Object.entries(cluster.severity_distribution).forEach(([severity, count]) => {
      acc[severity] = (acc[severity] || 0) + count;
    });
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 p-2 rounded-lg">
                <Activity className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Operational Intelligence Dashboard
                </h1>
                <p className="text-sm text-gray-600">
                  AI-Powered Incident Analysis & Pattern Detection
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-sm text-gray-500">Last Updated</p>
              <p className="text-sm font-medium text-gray-900">
                {new Date().toLocaleString()}
              </p>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <MetricCard
            title="Total Incidents"
            value={insights.metrics.total_incidents}
            icon={Activity}
            trend={`${insights.trends.recent_7d_count} in last 7 days`}
            iconColor="text-blue-600"
          />
          <MetricCard
            title="Top Recurring Issue"
            value={insights.metrics.cluster_count}
            icon={TrendingUp}
            trend="clusters detected"
            iconColor="text-orange-600"
          />
          <MetricCard
            title="Risk Score"
            value={insights.metrics.risk_score}
            icon={AlertTriangle}
            trend={`${insights.metrics.critical_incidents} critical incidents`}
            iconColor="text-red-600"
          />
          <MetricCard
            title="Stability Index"
            value={insights.metrics.stability_index}
            icon={Shield}
            trend={insights.trends.trend_direction}
            iconColor="text-green-600"
          />
        </div>

        <div className="mb-8">
          <ExecutiveSummary metrics={insights.metrics} trends={insights.trends} />
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          <TrendChart data={insights.trends.daily_incidents} />
          <WorkflowChart data={insights.trends.workflow_distribution} />
        </div>

        <div className="mb-8">
          <SeverityChart data={severityData} />
        </div>

        <ClusterPanel clusters={insights.clusters} />
      </main>

      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <p className="text-center text-sm text-gray-500">
            Operational Intelligence Platform - Powered by AI Pattern Detection
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
