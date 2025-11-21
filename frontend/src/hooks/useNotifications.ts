import { useState, useEffect } from 'react';
import { notificationService } from '@/services/notificationService';

/**
 * Hook to get unread notification count
 * Polls every 30 seconds
 */
export const useNotificationCount = () => {
  const [unreadCount, setUnreadCount] = useState(0);
  const [isLoading, setIsLoading] = useState(true);

  const fetchCount = async () => {
    try {
      const count = await notificationService.getUnreadCount();
      setUnreadCount(count);
    } catch (error) {
      console.error('Failed to fetch notification count:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchCount();

    // Poll every 30 seconds
    const interval = setInterval(fetchCount, 30000);

    return () => clearInterval(interval);
  }, []);

  return { unreadCount, isLoading, refetch: fetchCount };
};
