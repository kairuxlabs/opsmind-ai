import { useState, useEffect, useCallback } from "react";
import { useParams, Link } from "react-router-dom";
import { getWorkflow, submitFeedback } from "../api/client.js";
import HumanApproval from "./HumanApproval.jsx";
import AgentMonitor from "./AgentMonitor.jsx";

const STATUS_STYLE = {
  planning: "text-yellow-400",
  running: "text-blue-400",
  waiting_approval: "text-orange-400",
  executing: "text-purple-400",
  completed: "text-green-400",
  failed: "text-red-400",
  rejected: "text-gray-400",
};

function ConfidenceMeter({ value }) {
  const pct = Math.round((value || 0) * 100);
  const color = pct >= 80 ? "bg-green-500" : pct >= 60 ? "bg-yellow-500" : "bg-red-500";
  return (
    <div className="flex items-center gap-3">
      <div className="flex-1 bg-gray-800 rounded-full h-2">
        <div className={`${color} h-2 rounded-full transition-all`} style={{ width: `${pct}%` }} />
      </div>
      <span className="text-sm font-bold text-white w-10 text-right">{pct}%</span>
    </div>
  );
}

function FeedbackButtons({ workflowId, currentFeedback, onFeedback }) {
  const [sent, setSent] = useState(currentFeedback || null);

  const send = async (rating) => {
    setSent(rating);
    try {
      await submitFeedback(workflowId, rating);
      onFeedback?.(rating);
    } catch {
      setSent(null);
    }
  };

  if (sent) {
    return (
      <p className="text-sm text-gray-400">
        Feedback recorded: <span className="text-white font-medium">{sent === "helpful" ? "👍 Helpful" : "👎 Not Helpful"}</span>
      </p>
    );
  }

  return (
    <div className="flex items-center gap-3">
      <span className="text-sm text-gray-400">Was this helpful?</span>
      <button
        onClick={() => send("helpful")}
        className="px-3 py-1 bg-gray-800 hover:bg-green-900 border border-gray-700 hover:border-green-600 rounded-lg text-sm transition-colors"
      >
        👍 Helpful
      </button>
      <button
        onClick={() => send("not_helpful")}
        className="px-3 py-1 bg-gray-800 hover:bg-red-900 border border-gray-700 hover:border-red-600 rounded-lg text-sm transition-colors"
      >
        👎 Not Helpful
      </button>
    </div>
  );
}

export default function WorkflowView() {
  const { id } = useParams();
  const [wf, setWf] = useState(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(() => {
    getWorkflow(id)
      .then((data) => { setWf(data); setLoading(false); })
      .catch(() => setLoading(false));
  }, [id]);

  useEffect(() => { refresh(); }, [refresh]);

  useEffect(() => {
    if (!wf) return;
    if (["planning", "running", "executing"].includes(wf.status)) {
      const t = setInterval(refresh, 2000);
      return () => clearInterval(t);
    }
  }, [wf?.status, refresh]);

  if (loading) {
    return <div className="p-10 text-center text-gray-400 animate-pulse">Loading workflow…</div>;
  }

  if (!wf) {
    return (
      <div className="p-10 text-center">
        <p className="text-red-400 mb-4">Workflow not found.</p>
        <Link to="/" className="text-brand-600 underline">← Back</Link>
      </div>
    );
  }

  const executedAgents = new Set((wf.agent_logs || []).map((l) => l.agent));
  const allAgents = ["supervisor", ...(wf.route || []), "executor", "memory"];
  const uniqueAgents = [...new Set(allAgents)];

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">
            ← Command Center
          </Link>
          <h2 className="text-2xl font-bold">Workflow</h2>
          <p className="text-gray-600 text-xs font-mono mt-0.5">{id}</p>
        </div>
        <span className={`font-semibold uppercase text-sm tracking-wide ${STATUS_STYLE[wf.status] || "text-gray-400"}`}>
          ● {wf.status?.replace(/_/g, " ")}
        </span>
      </div>

      {/* Request + Route */}
      <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-6">
        <p className="text-gray-500 text-xs mb-1 uppercase tracking-wide">Request</p>
        <p className="font-medium text-gray-100">{wf.user_query}</p>
        {wf.goal && (
          <p className="text-brand-600 text-sm mt-2">
            Goal: <span className="font-mono bg-gray-800 px-1.5 py-0.5 rounded text-xs">{wf.goal}</span>
          </p>
        )}
        {wf.route?.length > 0 && (
          <div className="mt-3">
            <p className="text-gray-600 text-xs uppercase tracking-wide mb-1.5">Agent Route</p>
            <div className="flex items-center gap-1.5 flex-wrap">
              <span className="text-xs bg-brand-900 text-brand-400 border border-brand-700 px-2 py-0.5 rounded font-mono">supervisor</span>
              {wf.route.map((a, i) => (
                <span key={i} className="flex items-center gap-1">
                  <span className="text-gray-600 text-xs">→</span>
                  <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-mono">{a}</span>
                </span>
              ))}
              <span className="text-gray-600 text-xs">→</span>
              <span className="text-xs bg-gray-800 text-gray-300 px-2 py-0.5 rounded font-mono">executor</span>
            </div>
          </div>
        )}
      </div>

      {/* Agent Monitor */}
      <AgentMonitor agents={uniqueAgents} executedAgents={executedAgents} agentLogs={wf.agent_logs || []} />

      {/* Health Score */}
      {wf.health_score > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-6">
          <div className="flex items-center justify-between mb-2">
            <p className="text-gray-400 text-sm font-medium">Enterprise Health Score</p>
            <span className={`text-2xl font-bold ${wf.health_score >= 70 ? "text-green-400" : wf.health_score >= 50 ? "text-yellow-400" : "text-red-400"}`}>
              {wf.health_score}
            </span>
          </div>
          <ConfidenceMeter value={wf.health_score / 100} />
        </div>
      )}

      {/* Human Approval */}
      {wf.status === "waiting_approval" && (
        <>
          {/* Confidence + Explanation before approval */}
          {wf.confidence > 0 && (
            <div className="bg-gray-900 rounded-xl border border-gray-800 p-5 mb-4">
              <p className="text-gray-400 text-sm font-medium mb-2">AI Confidence</p>
              <ConfidenceMeter value={wf.confidence} />
              {wf.explanation?.length > 0 && (
                <div className="mt-4">
                  <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Why AI recommends this</p>
                  <ul className="space-y-1">
                    {wf.explanation.map((e, i) => (
                      <li key={i} className="text-sm text-gray-300 flex gap-2">
                        <span className="text-brand-600 flex-shrink-0">›</span>
                        {e}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
          <HumanApproval
            workflowId={id}
            recommendations={wf.recommendations}
            risks={wf.risks}
            insights={wf.insights}
            onDecision={refresh}
          />
        </>
      )}

      {/* Completed report */}
      {wf.status === "completed" && wf.execution_result && (
        <div className="bg-gray-900 rounded-xl border border-green-800 p-6 mt-6">
          <div className="flex items-start justify-between mb-4">
            <h3 className="font-bold text-green-400">✓ Report Generated</h3>
            {wf.confidence > 0 && (
              <div className="text-right">
                <p className="text-gray-500 text-xs mb-1">AI Confidence</p>
                <span className="text-white font-bold">{Math.round(wf.confidence * 100)}%</span>
              </div>
            )}
          </div>

          {wf.explanation?.length > 0 && (
            <div className="mb-4 p-3 bg-gray-800 rounded-lg">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Decision Reasoning</p>
              <ul className="space-y-1">
                {wf.explanation.map((e, i) => (
                  <li key={i} className="text-sm text-gray-300 flex gap-2">
                    <span className="text-brand-600 flex-shrink-0">›</span>{e}
                  </li>
                ))}
              </ul>
            </div>
          )}

          {wf.recommendations?.length > 0 && (
            <div className="mb-4">
              <p className="text-gray-500 text-xs uppercase tracking-wide mb-2">Recommendations</p>
              <ol className="space-y-3">
                {wf.recommendations.map((rec, i) => {
                  const text = typeof rec === "string" ? rec : rec.text;
                  const reasons = typeof rec === "string" ? [] : (rec.reasons || []);
                  return (
                    <li key={i} className="bg-gray-800 rounded-lg p-3 border border-gray-700">
                      <div className="flex gap-2 text-sm mb-1">
                        <span className="text-brand-600 font-bold shrink-0">{i + 1}.</span>
                        <span className="text-gray-200 font-medium">{text}</span>
                      </div>
                      {reasons.length > 0 && (
                        <ul className="ml-5 space-y-0.5">
                          {reasons.map((r, j) => (
                            <li key={j} className="text-xs text-gray-400 flex gap-1.5">
                              <span className="text-brand-700 flex-shrink-0">›</span>
                              {r}
                            </li>
                          ))}
                        </ul>
                      )}
                    </li>
                  );
                })}
              </ol>
            </div>
          )}

          <pre className="whitespace-pre-wrap text-sm text-gray-300 font-mono leading-relaxed mb-6">
            {wf.execution_result}
          </pre>

          <div className="border-t border-gray-800 pt-4">
            <FeedbackButtons workflowId={id} currentFeedback={wf.feedback} onFeedback={refresh} />
          </div>
        </div>
      )}

      {wf.status === "rejected" && (
        <div className="bg-gray-900 rounded-xl border border-gray-700 p-8 mt-6 text-center">
          <p className="text-gray-400 mb-3">Workflow rejected.</p>
          <Link to="/" className="text-brand-600 underline">Create new workflow →</Link>
        </div>
      )}
    </div>
  );
}
