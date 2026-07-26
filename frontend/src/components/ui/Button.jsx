import { cn } from "../../lib/utils";
import { Loader2 } from "lucide-react";

export function Button({ children, className, variant = "primary", isLoading, icon: Icon, ...props }) {
  const variants = {
    primary: "bg-brand-600 hover:bg-brand-500 text-white shadow-[0_0_15px_rgba(2,132,199,0.5)] border border-brand-500/50",
    success: "bg-success-500 hover:bg-emerald-400 text-white shadow-[0_0_15px_rgba(16,185,129,0.5)] border border-success-500/50",
    danger: "bg-danger-500 hover:bg-rose-400 text-white shadow-[0_0_15px_rgba(239,68,68,0.5)] border border-danger-500/50",
    warning: "bg-warning-500 hover:bg-amber-400 text-slate-900 shadow-[0_0_15px_rgba(245,158,11,0.5)] border border-warning-500/50",
    ghost: "bg-transparent hover:bg-slate-800 text-slate-300 border border-transparent",
    secondary: "bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-600/50 shadow-[0_0_10px_rgba(148,163,184,0.15)]",
  };

  return (
    <button
      className={cn(
        "flex items-center justify-center gap-2 px-6 py-2.5 rounded-xl font-medium transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed",
        variants[variant],
        className
      )}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading && <Loader2 size={18} className="animate-spin" />}
      {!isLoading && Icon && <Icon size={18} />}
      {children}
    </button>
  );
}
