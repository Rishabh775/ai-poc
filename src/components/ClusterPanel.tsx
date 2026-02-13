import { AlertCircle, TrendingUp, Calendar } from 'lucide-react';
import { Cluster } from '../services/api';

interface ClusterPanelProps {
  clusters: Cluster[];
}

const severityColors: Record<string, string> = {
  critical: 'bg-red-100 text-red-800 border-red-200',
  high: 'bg-orange-100 text-orange-800 border-orange-200',
  medium: 'bg-yellow-100 text-yellow-800 border-yellow-200',
  low: 'bg-green-100 text-green-800 border-green-200'
};

export function ClusterPanel({ clusters }: ClusterPanelProps) {
  const topClusters = clusters.slice(0, 5);

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-gray-900">AI-Detected Issue Clusters</h3>
        <span className="text-sm text-gray-500">{clusters.length} clusters identified</span>
      </div>

      <div className="space-y-4">
        {topClusters.map((cluster) => (
          <div
            key={cluster.cluster_id}
            className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow"
          >
            <div className="flex items-start justify-between mb-3">
              <div className="flex items-center space-x-3">
                <div className="bg-blue-100 p-2 rounded-lg">
                  <AlertCircle className="w-5 h-5 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-900">
                    Cluster #{cluster.cluster_id}
                  </h4>
                  <p className="text-sm text-gray-600 capitalize">
                    {cluster.workflow_type.replace(/_/g, ' ')} workflow
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold text-gray-900">
                  {cluster.impact_score}
                </div>
                <div className="text-xs text-gray-500">impact score</div>
              </div>
            </div>

            <p className="text-sm text-gray-700 mb-3 leading-relaxed">
              {cluster.summary}
            </p>

            <div className="flex items-center space-x-4 text-sm text-gray-600 mb-3">
              <div className="flex items-center space-x-1">
                <TrendingUp className="w-4 h-4" />
                <span>{cluster.incident_count} incidents</span>
              </div>
              <div className="flex items-center space-x-1">
                <Calendar className="w-4 h-4" />
                <span>
                  {new Date(cluster.first_seen).toLocaleDateString()} -
                  {new Date(cluster.last_seen).toLocaleDateString()}
                </span>
              </div>
            </div>

            <div className="border-t border-gray-200 pt-3">
              <p className="text-xs font-medium text-gray-700 mb-2">Example Tickets:</p>
              <div className="space-y-2">
                {cluster.example_tickets.slice(0, 2).map((ticket) => (
                  <div
                    key={ticket.id}
                    className="flex items-start justify-between bg-gray-50 rounded p-2"
                  >
                    <div className="flex-1">
                      <p className="text-xs font-medium text-gray-900">{ticket.id}</p>
                      <p className="text-xs text-gray-600 mt-1 line-clamp-1">
                        {ticket.title}
                      </p>
                    </div>
                    <span
                      className={`text-xs px-2 py-1 rounded border ${
                        severityColors[ticket.severity] || severityColors.medium
                      }`}
                    >
                      {ticket.severity}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
