from django.db import models
from django.conf import settings
from django.utils import timezone


class ConversationManager(models.Manager):
    """
    Custom manager for Conversation model with conversation creation logic.
    """
    
    def get_or_create_conversation(self, user1, user2):
        """
        Get existing conversation between two users or create a new one.
        Returns tuple (conversation, created).
        """
        # Find existing conversation between these two users
        existing_conversation = self.filter(
            participants__user=user1
        ).filter(
            participants__user=user2
        ).filter(
            participants__is_active=True
        ).distinct().first()
        
        if existing_conversation:
            return existing_conversation, False
        
        # Create new conversation
        conversation = self.create()
        
        # Add both users as participants
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=user1
        )
        ConversationParticipant.objects.create(
            conversation=conversation,
            user=user2
        )
        
        return conversation, True
    
    def get_user_conversations(self, user):
        """
        Get all active conversations for a user.
        """
        return self.filter(
            participants__user=user,
            participants__is_active=True,
            is_active=True
        ).distinct().order_by('-updated_at')
    
    def can_users_message(self, user1, user2):
        """
        Check if two users can message each other based on privacy settings.
        Users can only message each other if they follow each other mutually.
        """
        try:
            from apps.interactions.models import Follow
            
            # Check mutual following - both users must follow each other
            follows_target = Follow.objects.filter(
                follower=user1,
                following=user2
            ).exists()
            
            followed_by_target = Follow.objects.filter(
                follower=user2,
                following=user1
            ).exists()
            
            return follows_target and followed_by_target
        
        except ImportError:
            # If Follow model doesn't exist, allow messaging
            return True


class Conversation(models.Model):
    """
    Model representing a conversation between users.
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    objects = ConversationManager()
    
    class Meta:
        db_table = 'conversations'
        ordering = ['-updated_at']
    
    def __str__(self):
        participants = self.participants.all()[:2]
        if len(participants) >= 2:
            return f"Conversation between {participants[0].user.username} and {participants[1].user.username}"
        return f"Conversation {self.id}"
    
    @property
    def last_message(self):
        """Get the most recent message in this conversation."""
        return self.messages.filter(is_deleted=False).first()
    
    @property
    def participant_count(self):
        """Get the number of participants in this conversation."""
        return self.participants.count()
    
    def get_other_participant(self, user):
        """Get the other participant in a two-person conversation."""
        return self.participants.exclude(user=user).first()
    
    def add_message(self, sender, content):
        """Add a new message to this conversation and update timestamp."""
        message = DirectMessage.objects.create(
            conversation=self,
            sender=sender,
            content=content
        )
        # Update conversation timestamp
        self.updated_at = timezone.now()
        self.save(update_fields=['updated_at'])
        return message
    
    def deactivate_conversation(self):
        """Deactivate the conversation."""
        self.is_active = False
        self.save(update_fields=['is_active'])
    
    def get_active_participants(self):
        """Get all active participants in the conversation."""
        return self.participants.filter(is_active=True)
    
    def can_user_access(self, user):
        """Check if a user can access this conversation."""
        return self.participants.filter(user=user, is_active=True).exists()


class ConversationParticipant(models.Model):
    """
    Model representing a user's participation in a conversation.
    """
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='participants'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='conversation_participants'
    )
    joined_at = models.DateTimeField(auto_now_add=True)
    last_read_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'conversation_participants'
        unique_together = ['conversation', 'user']
        ordering = ['joined_at']
    
    def __str__(self):
        return f"{self.user.username} in conversation {self.conversation.id}"
    
    def mark_as_read(self):
        """Mark all messages in this conversation as read for this user."""
        self.last_read_at = timezone.now()
        self.save(update_fields=['last_read_at'])
    
    def get_unread_count(self):
        """Get the count of unread messages for this participant."""
        if not self.last_read_at:
            return self.conversation.messages.filter(is_deleted=False).count()
        
        return self.conversation.messages.filter(
            created_at__gt=self.last_read_at,
            is_deleted=False
        ).exclude(sender=self.user).count()


class DirectMessage(models.Model):
    """
    Model representing a direct message within a conversation.
    """
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE, 
        related_name='messages'
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='sent_messages'
    )
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'direct_messages'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Message from {self.sender.username} at {self.created_at}"
    
    def delete_message(self):
        """Soft delete the message."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def is_read_by_user(self, user):
        """Check if this message has been read by a specific user."""
        if user == self.sender:
            return True  # Sender has always "read" their own message
        
        participant = self.conversation.participants.filter(user=user).first()
        if not participant or not participant.last_read_at:
            return False
        
        return self.created_at <= participant.last_read_at
