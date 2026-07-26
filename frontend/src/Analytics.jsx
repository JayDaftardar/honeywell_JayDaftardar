import { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Leaf, DollarSign, Zap, TrendingDown, RefreshCw, AlertTriangle } from 'lucide-react';
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
  const [isMissingData, setIsMissingData] = useState(false);

  const fetchAnalytics = useCallback(async () => {
    setLoading(true);
    setError(null);
    setIsMissingData(false);
    setData(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/analytics/comparison`);
      setData(response.data);
    } catch (err) {
      if (err.response?.status === 400) {
        setIsMissingData(true);
      } else {
        setError(err.response?.data?.detail || err.message);
      }
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAnalytics(); }, [fetchAnalytics]);

  if (loading) return (
    <div className="flex-1 flex items-center justify-center min-h-[500px]">
      <div className="w-8 h-8 border-4 border-brand-500 border-t-transparent rounded-full animate-spin"></div>
    </div>
  );

  if (isMissingData) return (
    <div className="flex-1 flex flex-col items-center justify-center min-h-[500px] gap-6">
      <div className="flex flex-col items-center gap-4 max-w-md text-center">
        <div className="w-16 h-16 rounded-2xl bg-amber-500/10 border border-amber-500/20 flex items-center justify-center">
          <AlertTriangle size={32} className="text-amber-400" />
        </div>
        <h2 className="text-xl font-bold text-slate-100">Simulation Data Required</h2>
        <p className="text-slate-400 text-sm leading-relaxed">No real simulation data found yet. To see a genuine energy comparison:</p>
        <ol className="text-left text-sm text-slate-300 space-y-2 bg-slate-900/50 rounded-xl p-4 border border-slate-800 w-full">
          <li className="flex gap-2"><span className="text-brand-400 font-bold">1.</span> Dashboard: click <strong className="text-white">Start Baseline Run</strong>, wait ~1 min.</li>
          <li className="flex gap-2"><span className="text-emerald-400 font-bold">2.</span> Click <strong className="text-white">Start AI Run</strong>, wait ~1 min.</li>
          <li className="flex gap-2"><span className="text-indigo-400 font-bold">3.</span> Come back and click <strong className="text-white">Refresh Analytics</strong>.</li>
        </ol>
        <button onClick={fetchAnalytics} className="flex items-center gap-2 px-5 py-2.5 rounded-xl bg-brand-500 hover:bg-brand-400 text-white font-semibold transition-all duration-200 text-sm">
          <RefreshCw size={15} /> Refresh Analytics
        </button>
      </div>
    </div>
  );

  if (error) return (
    <div className="flex-1 flex items-center justify-center min-h-[500px]">
      <div className="text-rose-400 bg-rose-500/10 px-4 py-3 rounded-xl border border-rose-500/20">Failed to load analytics: {error}</div>
    </div>
  );

  if (!data) return null;

  const chartData = [
    { name: 'Energy (kWh)', Baseline: data.baseline_energy_kwh, MistralAI: data.ai_energy_kwh },
    { name: 'Cost ($)',     Baseline: +(data.baseline_energy_kwh * 0.15).toFixed(2), MistralAI: +(data.ai_energy_kwh * 0.15).toFixed(2) },
    { name: 'Carbon (kg)', Baseline: +(data.baseline_energy_kwh * 0.386).toFixed(2), MistralAI: +(data.ai_energy_kwh * 0.386).toFixed(2) },
  ];

  return (
    <div className="flex flex-col gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-100">Energy Analytics</h1>
          <p className="text-slate-400 text-sm mt-0.5">Real simulation comparison — Baseline vs Mistral AI control</p>
        </div>
        <button onClick={fetchAnalytics} className="flex items-center gap-2 px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-300 hover:text-white font-medium transition-all duration-200 text-sm">
          <RefreshCw size={14} /> Refresh
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard title="Energy Saved"   value={data.energy_saved_kwh}  unit="kWh"     icon={Zap}          colorClass="text-brand-400" />
        <StatCard title="Cost Reduction" value={data.cost_saved_usd}     unit="USD"     icon={DollarSign}   colorClass="text-emerald-400" />
        <StatCard title="Carbon Avoided" value={data.carbon_reduced_kg}  unit="kg CO2"  icon={Leaf}         colorClass="text-green-400" />
        <StatCard title="AI Efficiency"  value={data.savings_percentage} unit="%"       icon={TrendingDown} colorClass="text-indigo-400" />
      </div>

      <div className="glass-panel p-6 rounded-2xl border border-slate-800/50">
        <div className="mb-6">
          <h2 className="text-xl font-bold text-slate-100 mb-1">Baseline vs AI Performance</h2>
          <p className="text-slate-400 text-sm">Comparing traditional static setpoint control to Mistral dynamic optimization.</p>
        </div>
        <div style={{ height: 350 }}>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 5 }} barGap={8}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(255,255,255,0.05)" />
              <XAxis dataKey="name" tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <YAxis tick={{ fill: '#94a3b8' }} axisLine={false} tickLine={false} />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.02)' }} />
              <Legend wrapperStyle={{ paddingTop: '20px' }} />
              <Bar dataKey="Baseline"  fill="#475569" radius={[4,4,0,0]} name="Standard Control (22C fixed)" />
              <Bar dataKey="MistralAI" fill="#0ea5e9" radius={[4,4,0,0]} name="Mistral AI Autonomous Control" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="glass-panel p-5 rounded-2xl border border-slate-800/50">
        <h3 className="text-sm font-semibold text-slate-300 mb-3 uppercase tracking-wider">Raw Simulation Evidence</h3>
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
            <p className="text-xs text-slate-500 uppercase tracking-wider mb-2">Baseline Run</p>
            <p className="text-slate-200 font-bold text-lg">{data.baseline_avg_watts.toLocaleString()} W</p>
            <p className="text-slate-400 text-xs">avg HVAC demand</p>
            <p className="text-slate-500 text-xs mt-1">{data.baseline_steps} sensor readings recorded</p>
            <p className="text-slate-500 text-xs">{data.baseline_energy_kwh} kWh equiv. per 8-hr day</p>
          </div>
          <div className="bg-slate-900/50 rounded-xl p-4 border border-emerald-900/40">
            <p className="text-xs text-emerald-500 uppercase tracking-wider mb-2">AI Run (Mistral)</p>
            <p className="text-emerald-300 font-bold text-lg">{data.ai_avg_watts.toLocaleString()} W</p>
            <p className="text-slate-400 text-xs">avg HVAC demand</p>
            <p className="text-slate-500 text-xs mt-1">{data.ai_steps} sensor readings recorded</p>
            <p className="text-slate-500 text-xs">{data.ai_energy_kwh} kWh equiv. per 8-hr day</p>
          </div>
        </div>
        <p className="text-xs text-slate-600 mt-3">
          Normalized: avg W x 8 operating hours / 1000 = kWh/day. Ensures fair comparison regardless of demo run duration. Cost: $0.15/kWh (US commercial avg). Carbon: 0.386 kg CO2/kWh (EPA 2023).
        </p>
      </div>

    </div>
  );
}
