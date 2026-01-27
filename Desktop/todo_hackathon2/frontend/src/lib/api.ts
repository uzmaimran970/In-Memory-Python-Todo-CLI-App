/**
 * API Client Wrapper - Phase II Todo Hackathon
 * Handles all backend API communication with JWT authentication
 */

import {
  User,
  Task,
  AuthResponse,
  SignupData,
  LoginData,
  CreateTaskData,
  UpdateTaskData,
  TaskListResponse,
  APIError,
} from '@/types';
import { getAuthToken, clearAuthToken } from './auth';

// Use relative URL - Next.js rewrites will proxy to backend
const API_BASE_URL = "";
// Log configuration on module load
console.log('[API] Configuration loaded:', {
  API_BASE_URL,
  NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_BETTER_AUTH_URL: process.env.NEXT_PUBLIC_BETTER_AUTH_URL,
  hasBetterAuthSecret: !!process.env.BETTER_AUTH_SECRET,
});

/**
 * Generic API request wrapper with JWT auto-inclusion and error handling
 */
async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getAuthToken();

  // Debug logging
  console.log('[API] Request to:', endpoint);
  console.log('[API] Token from localStorage:', token ? `${token.substring(0, 20)}...` : 'NO TOKEN');

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
  };

  // Add JWT token if available
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
    console.log('[API] Authorization header set:', `Bearer ${token.substring(0, 20)}...`);
  } else {
    console.warn('[API] No token available - request will be unauthenticated');
  }

  // Merge with any additional headers from options
  if (options.headers) {
    Object.assign(headers, options.headers);
  }

  try {
    console.log('[API] Fetching:', `${API_BASE_URL}${endpoint}`, {
      method: options.method || 'GET',
      headers,
      hasBody: !!options.body
    });

    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      ...options,
      headers,
    });

    console.log('[API] Response received:', {
      status: response.status,
      statusText: response.statusText,
      ok: response.ok,
      url: response.url
    });

    // Handle 401 Unauthorized - session expired
    if (response.status === 401) {
      console.error('[API] 401 UNAUTHORIZED - Token invalid or expired');
      console.error('[API] Current token:', getAuthToken() ? `${getAuthToken()?.substring(0, 20)}...` : 'NO TOKEN');
      clearAuthToken();
      if (typeof window !== 'undefined') {
        console.error('[API] Redirecting to login with session_expired error');
        window.location.href = '/login?error=session_expired';
      }
      throw new Error('Session expired. Please log in again.');
    }

    // Handle 403 Forbidden - permission denied
    if (response.status === 403) {
      throw new Error("You don't have permission to access this resource.");
    }

    // Handle 404 Not Found
    if (response.status === 404) {
      throw new Error('Resource not found.');
    }

    // Handle 500 Server Error
    if (response.status >= 500) {
      throw new Error('Server error. Please try again later.');
    }

    // Handle other error responses
    if (!response.ok) {
      const errorData: APIError = await response.json().catch(() => ({
        detail: 'An unexpected error occurred',
        status_code: response.status,
      }));
      throw new Error(errorData.detail || 'Request failed');
    }

    // Return empty object for 204 No Content
    if (response.status === 204) {
      return {} as T;
    }

    return await response.json();
  } catch (error) {
    // Network error or fetch failed
    if (error instanceof TypeError && error.message === 'Failed to fetch') {
      throw new Error('Unable to connect. Please check your internet connection.');
    }
    throw error;
  }
}

/**
 * Authentication API
 */
export const api = {
  // Signup
  signup: async (data: SignupData): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/api/auth/signup', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Login
  login: async (data: LoginData): Promise<AuthResponse> => {
    return apiRequest<AuthResponse>('/api/auth/login', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Get current user
  getMe: async (): Promise<User> => {
    return apiRequest<User>('/api/auth/me', {
      method: 'GET',
    });
  },

  // Get all tasks for authenticated user
  getTasks: async (): Promise<Task[]> => {
    const response = await apiRequest<TaskListResponse>('/api/tasks', {
      method: 'GET',
    });
    return response.tasks || [];
  },

  // Create new task
  createTask: async (data: CreateTaskData): Promise<Task> => {
    return apiRequest<Task>('/api/tasks', {
      method: 'POST',
      body: JSON.stringify(data),
    });
  },

  // Update task
  updateTask: async (taskId: number, data: UpdateTaskData): Promise<Task> => {
    return apiRequest<Task>(`/api/tasks/${taskId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  },

  // Toggle task completion
  toggleTask: async (taskId: number): Promise<Task> => {
    return apiRequest<Task>(`/api/tasks/${taskId}/complete`, {
      method: 'PATCH',
    });
  },

  // Delete task
  deleteTask: async (taskId: number): Promise<void> => {
    return apiRequest<void>(`/api/tasks/${taskId}`, {
      method: 'DELETE',
    });
  },
};
