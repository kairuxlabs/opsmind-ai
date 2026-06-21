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

function RateBar({ label, value, target, good }) {
  const pct = Math.min(value ?? 0, 100);
  const ok = good ? pct >= target : pct <= target;
  return (
    <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
      <div className="flex-1">
        <div className="flex items-center justify-between mb-1">
          <span className="text-gray-300 text-sm">{label}</span>
          <div className="flex items-center gap-2">
            <span className="text-gray-500 text-xs">{good ? `≥${target}%` : `≤${target}%`}</span>
            <span className={ok ? "text-green-400 text-xs" : "text-red-400 text-xs"}>
              {ok ? "✓" : "✗"} {pct}%
            </span>
          </div>
        </div>
        <div className="w-full bg-gray-800 rounded-full h-1.5">
          <div
            className={`h-1.5 rounded-full transition-all ${ok ? "bg-green-500" : "bg-red-500"}`}
            style={{ width: `${pct}%` }}
          />
        </div>
      </div>
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
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
            <MetricCard
              label="Workflows Today"
              value={metrics?.workflows_today ?? 0}
              color="text-brand-400"
            />
            <MetricCard
              label="Avg Agent Latency"
              value={metrics?.avg_latency_ms ?? 0}
              unit="ms"
              color={metrics?.avg_latency_ms > 5000 ? "text-red-400" : "text-green-400"}
            />
            <MetricCard
              label="Completed"
              value={metrics?.human_approvals ?? 0}
              color="text-blue-400"
            />
            <MetricCard
              label="Risks Detected"
              value={metrics?.risks_detected ?? 0}
              color={metrics?.risks_detected > 5 ? "text-red-400" : "text-yellow-400"}
            />
          </div>

          <div className="grid grid-cols-3 gap-4 mb-8">
            <MetricCard
              label="Success Rate"
              value={metrics?.success_rate ?? 0}
              unit="%"
              color={(metrics?.success_rate ?? 0) >= 90 ? "text-green-400" : "text-yellow-400"}
            />
            <MetricCard
              label="Approval Rate"
              value={metrics?.approval_rate ?? 0}
              unit="%"
              color={(metrics?.approval_rate ?? 0) >= 70 ? "text-green-400" : "text-orange-400"}
            />
            <MetricCard
              label="Error Rate"
              value={metrics?.error_rate ?? 0}
              unit="%"
              color={(metrics?.error_rate ?? 0) > 10 ? "text-red-400" : "text-green-400"}
            />
          </div>

          {/* Langfuse tracing card */}
          <div className={`rounded-xl border p-5 mb-6 flex items-start gap-4 ${metrics?.langfuse_enabled ? "bg-purple-950/20 border-purple-800/50" : "bg-gray-900 border-gray-800"}`}>
            <div className="text-2xl leading-none mt-0.5">🔭</div>
            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between mb-1">
                <p className="font-semibold text-gray-200 text-sm">LLM Observability — Langfuse</p>
                {metrics?.langfuse_enabled ? (
                  <span className="text-xs bg-purple-900 text-purple-300 border border-purple-700 px-2 py-0.5 rounded font-medium">Active</span>
                ) : (
                  <span className="text-xs bg-gray-800 text-gray-500 border border-gray-700 px-2 py-0.5 rounded">Not Configured</span>
                )}
              </div>
              {metrics?.langfuse_enabled ? (
                <p className="text-xs text-gray-400">
                  Tracing token usage, latency, and errors per agent call.{" "}
                  <a href={metrics.langfuse_host} target="_blank" rel="noopener noreferrer" className="text-purple-400 underline hover:text-purple-300">
                    Open dashboard →
                  </a>
                </p>
              ) : (
                <p className="text-xs text-gray-500">
                  Set <code className="bg-gray-800 px-1 rounded">LANGFUSE_PUBLIC_KEY</code> and{" "}
                  <code className="bg-gray-800 px-1 rounded">LANGFUSE_SECRET_KEY</code> in <code className="bg-gray-800 px-1 rounded">.env</code> to enable per-agent LLM tracing.
                </p>
              )}
            </div>
          </div>

          <div className="bg-gray-900 rounded-xl border border-gray-800 p-6">
            <h3 className="font-semibold text-gray-200 mb-4">System Health</h3>
            <div className="space-y-3">
              <RateBar
                label="Workflow Success Rate"
                value={metrics?.success_rate}
                target={95}
                good={true}
              />
              <RateBar
                label="Human Approval Rate"
                value={metrics?.approval_rate}
                target={70}
                good={true}
              />
              <RateBar
                label="Error Rate"
                value={metrics?.error_rate}
                target={10}
                good={false}
              />
              <div className="flex items-center justify-between py-2 border-b border-gray-800 last:border-0">
                <span className="text-gray-300 text-sm">Agent Latency</span>
                <div className="flex items-center gap-2">
                  <span className="text-gray-500 text-xs">≤5000ms</span>
                  <span className={
                    (metrics?.avg_latency_ms ?? 0) <= 5000
                      ? "text-green-400 text-xs"
                      : "text-red-400 text-xs"
                  }>
                    {(metrics?.avg_latency_ms ?? 0) <= 5000 ? "✓" : "✗"} {metrics?.avg_latency_ms ?? 0}ms
                  </span>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
