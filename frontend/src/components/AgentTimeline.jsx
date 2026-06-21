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

function formatOffset(ms) {
  const s = Math.floor(ms / 1000);
  const m = Math.floor(s / 60);
  return `+${m}:${String(s % 60).padStart(2, "0")}`;
}

function buildPipeline(route) {
  const dynamic = (route || []).filter(
    (a) => a !== "supervisor" && a !== "critique" && a !== "executor" && a !== "memory"
  );
  // supervisor → dynamic route → critique → [approval] → executor → memory
  return ["supervisor", ...new Set(dynamic), "critique", "executor", "memory"];
}

export default function AgentTimeline({ agentLogs, route, status }) {
  const logs = agentLogs || [];
  const logByAgent = Object.fromEntries(logs.map((l) => [l.agent, l]));

  const isActive = ["starting", "planning", "running", "executing"].includes(status);
  const pipeline = buildPipeline(route);

  // Max latency for bar scaling (use completed agents only)
  const maxLatency = Math.max(...logs.map((l) => l.latency_ms), 800);

  // Cumulative offsets: each agent's start = sum of all previous latencies
  let cumulative = 0;
  const offsets = {};
  for (const agent of pipeline) {
    offsets[agent] = cumulative;
    if (logByAgent[agent]) cumulative += logByAgent[agent].latency_ms;
  }

  // Currently running = first pipeline agent not yet in logs (only when active)
  const currentAgent = isActive ? pipeline.find((a) => !logByAgent[a]) : null;

  const totalMs = logs.reduce((s, l) => s + l.latency_ms, 0);

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
      <div className="flex items-center justify-between mb-5">
        <h3 className="font-semibold text-gray-300 text-sm uppercase tracking-wide">
          Agent Timeline
        </h3>
        {totalMs > 0 && (
          <span className="text-xs text-gray-500 font-mono">
            {(totalMs / 1000).toFixed(1)}s elapsed
          </span>
        )}
      </div>

      <div className="space-y-0.5">
        {pipeline.map((agent) => {
          const log = logByAgent[agent];
          const done = !!log;
          const running = agent === currentAgent;
          const pending = !done && !running;
          const isApprovalBefore = agent === "executor";

          return (
            <div key={agent}>
              {/* Human approval divider */}
              {isApprovalBefore && (
                <div className="flex items-center gap-2 my-3">
                  <div className="flex-1 h-px bg-orange-800/60" />
                  <span className="text-xs text-orange-500/80 font-medium px-1">
                    ⏳ Human Approval
                  </span>
                  <div className="flex-1 h-px bg-orange-800/60" />
                </div>
              )}

              <div
                className={`flex items-center gap-3 py-2.5 rounded-lg px-2 transition-colors ${
                  running ? "bg-blue-950/30" : ""
                }`}
              >
                {/* Status dot */}
                <div className="w-5 flex items-center justify-center shrink-0">
                  {done ? (
                    <span className="text-green-400 text-sm font-bold">✓</span>
                  ) : running ? (
                    <span className="w-2.5 h-2.5 rounded-full bg-blue-400 animate-pulse inline-block" />
                  ) : (
                    <span className="w-2 h-2 rounded-full bg-gray-700 inline-block" />
                  )}
                </div>

                {/* Icon + name */}
                <div className="w-32 shrink-0 flex items-center gap-2">
                  <span className="text-base leading-none">{AGENT_ICONS[agent] ?? "●"}</span>
                  <span
                    className={`text-sm font-medium ${
                      done
                        ? "text-gray-100"
                        : running
                        ? "text-blue-300"
                        : "text-gray-600"
                    }`}
                  >
                    {agent}
                  </span>
                </div>

                {/* Latency bar */}
                <div className="flex-1 h-1.5 bg-gray-800 rounded-full overflow-hidden">
                  {done && (
                    <div
                      className="h-full bg-brand-600 rounded-full transition-all duration-700"
                      style={{
                        width: `${Math.max(
                          (log.latency_ms / maxLatency) * 100,
                          2
                        )}%`,
                      }}
                    />
                  )}
                  {running && (
                    <div className="h-full w-1/3 bg-blue-500/60 rounded-full animate-pulse" />
                  )}
                </div>

                {/* Latency value */}
                <div className="w-20 text-right shrink-0">
                  {done && (
                    <span className="text-xs text-gray-400 font-mono">
                      {log.latency_ms}ms
                    </span>
                  )}
                  {running && (
                    <span className="text-xs text-blue-400 font-mono animate-pulse">
                      running…
                    </span>
                  )}
                  {pending && (
                    <span className="text-xs text-gray-700">—</span>
                  )}
                </div>

                {/* Relative time offset */}
                <div className="w-12 text-right shrink-0">
                  {(done || running) && (
                    <span className="text-xs text-gray-600 font-mono">
                      {formatOffset(offsets[agent])}
                    </span>
                  )}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
