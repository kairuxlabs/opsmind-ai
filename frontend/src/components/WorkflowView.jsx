import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { getWorkflow } from "../api/client.js";
import HumanApproval from "./HumanApproval.jsx";
import AgentMonitor from "./AgentMonitor.jsx";

const AGENTS = ["supervisor", "planner", "knowledge", "analytics", "decision", "executor", "memory"];

const STATUS_STYLE = {
  planning: "text-yellow-400",
  running: "text-blue-400",
  waiting_approval: "text-orange-400",
  executing: "text-purple-400",
  completed: "text-green-400",
  failed: "text-red-400",
  rejected: "text-gray-400",
};

export default function WorkflowView() {
  const { id } = useParams();
  const [wf, setWf] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    getWorkflow(id)
      .then((data) => {
        setWf(data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  useEffect(() => {
    refresh();
  }, [refresh]);

  useEffect(() => {
    if (!wf) return;
    if (["planning", "running", "executing"].includes(wf.status)) {
      const t = setInterval(refresh, 2000);
      return () => clearInterval(t);
    }
  }, [wf?.status, refresh]);

  if (loading) {
    return (
      <div className="p-10 text-center text-gray-400">
        <div className="animate-pulse">Loading workflow…</div>
      </div>
    );
  }

  if (!wf) {
    return (
      <div className="p-10 text-center">
        <p className="text-red-400 mb-4">Workflow not found.</p>
        <Link to="/" className="text-brand-600 underline">← Back to Dashboard</Link>
      </div>
    );
  }

  const executedAgents = new Set((wf.agent_logs || []).map((l) => l.agent));

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">
            ← Command Center
          </Link>
          <h2 className="text-2xl font-bold">Workflow</h2>
          <p className="text-gray-600 text-xs font-mono mt-0.5">{id}</p>
        </div>
        <span
          className={`font-semibold uppercase text-sm tracking-wide ${
            STATUS_STYLE[wf.status] || "text-gray-400"
          }`}
        >
          ● {wf.status?.replace(/_/g, " ")}
        </span>
      </div>

      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-6">
        <p className="text-gray-500 text-xs mb-1 uppercase tracking-wide">Request</p>
        <p className="font-medium text-gray-100">{wf.user_query}</p>
        {wf.goal && (
          <p className="text-brand-600 text-sm mt-2">
            Goal:{" "}
            <span className="font-mono bg-gray-800 px-1.5 py-0.5 rounded text-xs">
              {wf.goal}
            </span>
          </p>
        )}
        {wf.tasks?.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-1.5">
            {wf.tasks.map((t, i) => (
              <span
                key={i}
                className="text-xs bg-gray-800 text-gray-400 px-2 py-0.5 rounded font-mono"
              >
                {t}
              </span>
            ))}
          </div>
        )}
      </div>

      <AgentMonitor
        agents={AGENTS}
        executedAgents={executedAgents}
        agentLogs={wf.agent_logs || []}
      />

      {wf.status === "waiting_approval" && (
        <HumanApproval
          workflowId={id}
          recommendations={wf.recommendations}
          risks={wf.risks}
          insights={wf.insights}
          onDecision={refresh}
        />
      )}

      {wf.status === "completed" && wf.execution_result && (
        <div className="bg-gray-900 rounded-xl border border-green-800 p-6 mt-6">
          <h3 className="font-bold text-green-400 mb-4">✓ Report Generated</h3>
          <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed">
            {wf.execution_result}
          </pre>
        </div>
      )}

      {wf.status === "rejected" && (
        <div className="bg-gray-900 rounded-xl border border-gray-700 p-8 mt-6 text-center">
          <p className="text-gray-400 mb-3">Workflow rejected.</p>
          <Link to="/" className="text-brand-600 underline">
            Create new workflow →
          </Link>
        </div>
      )}
    </div>
  );
}
