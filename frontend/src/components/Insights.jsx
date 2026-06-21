export default function Insights({ metrics }) {
  if (!metrics) return null;
  const items = [
    { label: "Workflows Today", value: metrics.workflows_today, color: "text-blue-400" },
    { label: "Avg Execution", value: `${metrics.avg_latency_ms}ms`, color: "text-purple-400" },
    { label: "Human Approvals", value: metrics.human_approvals, color: "text-green-400" },
    { label: "Risks Detected", value: metrics.risks_detected, color: "text-orange-400" },
  ];
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {items.map((item) => (
        <div key={item.label} className="bg-gray-900 rounded-lg p-4 border border-gray-800">
          <p className="text-gray-500 text-xs mb-1">{item.label}</p>
          <p className={`text-2xl font-bold ${item.color}`}>{item.value}</p>
        </div>
      ))}
    </div>
  );
}
