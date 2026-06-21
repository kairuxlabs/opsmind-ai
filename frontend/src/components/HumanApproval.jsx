import { useState } from "react";
import { submitApproval } from "../api/client.js";

const RISK_COLORS = {
  Critical: "bg-red-900 text-red-300",
  High: "bg-orange-900 text-orange-300",
  Medium: "bg-yellow-900 text-yellow-300",
  Low: "bg-green-900 text-green-300",
};

export default function HumanApproval({ workflowId, recommendations, risks, insights, onDecision }) {
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);

  const decide = async (approved) => {
    setLoading(true);
    try {
      await submitApproval(workflowId, approved, comment);
      onDecision();
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-900 rounded-xl border border-orange-700 p-6 mt-6">
      <h3 className="font-bold text-orange-400 mb-4 text-lg">⏳ Human Approval Required</h3>

      {insights?.summary && (
        <div className="mb-4 p-3 bg-gray-800 rounded-lg border border-gray-700">
          <p className="text-xs text-gray-400 mb-1 uppercase tracking-wide">AI Insight</p>
          <p className="text-sm text-gray-200">{insights.summary}</p>
          {insights.key_finding && (
            <p className="text-xs text-gray-400 mt-1">{insights.key_finding}</p>
          )}
        </div>
      )}

      {risks?.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">
            Identified Risks
          </p>
          <div className="space-y-2">
            {risks.map((r, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span
                  className={`px-2 py-0.5 rounded text-xs font-bold shrink-0 mt-0.5 ${
                    RISK_COLORS[r.risk_level] || "bg-gray-700 text-gray-300"
                  }`}
                >
                  {r.risk_level}
                </span>
                <span>
                  <span className="font-medium text-gray-200">{r.project}</span>
                  {r.reason && <span className="text-gray-400"> — {r.reason}</span>}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {recommendations?.length > 0 && (
        <div className="mb-4">
          <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">
            Recommended Actions
          </p>
          <ol className="space-y-2">
            {recommendations.map((rec, i) => (
              <li key={i} className="flex gap-2 text-sm">
                <span className="text-brand-600 font-bold shrink-0">{i + 1}.</span>
                <span className="text-gray-200">{rec}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      <textarea
        className="w-full bg-gray-800 rounded-lg px-3 py-2 text-sm border border-gray-700 focus:outline-none focus:border-brand-600 mb-4 resize-none text-gray-200"
        rows={2}
        placeholder="Optional comment for audit trail…"
        value={comment}
        onChange={(e) => setComment(e.target.value)}
      />

      <div className="flex gap-3">
        <button
          onClick={() => decide(true)}
          disabled={loading}
          className="flex-1 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
        >
          ✓ Approve & Execute
        </button>
        <button
          onClick={() => decide(false)}
          disabled={loading}
          className="flex-1 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
        >
          ✗ Reject
        </button>
      </div>
    </div>
  );
}
