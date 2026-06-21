import { Routes, Route, NavLink } from "react-router-dom";
import Dashboard from "./components/Dashboard.jsx";
import WorkflowView from "./components/WorkflowView.jsx";
import MemoryCenter from "./components/MemoryCenter.jsx";
import Observability from "./components/Observability.jsx";

const navLinkClass = ({ isActive }) =>
  `text-sm transition-colors ${isActive ? "text-white font-medium" : "text-gray-500 hover:text-gray-300"}`;

export default function App() {
  return (
    <div className="min-h-screen">
      <nav className="bg-gray-900 border-b border-gray-800 px-6 py-4 flex items-center gap-6">
        <div className="flex items-center gap-2 mr-4">
          <span className="text-brand-600 font-bold text-xl">⚡</span>
          <span className="font-bold text-lg tracking-tight">OpsMind AI</span>
        </div>
        <NavLink to="/" end className={navLinkClass}>Command Center</NavLink>
        <NavLink to="/memory" className={navLinkClass}>Memory</NavLink>
        <NavLink to="/observability" className={navLinkClass}>Observability</NavLink>
        <span className="text-gray-700 text-xs ml-auto">
          Enterprise AI Operating System v3.0
        </span>
      </nav>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/workflow/:id" element={<WorkflowView />} />
        <Route path="/memory" element={<MemoryCenter />} />
        <Route path="/observability" element={<Observability />} />
      </Routes>
    </div>
  );
}
