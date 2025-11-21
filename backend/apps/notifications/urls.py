from django.urls import path
from .views import (
    NotificationListView,
    mark_notifications_read,
    notification_count,
    delete_notification,
    clear_all_notifications
)

app_name = 'notifications'

urlpatterns = [
    # List notifications
    path('', NotificationListView.as_view(), name='notification-list'),
    
    # Mark as read
    path('mark-read/', mark_notifications_read, name='mark-read'),
    
    # Get unread count
    path('count/', notification_count, name='notification-count'),
    
    # Delete specific notification
    path('<int:pk>/delete/', delete_notification, name='delete-notification'),
    
    # Clear all notifications
    path('clear/', clear_all_notifications, name='clear-all'),
]
