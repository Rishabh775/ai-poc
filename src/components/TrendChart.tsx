import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface TrendChartProps {
  data: Array<{ date: string; count: number }>;
}

export function TrendChart({ data }: TrendChartProps) {
  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-6 shadow-card">
      <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-500">
        Incidents over time
      </h3>
      <p className="mt-1 text-lg font-semibold text-zinc-900">90-day trend</p>
      <div className="mt-4 h-[260px]">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e4e4e7" vertical={false} />
            <XAxis
              dataKey="date"
              tick={{ fontSize: 11, fill: "#71717a" }}
              tickFormatter={(value) => {
                const date = new Date(value);
                return `${date.getMonth() + 1}/${date.getDate()}`;
              }}
            />
            <YAxis tick={{ fontSize: 11, fill: "#71717a" }} />
            <Tooltip
              contentStyle={{
                backgroundColor: "#fff",
                border: "1px solid #e4e4e7",
                borderRadius: "8px",
                boxShadow: "0 4px 6px -1px rgb(0 0 0 / 0.07)",
              }}
              labelFormatter={(value) => new Date(value).toLocaleDateString()}
            />
            <Line
              type="monotone"
              dataKey="count"
              stroke="#0ea5e9"
              strokeWidth={2}
              dot={{ fill: "#0ea5e9", r: 2.5 }}
              activeDot={{ r: 5, fill: "#0ea5e9", stroke: "#fff", strokeWidth: 2 }}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
