/**
 * WebSocket Client for Real-time Updates (T049-T050)
 *
 * Connects to the WebSocket service for live task updates.
 * Handles reconnection, authentication, and message routing.
 */

export type WebSocketMessageType =
  | 'connected'
  | 'task.created'
  | 'task.updated'
  | 'task.deleted'
  | 'task.completed'
  | 'notification'
  | 'pong'
  | 'status';

export interface WebSocketMessage {
  type: WebSocketMessageType;
  task_id?: number;
  payload?: Record<string, unknown>;
  title?: string;
  body?: string;
  timestamp?: string;
  notification_type?: string;
  metadata?: Record<string, unknown>;
  [key: string]: unknown;
}

export type MessageHandler = (message: WebSocketMessage) => void;

interface WebSocketClientConfig {
  url: string;
  userId: string;
  token?: string;
  onMessage?: MessageHandler;
  onConnect?: () => void;
  onDisconnect?: () => void;
  onError?: (error: Event) => void;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  pingInterval?: number;
}

/**
 * WebSocket client with auto-reconnection and keep-alive.
 */
export class TaskWebSocketClient {
  private ws: WebSocket | null = null;
  private config: Required<WebSocketClientConfig>;
  private reconnectAttempts = 0;
  private reconnectTimer: NodeJS.Timeout | null = null;
  private pingTimer: NodeJS.Timeout | null = null;
  private isManualClose = false;
  private messageHandlers: Map<WebSocketMessageType, MessageHandler[]> = new Map();

  constructor(config: WebSocketClientConfig) {
    this.config = {
      reconnectInterval: 3000,
      maxReconnectAttempts: 10,
      pingInterval: 30000,
      onMessage: () => {},
      onConnect: () => {},
      onDisconnect: () => {},
      onError: () => {},
      token: '',
      ...config,
    };
  }

  /**
   * Connect to WebSocket server.
   */
  connect(): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      return; // Already connected
    }

    const url = this.config.token
      ? `${this.config.url}/${this.config.userId}?token=${this.config.token}`
      : `${this.config.url}/${this.config.userId}`;

    try {
      this.ws = new WebSocket(url);

      this.ws.onopen = () => {
        this.reconnectAttempts = 0;
        this.startPing();
        this.config.onConnect();
      };

      this.ws.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          // Call global handler
          this.config.onMessage(message);
          // Call type-specific handlers
          const handlers = this.messageHandlers.get(message.type) || [];
          handlers.forEach(handler => handler(message));
        } catch (e) {
          console.error('Failed to parse WebSocket message:', e);
        }
      };

      this.ws.onclose = () => {
        this.stopPing();
        this.config.onDisconnect();

        if (!this.isManualClose) {
          this.attemptReconnect();
        }
      };

      this.ws.onerror = (error) => {
        this.config.onError(error);
      };
    } catch (e) {
      console.error('WebSocket connection failed:', e);
      this.attemptReconnect();
    }
  }

  /**
   * Disconnect from WebSocket server.
   */
  disconnect(): void {
    this.isManualClose = true;
    this.stopPing();
    this.stopReconnect();

    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * Register a handler for a specific message type.
   */
  on(type: WebSocketMessageType, handler: MessageHandler): () => void {
    if (!this.messageHandlers.has(type)) {
      this.messageHandlers.set(type, []);
    }
    this.messageHandlers.get(type)!.push(handler);

    // Return unsubscribe function
    return () => {
      const handlers = this.messageHandlers.get(type) || [];
      const index = handlers.indexOf(handler);
      if (index > -1) {
        handlers.splice(index, 1);
      }
    };
  }

  /**
   * Send a message to the server.
   */
  send(data: string): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(data);
    }
  }

  /**
   * Check if connected.
   */
  get isConnected(): boolean {
    return this.ws?.readyState === WebSocket.OPEN;
  }

  private startPing(): void {
    this.pingTimer = setInterval(() => {
      this.send('ping');
    }, this.config.pingInterval);
  }

  private stopPing(): void {
    if (this.pingTimer) {
      clearInterval(this.pingTimer);
      this.pingTimer = null;
    }
  }

  private attemptReconnect(): void {
    if (this.reconnectAttempts >= this.config.maxReconnectAttempts) {
      console.warn('Max reconnect attempts reached');
      return;
    }

    this.reconnectAttempts++;
    const delay = this.config.reconnectInterval * Math.min(this.reconnectAttempts, 5);

    this.reconnectTimer = setTimeout(() => {
      console.log(`Reconnecting... attempt ${this.reconnectAttempts}`);
      this.connect();
    }, delay);
  }

  private stopReconnect(): void {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }
}

/**
 * Get WebSocket URL based on environment.
 */
export function getWebSocketUrl(): string {
  if (typeof window === 'undefined') return '';

  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  const wsHost = process.env.NEXT_PUBLIC_WS_URL || `${protocol}//${window.location.host}`;
  return `${wsHost}/ws`;
}
