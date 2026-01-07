/**
 * UI State Type Definitions - Phase II Todo Hackathon
 * Client-side state management types
 */

import { Task } from './api';

// Filter Types
export type FilterType = 'all' | 'active' | 'completed';

// Toast Notification Types
export type ToastType = 'success' | 'error' | 'info';

export interface Toast {
  id: string;
  type: ToastType;
  message: string;
  duration?: number;
}

// Modal State Types
export interface ModalState {
  isOpen: boolean;
  data?: any;
}

export interface CreateTaskModalState extends ModalState {
  data?: never;
}

export interface EditTaskModalState extends ModalState {
  data?: Task;
}

export interface DeleteTaskModalState extends ModalState {
  data?: Task;
}

// UI State
export interface UIState {
  activeFilter: FilterType;
  isLoading: boolean;
  error: string | null;
  modals: {
    createTask: CreateTaskModalState;
    editTask: EditTaskModalState;
    deleteTask: DeleteTaskModalState;
  };
}

// Component Props Types
export interface ButtonProps {
  variant?: 'primary' | 'secondary' | 'danger';
  size?: 'small' | 'medium' | 'large';
  loading?: boolean;
  disabled?: boolean;
  children: React.ReactNode;
  onClick?: () => void;
  type?: 'button' | 'submit' | 'reset';
  className?: string;
}

export interface InputProps {
  label?: string;
  error?: string;
  helperText?: string;
  maxLength?: number;
  showCharCount?: boolean;
  type?: 'text' | 'email' | 'password' | 'textarea';
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  disabled?: boolean;
  required?: boolean;
  className?: string;
}

export interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  children: React.ReactNode;
  className?: string;
}
