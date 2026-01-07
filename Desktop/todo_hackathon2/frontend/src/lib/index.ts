/**
 * Centralized Library Exports - Phase II Todo Hackathon
 * Barrel file for easy imports across the application
 */

// API client
export { api } from './api';

// Authentication utilities
export {
  getAuthToken,
  setAuthToken,
  clearAuthToken,
  isAuthenticated,
} from './auth';

// Validation utilities
export {
  validateEmail,
  validatePassword,
  validateTitle,
  validateDescription,
  validateName,
} from './validation';
