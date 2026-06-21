import { Routes, Route } from "react-router-dom";
import Dashboard from "./components/Dashboard.jsx";
import WorkflowView from "./components/WorkflowView.jsx";

export default function App() {
  return (
    <div className="min-h-screen">
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-3">
        <span className="text-brand-600 font-bold text-xl">⚡</span>
        <span className="font-bold text-lg tracking-tight">OpsMind AI</span>
        <span className="text-gray-500 text-sm ml-auto">
          Decision Intelligence Platform v2.0
        </span>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/workflow/:id" element={<WorkflowView />} />
      </Routes>
    </div>
  );
}
