import { useEffect, useState } from 'react';
import { 
  Play, 
  Pause, 
  Square,
  Thermometer,
  ThermometerSun,
  Droplets,
  Wind,
  Zap,
  Activity,
  AlertCircle,
  Download
} from 'lucide-react';

import { useSimulationControl } from './hooks/useSimulationControl';
import { useLiveSensors } from './hooks/useLiveSensors';
import { StatCard } from './components/ui/StatCard';
import { Button } from './components/ui/Button';
import { DecisionFeed } from './components/ui/DecisionFeed';
import { LiveChart } from './components/charts/LiveChart';

export function Dashboard() {
  const { 
    status, 
    loading, 
    error, 
    startSimulation, 
    pauseSimulation, 
    resumeSimulation, 
    stopSimulation,
    fetchStatus
  } = useSimulationControl();

  const { dataHistory, latestData, decisions, isConnected } = useLiveSensors();
  const [exportStatus, setExportStatus] = useState(null); // null | 'loading' | 'success' | 'error'

  const exportModifiedIdf = async () => {
    setExportStatus('loading');
    try {
      const res = await fetch('http://127.0.0.1:8000/simulation/export-modified-idf', { method: 'POST' });
      const data = await res.json();
      if (res.ok && data.success) {
        setExportStatus('success');
        setTimeout(() => setExportStatus(null), 5000);
      } else {
        setExportStatus('error');
        setTimeout(() => setExportStatus(null), 4000);
      }
    } catch (e) {
      setExportStatus('error');
      setTimeout(() => setExportStatus(null), 4000);
    }
  };

  useEffect(() => {
    fetchStatus();
    // Poll status occasionally to stay in sync if multiple clients exist
    const interval = setInterval(fetchStatus, 5000);
    return () => clearInterval(interval);
  }, [fetchStatus]);

  return (
    <div className="min-h-full p-4 md:p-6 lg:p-8 flex flex-col gap-6">
      {/* HEADER */}
      <header className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-brand-400 to-emerald-400 inline-block mb-1">
            Smart Building AI
          </h1>
          <div className="flex items-center gap-3 text-sm">
            <span className="flex items-center gap-1.5 text-slate-400 font-medium bg-slate-900/50 px-3 py-1 rounded-full border border-slate-800">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-[0_0_8px_rgba(16,185,129,0.8)]' : 'bg-rose-500'}`} />
              {isConnected ? 'Live Stream Active' : 'Disconnected'}
            </span>
            <span className="flex items-center gap-1.5 text-slate-400 font-medium bg-slate-900/50 px-3 py-1 rounded-full border border-slate-800 uppercase tracking-wider text-xs">
              Status: <span className="text-slate-200">{status}</span>
            </span>
          </div>
        </div>
        
        {/* CONTROLS */}
        <div className="flex flex-wrap items-center gap-3 p-2 bg-slate-900/30 rounded-2xl border border-slate-800/50 backdrop-blur-md">
          {error && (
            <div className="text-xs text-rose-400 flex items-center gap-1 mr-2 px-2">
              <AlertCircle size={14} /> {error}
            </div>
          )}
          
          {(status === 'stopped' || status === 'finished') && (
            <Button variant="primary" icon={Play} onClick={startSimulation} isLoading={loading}>
              Start Autonomous Loop
            </Button>
          )}
          
          {status === 'running' && (
            <Button variant="warning" icon={Pause} onClick={pauseSimulation} isLoading={loading}>
              Pause
            </Button>
          )}
          
          {status === 'paused' && (
            <Button variant="success" icon={Play} onClick={resumeSimulation} isLoading={loading}>
              Resume
            </Button>
          )}
          
          {(status === 'running' || status === 'paused') && (
            <Button variant="danger" icon={Square} onClick={stopSimulation} isLoading={loading}>
              Stop
            </Button>
          )}

          {(status === 'stopped' || status === 'finished') && decisions.length > 0 && (
            <Button 
              variant="secondary" 
              icon={Download} 
              onClick={exportModifiedIdf}
              isLoading={exportStatus === 'loading'}
            >
              {exportStatus === 'success' ? '✓ IDF Exported!' : 
               exportStatus === 'error'  ? '✗ Export Failed' : 
               'Export Modified IDF'}
            </Button>
          )}
        </div>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 flex-1">
        
        {/* MAIN CONTENT AREA */}
        <div className="lg:col-span-3 flex flex-col gap-6">
          
          {/* STATS ROW */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <StatCard 
              title="Indoor Temp" 
              value={latestData?.indoor_temp} 
              unit="°C" 
              icon={Thermometer} 
              colorClass="text-brand-400"
            />
            <StatCard 
              title="Outdoor Temp" 
              value={latestData?.outdoor_temp} 
              unit="°C" 
              icon={ThermometerSun} 
              colorClass="text-amber-400"
            />
            <StatCard 
              title="Humidity" 
              value={latestData?.humidity} 
              unit="%" 
              icon={Droplets} 
              colorClass="text-indigo-400"
            />
            <StatCard 
              title="Total Power" 
              value={latestData?.hvac_energy} 
              unit="W" 
              icon={Zap} 
              colorClass="text-rose-400"
            />
          </div>

          {/* CHARTS AREA */}
          <div className="flex flex-col gap-6 flex-1">
            <LiveChart 
              title="Temperature Profile" 
              data={dataHistory} 
              dataKey="indoor_temp" 
              secondaryDataKey="outdoor_temp"
              color="#0ea5e9"
              secondaryColor="#f59e0b"
              unit="°C"
            />
            <LiveChart 
              title="HVAC Energy Demand" 
              data={dataHistory} 
              dataKey="hvac_energy"
              secondaryDataKey="cooling_energy"
              color="#f43f5e"
              secondaryColor="#8b5cf6"
              unit="Watts"
            />
          </div>
        </div>
        
        {/* RIGHT COLUMN: DECISION FEED */}
        <div className="lg:col-span-1 flex flex-col overflow-hidden sticky top-4 h-[calc(100vh-2rem)]">
          <DecisionFeed decisions={decisions} />
        </div>
      </div>
    </div>
  );
}
