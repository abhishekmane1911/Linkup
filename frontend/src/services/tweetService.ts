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

  async getUserReplies(userId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/user/${userId}/replies/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getUserMedia(userId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/user/${userId}/media/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getUserLikes(userId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/user/${userId}/likes/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getUserRetweets(userId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/user/${userId}/retweets/`, {
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
      
      
      let hashtags: { id: number; name: string; usage_count: number }[];
      
      if (Array.isArray(response.data)) {
        
        hashtags = response.data;
      } else if (response.data.results && Array.isArray(response.data.results)) {
        
        hashtags = response.data.results;
      } else {
        console.error('Unexpected response format:', response.data);
        return [];
      }
      
      
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

  


  // Like/Unlike Tweet
  async likeTweet(tweetId: number): Promise<{ likes_count: number }> {
    const response = await api.post(`/interactions/tweets/${tweetId}/like/`);
    return { likes_count: response.data.likes_count };
  }

  async unlikeTweet(tweetId: number): Promise<{ likes_count: number }> {
    const response = await api.delete(`/interactions/tweets/${tweetId}/like/`);
    return { likes_count: response.data.likes_count };
  }

  // Retweet/Unretweet Tweet
  async retweetTweet(tweetId: number): Promise<{ retweets_count: number }> {
    const response = await api.post(`/interactions/tweets/${tweetId}/retweet/`);
    return { retweets_count: response.data.retweets_count };
  }

  async unretweetTweet(tweetId: number): Promise<{ retweets_count: number }> {
    const response = await api.delete(`/interactions/tweets/${tweetId}/retweet/`);
    return { retweets_count: response.data.retweets_count };
  }

  // Bookmark/Unbookmark Tweet
  async bookmarkTweet(tweetId: number): Promise<{ bookmarks_count: number }> {
    const response = await api.post(`/interactions/tweets/${tweetId}/bookmark/`);
    return { bookmarks_count: response.data.bookmarks_count };
  }

  async unbookmarkTweet(tweetId: number): Promise<{ bookmarks_count: number }> {
    const response = await api.delete(`/interactions/tweets/${tweetId}/bookmark/`);
    return { bookmarks_count: response.data.bookmarks_count };
  }

  async getBookmarkedTweets(page = 1, pageSize = 20): Promise<{ bookmarks: any[]; count: number }> {
    const response = await api.get<{ bookmarks: any[]; count: number }>('/interactions/bookmarks/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  // Replies/Comments
  async getTweetReplies(tweetId: number, page = 1, pageSize = 20): Promise<FeedResponse> {
    const response = await api.get<FeedResponse>(`/tweets/${tweetId}/replies/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async createReply(tweetId: number, content: string, mediaFiles?: File[]): Promise<TweetResponse> {
    const formData = new FormData();
    formData.append('content', content);
    
    if (mediaFiles) {
      mediaFiles.forEach((file) => {
        formData.append('media_files', file);
      });
    }

    const response = await api.post<TweetResponse>(`/tweets/${tweetId}/replies/`, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    return response.data;
  }

}

export const tweetService = new TweetService();