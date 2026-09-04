import { useEffect, useRef, useState, useCallback } from 'react';
import { RealtimeEvent } from '../types/event';

const getWsBaseUrl = () => import.meta.env.VITE_WS_BASE_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1`;

export function useExamWebSocket(attemptId?: string) {
  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!attemptId) return;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = `${getWsBaseUrl()}/ws/exams/${attemptId}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const parsed: RealtimeEvent = JSON.parse(event.data);
        setLastEvent(parsed);
      } catch {
        // Ping / Pong frame
      }
    };

    ws.onclose = () => {
      setConnected(false);
      // Exponential backoff reconnect
      setTimeout(() => {
        if (wsRef.current === ws) {
          connect();
        }
      }, 3000);
    };

    wsRef.current = ws;
  }, [attemptId]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  const sendPing = () => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type: 'PING' }));
    }
  };

  return { connected, lastEvent, sendPing };
}
