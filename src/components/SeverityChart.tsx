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

interface SeverityChartProps {
  data: Record<string, number>;
}

const SEVERITY_COLORS: Record<string, string> = {
  critical: "#dc2626",
  high: "#ea580c",
  medium: "#f59e0b",
  low: "#22c55e",
};

export function SeverityChart({ data }: SeverityChartProps) {
  const chartData = Object.entries(data).map(([severity, count]) => ({
    severity: severity.charAt(0).toUpperCase() + severity.slice(1),
    count,
    color: SEVERITY_COLORS[severity] || "#71717a",
  }));

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-card">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Severity
      </h3>
      <p className="mt-1 text-lg font-semibold text-zinc-900">
        Incident breakdown
      </p>
      <div className="mt-4 h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData}>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#e4e4e7"
              vertical={false}
            />
            <XAxis
              dataKey="severity"
              tick={{ fontSize: 11, fill: "#71717a" }}
            />
            <YAxis tick={{ fontSize: 11, fill: "#71717a" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e4e4e7",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
              }}
              formatter={(value: number) => [value, "Incidents"]}
            />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {chartData.map((entry, index) => (
                <Cell key={index} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
