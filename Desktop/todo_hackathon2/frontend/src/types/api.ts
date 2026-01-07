/**
 * API Type Definitions - Phase II Todo Hackathon
 * Matches backend FastAPI contract specifications
 */

// User Entity
export interface User {
  id: number;
  email: string;
  name?: string;
  created_at: string;
}

// Task Entity
export interface Task {
  id: number;
  title: string;
  description?: string;
  is_completed: boolean;
  created_at: string;
  user_id: number;
}

// Authentication Types
export interface AuthResponse {
  user: User;
  token: string;
}

export interface SignupData {
  email: string;
  password: string;
  name?: string;
}

export interface LoginData {
  email: string;
  password: string;
}

// Task Operation Types
export interface CreateTaskData {
  title: string;
  description?: string;
}

export interface UpdateTaskData {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

// API Response Types
export interface TaskListResponse {
  tasks: Task[];
  total: number;
}

// API Error Types
export interface APIError {
  detail: string;
  status_code: number;
}

export interface ValidationError {
  field: string;
  message: string;
}
