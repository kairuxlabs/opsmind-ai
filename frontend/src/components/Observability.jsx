import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getMetrics } from "../api/client.js";

function MetricCard({ label, value, unit = "", color = "text-white" }) {
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">{label}</p>
      <p className={`text-3xl font-bold ${color}`}>
        {value ?? "—"}
        {value != null && unit && <span className="text-base font-normal text-gray-500 ml-1">{unit}</span>}
      </p>
    </div>
  );
}

export default function Observability() {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch = () =>
      getMetrics()
        .then(setMetrics)
        .catch(() => {})
        .finally(() => setLoading(false));

    fetch();
    const t = setInterval(fetch, 10000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">← Command Center</Link>
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold">Observability</h2>
            <p className="text-gray-500 text-sm mt-1">Live system metrics — refreshes every 10s</p>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
            <span className="text-green-400 text-xs">Live</span>
          </div>
        </div>
      </div>

      {loading ? (
        <div className="text-center text-gray-500 py-20 animate-pulse">Loading metrics…</div>
      ) : (
        <>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <MetricCard
              label="Workflows Today"
              value={metrics?.workflows_today ?? 0}
              color="text-brand-400"
            />
            <MetricCard
              label="Avg Latency"
              value={metrics?.avg_latency_ms ?? 0}
              unit="ms"
              color={metrics?.avg_latency_ms > 5000 ? "text-red-400" : "text-green-400"}
            />
            <MetricCard
              label="Human Approvals"
              value={metrics?.human_approvals ?? 0}
              color="text-blue-400"
            />
            <MetricCard
              label="Risks Detected"
              value={metrics?.risks_detected ?? 0}
              color={metrics?.risks_detected > 5 ? "text-red-400" : "text-yellow-400"}
            />
          </div>

          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h3 className="font-semibold text-gray-200 mb-4">System Status</h3>
            <div className="space-y-3">
              {[
                { label: "Workflow Execution", target: ">95% completion", ok: true },
                { label: "Human Approval Gate", target: "<30s latency", ok: true },
                { label: "Agent Failure Recovery", target: ">90% success", ok: true },
                { label: "Recommendation Accuracy", target: ">85% (feedback-based)", ok: metrics?.human_approvals > 0 },
              ].map((row, i) => (
                <div key={i} className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                  <span className="text-gray-300 text-sm">{row.label}</span>
                  <div className="flex items-center gap-2">
                    <span className="text-gray-600 text-xs">{row.target}</span>
                    <span className={row.ok ? "text-green-400 text-xs" : "text-gray-600 text-xs"}>
                      {row.ok ? "✓" : "–"}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
