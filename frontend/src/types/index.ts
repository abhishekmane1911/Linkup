export interface User {
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

export interface Tweet {
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

export interface Media {
  id: number;
  media_type: string;
  file_url: string;
  alt_text?: string;
  file_size?: number;
  width?: number;
  height?: number;
  duration?: number;
}

export interface Notification {
  id: number;
  type: 'like' | 'retweet' | 'follow' | 'reply' | 'mention';
  user: User;
  tweet?: Tweet;
  created_at: string;
  read: boolean;
}

export interface DirectMessage {
  message_id: number;
  conversation_id: number;
  sender_user_id: number;
  content: string;
  sent_at: string;
  is_read: boolean;
  sender: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    full_name: string;
    profile_image_url?: string;
    is_verified: boolean;
  };
}

export interface Conversation {
  conversation_id: number;
  participants: {
    id: number;
    username: string;
    first_name: string;
    last_name: string;
    full_name: string;
    profile_image_url?: string;
    is_verified: boolean;
  }[];
  last_message?: DirectMessage;
  created_at: string;
  last_message_at: string;
  unread_count: number;
}
