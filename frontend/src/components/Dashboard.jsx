import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { createWorkflow, getMetrics, ingestFile } from "../api/client.js";

export default function Dashboard() {
  const [request, setRequest] = useState("");
  const [loading, setLoading] = useState(false);
  const [metrics, setMetrics] = useState(null);
  const [error, setError] = useState("");
  const [uploadMsg, setUploadMsg] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    getMetrics().then(setMetrics).catch(() => {});
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!request.trim()) return;
    setLoading(true);
    setError("");
    try {
      const data = await createWorkflow(request);
      navigate(`/workflow/${data.workflow_id}`);
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to create workflow. Is the backend running?");
      setLoading(false);
    }
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
      <h1 className="text-3xl font-bold mb-2">Command Center</h1>
      <p className="text-gray-400 mb-8">
        Submit a request and let AI Digital Teammates handle it.
      </p>

      <form
        onSubmit={handleSubmit}
        className="bg-gray-900 rounded-xl p-6 border border-gray-800 mb-8"
      >
        <label className="block text-sm text-gray-400 mb-2">
          What do you need today?
        </label>
        <textarea
          className="w-full bg-gray-800 rounded-lg px-4 py-3 text-gray-100 border border-gray-700 focus:outline-none focus:border-brand-600 resize-none"
          rows={3}
          placeholder="Prepare weekly report and suggest priorities for next week"
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

      {metrics && (
        <div>
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wide mb-3">
            Today's Insights
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              { label: "Workflows Today", value: metrics.workflows_today, color: "text-blue-400" },
              { label: "Avg Latency", value: `${metrics.avg_latency_ms}ms`, color: "text-purple-400" },
              { label: "Human Approvals", value: metrics.human_approvals, color: "text-green-400" },
              { label: "Risks Detected", value: metrics.risks_detected, color: "text-orange-400" },
            ].map((m) => (
              <div
                key={m.label}
                className="bg-gray-900 rounded-lg p-4 border border-gray-800"
              >
                <p className="text-gray-500 text-xs mb-1">{m.label}</p>
                <p className={`text-2xl font-bold ${m.color}`}>{m.value}</p>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
