import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getMemoryHistory } from "../api/client.js";

function RecordCard({ record }) {
  const { key, value, updated_at } = record;
  const type = key.split(":")[0];
  const id = key.split(":")[1]?.slice(0, 8) + "…";

  const typeLabel = {
    workflow_history: { label: "Workflow", color: "text-blue-400 bg-blue-900/30 border-blue-800" },
    recommendation_history: { label: "Recommendations", color: "text-brand-400 bg-brand-900/30 border-brand-800" },
    feedback_history: { label: "Feedback", color: "text-green-400 bg-green-900/30 border-green-800" },
  }[type] || { label: type, color: "text-gray-400 bg-gray-800 border-gray-700" };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium px-2 py-0.5 rounded border ${typeLabel.color}`}>
            {typeLabel.label}
          </span>
          <span className="text-gray-600 text-xs font-mono">{id}</span>
        </div>
        <span className="text-gray-600 text-xs">
          {updated_at ? new Date(updated_at).toLocaleString() : "—"}
        </span>
      </div>

      {type === "workflow_history" && (
        <div className="space-y-1.5">
          <p className="text-sm text-gray-200 font-medium">{value.goal?.replace(/_/g, " ")}</p>
          <p className="text-xs text-gray-500 line-clamp-2">{value.query}</p>
          <div className="flex items-center gap-3 mt-2">
            <span className={`text-xs ${value.approved ? "text-green-400" : "text-gray-500"}`}>
              {value.approved ? "✓ Approved" : "✗ Not approved"}
            </span>
            {value.route?.length > 0 && (
              <span className="text-xs text-gray-600">Route: {value.route.join(" → ")}</span>
            )}
          </div>
        </div>
      )}

      {type === "recommendation_history" && (
        <div className="space-y-2">
          <p className="text-sm text-gray-200 font-medium">{value.goal?.replace(/_/g, " ")}</p>
          {value.confidence > 0 && (
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                <div
                  className="bg-brand-600 h-1.5 rounded-full"
                  style={{ width: `${Math.round(value.confidence * 100)}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">{Math.round(value.confidence * 100)}% confidence</span>
            </div>
          )}
          {value.recommendations?.slice(0, 2).map((r, i) => (
            <p key={i} className="text-xs text-gray-500 line-clamp-1">› {r}</p>
          ))}
          {value.feedback && (
            <span className="text-xs text-gray-400">
              {value.feedback === "helpful" ? "👍 Helpful" : "👎 Not Helpful"}
            </span>
          )}
        </div>
      )}

      {type === "feedback_history" && (
        <p className="text-sm text-gray-300">
          {value.rating === "helpful" ? "👍 Marked as Helpful" : "👎 Marked as Not Helpful"}
        </p>
      )}
    </div>
  );
}

export default function MemoryCenter() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMemoryHistory(30)
      .then(setData)
      .catch(() => setData({ records: [], count: 0 }))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-8">
        <div>
          <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">← Command Center</Link>
          <h2 className="text-2xl font-bold">Memory Center</h2>
          <p className="text-gray-500 text-sm mt-1">Workflow history, recommendations, and feedback</p>
        </div>
        {data && (
          <span className="text-gray-500 text-sm">{data.count} records</span>
        )}
      </div>

      {loading && (
        <div className="text-center text-gray-500 py-20 animate-pulse">Loading memory…</div>
      )}

      {!loading && (!data?.records?.length) && (
        <div className="text-center text-gray-600 py-20">
          <p className="text-lg mb-2">No memory records yet</p>
          <p className="text-sm">Complete a workflow to see history here</p>
          <Link to="/" className="text-brand-600 text-sm mt-4 inline-block">Create a workflow →</Link>
        </div>
      )}

      {!loading && data?.records?.length > 0 && (
        <div className="space-y-4">
          {data.records.map((record, i) => (
            <RecordCard key={i} record={record} />
          ))}
        </div>
      )}
    </div>
  );
}
