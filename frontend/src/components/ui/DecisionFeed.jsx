import { BrainCircuit, ChevronRight } from "lucide-react";

export function DecisionFeed({ decisions }) {
  return (
    <div className="glass-panel rounded-2xl flex flex-col h-full overflow-hidden border border-slate-800/50">
      <div className="p-4 border-b border-slate-800/50 bg-slate-900/40 flex items-center gap-3">
        <div className="p-2 bg-indigo-500/20 rounded-lg text-indigo-400">
          <BrainCircuit size={20} />
        </div>
        <h2 className="text-slate-200 font-semibold tracking-wide">Mistral AI Stream</h2>
      </div>
      
      <div className="flex-1 overflow-y-auto p-4 space-y-4 no-scrollbar">
        {decisions.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-slate-500">
            <BrainCircuit size={48} className="mb-4 opacity-20" />
            <p className="text-sm text-center px-4">Awaiting live data to start autonomous optimization...</p>
          </div>
        ) : (
          decisions.map((decision, idx) => (
            <div key={idx} className="bg-slate-900/50 border border-slate-800/50 rounded-xl p-4 animate-in fade-in slide-in-from-right-4 duration-500">
              <div className="flex justify-between items-start mb-2">
                <span className="px-2 py-1 bg-brand-500/20 text-brand-400 text-xs font-bold uppercase rounded tracking-wider">
                  {decision.action.replace("_", " ")}
                </span>
                <span className="text-xs text-slate-500 font-medium">
                  Conf: {(decision.confidence * 100).toFixed(0)}%
                </span>
              </div>
              <p className="text-slate-300 text-sm leading-relaxed mb-3">
                {decision.reasoning}
              </p>
              <div className="flex gap-4 text-xs font-medium">
                <div className="flex items-center gap-1.5 text-slate-400 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-slate-500">Temp:</span>
                  <span className="text-slate-200">{decision.applied_setpoint?.toFixed(1)}°C</span>
                </div>
                <div className="flex items-center gap-1.5 text-slate-400 bg-slate-950 px-2.5 py-1.5 rounded-lg border border-slate-800">
                  <span className="text-slate-500">Fan:</span>
                  <span className="text-slate-200">{decision.applied_fan_speed?.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
