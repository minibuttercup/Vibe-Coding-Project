/**
 * Auth API Functions
 * 
 * Provides functions for authentication operations:
 * - signup: Create new user account
 * - login: Authenticate with email/password
 * - logout: Sign out current user
 * - getCurrentUser: Get authenticated user info
 */

import api from './client';

// =====================================================
// TYPES
// =====================================================
export interface SignUpData {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginData {
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: {
    id: string;
    email: string;
    user_metadata: {
      first_name?: string;
      last_name?: string;
    };
  };
}

export interface UserResponse {
  id: string;
  email: string;
  user_metadata: {
    first_name?: string;
    last_name?: string;
  };
}

// =====================================================
// API FUNCTIONS
// =====================================================

/**
 * Sign up a new user
 */
export async function signUp(data: SignUpData): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/signup', data);
  
  // Store token in localStorage
  localStorage.setItem('access_token', response.access_token);
  
  return response;
}

/**
 * Login with email and password
 */
export async function login(data: LoginData): Promise<AuthResponse> {
  const response = await api.post<AuthResponse>('/auth/login', data);
  
  // Store token in localStorage
  localStorage.setItem('access_token', response.access_token);
  
  return response;
}

/**
 * Logout current user
 */
export async function logout(): Promise<void> {
  try {
    await api.post('/auth/logout', {});
  } finally {
    // Always remove token, even if API call fails
    localStorage.removeItem('access_token');
  }
}

/**
 * Get current authenticated user
 */
export async function getCurrentUser(): Promise<UserResponse | null> {
  const token = localStorage.getItem('access_token');
  if (!token) {
    return null;
  }
  
  try {
    return await api.get<UserResponse>('/auth/me');
  } catch {
    // Token is invalid or expired
    localStorage.removeItem('access_token');
    return null;
  }
}

/**
 * Check if user is authenticated
 */
export function isAuthenticated(): boolean {
  return !!localStorage.getItem('access_token');
}