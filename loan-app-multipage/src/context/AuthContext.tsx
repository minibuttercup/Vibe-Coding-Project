/**
 * Auth Context
 * 
 * Provides global authentication state management for the React app.
 * Handles login, logout, signup, and user state.
 */

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import * as authApi from '../api/auth';

// =====================================================
// TYPES
// =====================================================
interface User {
  id: string;
  email: string;
  user_metadata: {
    first_name?: string;
    last_name?: string;
  };
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, firstName: string, lastName: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

// =====================================================
// CONTEXT
// =====================================================
const AuthContext = createContext<AuthContextType | undefined>(undefined);

// =====================================================
// PROVIDER
// =====================================================
export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  /**
   * Check for existing authentication on mount
   */
  useEffect(() => {
    const initAuth = async () => {
      try {
        const currentUser = await authApi.getCurrentUser();
        setUser(currentUser);
      } catch {
        // User not authenticated
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  /**
   * Login with email and password
   */
  const login = useCallback(async (email: string, password: string) => {
    setIsLoading(true);
    try {
      const response = await authApi.login({ email, password });
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Sign up new user
   */
  const signup = useCallback(async (
    email: string,
    password: string,
    firstName: string,
    lastName: string
  ) => {
    setIsLoading(true);
    try {
      const response = await authApi.signUp({
        email,
        password,
        first_name: firstName,
        last_name: lastName,
      });
      setUser(response.user);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Logout current user
   */
  const logout = useCallback(async () => {
    setIsLoading(true);
    try {
      await authApi.logout();
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, []);

  /**
   * Refresh user data from server
   */
  const refreshUser = useCallback(async () => {
    try {
      const currentUser = await authApi.getCurrentUser();
      setUser(currentUser);
    } catch {
      setUser(null);
    }
  }, []);

  const value: AuthContextType = {
    user,
    isLoading,
    isAuthenticated: !!user,
    login,
    signup,
    logout,
    refreshUser,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

// =====================================================
// HOOK
// =====================================================
export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}