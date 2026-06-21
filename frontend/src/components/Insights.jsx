import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import { getInsights, getMetrics } from "../api/client.js";

const AGENT_ICONS = {
  supervisor: "⚙",
  planner: "📋",
  knowledge: "📚",
  analytics: "📊",
  decision: "🧠",
  critique: "🔍",
  executor: "⚡",
  memory: "💾",
};

function LatencyBar({ value, max }) {
  const pct = max > 0 ? Math.max((value / max) * 100, 2) : 0;
  const color =
    value < 2000 ? "bg-green-600" : value < 5000 ? "bg-yellow-600" : "bg-red-600";
  return (
    <div className="flex items-center gap-2 flex-1">
      <div className="flex-1 bg-gray-800 rounded-full h-1.5">
        <div className={`${color} h-1.5 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-xs font-mono text-gray-400 w-16 text-right">{value}ms</span>
    </div>
  );
}

export default function Insights() {
  const [insights, setInsights] = useState(null);
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      getInsights().catch(() => ({ agent_performance: [] })),
      getMetrics().catch(() => null),
    ]).then(([ins, m]) => {
      setInsights(ins);
      setMetrics(m);
    }).finally(() => setLoading(false));
  }, []);

  const perf = insights?.agent_performance || [];
  const maxAvg = Math.max(...perf.map((p) => p.avg_latency_ms), 1);
  const totalRuns = perf.reduce((s, p) => s + p.total_runs, 0);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">← Command Center</Link>
        <h2 className="text-2xl font-bold">Insights</h2>
        <p className="text-gray-500 text-sm mt-1">Agent performance analytics and system intelligence</p>
      </div>

      {loading ? (
        <div className="text-center text-gray-500 py-20 animate-pulse">Loading insights…</div>
      ) : (
        <>
          {/* Summary cards */}
          {metrics && (
            <div className="grid grid-cols-3 gap-4 mb-8">
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Total Agent Runs</p>
                <p className="text-3xl font-bold text-brand-400">{totalRuns}</p>
                <p className="text-gray-600 text-xs mt-1">across all workflows</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Success Rate</p>
                <p className={`text-3xl font-bold ${(metrics.success_rate ?? 0) >= 90 ? "text-green-400" : "text-yellow-400"}`}>
                  {metrics.success_rate ?? 0}%
                </p>
                <p className="text-gray-600 text-xs mt-1">workflows completed</p>
              </div>
              <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
                <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Approval Rate</p>
                <p className={`text-3xl font-bold ${(metrics.approval_rate ?? 0) >= 70 ? "text-green-400" : "text-orange-400"}`}>
                  {metrics.approval_rate ?? 0}%
                </p>
                <p className="text-gray-600 text-xs mt-1">human approved</p>
              </div>
            </div>
          )}

          {/* Agent Performance Table */}
          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
            <h3 className="font-semibold text-gray-200 mb-5">Agent Performance</h3>

            {perf.length === 0 ? (
              <p className="text-gray-600 text-sm text-center py-8">
                No agent runs recorded yet. Run a workflow to populate performance data.
              </p>
            ) : (
              <div className="space-y-0">
                {/* Header */}
                <div className="flex items-center gap-4 pb-2 border-b border-gray-800 mb-2">
                  <div className="w-36 shrink-0">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">Agent</span>
                  </div>
                  <div className="flex-1">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">Avg Latency</span>
                  </div>
                  <div className="w-16 text-right shrink-0">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">Min</span>
                  </div>
                  <div className="w-16 text-right shrink-0">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">Max</span>
                  </div>
                  <div className="w-16 text-right shrink-0">
                    <span className="text-xs text-gray-500 uppercase tracking-wide">Runs</span>
                  </div>
                </div>

                {perf.map((p) => (
                  <div key={p.agent} className="flex items-center gap-4 py-3 border-b border-gray-800/60 last:border-0">
                    <div className="w-36 shrink-0 flex items-center gap-2">
                      <span className="text-base">{AGENT_ICONS[p.agent] ?? "●"}</span>
                      <span className="text-sm font-medium text-gray-200">{p.agent}</span>
                    </div>
                    <LatencyBar value={p.avg_latency_ms} max={maxAvg} />
                    <div className="w-16 text-right shrink-0">
                      <span className="text-xs text-gray-500 font-mono">{p.min_latency_ms}ms</span>
                    </div>
                    <div className="w-16 text-right shrink-0">
                      <span className="text-xs text-gray-500 font-mono">{p.max_latency_ms}ms</span>
                    </div>
                    <div className="w-16 text-right shrink-0">
                      <span className="text-xs text-gray-400 font-semibold">{p.total_runs}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Latency breakdown by tier */}
          {perf.length > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
              <h3 className="font-semibold text-gray-200 mb-4">Latency Tiers</h3>
              <div className="grid grid-cols-3 gap-4">
                {[
                  {
                    label: "Fast (<2s)",
                    color: "text-green-400",
                    bg: "bg-green-900/20 border-green-800/40",
                    agents: perf.filter((p) => p.avg_latency_ms < 2000),
                  },
                  {
                    label: "Medium (2–5s)",
                    color: "text-yellow-400",
                    bg: "bg-yellow-900/20 border-yellow-800/40",
                    agents: perf.filter((p) => p.avg_latency_ms >= 2000 && p.avg_latency_ms < 5000),
                  },
                  {
                    label: "Slow (>5s)",
                    color: "text-red-400",
                    bg: "bg-red-900/20 border-red-800/40",
                    agents: perf.filter((p) => p.avg_latency_ms >= 5000),
                  },
                ].map((tier) => (
                  <div key={tier.label} className={`border rounded-xl p-4 ${tier.bg}`}>
                    <p className={`text-xs font-semibold uppercase tracking-wide mb-2 ${tier.color}`}>
                      {tier.label}
                    </p>
                    {tier.agents.length === 0 ? (
                      <p className="text-gray-600 text-xs">None</p>
                    ) : (
                      <div className="space-y-1">
                        {tier.agents.map((a) => (
                          <div key={a.agent} className="flex items-center gap-1.5 text-xs text-gray-300">
                            <span>{AGENT_ICONS[a.agent] ?? "●"}</span>
                            <span>{a.agent}</span>
                            <span className="text-gray-500 ml-auto">{a.avg_latency_ms}ms</span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
}
