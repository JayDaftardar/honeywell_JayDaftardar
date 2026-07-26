import { cn } from "../../lib/utils";

export function StatCard({ title, value, unit, icon: Icon, colorClass, trend }) {
  return (
    <div className="glass-panel p-5 rounded-2xl flex flex-col justify-between relative overflow-hidden group hover:-translate-y-1 transition-all duration-300">
      {/* Background glow effect */}
      <div className={cn("absolute -right-4 -top-4 w-24 h-24 rounded-full opacity-20 blur-2xl transition-opacity group-hover:opacity-40", colorClass)} />
      
      <div className="flex justify-between items-start mb-4 relative z-10">
        <h3 className="text-slate-400 font-medium text-sm tracking-wide uppercase">{title}</h3>
        {Icon && (
          <div className={cn("p-2 rounded-xl bg-slate-900/50", colorClass)}>
            <Icon size={20} className="text-current" />
          </div>
        )}
      </div>
      
      <div className="flex items-baseline gap-2 relative z-10">
        <span className="text-3xl font-bold text-slate-100 tabular-nums">
          {value !== null && value !== undefined ? Number(value).toFixed(2) : "--"}
        </span>
        <span className="text-slate-400 font-medium text-sm">{unit}</span>
      </div>
      
      {trend && (
        <div className="mt-3 text-xs font-medium relative z-10">
          <span className={trend > 0 ? "text-emerald-400" : "text-rose-400"}>
            {trend > 0 ? "↑" : "↓"} {Math.abs(trend)}%
          </span>
          <span className="text-slate-500 ml-2">vs baseline</span>
        </div>
      )}
    </div>
  );
}
