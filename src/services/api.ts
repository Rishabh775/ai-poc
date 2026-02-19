import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export interface Ticket {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  workflow_type: string;
  severity: string;
}

export interface Cluster {
  cluster_id: number;
  incident_count: number;
  impact_score: number;
  severity_distribution: Record<string, number>;
  workflow_type: string;
  example_tickets: Array<{
    id: string;
    title: string;
    severity: string;
    timestamp: string;
  }>;
  summary: string;
  first_seen: string;
  last_seen: string;
  recommended_action?: string;
  priority_level?: string;
  owner_team?: string;
  business_impact?: string;
  urgency_tag?: string;
  risk_score?: number;
  recurrence_signal?: string;
}

export interface ChangeTracking {
  trend_direction: string;
  delta_percent: number;
  new_clusters: number;
  resolved_clusters: number;
  stability_index: number;
}

export interface Metrics {
  total_incidents: number;
  top_issue: string;
  risk_score: number;
  stability_index: number;
  trend_direction: string;
  top_recurring_issue: string;
  critical_incidents: number;
  high_priority_incidents: number;
  cluster_count: number;
}

export interface Trends {
  daily_incidents: Array<{ date: string; count: number }>;
  severity_over_time: Array<{
    date: string;
    severity: string;
    count: number;
  }>;
  workflow_distribution: Record<string, number>;
  trend_direction: string;
  recent_7d_count: number;
  previous_7d_count: number;
}

export interface JiraDraft {
  draft: {
    summary: string;
    priority: string;
    impact_explanation: string;
    cluster_summary: string;
    example_tickets: Array<{
      id: string;
      title: string;
      severity: string;
    }>;
    recommended_action: string;
    owner_team: string;
    incident_count: number;
    impact_score: number;
    urgency_tag: string;
  };
  cluster_id: number;
}

export interface InsightsResponse {
  clusters: Cluster[];
  trends: Trends;
  change_tracking: ChangeTracking;
  metrics: Metrics;
  total_tickets: number;
}

export const api = {
  getInsights: async (): Promise<InsightsResponse> => {
    const response = await axios.get(`${API_BASE_URL}/insights`);
    return response.data;
  },

  getTickets: async () => {
    const response = await axios.get(`${API_BASE_URL}/tickets`);
    return response.data;
  },

  getCluster: async (clusterId: number): Promise<Cluster> => {
    const response = await axios.get(`${API_BASE_URL}/cluster/${clusterId}`);
    return response.data;
  },

  createJiraDraft: async (clusterId: number): Promise<JiraDraft> => {
    const response = await axios.post(
      `${API_BASE_URL}/jira-draft/${clusterId}`
    );
    return response.data;
  },
};
