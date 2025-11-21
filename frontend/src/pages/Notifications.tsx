import { useState, useEffect } from 'react';
import { Notification } from '@/types';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Button } from '@/components/ui/button';
import { Heart, Repeat2, UserPlus, MessageCircle, Loader2, CheckCheck, Trash2 } from 'lucide-react';
import { motion } from 'framer-motion';
import { formatDistanceToNow } from 'date-fns';
import { notificationService } from '@/services/notificationService';
import { useToast } from '@/hooks/use-toast';
import { getErrorMessage } from '@/lib/errorHandler';

const Notifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isMarkingRead, setIsMarkingRead] = useState(false);
  const { toast } = useToast();

  useEffect(() => {
    fetchNotifications();
  }, []);

  const fetchNotifications = async () => {
    setIsLoading(true);
    try {
      const response = await notificationService.getNotifications();
      setNotifications(response.results);
    } catch (error: any) {
      console.error('Failed to fetch notifications:', error);
      const errorMessage = typeof error.response?.data?.error === 'string' 
        ? error.response.data.error 
        : error.response?.data?.message || error.message || 'Please try again later';
      
      toast({
        title: 'Failed to load notifications',
        description: errorMessage,
        variant: 'destructive',
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleMarkAllRead = async () => {
    setIsMarkingRead(true);
    try {
      await notificationService.markAsRead();
      
      setNotifications(notifications.map(n => ({ ...n, read: true })));
      toast({
        title: 'All notifications marked as read',
      });
    } catch (error: any) {
      console.error('Failed to mark notifications as read:', error);
      toast({
        title: 'Failed to mark as read',
        description: 'Please try again later',
        variant: 'destructive',
      });
    } finally {
      setIsMarkingRead(false);
    }
  };

  const handleMarkRead = async (notificationId: number) => {
    try {
      await notificationService.markAsRead([notificationId]);
    
      setNotifications(notifications.map(n => 
        n.id === notificationId ? { ...n, read: true } : n
      ));
    } catch (error: any) {
      console.error('Failed to mark notification as read:', error);
    }
  };

  const handleDelete = async (notificationId: number) => {
    try {
      await notificationService.deleteNotification(notificationId);
     
      setNotifications(notifications.filter(n => n.id !== notificationId));
      toast({
        title: 'Notification deleted',
      });
    } catch (error: any) {
      console.error('Failed to delete notification:', error);
      toast({
        title: 'Failed to delete notification',
        description: 'Please try again later',
        variant: 'destructive',
      });
    }
  };

  const getNotificationIcon = (type: Notification['type']) => {
    switch (type) {
      case 'like':
        return <Heart className="w-8 h-8 text-pink-500 fill-pink-500" />;
      case 'retweet':
        return <Repeat2 className="w-8 h-8 text-green-500" />;
      case 'follow':
        return <UserPlus className="w-8 h-8 text-primary" />;
      case 'reply':
      case 'mention':
        return <MessageCircle className="w-8 h-8 text-primary" />;
    }
  };

  const getNotificationText = (notification: Notification) => {
    switch (notification.type) {
      case 'like':
        return 'liked your tweet';
      case 'retweet':
        return 'retweeted your tweet';
      case 'follow':
        return 'followed you';
      case 'reply':
        return 'replied to your tweet';
      case 'mention':
        return 'mentioned you in a tweet';
    }
  };

  const unreadCount = notifications.filter(n => !n.read).length;

  return (
    <div className="flex-1 border-r border-border">
      <header className="sticky top-0 z-10 bg-background/80 backdrop-blur-md border-b border-border p-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold">Notifications</h2>
          {unreadCount > 0 && (
            <Button
              variant="ghost"
              size="sm"
              onClick={handleMarkAllRead}
              disabled={isMarkingRead}
              className="gap-2"
            >
              {isMarkingRead ? (
                <Loader2 className="w-4 h-4 animate-spin" />
              ) : (
                <CheckCheck className="w-4 h-4" />
              )}
              Mark all read
            </Button>
          )}
        </div>
      </header>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
        {isLoading ? (
          <div className="flex justify-center items-center py-12">
            <Loader2 className="w-8 h-8 animate-spin text-primary" />
          </div>
        ) : notifications.length === 0 ? (
          <div className="p-8 text-center text-muted-foreground">
            <div className="mb-4">
              <Heart className="w-16 h-16 mx-auto text-muted-foreground/50" />
            </div>
            <h3 className="text-lg font-semibold mb-2">No notifications yet</h3>
            <p>When someone likes, retweets, or follows you, you'll see it here.</p>
          </div>
        ) : (
          notifications.map((notification) => (
          <motion.div
            key={notification.id}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className={`border-b border-border p-4 hover:bg-muted/50 transition-colors cursor-pointer ${
              !notification.read ? 'bg-primary/5' : ''
            }`}
            onClick={() => !notification.read && handleMarkRead(notification.id)}
          >
            <div className="flex gap-4">
              <div className="flex-shrink-0">
                {getNotificationIcon(notification.type)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <Avatar className="w-8 h-8">
                    <AvatarImage src={notification.user.profile_image_url} />
                    <AvatarFallback>{notification.user.full_name?.[0] || notification.user.username?.[0] || 'U'}</AvatarFallback>
                  </Avatar>
                </div>

                <p className="text-sm">
                  <span className="font-bold">{notification.user.full_name}</span>
                  {' '}
                  <span className="text-muted-foreground">{getNotificationText(notification)}</span>
                </p>

                <p className="text-sm text-muted-foreground mt-1">
                  {formatDistanceToNow(new Date(notification.created_at), { addSuffix: true })}
                </p>

                {notification.tweet && (
                  <div className="mt-2 p-3 border border-border rounded-lg bg-muted/30">
                    <p className="text-sm text-muted-foreground line-clamp-2">
                      {notification.tweet.content}
                    </p>
                  </div>
                )}
              </div>

              <div className="flex-shrink-0">
                <Button
                  variant="ghost"
                  size="icon"
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDelete(notification.id);
                  }}
                  className="h-8 w-8"
                >
                  <Trash2 className="w-4 h-4" />
                </Button>
              </div>
            </div>
          </motion.div>
          ))
        )}
      </motion.div>
    </div>
  );
};

export default Notifications;
