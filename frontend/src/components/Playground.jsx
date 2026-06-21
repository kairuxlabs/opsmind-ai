import { useState } from "react";
import { Link } from "react-router-dom";
import { runPlayground } from "../api/client.js";

const AGENTS = [
  { id: "supervisor", label: "Supervisor", desc: "Parses user request → goal + route", icon: "⚙" },
  { id: "planner", label: "Planner", desc: "Breaks goal into ordered tasks", icon: "📋" },
  { id: "analytics", label: "Analytics", desc: "KPIs, risk scoring, health score", icon: "📊" },
  { id: "decision", label: "Decision", desc: "Structured recommendations + confidence", icon: "🧠" },
  { id: "critique", label: "Critique", desc: "AI self-review of recommendations", icon: "🔍" },
];

const EXAMPLES = {
  supervisor: "Prepare a weekly operations report for Q2",
  planner: "Generate sprint planning tasks for mobile app launch",
  analytics: "Analyze current project portfolio risks and KPIs",
  decision: "What should we prioritize for the next two weeks?",
  critique: "Review the current action plan and flag any gaps",
};

function JsonView({ data }) {
  const text = JSON.stringify(data, null, 2);
  return (
    <pre className="text-xs text-gray-300 font-mono whitespace-pre-wrap leading-relaxed overflow-auto max-h-96">
      {text}
    </pre>
  );
}

export default function Playground() {
  const [selectedAgent, setSelectedAgent] = useState("supervisor");
  const [query, setQuery] = useState(EXAMPLES.supervisor);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAgentChange = (agentId) => {
    setSelectedAgent(agentId);
    setQuery(EXAMPLES[agentId] || "");
    setResult(null);
    setError(null);
  };

  const run = async () => {
    if (!query.trim()) return;
    setLoading(true);
    setError(null);
    setResult(null);
    try {
      const data = await runPlayground(selectedAgent, query.trim());
      setResult(data);
    } catch (e) {
      setError(e?.response?.data?.detail || "Agent call failed");
    } finally {
      setLoading(false);
    }
  };

  const agent = AGENTS.find((a) => a.id === selectedAgent);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">← Command Center</Link>
        <h2 className="text-2xl font-bold">Agent Playground</h2>
        <p className="text-gray-500 text-sm mt-1">Test individual agents in isolation — see raw output and latency</p>
      </div>

      <div className="grid grid-cols-5 gap-3 mb-6">
        {AGENTS.map((a) => (
          <button
            key={a.id}
            onClick={() => handleAgentChange(a.id)}
            className={`flex flex-col items-center gap-1.5 p-3 rounded-xl border transition-all text-center ${
              selectedAgent === a.id
                ? "bg-brand-900/30 border-brand-600 text-white"
                : "bg-gray-900 border-gray-800 text-gray-400 hover:border-gray-700 hover:text-gray-200"
            }`}
          >
            <span className="text-xl">{a.icon}</span>
            <span className="text-xs font-semibold">{a.label}</span>
          </button>
        ))}
      </div>

      {agent && (
        <div className="bg-gray-900 border border-gray-800 rounded-xl p-4 mb-4 flex items-center gap-3">
          <span className="text-2xl">{agent.icon}</span>
          <div>
            <p className="font-medium text-gray-200 text-sm">{agent.label} Agent</p>
            <p className="text-gray-500 text-xs">{agent.desc}</p>
          </div>
        </div>
      )}

      <div className="mb-4">
        <label className="text-xs text-gray-400 uppercase tracking-wide block mb-2">Query</label>
        <textarea
          className="w-full bg-gray-900 border border-gray-800 focus:border-brand-600 focus:outline-none rounded-xl px-4 py-3 text-sm text-gray-100 resize-none"
          rows={3}
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Enter a query for the selected agent…"
          disabled={loading}
        />
      </div>

      <button
        onClick={run}
        disabled={loading || !query.trim()}
        className="w-full bg-brand-600 hover:bg-brand-700 disabled:opacity-50 disabled:cursor-not-allowed text-white font-semibold py-2.5 rounded-xl transition-colors mb-8"
      >
        {loading ? (
          <span className="flex items-center justify-center gap-2">
            <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Running {agent?.label} Agent…
          </span>
        ) : (
          `▶ Run ${agent?.label} Agent`
        )}
      </button>

      {error && (
        <div className="bg-red-950/30 border border-red-800 rounded-xl p-4 mb-6">
          <p className="text-red-400 text-sm font-medium">Error</p>
          <p className="text-red-300 text-sm mt-1">{error}</p>
        </div>
      )}

      {result && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="font-semibold text-gray-200">Output</h3>
            <div className="flex items-center gap-3">
              <span className="text-xs text-gray-500">
                {agent?.icon} {agent?.label}
              </span>
              <span className={`text-xs font-mono font-bold px-2 py-0.5 rounded ${
                result.latency_ms < 2000 ? "bg-green-900 text-green-400" :
                result.latency_ms < 5000 ? "bg-yellow-900 text-yellow-400" : "bg-red-900 text-red-400"
              }`}>
                {result.latency_ms}ms
              </span>
            </div>
          </div>

          <div className="bg-gray-900 border border-gray-800 rounded-xl p-5">
            <JsonView data={result.output} />
          </div>

          {/* Highlight key fields based on agent type */}
          {result.output.goal && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Goal</p>
              <p className="text-sm font-mono text-brand-400">{result.output.goal}</p>
              {result.output.route?.length > 0 && (
                <div className="mt-2 flex items-center gap-1.5 flex-wrap">
                  {result.output.route.map((a, i) => (
                    <span key={i} className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-mono">{a}</span>
                  ))}
                </div>
              )}
            </div>
          )}

          {result.output.confidence != null && (
            <div className="bg-gray-900 border border-gray-800 rounded-xl p-4">
              <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Confidence</p>
              <p className="text-2xl font-bold text-white">
                {Math.round(result.output.confidence * 100)}%
              </p>
            </div>
          )}

          {result.output.critique_passed != null && (
            <div className={`border rounded-xl p-4 ${result.output.critique_passed ? "bg-green-950/20 border-green-800" : "bg-yellow-950/20 border-yellow-800"}`}>
              <p className="text-xs text-gray-400 uppercase tracking-wide mb-1">Critique Result</p>
              <p className={`font-semibold ${result.output.critique_passed ? "text-green-400" : "text-yellow-400"}`}>
                {result.output.critique_passed ? "✓ Passed" : "⚠ Issues Found"}
              </p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
