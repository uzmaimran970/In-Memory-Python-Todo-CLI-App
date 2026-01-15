/**
 * Chat API Client - Phase III AI Chatbot Integration
 * Handles all chat-related API communication with JWT authentication
 */

import { getAuthToken } from './auth';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "https://in-memory-python-todo-cli-app-production.up.railway.app";

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface ToolCallInfo {
  name: string;
  result: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  conversation_id: string;
  tool_calls?: ToolCallInfo[];
}

export interface ChatHistoryResponse {
  conversation_id: string | null;
  messages: ChatMessage[];
  total: number;
}

export interface ClearHistoryResponse {
  message: string;
  deleted_count: number;
}

/**
 * Send a chat message to the AI assistant
 */
export async function sendChatMessage(message: string): Promise<ChatResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Please login to use the chat');
  }

  const response = await fetch(`${API_BASE_URL}/api/chat`, {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ message }),
  });

  if (response.status === 401) {
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Chat request failed' }));
    throw new Error(error.detail || 'Chat request failed');
  }

  return response.json();
}

/**
 * Get conversation history for the current user
 */
export async function getChatHistory(limit: number = 50): Promise<ChatHistoryResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Please login to view chat history');
  }

  const response = await fetch(
    `${API_BASE_URL}/api/chat/history?limit=${limit}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    }
  );

  if (response.status === 401) {
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    throw new Error('Failed to load chat history');
  }

  return response.json();
}

/**
 * Clear all chat history for the current user
 */
export async function clearChatHistory(): Promise<ClearHistoryResponse> {
  const token = getAuthToken();

  if (!token) {
    throw new Error('Please login to clear chat history');
  }

  const response = await fetch(`${API_BASE_URL}/api/chat/clear`, {
    method: 'DELETE',
    headers: {
      'Authorization': `Bearer ${token}`,
    },
  });

  if (response.status === 401) {
    throw new Error('Session expired. Please login again.');
  }

  if (!response.ok) {
    throw new Error('Failed to clear chat history');
  }

  return response.json();
}
