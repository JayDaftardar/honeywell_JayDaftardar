import { useState, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8000';

export function useSimulationControl() {
  const [status, setStatus] = useState('stopped'); // running, paused, stopped
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const startSimulation = useCallback(async (mode = "ai") => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API_BASE_URL}/simulation/start?mode=${mode}`);
      setStatus('running');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const pauseSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API_BASE_URL}/simulation/pause`);
      setStatus('paused');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const resumeSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API_BASE_URL}/simulation/resume`);
      setStatus('running');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const stopSimulation = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      await axios.post(`${API_BASE_URL}/simulation/stop`);
      setStatus('stopped');
    } catch (err) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  }, []);
  
  const [currentMode, setCurrentMode] = useState(null);

  const fetchStatus = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/simulation/status`);
      if (response.data.running) {
        setStatus(response.data.paused ? 'paused' : 'running');
        setCurrentMode(response.data.mode);
      } else {
        setStatus('stopped');
        setCurrentMode(null);
      }
    } catch (err) {
      console.error("Failed to fetch status", err);
    }
  }, []);

  return {
    status,
    loading,
    error,
    currentMode,
    startSimulation,
    pauseSimulation,
    resumeSimulation,
    stopSimulation,
    fetchStatus
  };
}
