import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, Tooltip, CartesianGrid } from 'recharts';
import { cn } from "../../lib/utils";

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass p-3 rounded-lg border border-slate-700 shadow-2xl">
        <p className="text-slate-400 text-xs mb-1 font-medium">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 mt-1">
            <div className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
            <span className="text-slate-100 font-semibold tabular-nums text-sm">
              {Number(entry.value).toFixed(2)}
            </span>
            <span className="text-slate-400 text-xs">{entry.name}</span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function LiveChart({ data, title, dataKey, secondaryDataKey, color = "#0ea5e9", secondaryColor = "#10b981", height = 250, unit = "" }) {
  return (
    <div className="glass-panel p-5 rounded-2xl flex flex-col h-full border border-slate-800/50 relative overflow-hidden group">
      {/* Background glow behind chart */}
      <div 
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-3/4 h-3/4 rounded-full blur-3xl opacity-5 pointer-events-none transition-opacity group-hover:opacity-10" 
        style={{ backgroundColor: color }} 
      />
      
      <div className="flex justify-between items-center mb-4 relative z-10">
        <h3 className="text-slate-200 font-semibold tracking-wide">{title}</h3>
        <span className="text-xs text-slate-500 font-medium">{unit}</span>
      </div>
      
      <div className="flex-1 min-h-[200px] w-full relative z-10" style={{ height }}>
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
            <defs>
              <linearGradient id={`color-${dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={color} stopOpacity={0.3} />
                <stop offset="95%" stopColor={color} stopOpacity={0} />
              </linearGradient>
              {secondaryDataKey && (
                <linearGradient id={`color-${secondaryDataKey}`} x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={secondaryColor} stopOpacity={0.3} />
                  <stop offset="95%" stopColor={secondaryColor} stopOpacity={0} />
                </linearGradient>
              )}
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
            <XAxis 
              dataKey="time" 
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              minTickGap={20}
            />
            <YAxis 
              tick={{ fill: '#64748b', fontSize: 10 }}
              tickLine={false}
              axisLine={false}
              tickFormatter={(value) => value.toFixed(0)}
              domain={['auto', 'auto']}
            />
            <Tooltip content={<CustomTooltip />} />
            
            <Area 
              type="monotone" 
              dataKey={dataKey} 
              name={title.split(" ")[0]}
              stroke={color} 
              strokeWidth={2}
              fillOpacity={1} 
              fill={`url(#color-${dataKey})`} 
              isAnimationActive={false} 
            />
            {secondaryDataKey && (
              <Area 
                type="monotone" 
                dataKey={secondaryDataKey} 
                name="Secondary"
                stroke={secondaryColor} 
                strokeWidth={2}
                fillOpacity={1} 
                fill={`url(#color-${secondaryDataKey})`} 
                isAnimationActive={false} 
              />
            )}
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
