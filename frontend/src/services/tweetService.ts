import api from '@/lib/api';
import { Tweet, Media, User } from '@/types';

export interface CreateTweetRequest {
  content: string;
  parent_tweet?: number;
  community?: number;
  media_files?: File[];
}

export interface TweetResponse {
  id: number;
  content: string;
  created_at: string;
  updated_at: string;
  parent_tweet?: number;
  community?: number;
  author: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    profile_image_url?: string;
    is_verified: boolean;
  };
  likes_count: number;
  retweets_count: number;
  bookmarks_count: number;
  reply_count: number;
  is_reply: boolean;
  is_liked: boolean;
  is_retweeted: boolean;
  is_bookmarked: boolean;
  media: Media[];
  hashtags: string[];
}

export interface FeedResponse {
  count: number;
  next?: string;
  previous?: string;
  results: TweetResponse[];
}

export interface SearchParams {
  q?: string;
  hashtag?: string;
  user?: string;
  page?: number;
  page_size?: number;
}

class TweetService {
  async createTweet(tweetData: CreateTweetRequest): Promise<TweetResponse> {
    const formData = new FormData();
    formData.append('content', tweetData.content);
    
    if (tweetData.parent_tweet) {
      formData.append('parent_tweet', tweetData.parent_tweet.toString());
    }
    
    if (tweetData.community) {
      formData.append('community', tweetData.community.toString());
    }
    
    if (tweetData.media_files) {
      tweetData.media_files.forEach((file) => {
        formData.append('media_files', file);
      });
    }

    const response = await api.post<TweetResponse>('/tweets/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

  async getTweet(tweetId: number): Promise<TweetResponse> {
    const response = await api.get<TweetResponse>(`/tweets/${tweetId}/`);
    return response.data;
  }

  async updateTweet(tweetId: number, content: string): Promise<TweetResponse> {
    const response = await api.patch<TweetResponse>(`/tweets/${tweetId}/`, { content });
    return response.data;
  }

  async deleteTweet(tweetId: number): Promise<void> {
    await api.delete(`/tweets/${tweetId}/`);
  }

  async getHomeFeed(page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>('/tweets/feed/home/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getUserTweets(userId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/user/${userId}/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getTweetReplies(tweetId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/${tweetId}/replies/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async searchTweets(params: SearchParams): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>('/tweets/search/', { params });
    return response.data;
  }

  async getHashtagFeed(hashtag: string, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/hashtags/${hashtag}/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getTrendingHashtags(): Promise<{ hashtag: string; count: number }[]> {
    try {
      const response = await api.get('/tweets/hashtags/trending/');
      
      console.log('Trending hashtags response:', response.data);
      
      // Handle both paginated and non-paginated responses
      let hashtags: { id: number; name: string; usage_count: number }[];
      
      if (Array.isArray(response.data)) {
        // Non-paginated response
        hashtags = response.data;
      } else if (response.data.results && Array.isArray(response.data.results)) {
        // Paginated response
        hashtags = response.data.results;
      } else {
        console.error('Unexpected response format:', response.data);
        return [];
      }
      
      // Transform the backend response to match frontend expectations
      const transformed = hashtags.map(item => ({
        hashtag: item.name,
        count: item.usage_count
      }));
      
      console.log('Transformed hashtags:', transformed);
      return transformed;
    } catch (error) {
      console.error('Error fetching trending hashtags:', error);
      throw error;
    }
  }

  // Interaction methods
  async likeTweet(tweetId: number): Promise<{ liked: boolean; likes_count: number }> {
    const response = await api.post<{ liked: boolean; likes_count: number }>(`/interactions/tweets/${tweetId}/like/`);
    return response.data;
  }

  async retweetTweet(tweetId: number): Promise<{ retweeted: boolean; retweets_count: number }> {
    const response = await api.post<{ retweeted: boolean; retweets_count: number }>(`/interactions/tweets/${tweetId}/retweet/`);
    return response.data;
  }

  async bookmarkTweet(tweetId: number): Promise<{ bookmarked: boolean }> {
    const response = await api.post<{ bookmarked: boolean }>(`/interactions/tweets/${tweetId}/bookmark/`);
    return response.data;
  }

  async getBookmarkedTweets(page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>('/interactions/bookmarks/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }
}

export const tweetService = new TweetService();