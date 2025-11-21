import api from '@/lib/api';
import { User } from '@/types';

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

export interface FollowResponse {
  following: boolean;
  followers_count: number;
  following_count: number;
}

export interface UsersListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: UserProfile[];
}

class UserService {
  async getUser(userId: number): Promise<UserProfile> {
    const response = await api.get<UserProfile>(`/users/${userId}/`);
    return response.data;
  }

  async getUserByUsername(username: string): Promise<UserProfile> {
    try {
      
      const searchResponse = await api.get<{users: UserProfile[], count: number, query: string}>('/users/search/', {
        params: { q: username }
      });
      
      if (!searchResponse.data || !searchResponse.data.users) {
        throw new Error('Invalid response format');
      }
      
      const user = searchResponse.data.users.find(u => u.username === username);
      if (!user) {
        throw new Error('User not found');
      }
      
      
      const profileResponse = await api.get<UserProfile>(`/users/${user.id}/`);
      return profileResponse.data;
    } catch (error: any) {
      console.error('Failed to get user profile:', error);
      throw new Error(`User '${username}' not found`);
    }
  }

  async followUser(userId: number): Promise<FollowResponse> {
    const response = await api.post<FollowResponse>(`/interactions/users/${userId}/follow/`);
    return response.data;
  }

  async unfollowUser(userId: number): Promise<FollowResponse> {
    const response = await api.delete<FollowResponse>(`/interactions/users/${userId}/follow/`);
    return response.data;
  }

  async getFollowers(userId: number, page = 1, pageSize = 20): Promise<UsersListResponse> {
    const response = await api.get<{followers: UserProfile[], count: number}>(`/users/${userId}/followers/`, {
      params: { page, page_size: pageSize }
    });
    
    
    return {
      count: response.data.count,
      results: response.data.followers,
      next: null,
      previous: null
    };
  }

  async getFollowing(userId: number, page = 1, pageSize = 20): Promise<UsersListResponse> {
    const response = await api.get<{following: UserProfile[], count: number}>(`/users/${userId}/following/`, {
      params: { page, page_size: pageSize }
    });
    
   
    return {
      count: response.data.count,
      results: response.data.following,
      next: null,
      previous: null
    };
  }

  async searchUsers(query: string, page = 1, pageSize = 20): Promise<UsersListResponse> {
    const response = await api.get<{users: UserProfile[], count: number, query: string}>('/users/search/', {
      params: { q: query, page, page_size: pageSize }
    });
    
    
    return {
      count: response.data.count,
      results: response.data.users,
      next: null,
      previous: null
    };
  }

  async getSuggestedUsers(page = 1, pageSize = 10): Promise<UsersListResponse> {
    const response = await api.get<UsersListResponse>('/tweets/discover/users/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async updateProfileImage(imageFile: File): Promise<UserProfile> {
    console.log('updateProfileImage called with file:', imageFile);
    const formData = new FormData();
    formData.append('profile_image', imageFile);
    
    console.log('FormData entries:');
    for (const pair of formData.entries()) {
      console.log(pair[0], pair[1]);
    }

    const response = await api.patch<UserProfile>('/auth/profile/', formData);
    console.log('Profile image update response:', response.data);
    return response.data;
  }

  async updateBannerImage(imageFile: File): Promise<UserProfile> {
    console.log('updateBannerImage called with file:', imageFile);
    const formData = new FormData();
    formData.append('banner_image', imageFile);
    
    console.log('FormData entries:');
    for (const pair of formData.entries()) {
      console.log(pair[0], pair[1]);
    }

    const response = await api.patch<UserProfile>('/auth/profile/', formData);
    console.log('Banner image update response:', response.data);
    return response.data;
  }
}

export const userService = new UserService();