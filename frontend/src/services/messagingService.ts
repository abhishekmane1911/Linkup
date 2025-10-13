import api from '@/lib/api';
import { DirectMessage, Conversation } from '@/types';

export interface ConversationResponse {
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
  last_message?: {
    message_id: number;
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
  };
  created_at: string;
  last_message_at: string;
  unread_count: number;
}

export interface MessageResponse {
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

export interface ConversationsListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: ConversationResponse[];
}

export interface MessagesListResponse {
  count: number;
  next?: string;
  previous?: string;
  results: MessageResponse[];
}

export interface SendMessageRequest {
  content: string;
  recipient_id?: number;
}class
 MessagingService {
  async getConversations(page = 1, pageSize = 20): Promise<ConversationsListResponse> {
    const response = await api.get<ConversationsListResponse>('/messaging/conversations/', {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async getConversation(conversationId: number): Promise<ConversationResponse> {
    const response = await api.get<ConversationResponse>(`/messaging/conversations/${conversationId}/`);
    return response.data;
  }

  async getMessages(conversationId: number, page = 1, pageSize = 50): Promise<MessagesListResponse> {
    const response = await api.get<MessagesListResponse>(`/messaging/conversations/${conversationId}/messages/`, {
      params: { page, page_size: pageSize }
    });
    return response.data;
  }

  async sendMessage(conversationId: number, messageData: SendMessageRequest): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>(`/messaging/conversations/${conversationId}/messages/create/`, messageData);
    return response.data;
  }

  async createConversation(recipientId: number, initialMessage: string): Promise<MessageResponse> {
    const response = await api.post<MessageResponse>('/messaging/messages/create/', {
      recipient_id: recipientId,
      content: initialMessage
    });
    return response.data;
  }

  async markMessagesAsRead(conversationId: number): Promise<void> {
    await api.post(`/messaging/conversations/${conversationId}/mark-read/`);
  }

  async deleteConversation(conversationId: number): Promise<void> {
    await api.delete(`/messaging/conversations/${conversationId}/`);
  }

  async deleteMessage(conversationId: number, messageId: number): Promise<void> {
    await api.delete(`/messaging/messages/${messageId}/delete/`);
  }
}

export const messagingService = new MessagingService();