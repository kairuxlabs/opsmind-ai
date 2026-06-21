import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { createWorkflow, getMetrics, getWorkflows, ingestFile } from "../api/client.js";

const TEMPLATES = [
  {
    icon: "📊",
    label: "Weekly Ops Report",
    query: "Prepare a comprehensive weekly operations report, analyze project health, identify top risks, and suggest priorities for next week",
  },
  {
    icon: "⚠",
    label: "Project Risk Analysis",
    query: "Analyze all current project portfolio risks, identify critical blockers, and provide mitigation recommendations with owners",
  },
  {
    icon: "⚡",
    label: "Quick Decision",
    query: "Give me a quick recommendation on resource allocation across all active projects based on current velocity and risk data",
  },
  {
    icon: "🔄",
    label: "Sprint Retrospective",
    query: "Conduct a sprint retrospective: what went well, what blockers slowed velocity, and what process changes should we make next sprint",
  },
];

const STATUS_STYLE = {
  starting: "text-gray-400 bg-gray-800",
  planning: "text-yellow-400 bg-yellow-900/30",
  running: "text-blue-400 bg-blue-900/30",
  waiting_approval: "text-orange-400 bg-orange-900/30",
  executing: "text-purple-400 bg-purple-900/30",
  completed: "text-green-400 bg-green-900/30",
  failed: "text-red-400 bg-red-900/30",
  rejected: "text-gray-500 bg-gray-800",
};

function timeAgo(iso) {
  if (!iso) return "";
  const diff = Date.now() - new Date(iso).getTime();
  const m = Math.floor(diff / 60000);
  if (m < 1) return "just now";
  if (m < 60) return `${m}m ago`;
  const h = Math.floor(m / 60);
  if (h < 24) return `${h}h ago`;
  return `${Math.floor(h / 24)}d ago`;
}

export default function Dashboard() {
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [workflows, setWorkflows] = useState([]);
  const [error, setError] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => {});
    getWorkflows(8).then(setWorkflows).catch(() => {});
  }, []);

  const launch = async (query) => {
    if (!query.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await createWorkflow(query);
      navigate(`/workflow/${data.workflow_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create workflow. Is the backend running?");
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    launch(request);
  };

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    try {
      const result = await ingestFile(file);
      setUploadMsg(`✓ Ingested ${result.ingested} chunks from ${result.filename}`);
    } catch {
      setUploadMsg("✗ Upload failed");
    }
  };

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-1">Command Center</h1>
        <p className="text-gray-400 text-sm">
          AI Digital Teammates collaborate autonomously to support your decisions.
        </p>
      </div>

      {/* Templates */}
      <div className="mb-4">
        <p className="text-xs text-gray-500 uppercase tracking-wide mb-3">Quick Templates</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
          {TEMPLATES.map((t) => (
            <button
              key={t.label}
              onClick={() => setRequest(t.query)}
              disabled={loading}
              className="flex flex-col items-start gap-1.5 bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-3.5 text-left transition-all group disabled:opacity-50"
            >
              <span className="text-xl">{t.icon}</span>
              <span className="text-xs font-semibold text-gray-300 group-hover:text-white transition-colors leading-tight">
                {t.label}
              </span>
            </button>
          ))}
        </div>
      </div>

      {/* Workflow submission */}
      <form onSubmit={handleSubmit} className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-8">
        <label className="block text-sm text-gray-400 mb-2">What do you need today?</label>
        <textarea
          className="w-full bg-gray-800 rounded-lg px-4 py-3 text-gray-100 border border-gray-700 focus:outline-none focus:border-brand-600 resize-none"
          rows={3}
          placeholder="Describe your workflow request…"
          value={request}
          onChange={(e) => setRequest(e.target.value)}
        />
        {error && <p className="text-red-400 text-sm mt-2">{error}</p>}
        <div className="flex items-center gap-4 mt-4">
          <button
            type="submit"
            disabled={loading || !request.trim()}
            className="bg-brand-600 hover:bg-brand-700 disabled:opacity-50 text-white font-semibold px-6 py-2 rounded-lg transition-colors"
          >
            {loading ? "Launching AI agents…" : "▶ Run AI Workflow"}
          </button>
          <label className="text-sm text-gray-400 cursor-pointer hover:text-gray-200 transition-colors">
            <input type="file" accept=".csv,.txt,.pdf" className="hidden" onChange={handleUpload} />
            + Upload knowledge file
          </label>
        </div>
        {uploadMsg && <p className="text-green-400 text-sm mt-2">{uploadMsg}</p>}
      </form>

      {/* Metrics */}
      {metrics && (
        <div className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Live Metrics</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Workflows Today", value: metrics.workflows_today, color: "text-blue-400" },
              { label: "Avg Latency", value: `${metrics.avg_latency_ms}ms`, color: "text-purple-400" },
              { label: "Human Approvals", value: metrics.human_approvals, color: "text-green-400" },
              { label: "Risks Detected", value: metrics.risks_detected, color: "text-orange-400" },
            ].map((m) => (
              <div key={m.label} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
                <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Workflows */}
      {workflows.length > 0 && (
        <div className="mb-8">
          <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Recent Workflows</h2>
          <div className="space-y-2">
            {workflows.map((wf) => (
              <Link
                key={wf.id}
                to={`/workflow/${wf.id}`}
                className="flex items-center gap-3 bg-gray-900 border border-gray-800 hover:border-gray-700 rounded-xl px-4 py-3 transition-colors group"
              >
                <span className={`text-xs font-semibold px-2 py-0.5 rounded shrink-0 ${STATUS_STYLE[wf.status] || "text-gray-400 bg-gray-800"}`}>
                  {wf.status?.replace(/_/g, " ")}
                </span>
                <span className="text-sm text-gray-300 truncate flex-1 group-hover:text-white transition-colors">
                  {wf.user_query}
                </span>
                <span className="text-xs text-gray-600 shrink-0">{timeAgo(wf.created_at)}</span>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* System links */}
      <div>
        <h2 className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">System</h2>
        <div className="grid grid-cols-3 gap-4">
          {[
            { to: "/insights", title: "Insights", desc: "Agent performance and analytics" },
            { to: "/memory", title: "Memory Center", desc: "Workflow history and feedback" },
            { to: "/observability", title: "Observability", desc: "Live metrics and system health" },
          ].map((l) => (
            <Link
              key={l.to}
              to={l.to}
              className="bg-gray-900 border border-gray-800 hover:border-gray-600 rounded-xl p-5 transition-colors group"
            >
              <p className="text-white font-medium mb-1 group-hover:text-brand-400 transition-colors">{l.title}</p>
              <p className="text-gray-500 text-xs">{l.desc}</p>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
