import { Lightbulb, TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { Metrics, Trends } from '../services/api';

interface ExecutiveSummaryProps {
  metrics: Metrics;
  trends: Trends;
}

export function ExecutiveSummary({ metrics, trends }: ExecutiveSummaryProps) {
  const getTrendIcon = () => {
    if (trends.trend_direction === 'increasing') {
      return <TrendingUp className="w-5 h-5 text-red-600" />;
    } else if (trends.trend_direction === 'decreasing') {
      return <TrendingDown className="w-5 h-5 text-green-600" />;
    }
    return <Minus className="w-5 h-5 text-gray-600" />;
  };

  const getTrendColor = () => {
    if (trends.trend_direction === 'increasing') return 'text-red-600';
    if (trends.trend_direction === 'decreasing') return 'text-green-600';
    return 'text-gray-600';
  };

  return (
    <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-lg shadow-sm border border-blue-200 p-6">
      <div className="flex items-start space-x-4">
        <div className="bg-blue-600 p-3 rounded-lg">
          <Lightbulb className="w-6 h-6 text-white" />
        </div>
        <div className="flex-1">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            Executive Summary
          </h3>
          <div className="space-y-2 text-sm text-gray-700">
            <p>
              <span className="font-semibold">System Status:</span> Analyzed {metrics.total_incidents} incidents
              across {metrics.cluster_count} recurring patterns over the past 90 days.
            </p>
            <p>
              <span className="font-semibold">Primary Concern:</span> {metrics.top_recurring_issue}
            </p>
            <p className="flex items-center space-x-2">
              <span className="font-semibold">Trend:</span>
              <span className="flex items-center space-x-1">
                {getTrendIcon()}
                <span className={getTrendColor()}>
                  Incidents are {trends.trend_direction} ({trends.recent_7d_count} in last 7 days vs{' '}
                  {trends.previous_7d_count} previous)
                </span>
              </span>
            </p>
            <p>
              <span className="font-semibold">Risk Assessment:</span> {metrics.critical_incidents} critical
              and {metrics.high_priority_incidents} high-priority incidents require immediate attention.
            </p>
            <div className="mt-4 pt-4 border-t border-blue-200">
              <p className="font-semibold text-gray-900 mb-1">Recommended Actions:</p>
              <ul className="list-disc list-inside space-y-1 text-gray-700">
                <li>Prioritize resolution of top 3 recurring clusters</li>
                <li>Investigate root cause of {trends.trend_direction === 'increasing' ? 'incident spike' : 'primary workflow issues'}</li>
                <li>Deploy automated monitoring for high-impact patterns</li>
                <li>Review deployment processes for regression prevention</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
