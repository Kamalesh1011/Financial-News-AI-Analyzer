import { useState, useEffect, useRef } from "react";

interface WebSocketMessage {
  type: string;
  data: unknown;
}

const WS_BASE = (import.meta.env.VITE_API_BASE_URL || "http://localhost:8000").replace(/^http/, "ws");

export function useWebSocket() {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let mounted = true;

    const doConnect = () => {
      if (!mounted) return;
      try {
        const ws = new WebSocket(`${WS_BASE}/ws`);

        ws.onopen = () => {
          if (mounted) setIsConnected(true);
        };

        ws.onmessage = (event) => {
          try {
            const msg = JSON.parse(event.data) as WebSocketMessage;
            if (mounted) setLastMessage(msg);
          } catch {
            // ignore parse errors
          }
        };

        ws.onclose = () => {
          if (mounted) {
            setIsConnected(false);
            reconnectTimer.current = setTimeout(doConnect, 5000);
          }
        };

        ws.onerror = () => {
          ws.close();
        };

        wsRef.current = ws;
      } catch {
        if (mounted) {
          reconnectTimer.current = setTimeout(doConnect, 5000);
        }
      }
    };

    doConnect();

    return () => {
      mounted = false;
      wsRef.current?.close();
      if (reconnectTimer.current) clearTimeout(reconnectTimer.current);
    };
  }, []);

  return { isConnected, lastMessage };
}
