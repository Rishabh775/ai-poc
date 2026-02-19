import { AlertCircle } from "lucide-react";

interface TopIssueCardProps {
  summary: string;
  criticalCount: number;
  highCount: number;
}

export function TopIssueCard({ summary, criticalCount, highCount }: TopIssueCardProps) {
  return (
    <div className="rounded-xl border border-amber-200/60 bg-gradient-to-br from-amber-50 to-orange-50 p-5 shadow-card">
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-amber-500/10 p-2">
          <AlertCircle className="h-5 w-5 text-amber-600" strokeWidth={2} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-xs font-semibold uppercase tracking-wider text-amber-700/80">
            Primary recurring pattern
          </p>
          <p className="mt-2 text-sm leading-relaxed text-zinc-800">
            {summary}
          </p>
          <div className="mt-3 flex items-center gap-3 text-xs text-zinc-500">
            {criticalCount > 0 && (
              <span className="font-medium text-red-600">
                {criticalCount} critical
              </span>
            )}
            {highCount > 0 && (
              <span className="font-medium text-orange-600">
                {highCount} high
              </span>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
