import React, { createContext, useContext, useState, useEffect } from 'react';
import { User } from '@/types';
import { authService, LoginRequest, RegisterRequest } from '@/services/authService';
import { tokenManager } from '@/lib/api';

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  signup: (userData: RegisterRequest) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
  updateUser: (userData: Partial<User>) => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initializeAuth = async () => {
      try {
        // Check if we have tokens and they're valid
        if (authService.isAuthenticated()) {
          // Try to get current user from API
          const currentUser = await authService.getCurrentUser();
          setUser(currentUser);
          localStorage.setItem('user', JSON.stringify(currentUser));
        } else {
          // Clear any stale data
          tokenManager.clearTokens();
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
        tokenManager.clearTokens();
      } finally {
        setIsLoading(false);
      }
    };

    initializeAuth();
  }, []);

  const login = async (email: string, password: string) => {
    try {
      setIsLoading(true);
      const response = await authService.login({ email, password });
      
      // Convert backend user format to frontend format
      const userData: User = {
        id: response.user.id,
        username: response.user.username,
        email: response.user.email,
        first_name: response.user.first_name,
        last_name: response.user.last_name,
        full_name: `${response.user.first_name} ${response.user.last_name}`.trim(),
        is_verified: response.user.is_verified,
        profile_image_url: response.user.profile_image,
        date_joined: new Date().toISOString(), // Will be updated when we fetch full profile
        is_private: false,
        followers_count: 0,
        following_count: 0,
        tweets_count: 0,
        is_following: false,
      };

      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      
      // Fetch complete user profile
      try {
        const fullProfile = await authService.getCurrentUser();
        setUser(fullProfile);
        localStorage.setItem('user', JSON.stringify(fullProfile));
      } catch (profileError) {
        console.error('Failed to fetch full profile:', profileError);
      }
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (userData: RegisterRequest) => {
    try {
      setIsLoading(true);
      await authService.register(userData);
      
      // After successful registration, log the user in
      await login(userData.email, userData.password);
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = async () => {
    try {
      await authService.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      localStorage.removeItem('user');
    }
  };

  const updateUser = (userData: Partial<User>) => {
    if (user) {
      const updatedUser = { ...user, ...userData };
      setUser(updatedUser);
      localStorage.setItem('user', JSON.stringify(updatedUser));
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, signup, logout, isLoading, updateUser }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
