/**
 * React Hook for WebSocket Real-time Updates (T051-T052)
 *
 * Provides real-time task updates via WebSocket connection.
 * Auto-connects when authenticated user is available.
 */
'use client';

import { useEffect, useRef, useCallback, useState } from 'react';
import {
  TaskWebSocketClient,
  getWebSocketUrl,
  WebSocketMessage,
  WebSocketMessageType,
  MessageHandler,
} from '@/lib/websocket';

interface UseWebSocketOptions {
  userId: string | null;
  token?: string | null;
  enabled?: boolean;
  onTaskCreated?: (payload: Record<string, unknown>) => void;
  onTaskUpdated?: (payload: Record<string, unknown>) => void;
  onTaskDeleted?: (payload: Record<string, unknown>) => void;
  onTaskCompleted?: (payload: Record<string, unknown>) => void;
  onNotification?: (message: WebSocketMessage) => void;
}

interface UseWebSocketReturn {
  isConnected: boolean;
  lastMessage: WebSocketMessage | null;
  notifications: WebSocketMessage[];
  clearNotifications: () => void;
}

/**
 * Hook for WebSocket real-time updates.
 *
 * Usage:
 * ```tsx
 * const { isConnected, lastMessage, notifications } = useWebSocket({
 *   userId: currentUser?.id,
 *   token: authToken,
 *   onTaskCreated: (payload) => refetchTasks(),
 *   onTaskUpdated: (payload) => refetchTasks(),
 * });
 * ```
 */
export function useWebSocket(options: UseWebSocketOptions): UseWebSocketReturn {
  const {
    userId,
    token,
    enabled = true,
    onTaskCreated,
    onTaskUpdated,
    onTaskDeleted,
    onTaskCompleted,
    onNotification,
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);
  const [notifications, setNotifications] = useState<WebSocketMessage[]>([]);
  const clientRef = useRef<TaskWebSocketClient | null>(null);

  // Stable callback refs to avoid reconnection on handler changes
  const handlersRef = useRef(options);
  handlersRef.current = options;

  const clearNotifications = useCallback(() => {
    setNotifications([]);
  }, []);

  useEffect(() => {
    if (!userId || !enabled) {
      return;
    }

    const wsUrl = getWebSocketUrl();
    if (!wsUrl) return;

    const client = new TaskWebSocketClient({
      url: wsUrl,
      userId,
      token: token || undefined,
      onConnect: () => {
        setIsConnected(true);
      },
      onDisconnect: () => {
        setIsConnected(false);
      },
      onMessage: (message) => {
        setLastMessage(message);
      },
      onError: (error) => {
        console.error('WebSocket error:', error);
      },
    });

    // Register type-specific handlers
    client.on('task.created', (msg) => {
      handlersRef.current.onTaskCreated?.(msg.payload || {});
    });

    client.on('task.updated', (msg) => {
      handlersRef.current.onTaskUpdated?.(msg.payload || {});
    });

    client.on('task.deleted', (msg) => {
      handlersRef.current.onTaskDeleted?.(msg.payload || {});
    });

    client.on('task.completed', (msg) => {
      handlersRef.current.onTaskCompleted?.(msg.payload || {});
    });

    client.on('notification', (msg) => {
      setNotifications(prev => [...prev, msg]);
      handlersRef.current.onNotification?.(msg);
    });

    client.connect();
    clientRef.current = client;

    // Cleanup on unmount or userId change
    return () => {
      client.disconnect();
      clientRef.current = null;
      setIsConnected(false);
    };
  }, [userId, token, enabled]);

  return {
    isConnected,
    lastMessage,
    notifications,
    clearNotifications,
  };
}
