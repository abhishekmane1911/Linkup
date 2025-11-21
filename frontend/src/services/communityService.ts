import api from '@/lib/api';

export interface Community {
  id: number;
  name: string;
  description: string;
  owner: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    profile_image?: string;
  };
  privacy: 'public' | 'private';
  banner_image_url?: string;
  is_active: boolean;
  created_at: string;
  members_count: number;
  posts_count: number;
  is_member: boolean;
  user_role?: 'owner' | 'admin' | 'moderator' | 'member' | null;
  rules?: string;
}

export interface CommunityListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: Community[];
}

class CommunityService {
  async getCommunities(page = 1, pageSize = 20): Promise<CommunityListResponse> {
    const response = await api.get<CommunityListResponse>('/communities/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getCommunity(communityId: number): Promise<Community> {
    const response = await api.get<Community>(`/communities/${communityId}/`);
    return response.data;
  }

  async createCommunity(data: {
    name: string;
    description: string;
    privacy: 'public' | 'private';
    rules?: string;
  }): Promise<Community> {
    const response = await api.post<Community>('/communities/', data);
    return response.data;
  }

  async updateCommunity(communityId: number, data: Partial<Community>): Promise<Community> {
    const response = await api.patch<Community>(`/communities/${communityId}/`, data);
    return response.data;
  }

  async joinCommunity(communityId: number): Promise<{ message: string }> {
    const response = await api.post(`/communities/${communityId}/join/`);
    return response.data;
  }

  async leaveCommunity(communityId: number): Promise<{ message: string }> {
    const response = await api.post(`/communities/${communityId}/leave/`);
    return response.data;
  }

  async getCommunityFeed(communityId: number, page = 1, pageSize = 20) {
    const response = await api.get(`/communities/${communityId}/feed/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getMyCommunities(page = 1, pageSize = 20): Promise<CommunityListResponse> {
    const response = await api.get<CommunityListResponse>('/communities/my-communities/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async discoverCommunities(page = 1, pageSize = 20): Promise<CommunityListResponse> {
    const response = await api.get<CommunityListResponse>('/communities/discover/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async searchCommunities(query: string, page = 1, pageSize = 20): Promise<CommunityListResponse> {
    const response = await api.get<CommunityListResponse>('/communities/search/', {
      params: { q: query, page, page_size: pageSize }
    });
    return response.data;
  }

  async updateCommunityBanner(communityId: number, imageFile: File): Promise<Community> {
    const formData = new FormData();
    formData.append('banner_image', imageFile);

    const response = await api.patch<Community>(`/communities/${communityId}/`, formData);
    return response.data;
  }
}

export const communityService = new CommunityService();
