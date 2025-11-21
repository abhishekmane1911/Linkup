from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class Notification(models.Model):
    """
    Notification model to track user notifications.
    Automatically created via database triggers.
    """
    NOTIFICATION_TYPES = [
        ('like', 'Like'),
        ('retweet', 'Retweet'),
        ('follow', 'Follow'),
        ('reply', 'Reply'),
        ('mention', 'Mention'),
    ]
    
    
    recipient = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_received',
        help_text="User who receives this notification",
        db_index=True
    )
    
    
    actor = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications_sent',
        help_text="User who triggered this notification"
    )
    

    notification_type = models.CharField(
        max_length=20,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification",
        db_index=True
    )
    
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')
    
    
    is_read = models.BooleanField(
        default=False,
        help_text="Whether the notification has been read",
        db_index=True
    )
    
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['recipient', '-created_at']),
            models.Index(fields=['recipient', 'is_read']),
            models.Index(fields=['actor', 'notification_type']),
        ]
        
        unique_together = ['recipient', 'actor', 'notification_type', 'content_type', 'object_id']
    
    def __str__(self):
        return f"{self.actor.username} {self.notification_type} → {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            from django.utils import timezone
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    @classmethod
    def create_notification(cls, recipient, actor, notification_type, content_object=None):
        """
        Create a notification if it doesn't already exist.
        Prevents duplicate notifications.
        """
        
        if recipient.id == actor.id:
            return None
        
        
        content_type = None
        object_id = None
        if content_object:
            content_type = ContentType.objects.get_for_model(content_object)
            object_id = content_object.id
        
        
        notification, created = cls.objects.get_or_create(
            recipient=recipient,
            actor=actor,
            notification_type=notification_type,
            content_type=content_type,
            object_id=object_id,
            defaults={'is_read': False}
        )
        
        return notification if created else None
