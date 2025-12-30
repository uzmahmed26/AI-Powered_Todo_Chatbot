import React, { createContext, useState, useContext, useEffect } from 'react';
import { apiClient } from '../services/api';
import {jwtDecode} from 'jwt-decode';

interface User {
  id: string;
  email: string;
  full_name: string | null;
  is_active: boolean;
  created_at: string;
}

interface TokenPayload {
  user_id: string;
  email: string;
  exp: number;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  signin: (email: string, password: string) => Promise<void>;
  signup: (email: string, password: string, fullName: string) => Promise<void>;
  signout: () => void;
  refreshToken: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Check for existing token on mount
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const decoded: TokenPayload = jwtDecode(token);
        // Check if token is expired
        if (decoded.exp * 1000 > Date.now()) {
          // Token valid, fetch user info
          fetchCurrentUser();
        } else {
          // Token expired, try to refresh
          refreshToken();
        }
      } catch (error) {
        console.error('Invalid token:', error);
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await apiClient.getCurrentUser();
      setUser(response);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      signout();
    }
  };

  const signin = async (email: string, password: string) => {
    try {
      const response = await apiClient.signin(email, password);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setUser(response.user);
    } catch (error) {
      console.error('Signin failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string, fullName: string) => {
    try {
      const response = await apiClient.signup(email, password, fullName);
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('refresh_token', response.refresh_token);
      setUser(response.user);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    }
  };

  const signout = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    setUser(null);
  };

  const refreshToken = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        signout();
        return;
      }

      const response = await apiClient.refreshToken(refreshToken);
      localStorage.setItem('access_token', response.access_token);
      await fetchCurrentUser();
    } catch (error) {
      console.error('Token refresh failed:', error);
      signout();
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated: !!user,
        isLoading,
        signin,
        signup,
        signout,
        refreshToken,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
