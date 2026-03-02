import axios from "axios";

const API_BASE_URL = "http://localhost:8000";

export interface Ticket {
  id: string;
  title: string;
  description: string;
  timestamp: string;
  workflow_type: string;
  severity: string;
  category?: string;
}

export interface Cluster {
  cluster_id: number;
  custom_name?: string;
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
  all_tickets: Array<{
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
  top_keywords?: string[];
  representative_ticket?: {
    id: string;
    title: string;
    severity: string;
    timestamp: string;
  };
  semantic_cohesion_score?: number;
  cluster_confidence_score?: number;
  confidence_label?: "high" | "medium" | "low";
}

export interface ClusterChange {
  cluster_id: number;
  previous_7d_count: number;
  recent_7d_count: number;
  trend: "new" | "increasing" | "decreasing" | "resolved" | "stable";
}

export interface ChangeTracking {
  trend_direction: string;
  delta_percent: number;
  new_clusters: number;
  resolved_clusters: number;
  stability_index: number;
  cluster_changes: ClusterChange[];
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
  average_cluster_confidence: number;
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

export interface Config {
  similarity_threshold: number;
  dbscan_eps: number;
  min_samples: number;
  severity_weights: Record<string, number>;
  workflow_encodings: Record<string, number[]>;
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
    confidence_score?: number;
    top_keywords?: string[];
  };
  cluster_id: number;
}

export interface DuplicateCheckRequest {
  title: string;
  description?: string;
  workflow_type?: string;
  severity?: string;
  title_only?: boolean;
}

export interface DuplicateCheckResponse {
  is_duplicate: boolean;
  confidence_score: number;
  matched_cluster_id: number | null;
  similar_tickets: Array<{
    id: string;
    title: string;
    severity: string;
    timestamp: string;
  }>;
  message: string;
}

export interface ClusterAssignmentRequest {
  title: string;
  description: string;
  workflow_type: string;
  severity: string;
}

export interface CreateTicketRequest {
  title: string;
  description: string;
  workflow_type: string;
  severity: string;
  category?: string;
}

export interface ClusterAssignmentResponse {
  assigned_cluster_id: number;
  created_new_cluster: boolean;
  similarity_score: number;
  message: string;
}

export interface InsightsResponse {
  clusters: Cluster[];
  unclustered_tickets: Array<{
    id: string;
    title: string;
    severity: string;
    timestamp: string;
  }>;
  trends: Trends;
  change_tracking: ChangeTracking;
  metrics: Metrics;
  total_tickets: number;
  config: Config;
}

export interface TicketWithCluster extends Ticket {
  cluster_id: number | null;
  cluster_workflow: string | null;
  cluster_priority: string | null;
  cluster_impact: number | null;
  cluster_confidence: number | null;
}

export interface TicketsWithClustersResponse {
  tickets: TicketWithCluster[];
  total: number;
  clusters: Cluster[];
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

  getTicketsWithClusters: async (): Promise<TicketsWithClustersResponse> => {
    const response = await axios.get(`${API_BASE_URL}/tickets-with-clusters`);
    return response.data;
  },

  searchTickets: async (query: string): Promise<{tickets: Array<{id: string, title: string, severity: string, workflow_type: string}>, total: number}> => {
    const response = await axios.get(`${API_BASE_URL}/tickets/search`, { params: { q: query } });
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

  checkDuplicate: async (request: DuplicateCheckRequest): Promise<DuplicateCheckResponse> => {
    const response = await axios.post(
      `${API_BASE_URL}/check-duplicate`,
      request
    );
    return response.data;
  },

  assignCluster: async (request: ClusterAssignmentRequest): Promise<ClusterAssignmentResponse> => {
    const response = await axios.post(
      `${API_BASE_URL}/assign-cluster`,
      request
    );
    return response.data;
  },

  manuallyAssignCluster: async (ticketId: string, clusterId: number) => {
    const response = await axios.post(`${API_BASE_URL}/clusters/assign`, {
      ticket_id: ticketId,
      cluster_id: clusterId,
    });
    return response.data;
  },

  mergeClusters: async (sourceClusterId: number, targetClusterId: number) => {
    const response = await axios.post(`${API_BASE_URL}/clusters/merge`, {
      source_cluster_id: sourceClusterId,
      target_cluster_id: targetClusterId,
    });
    return response.data;
  },

  getConfig: async (): Promise<Config> => {
    const response = await axios.get(`${API_BASE_URL}/config`);
    return response.data;
  },

  createTicket: async (request: CreateTicketRequest) => {
    const response = await axios.post(`${API_BASE_URL}/tickets`, request);
    return response.data;
  },

  updateClusterName: async (clusterId: number, name: string) => {
    const response = await axios.post(`${API_BASE_URL}/clusters/name`, {
      cluster_id: clusterId,
      name,
    });
    return response.data;
  },

  getClusterNames: async (): Promise<Record<number, string>> => {
    const response = await axios.get(`${API_BASE_URL}/clusters/names`);
    return response.data;
  },

  bulkAssignTickets: async (ticketIds: string[], clusterId: number) => {
    const response = await axios.post(`${API_BASE_URL}/clusters/bulk-assign`, {
      ticket_ids: ticketIds,
      cluster_id: clusterId,
    });
    return response.data;
  },

  unassignTicket: async (ticketId: string) => {
    const response = await axios.post(`${API_BASE_URL}/clusters/unassign`, {
      ticket_id: ticketId,
    });
    return response.data;
  },
};
