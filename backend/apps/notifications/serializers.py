from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Notification
from apps.tweets.models import Tweet

User = get_user_model()


class NotificationUserSerializer(serializers.ModelSerializer):
    """Serializer for user in notifications."""
    full_name = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'profile_image_url']
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()


class NotificationTweetSerializer(serializers.ModelSerializer):
    """Serializer for tweet in notifications."""
    
    class Meta:
        model = Tweet
        fields = ['id', 'content', 'created_at']


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for notifications."""
    user = NotificationUserSerializer(source='actor', read_only=True)
    tweet = serializers.SerializerMethodField()
    type = serializers.CharField(source='notification_type', read_only=True)
    read = serializers.BooleanField(source='is_read', read_only=True)
    
    class Meta:
        model = Notification
        fields = ['id', 'type', 'user', 'tweet', 'created_at', 'read']
    
    def get_tweet(self, obj):
        """Get tweet object if notification is related to a tweet."""
        if obj.content_object and isinstance(obj.content_object, Tweet):
            return NotificationTweetSerializer(obj.content_object).data
        return None


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read."""
    notification_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="List of notification IDs to mark as read. If empty, marks all as read."
    )
