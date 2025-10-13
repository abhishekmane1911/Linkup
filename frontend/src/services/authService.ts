import api, { tokenManager } from '@/lib/api';
import { User } from '@/types';

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access: string;
  refresh: string;
  user: {
    id: number;
    username: string;
    email: string;
    first_name: string;
    last_name: string;
    is_verified: boolean;
    profile_image: string | null;
  };
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  password_confirm: string;
  first_name: string;
  last_name: string;
  bio?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  phone_number?: string;
}

export interface RegisterResponse {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  bio?: string;
  location?: string;
  website?: string;
  is_verified: boolean;
  date_joined: string;
}

export interface UserProfile {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  bio?: string;
  location?: string;
  website?: string;
  birth_date?: string;
  phone_number?: string;
  profile_image?: string;
  banner_image?: string;
  profile_image_url?: string;
  banner_image_url?: string;
  is_verified: boolean;
  is_private: boolean;
  date_joined: string;
  last_login?: string;
  followers_count: number;
  following_count: number;
  tweets_count: number;
  is_following: boolean;
}

export interface PasswordChangeRequest {
  old_password: string;
  new_password: string;
  new_password_confirm: string;
}

class AuthService {
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    // Django JWT expects 'email' field since USERNAME_FIELD = 'email'
    const loginData = {
      email: credentials.email,
      password: credentials.password
    };
    
    const response = await api.post<LoginResponse>('/auth/login/', loginData);
    
    // Store tokens
    tokenManager.setTokens(response.data.access, response.data.refresh);
    
    return response.data;
  }

  async register(userData: RegisterRequest): Promise<RegisterResponse> {
    const response = await api.post<RegisterResponse>('/auth/register/', userData);
    return response.data;
  }

  async logout(): Promise<void> {
    try {
      await api.post('/auth/logout/');
    } catch (error) {
      // Even if logout fails on server, clear local tokens
      console.error('Logout error:', error);
    } finally {
      tokenManager.clearTokens();
    }
  }

  async getCurrentUser(): Promise<UserProfile> {
    const response = await api.get<UserProfile>('/auth/profile/me/');
    return response.data;
  }

  async updateProfile(profileData: Partial<UserProfile>): Promise<UserProfile> {
    const response = await api.patch<UserProfile>('/auth/profile/', profileData);
    return response.data;
  }

  async changePassword(passwordData: PasswordChangeRequest): Promise<void> {
    await api.post('/auth/password/change/', passwordData);
  }

  async refreshToken(): Promise<string> {
    const refreshToken = tokenManager.getRefreshToken();
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    const response = await api.post<{ access: string }>('/auth/token/refresh/', {
      refresh: refreshToken
    });

    const newAccessToken = response.data.access;
    tokenManager.setTokens(newAccessToken, refreshToken);
    
    return newAccessToken;
  }

  isAuthenticated(): boolean {
    const token = tokenManager.getAccessToken();
    return token !== null && !tokenManager.isTokenExpired(token);
  }
}

export const authService = new AuthService();