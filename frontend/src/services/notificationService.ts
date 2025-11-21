import api from '@/lib/api';
import { Notification } from '@/types';

export interface NotificationResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Notification[];
}

export interface UnreadCountResponse {
  unread_count: number;
}

export interface MarkReadRequest {
  notification_ids?: number[];
}

class NotificationService {
  
  async getNotifications(page = 1, isRead?: boolean): Promise<NotificationResponse> {
    const params: any = { page };
    if (isRead !== undefined) {
      params.is_read = isRead;
    }
    const response = await api.get<NotificationResponse>('/notifications/', { params });
    return response.data;
  }

  
  async getUnreadCount(): Promise<number> {
    const response = await api.get<UnreadCountResponse>('/notifications/count/');
    return response.data.unread_count;
  }

  
  async markAsRead(notificationIds?: number[]): Promise<void> {
    const data: MarkReadRequest = notificationIds ? { notification_ids: notificationIds } : {};
    await api.post('/notifications/mark-read/', data);
  }

  
  async deleteNotification(notificationId: number): Promise<void> {
    await api.delete(`/notifications/${notificationId}/delete/`);
  }

  
  async clearAll(): Promise<void> {
    await api.delete('/notifications/clear/');
  }
}

export const notificationService = new NotificationService();
