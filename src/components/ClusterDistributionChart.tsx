import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from "recharts";
import { Cluster } from "../services/api";

interface ClusterDistributionChartProps {
  clusters: Cluster[];
}

const COLORS = ["#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6", "#6366f1"];

export function ClusterDistributionChart({
  clusters,
}: ClusterDistributionChartProps) {
  const chartData = clusters.slice(0, 8).map((c) => ({
    name: `#${c.cluster_id}`,
    count: c.incident_count,
    workflow: c.workflow_type,
  }));

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-card">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Clusters
      </h3>
      <p className="mt-1 text-lg font-semibold text-zinc-900">
        Incident distribution
      </p>
      <div className="mt-4 h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart
            data={chartData}
            layout="vertical"
            margin={{ left: 32, right: 16 }}
          >
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e4e4e7"
              horizontal={false}
            />
            <XAxis
              type="number"
              tick={{ fontSize: 11, fill: "#71717a" }}
            />
            <YAxis
              dataKey="name"
              type="category"
              tick={{ fontSize: 11, fill: "#71717a" }}
              width={32}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e4e4e7",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
              }}
              formatter={(
                value: number,
                _name: string,
                props: { payload?: { workflow?: string } }
              ) => [
                `${value} incidents${
                  props.payload?.workflow
                    ? ` · ${props.payload.workflow}`
                    : ""
                }`,
                "Count",
              ]}
            />
            <Bar dataKey="count" radius={[0, 4, 4, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={COLORS[index % COLORS.length]} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
