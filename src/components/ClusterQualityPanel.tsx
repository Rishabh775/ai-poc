import { Activity, CheckCircle2, AlertTriangle, XCircle, HelpCircle } from "lucide-react";
import { QualityMetrics } from "../services/api";

interface ClusterQualityPanelProps {
  quality: QualityMetrics;
}

export function ClusterQualityPanel({ quality }: ClusterQualityPanelProps) {
  const getSilhouetteIcon = (score: number | null) => {
    if (score === null) return <HelpCircle className="h-5 w-5 text-zinc-400" />;
    if (score >= 0.5) return <CheckCircle2 className="h-5 w-5 text-emerald-600" />;
    if (score >= 0.25) return <AlertTriangle className="h-5 w-5 text-amber-600" />;
    return <XCircle className="h-5 w-5 text-red-600" />;
  };

  const getSilhouetteColor = (score: number | null) => {
    if (score === null) return "bg-zinc-100";
    if (score >= 0.5) return "bg-emerald-50";
    if (score >= 0.25) return "bg-amber-50";
    return "bg-red-50";
  };

  const silhouette = quality.silhouette_score;
  const maxCount = Math.max(
    ...Object.values(quality.confusion_matrix).flatMap((row) =>
      Object.values(row)
    ),
    1
  );

  return (
    <div className="rounded-xl border border-zinc-200 bg-white shadow-card">
      <div className="border-b border-zinc-100 px-5 py-4">
        <div className="flex items-center gap-2">
          <Activity className="h-5 w-5 text-zinc-600" />
          <h2 className="text-lg font-semibold text-zinc-900">
            Clustering Quality
          </h2>
        </div>
      </div>

      <div className="p-5 space-y-6">
        <div className={`rounded-lg p-4 ${getSilhouetteColor(silhouette)}`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              {getSilhouetteIcon(silhouette)}
              <div>
                <p className="font-medium text-zinc-900">Silhouette Score</p>
                <p className="text-sm text-zinc-600">
                  {quality.silhouette_interpretation}
                </p>
              </div>
            </div>
            <div className="text-right">
              <p className="text-2xl font-bold text-zinc-900">
                {silhouette !== null ? silhouette.toFixed(3) : "N/A"}
              </p>
              <p className="text-xs text-zinc-500">range: -1 to 1</p>
            </div>
          </div>
          {silhouette !== null && (
            <div className="mt-3">
              <div className="h-2 rounded-full bg-zinc-200 overflow-hidden">
                <div
                  className={`h-full ${
                    silhouette >= 0.5
                      ? "bg-emerald-500"
                      : silhouette >= 0.25
                      ? "bg-amber-500"
                      : "bg-red-500"
                  }`}
                  style={{ width: `${Math.max(0, silhouette * 100)}%` }}
                />
              </div>
              <div className="mt-1 flex justify-between text-xs text-zinc-500">
                <span>Poor</span>
                <span>Fair</span>
                <span>Good</span>
              </div>
            </div>
          )}
        </div>

        <div>
          <h3 className="text-sm font-medium text-zinc-700 mb-3">
            Confusion Matrix
            <span className="font-normal text-zinc-500 ml-2">
              (Ground Truth vs Clusters)
            </span>
          </h3>
          <div className="overflow-x-auto">
            <table className="w-full text-xs">
              <thead>
                <tr className="border-b border-zinc-200">
                  <th className="text-left py-2 px-1 font-medium text-zinc-600">
                    Category
                  </th>
                  {quality.cluster_labels.map((label) => (
                    <th
                      key={label}
                      className="text-center py-2 px-1 font-medium text-zinc-600"
                    >
                      {label}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {quality.ground_truth_categories.map((category) => {
                  const row = quality.confusion_matrix[category] || {};
                  const hasData = Object.values(row).some((v) => v > 0);
                  if (!hasData) return null;

                  return (
                    <tr key={category} className="border-b border-zinc-100">
                      <td className="py-2 px-1 font-medium text-zinc-700">
                        {category}
                      </td>
                      {quality.cluster_labels.map((clusterLabel) => {
                        const count = row[clusterLabel] || 0;
                        const intensity = count / maxCount;
                        return (
                          <td key={clusterLabel} className="text-center py-2 px-1">
                            {count > 0 ? (
                              <span
                                className={`inline-block px-2 py-1 rounded font-medium ${
                                  intensity > 0.5
                                    ? "bg-blue-600 text-white"
                                    : intensity > 0.25
                                    ? "bg-blue-400 text-white"
                                    : "bg-blue-200 text-blue-900"
                                }`}
                              >
                                {count}
                              </span>
                            ) : (
                              <span className="text-zinc-300">0</span>
                            )}
                          </td>
                        );
                      })}
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
          <p className="mt-2 text-xs text-zinc-500">
            Higher numbers indicate better cluster-category alignment
          </p>
        </div>

        <div className="grid grid-cols-2 gap-4 text-sm">
          <div className="bg-zinc-50 rounded-lg p-3">
            <p className="text-zinc-600">Total Clusters</p>
            <p className="text-lg font-semibold text-zinc-900">
              {quality.cluster_labels.length}
            </p>
          </div>
          <div className="bg-zinc-50 rounded-lg p-3">
            <p className="text-zinc-600">Categories</p>
            <p className="text-lg font-semibold text-zinc-900">
              {quality.ground_truth_categories.length}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
