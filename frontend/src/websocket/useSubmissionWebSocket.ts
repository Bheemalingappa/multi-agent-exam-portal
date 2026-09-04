import { useEffect, useRef, useState, useCallback } from 'react';
import { RealtimeEvent } from '../types/event';

const getWsBaseUrl = () => import.meta.env.VITE_WS_BASE_URL || `${window.location.protocol === 'https:' ? 'wss:' : 'ws:'}//${window.location.host}/api/v1`;

export function useSubmissionWebSocket(submissionId?: string) {
  const [lastEvent, setLastEvent] = useState<RealtimeEvent | null>(null);
  const [connected, setConnected] = useState<boolean>(false);
  const wsRef = useRef<WebSocket | null>(null);

  const connect = useCallback(() => {
    if (!submissionId) return;
    const token = localStorage.getItem('access_token');
    if (!token) return;

    const wsUrl = `${getWsBaseUrl()}/ws/submissions/${submissionId}?token=${token}`;
    const ws = new WebSocket(wsUrl);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      try {
        const parsed: RealtimeEvent = JSON.parse(event.data);
        setLastEvent(parsed);
      } catch {
        // Handle non-JSON frame
      }
    };

    ws.onclose = () => {
      setConnected(false);
      setTimeout(() => {
        if (wsRef.current === ws) {
          connect();
        }
      }, 3000);
    };

    wsRef.current = ws;
  }, [submissionId]);

  useEffect(() => {
    connect();
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [connect]);

  return { connected, lastEvent };
}
