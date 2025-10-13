from rest_framework import serializers
from .models import Like, Retweet, Bookmark, Follow
from apps.authentication.serializers import UserBasicSerializer


class LikeSerializer(serializers.ModelSerializer):
    """
    Serializer for Like model.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'tweet', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class RetweetSerializer(serializers.ModelSerializer):
    """
    Serializer for Retweet model.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Retweet
        fields = ['id', 'user', 'tweet', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class BookmarkSerializer(serializers.ModelSerializer):
    """
    Serializer for Bookmark model.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Bookmark
        fields = ['id', 'user', 'tweet', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class FollowSerializer(serializers.ModelSerializer):
    """
    Serializer for Follow model.
    """
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = Follow
        fields = ['id', 'follower', 'following', 'created_at']
        read_only_fields = ['id', 'follower', 'following', 'created_at']