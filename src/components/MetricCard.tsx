import { LucideIcon } from "lucide-react";

interface MetricCardProps {
  title: string;
  value: string | number;
  icon: LucideIcon;
  trend?: string;
  iconColor?: string;
  hero?: boolean;
}

export function MetricCard({
  title,
  value,
  icon: Icon,
  trend,
  iconColor = "text-sky-600",
  hero = false,
}: MetricCardProps) {
  if (hero) {
    return (
      <div className="relative overflow-hidden rounded-xl bg-gradient-to-br from-zinc-900 to-zinc-800 p-6 text-white shadow-card">
        <div className="absolute right-4 top-4 opacity-20">
          <Icon className="h-16 w-16" strokeWidth={1.5} />
        </div>
        <p className="text-sm font-medium text-zinc-400">{title}</p>
        <p className="mt-2 text-4xl font-bold tracking-tight">{value}</p>
        {trend && (
          <p className="mt-1 text-sm text-zinc-400">{trend}</p>
        )}
      </div>
    );
  }

  return (
    <div className="rounded-xl border border-zinc-200 bg-white p-5 shadow-card transition-shadow hover:shadow-card-hover">
      <div className="flex items-start justify-between">
        <div>
          <p className="text-xs font-medium uppercase tracking-wider text-zinc-500">
            {title}
          </p>
          <p className="mt-2 text-2xl font-bold text-zinc-900">{value}</p>
          {trend && (
            <p className="mt-1 text-xs text-zinc-500">{trend}</p>
          )}
        </div>
        <div className={`rounded-lg bg-zinc-100 p-2.5 ${iconColor}`}>
          <Icon className="h-5 w-5" strokeWidth={2} />
        </div>
      </div>
    </div>
  );
}
