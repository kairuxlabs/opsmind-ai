import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import {
  getMemoryHistory,
  getMemoryStats,
  getEntityMemories,
  getFeedbackHistory,
} from "../api/client.js";

// ── Stats bar ────────────────────────────────────────────────────────────────

function StatCard({ label, value, sub, color = "text-white" }) {
  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-4 flex flex-col gap-1">
      <p className="text-gray-500 text-xs uppercase tracking-wide">{label}</p>
      <p className={`text-2xl font-bold ${color}`}>{value ?? "—"}</p>
      {sub && <p className="text-gray-600 text-xs">{sub}</p>}
    </div>
  );
}

function StatsPanel({ stats }) {
  if (!stats) return null;
  const topGoals = Object.entries(stats.goal_counts || {})
    .sort((a, b) => b[1] - a[1])
    .slice(0, 3);

  return (
    <div className="mb-8">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <StatCard
          label="Workflows"
          value={stats.total_workflows}
          sub={`${stats.total_approved} approved`}
          color="text-brand-400"
        />
        <StatCard
          label="Approval Rate"
          value={`${stats.approval_rate}%`}
          color={stats.approval_rate >= 70 ? "text-green-400" : "text-yellow-400"}
        />
        <StatCard
          label="Helpful Rate"
          value={`${stats.helpful_rate}%`}
          sub={`${stats.helpful} / ${stats.total_feedbacks} feedbacks`}
          color={stats.helpful_rate >= 70 ? "text-green-400" : "text-orange-400"}
        />
        <StatCard
          label="Entities Tracked"
          value={stats.entities_tracked}
          sub="projects, teams"
          color="text-purple-400"
        />
      </div>
      {topGoals.length > 0 && (
        <div className="bg-gray-900 rounded-xl border border-gray-800 p-4">
          <p className="text-gray-500 text-xs uppercase tracking-wide mb-3">Most Common Goals</p>
          <div className="flex flex-wrap gap-2">
            {topGoals.map(([goal, count]) => (
              <span
                key={goal}
                className="text-xs bg-gray-800 border border-gray-700 text-gray-300 px-3 py-1 rounded-full"
              >
                {goal.replace(/_/g, " ")} · {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

// ── Record cards ──────────────────────────────────────────────────────────────

const TYPE_META = {
  workflow_history: { label: "Workflow", color: "text-blue-400 bg-blue-900/30 border-blue-800" },
  recommendation_history: { label: "Recommendations", color: "text-brand-400 bg-brand-900/30 border-brand-800" },
  feedback_history: { label: "Feedback", color: "text-green-400 bg-green-900/30 border-green-800" },
  entity_memory: { label: "Entity", color: "text-purple-400 bg-purple-900/30 border-purple-800" },
};

function RecordCard({ record }) {
  const { key, value, updated_at } = record;
  const type = key.split(":")[0];
  const shortId = key.split(":").slice(1).join(":").slice(0, 20);
  const meta = TYPE_META[type] || { label: type, color: "text-gray-400 bg-gray-800 border-gray-700" };

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-5">
      <div className="flex items-start justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className={`text-xs font-medium px-2 py-0.5 rounded border ${meta.color}`}>
            {meta.label}
          </span>
          <span className="text-gray-600 text-xs font-mono truncate max-w-[160px]">{shortId}</span>
        </div>
        <span className="text-gray-600 text-xs shrink-0">
          {updated_at ? new Date(updated_at).toLocaleString() : "—"}
        </span>
      </div>

      {type === "workflow_history" && (
        <div className="space-y-1.5">
          <p className="text-sm text-gray-200 font-medium">{value.goal?.replace(/_/g, " ")}</p>
          <p className="text-xs text-gray-500 line-clamp-2">{value.query}</p>
          <div className="flex items-center gap-3 mt-2 flex-wrap">
            <span className={`text-xs ${value.approved ? "text-green-400" : "text-gray-500"}`}>
              {value.approved ? "✓ Approved" : "✗ Not approved"}
            </span>
            {value.health_score > 0 && (
              <span className="text-xs text-gray-500">Health: {value.health_score}</span>
            )}
            {value.route?.length > 0 && (
              <span className="text-xs text-gray-600">{value.route.join(" → ")}</span>
            )}
          </div>
        </div>
      )}

      {type === "recommendation_history" && (
        <div className="space-y-2">
          <p className="text-sm text-gray-200 font-medium">{value.goal?.replace(/_/g, " ")}</p>
          {value.confidence > 0 && (
            <div className="flex items-center gap-2">
              <div className="flex-1 bg-gray-800 rounded-full h-1.5">
                <div
                  className="bg-brand-600 h-1.5 rounded-full"
                  style={{ width: `${Math.round(value.confidence * 100)}%` }}
                />
              </div>
              <span className="text-xs text-gray-400">{Math.round(value.confidence * 100)}%</span>
            </div>
          )}
          {value.recommendations?.slice(0, 2).map((r, i) => {
            const text = typeof r === "string" ? r : r.text;
            return (
              <p key={i} className="text-xs text-gray-500 line-clamp-1">› {text}</p>
            );
          })}
          <div className="flex items-center gap-3">
            {value.critique_passed != null && (
              <span className={`text-xs ${value.critique_passed ? "text-green-400" : "text-yellow-400"}`}>
                {value.critique_passed ? "✓ Critique passed" : "⚠ Critique flagged"}
              </span>
            )}
            {value.feedback && (
              <span className="text-xs text-gray-400">
                {value.feedback === "helpful" ? "👍 Helpful" : "👎 Not Helpful"}
              </span>
            )}
          </div>
        </div>
      )}

      {type === "feedback_history" && (
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-300">
            {value.rating === "helpful" ? "👍 Marked as Helpful" : "👎 Marked as Not Helpful"}
          </span>
          <span className="text-xs text-gray-600">{value.timestamp?.slice(0, 10)}</span>
        </div>
      )}

      {type === "entity_memory" && (
        <div className="space-y-1.5">
          <p className="text-sm text-gray-200 font-medium">{value.project || shortId}</p>
          {value.last_risk_level && (
            <span className={`text-xs px-2 py-0.5 rounded font-medium ${
              value.last_risk_level === "Critical" ? "bg-red-900 text-red-300" :
              value.last_risk_level === "High" ? "bg-orange-900 text-orange-300" :
              "bg-yellow-900 text-yellow-300"
            }`}>
              {value.last_risk_level}
            </span>
          )}
          {value.last_reason && (
            <p className="text-xs text-gray-500">{value.last_reason}</p>
          )}
          <p className="text-xs text-gray-600">
            Seen in {value.sessions?.length ?? 1} session{value.sessions?.length !== 1 ? "s" : ""}
            {value.last_seen_goal ? ` · ${value.last_seen_goal.replace(/_/g, " ")}` : ""}
          </p>
        </div>
      )}
    </div>
  );
}

// ── Tabs ──────────────────────────────────────────────────────────────────────

const TABS = [
  { key: "all", label: "All" },
  { key: "workflow", label: "Workflows" },
  { key: "feedback", label: "Feedback" },
  { key: "entities", label: "Entities" },
];

// ── Main component ────────────────────────────────────────────────────────────

export default function MemoryCenter() {
  const [tab, setTab] = useState("all");
  const [stats, setStats] = useState(null);
  const [records, setRecords] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMemoryStats().then(setStats).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const fetch =
      tab === "entities" ? getEntityMemories(30)
      : tab === "feedback" ? getFeedbackHistory(30).then((d) => ({ records: d.records }))
      : getMemoryHistory(40);

    fetch
      .then((d) => {
        let recs = d.records || [];
        if (tab === "workflow") recs = recs.filter((r) => r.key.startsWith("workflow_history:") || r.key.startsWith("recommendation_history:"));
        setRecords(recs);
      })
      .catch(() => setRecords([]))
      .finally(() => setLoading(false));
  }, [tab]);

  return (
    <div className="max-w-4xl mx-auto px-6 py-10">
      <div className="flex items-center justify-between mb-6">
        <div>
          <Link to="/" className="text-gray-500 text-sm hover:text-gray-300 mb-1 block">← Command Center</Link>
          <h2 className="text-2xl font-bold">Memory Center</h2>
          <p className="text-gray-500 text-sm mt-1">Long-term memory, entity tracking, and feedback learning</p>
        </div>
      </div>

      <StatsPanel stats={stats} />

      {/* Tabs */}
      <div className="flex gap-1 mb-6 bg-gray-900 rounded-xl border border-gray-800 p-1">
        {TABS.map((t) => (
          <button
            key={t.key}
            onClick={() => setTab(t.key)}
            className={`flex-1 text-sm py-1.5 rounded-lg font-medium transition-colors ${
              tab === t.key
                ? "bg-gray-800 text-white"
                : "text-gray-500 hover:text-gray-300"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {loading && (
        <div className="text-center text-gray-500 py-16 animate-pulse">Loading memory…</div>
      )}

      {!loading && records.length === 0 && (
        <div className="text-center text-gray-600 py-16">
          <p className="text-lg mb-2">No records yet</p>
          <p className="text-sm">Complete a workflow to see history here.</p>
          <Link to="/" className="text-brand-600 text-sm mt-4 inline-block">Create a workflow →</Link>
        </div>
      )}

      {!loading && records.length > 0 && (
        <div className="space-y-4">
          {records.map((record, i) => (
            <RecordCard key={i} record={record} />
          ))}
        </div>
      )}
    </div>
  );
}
