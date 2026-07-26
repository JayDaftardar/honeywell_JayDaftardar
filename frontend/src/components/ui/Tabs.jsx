import { BarChart2, Activity } from 'lucide-react';
import { cn } from "../../lib/utils";

export function Tabs({ activeTab, setActiveTab }) {
  return (
    <div className="flex bg-slate-900/50 p-1 rounded-xl border border-slate-800/50 w-fit backdrop-blur-md">
      <button
        onClick={() => setActiveTab('dashboard')}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300",
          activeTab === 'dashboard' 
            ? "bg-brand-600 text-white shadow-lg shadow-brand-900/50" 
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
        )}
      >
        <Activity size={16} />
        Live Operation
      </button>
      <button
        onClick={() => setActiveTab('analytics')}
        className={cn(
          "flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300",
          activeTab === 'analytics' 
            ? "bg-brand-600 text-white shadow-lg shadow-brand-900/50" 
            : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
        )}
      >
        <BarChart2 size={16} />
        Analytics & Reports
      </button>
    </div>
  );
}
