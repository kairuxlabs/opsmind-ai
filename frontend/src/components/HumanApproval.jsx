import { useState } from "react";
import { submitApproval } from "../api/client.js";

const RISK_COLORS = {
  Critical: "bg-red-900 text-red-300",
  High: "bg-orange-900 text-orange-300",
  Medium: "bg-yellow-900 text-yellow-300",
  Low: "bg-green-900 text-green-300",
};

function normaliseRecs(recommendations) {
  return (recommendations || []).map((r) =>
    typeof r === "string" ? { text: r, reasons: [] } : { text: r.text ?? "", reasons: r.reasons ?? [] }
  );
}

export default function HumanApproval({ workflowId, recommendations, risks, insights, onDecision }) {
  const [comment, setComment] = useState("");
  const [mode, setMode] = useState("view"); // "view" | "edit" | "submitting"
  const [editedRecs, setEditedRecs] = useState([]);

  const loading = mode === "submitting";

  const enterEdit = () => {
    setEditedRecs(normaliseRecs(recommendations));
    setMode("edit");
  };

  const updateText = (idx, text) =>
    setEditedRecs((prev) => prev.map((r, i) => (i === idx ? { ...r, text } : r)));

  const decide = async (approved, modified = null) => {
    setMode("submitting");
    try {
      await submitApproval(workflowId, approved, comment, modified);
      onDecision();
    } catch {
      setMode(modified ? "edit" : "view");
    }
  };

  const displayRecs = mode === "edit" ? editedRecs : normaliseRecs(recommendations);

  return (
    <div className="bg-gray-900 rounded-xl border border-orange-700 p-6 mt-6">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-bold text-orange-400 text-lg">⏳ Human Approval Required</h3>
        {mode === "edit" && (
          <span className="text-xs bg-blue-900 text-blue-300 border border-blue-700 px-2 py-0.5 rounded font-medium">
            ✏ Edit Mode
          </span>
        )}
      </div>

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
          <p className="text-xs font-semibold text-gray-400 mb-2 uppercase tracking-wide">Identified Risks</p>
          <div className="space-y-2">
            {risks.map((r, i) => (
              <div key={i} className="flex items-start gap-2 text-sm">
                <span className={`px-2 py-0.5 rounded text-xs font-bold shrink-0 mt-0.5 ${RISK_COLORS[r.risk_level] || "bg-gray-700 text-gray-300"}`}>
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

      {displayRecs.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <p className="text-xs font-semibold text-gray-400 uppercase tracking-wide">Recommended Actions</p>
            {mode === "edit" && (
              <p className="text-xs text-blue-400">Edit the action text — reasons stay as AI context</p>
            )}
          </div>
          <ol className="space-y-3">
            {displayRecs.map((rec, i) => (
              <li key={i} className={`rounded-lg p-3 border transition-colors ${mode === "edit" ? "bg-blue-950/20 border-blue-800/60" : "bg-gray-800 border-gray-700"}`}>
                <div className="flex gap-2 mb-1.5">
                  <span className="text-brand-600 font-bold shrink-0 text-sm mt-1">{i + 1}.</span>
                  <div className="flex-1">
                    {mode === "edit" ? (
                      <textarea
                        value={rec.text}
                        onChange={(e) => updateText(i, e.target.value)}
                        rows={2}
                        className="w-full bg-gray-900 border border-blue-700 focus:border-blue-500 focus:outline-none rounded-lg px-2.5 py-1.5 text-sm text-gray-100 resize-none"
                      />
                    ) : (
                      <span className="text-gray-200 font-medium text-sm">{rec.text}</span>
                    )}
                  </div>
                </div>
                {rec.reasons.length > 0 && (
                  <ul className="ml-5 space-y-0.5 mt-1">
                    {rec.reasons.map((r, j) => (
                      <li key={j} className="text-xs text-gray-400 flex gap-1.5">
                        <span className="text-brand-700 flex-shrink-0">›</span>
                        {r}
                      </li>
                    ))}
                  </ul>
                )}
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
        disabled={loading}
      />

      {mode === "edit" ? (
        <div className="flex gap-3">
          <button
            onClick={() => decide(true, editedRecs)}
            disabled={loading}
            className="flex-1 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            ✓ Save & Execute
          </button>
          <button
            onClick={() => setMode("view")}
            disabled={loading}
            className="px-4 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            Cancel
          </button>
        </div>
      ) : (
        <div className="flex gap-3">
          <button
            onClick={() => decide(true)}
            disabled={loading}
            className="flex-1 bg-green-700 hover:bg-green-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            {loading ? "Processing…" : "✓ Approve & Execute"}
          </button>
          <button
            onClick={enterEdit}
            disabled={loading}
            className="px-4 bg-blue-800 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            ✏ Modify
          </button>
          <button
            onClick={() => decide(false)}
            disabled={loading}
            className="px-4 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white font-semibold py-2 rounded-lg transition-colors"
          >
            ✗ Reject
          </button>
        </div>
      )}
    </div>
  );
}
