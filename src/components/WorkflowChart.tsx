import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts";

interface WorkflowChartProps {
  data: Record<string, number>;
}

const COLORS = ["#0ea5e9", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"];

export function WorkflowChart({ data }: WorkflowChartProps) {
  const chartData = Object.entries(data).map(([name, value]) => ({
    name: name.replace(/_/g, " ").replace(/\b\w/g, (l) => l.toUpperCase()),
    value,
  }));

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-card">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        By workflow
      </h3>
      <p className="mt-1 text-lg font-semibold text-zinc-900">
        Ownership distribution
      </p>
      <div className="mt-4 h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <PieChart>
            <Pie
              data={chartData}
              cx="50%"
              cy="50%"
              innerRadius={60}
              outerRadius={90}
              paddingAngle={2}
              dataKey="value"
              label={({ name, percent }) =>
                `${name} ${(percent * 100).toFixed(0)}%`
              }
            >
              {chartData.map((entry, index) => (
                <Cell key={entry.name} fill={COLORS[index % COLORS.length]} />
              ))}
            </Pie>
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e4e4e7",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
              }}
              formatter={(value: number) => [value, "Incidents"]}
            />
          </PieChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
