import { useState, useEffect, useRef, useCallback } from 'react';

const WS_URL = 'ws://127.0.0.1:8000/sensor/live';
const MAX_DATA_POINTS = 50;

export function useLiveSensors() {
  const [dataHistory, setDataHistory] = useState([]);
  const [latestData, setLatestData] = useState(null);
  const [decisions, setDecisions] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);

  const connect = useCallback(() => {
    // Prevent multiple connections
    if (wsRef.current && (wsRef.current.readyState === WebSocket.OPEN || wsRef.current.readyState === WebSocket.CONNECTING)) {
      return;
    }

    const ws = new WebSocket(WS_URL);

    ws.onopen = () => {
      console.log('Connected to live sensors');
      setIsConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        
        if (payload.type === 'ai_decision') {
          setDecisions((prev) => [payload, ...prev].slice(0, 20));
        } else {
          const newDataPoint = {
            time: new Date().toLocaleTimeString(),
            ...payload
          };

          setLatestData(newDataPoint);
          setDataHistory((prev) => {
            const nextHistory = [...prev, newDataPoint];
            if (nextHistory.length > MAX_DATA_POINTS) {
              return nextHistory.slice(nextHistory.length - MAX_DATA_POINTS);
            }
            return nextHistory;
          });
        }
      } catch (err) {
        console.error('Failed to parse websocket message', err);
      }
    };

    ws.onclose = (e) => {
      console.log('Disconnected from live sensors', e.reason);
      setIsConnected(false);
      wsRef.current = null;
      // Reconnect
      setTimeout(() => connect(), 3000);
    };

    ws.onerror = (error) => {
      console.error('WebSocket Error');
      // On error, onclose will also fire, so we just let onclose handle reconnect
    };

    wsRef.current = ws;
  }, []);

  useEffect(() => {
    connect();
    
    return () => {
      if (wsRef.current) {
        // Prevent onclose from triggering a reconnect when we explicitly unmount
        wsRef.current.onclose = null; 
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  return {
    dataHistory,
    latestData,
    decisions,
    isConnected,
  };
}
