const AGENT_LABELS = {
  supervisor: "Supervisor",
  planner: "Planner",
  knowledge: "Knowledge",
  analytics: "Analytics",
  decision: "Decision",
  executor: "Executor",
  memory: "Memory",
};

export default function AgentMonitor({ agents, executedAgents, agentLogs }) {
  const logsByAgent = Object.fromEntries((agentLogs || []).map((l) => [l.agent, l]));

  return (
    <div className="bg-gray-900 rounded-xl border border-gray-800 p-6 mb-6">
      <h3 className="font-semibold text-gray-300 mb-4">Agent Pipeline</h3>
      <div className="space-y-1">
        {agents.map((agent, idx) => {
          const done = executedAgents.has(agent);
          const log = logsByAgent[agent];
          return (
            <div key={agent} className="flex items-center gap-3 py-2 border-b border-gray-800 last:border-0">
              <span className={`text-sm font-mono w-4 text-center ${done ? "text-green-400" : "text-gray-600"}`}>
                {done ? "✓" : String(idx + 1)}
              </span>
              <span className={`font-medium w-28 text-sm ${done ? "text-gray-100" : "text-gray-500"}`}>
                {AGENT_LABELS[agent]}
              </span>
              {log ? (
                <span className="text-xs text-gray-500 font-mono">{log.latency_ms}ms</span>
              ) : (
                <span className="text-xs text-gray-700">pending</span>
              )}
              <div className="ml-auto">
                {done ? (
                  <span className="w-2 h-2 rounded-full bg-green-500 inline-block" />
                ) : (
                  <span className="w-2 h-2 rounded-full bg-gray-700 inline-block" />
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
