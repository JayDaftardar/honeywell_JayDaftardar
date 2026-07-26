import { useState, useEffect } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Leaf, DollarSign, Zap, TrendingDown } from 'lucide-react';
import { StatCard } from './components/ui/StatCard';

const API_BASE_URL = 'http://127.0.0.1:8000';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="glass p-3 rounded-lg border border-slate-700 shadow-2xl">
        <p className="text-slate-400 text-xs mb-2 font-medium">{label}</p>
        {payload.map((entry, index) => (
          <div key={index} className="flex items-center gap-2 mt-1">
            <div className="w-3 h-3 rounded-sm" style={{ backgroundColor: entry.color }} />
            <span className="text-slate-400 text-xs">{entry.name}:</span>
            <span className="text-slate-100 font-semibold tabular-nums text-sm">
              {Number(entry.value).toFixed(2)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export function Analytics() {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAnalytics = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/analytics/comparison`);
        setData(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };
    fetchAnalytics();
  }, []);

  if (loading) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[500px]">
        <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex-1 flex items-center justify-center min-h-[500px]">
        <div className="text-rose-400 bg-rose-500/10 px-4 py-3 rounded-xl border border-rose-500/20">
          Failed to load analytics: {error}
        </div>
      </div>
    );
  }

  // Formatting data for the bar chart
  const chartData = [
    {
      name: 'Energy (kWh)',
      Baseline: data.energy_saved_kwh / (data.savings_percentage / 100), // Reverse engineered baseline for visual
      MistralAI: (data.energy_saved_kwh / (data.savings_percentage / 100)) - data.energy_saved_kwh,
    },
    {
      name: 'Cost ($)',
      Baseline: data.cost_saved_usd / (data.savings_percentage / 100),
      MistralAI: (data.cost_saved_usd / (data.savings_percentage / 100)) - data.cost_saved_usd,
    },
    {
      name: 'Carbon (kgCO2)',
      Baseline: data.carbon_reduced_kg / (data.savings_percentage / 100),
      MistralAI: (data.carbon_reduced_kg / (data.savings_percentage / 100)) - data.carbon_reduced_kg,
    }
  ];

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      
      {/* HERO METRICS */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard 
          title="Total Energy Saved" 
          value={data.energy_saved_kwh} 
          unit="kWh" 
          icon={Zap} 
          colorClass="text-brand-400"
        />
        <StatCard 
          title="Cost Reduction" 
          value={data.cost_saved_usd} 
          unit="USD" 
          icon={DollarSign} 
          colorClass="text-emerald-400"
        />
        <StatCard 
          title="Carbon Avoided" 
          value={data.carbon_reduced_kg} 
          unit="kg" 
          icon={Leaf} 
          colorClass="text-green-400"
        />
        <StatCard 
          title="Overall Efficiency" 
          value={data.savings_percentage} 
          unit="%" 
          icon={TrendingDown} 
          colorClass="text-indigo-400"
        />
      </div>

      {/* COMPARISON CHART */}
      <div className="glass-panel p-6 rounded-2xl border border-slate-800/50 min-h-[400px] flex flex-col">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-slate-100 mb-1">Baseline vs AI Performance</h2>
          <p className="text-slate-400 text-sm">Comparing traditional static setpoint control to Mistral's dynamic optimization.</p>
        </div>
        
        <div className="flex-1 w-full relative">
          <ResponsiveContainer width="100%" height="100%">
            <BarChart
              data={chartData}
              margin={{ top: 20, right: 30, left: 20, bottom: 5 }}
              barGap={8}
            >
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              
              <Bar 
                dataKey="Baseline" 
                fill="#475569" 
                radius={[4, 4, 0, 0]} 
                name="Standard Control (22°C)"
              />
              <Bar 
                dataKey="MistralAI" 
                fill="#0ea5e9" 
                radius={[4, 4, 0, 0]} 
                name="Mistral Autonomous AI"
              />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>
      
    </div>
  );
}
