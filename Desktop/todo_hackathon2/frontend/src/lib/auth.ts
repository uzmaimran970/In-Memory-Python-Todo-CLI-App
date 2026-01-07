/**
 * Authentication Utility Functions - Phase II Todo Hackathon
 * Handles JWT token storage and retrieval
 */

const AUTH_TOKEN_KEY = 'auth_token';

/**
 * Get authentication token from storage
 * Prefers HTTP-only cookies, falls back to localStorage
 */
export function getAuthToken(): string | null {
  // Try to get from localStorage (fallback for development)
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem(AUTH_TOKEN_KEY);
    console.log('[AUTH] Getting token from localStorage:', token ? `${token.substring(0, 20)}... (length: ${token.length})` : 'NO TOKEN FOUND');
    return token;
  }
  console.log('[AUTH] Cannot access localStorage (not in browser)');
  return null;
}

/**
 * Set authentication token in storage
 * Stores in localStorage (in production, should use HTTP-only cookies)
 */
export function setAuthToken(token: string): void {
  if (typeof window !== 'undefined') {
    console.log('[AUTH] Saving token to localStorage:', token ? `${token.substring(0, 20)}...` : 'EMPTY TOKEN');
    localStorage.setItem(AUTH_TOKEN_KEY, token);
    console.log('[AUTH] Token saved. Verifying:', localStorage.getItem(AUTH_TOKEN_KEY) ? 'SUCCESS' : 'FAILED');
  }
}

/**
 * Clear authentication token from storage
 * Used during logout
 */
export function clearAuthToken(): void {
  if (typeof window !== 'undefined') {
    console.log('[AUTH] Clearing token from localStorage');
    localStorage.removeItem(AUTH_TOKEN_KEY);
    console.log('[AUTH] Token cleared. Verification:', localStorage.getItem(AUTH_TOKEN_KEY) === null ? 'SUCCESS' : 'FAILED');
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  const token = getAuthToken();
  return token !== null && token.length > 0;
}
