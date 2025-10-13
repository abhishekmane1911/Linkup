from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Tweet, Media, Hashtag, TweetHashtag

User = get_user_model()


class HashtagSerializer(serializers.ModelSerializer):
    """
    Serializer for hashtags.
    """
    class Meta:
        model = Hashtag
        fields = ['id', 'name', 'usage_count']
        read_only_fields = fields


class MediaSerializer(serializers.ModelSerializer):
    """
    Serializer for media attachments.
    """
    file_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Media
        fields = [
            'id', 'media_type', 'file_url', 'alt_text', 
            'file_size', 'width', 'height', 'duration'
        ]
        read_only_fields = fields
    
    def get_file_url(self, obj):
        """Get the media file URL."""
        if obj.file:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url
        return None


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for including author information in tweets.
    """
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'first_name', 'last_name', 
            'is_verified', 'profile_image_url'
        ]
        read_only_fields = fields
    
    def get_profile_image_url(self, obj):
        """Get the profile image URL."""
        return obj.get_profile_image_url()


class CommunityBasicSerializer(serializers.ModelSerializer):
    """
    Basic community serializer for including community information in tweets.
    """
    banner_image_url = serializers.SerializerMethodField()
    
    class Meta:
        from apps.communities.models import Community
        model = Community
        fields = ['id', 'name', 'description', 'privacy', 'banner_image_url']
        read_only_fields = fields
    
    def get_banner_image_url(self, obj):
        """Get the community banner image URL."""
        return obj.get_banner_image_url()


class TweetSerializer(serializers.ModelSerializer):
    """
    Tweet serializer with author information and interaction counts.
    """
    author = UserBasicSerializer(read_only=True)
    community = CommunityBasicSerializer(read_only=True)
    media = MediaSerializer(many=True, read_only=True)
    hashtags = serializers.SerializerMethodField()
    parent_tweet_info = serializers.SerializerMethodField()
    likes_count = serializers.ReadOnlyField()
    retweets_count = serializers.ReadOnlyField()
    bookmarks_count = serializers.ReadOnlyField()
    reply_count = serializers.ReadOnlyField()
    is_reply = serializers.ReadOnlyField()
    
    # These will be implemented when we add social interactions
    is_liked = serializers.SerializerMethodField()
    is_retweeted = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    
    class Meta:
        model = Tweet
        fields = [
            'id', 'content', 'author', 'community', 'parent_tweet', 'parent_tweet_info', 'media', 'hashtags', 'created_at', 
            'updated_at', 'likes_count', 'retweets_count', 'bookmarks_count', 'reply_count',
            'is_reply', 'is_liked', 'is_retweeted', 'is_bookmarked'
        ]
        read_only_fields = [
            'id', 'author', 'community', 'created_at', 'updated_at', 'likes_count', 
            'retweets_count', 'bookmarks_count', 'reply_count', 'is_reply', 'is_liked', 
            'is_retweeted', 'is_bookmarked', 'media', 'hashtags', 'parent_tweet_info'
        ]
    
    def get_hashtags(self, obj):
        """Get hashtags associated with this tweet."""
        hashtags = obj.get_hashtags()
        return HashtagSerializer(hashtags, many=True).data
    
    def get_parent_tweet_info(self, obj):
        """Get basic info about parent tweet if this is a reply."""
        if obj.parent_tweet and not obj.parent_tweet.is_deleted:
            return {
                'id': obj.parent_tweet.id,
                'content': obj.parent_tweet.content[:100] + "..." if len(obj.parent_tweet.content) > 100 else obj.parent_tweet.content,
                'author': UserBasicSerializer(obj.parent_tweet.author).data,
                'created_at': obj.parent_tweet.created_at
            }
        return None
    
    def get_is_liked(self, obj):
        """Check if the current user has liked this tweet."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_is_retweeted(self, obj):
        """Check if the current user has retweeted this tweet."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.retweets.filter(user=request.user).exists()
        return False
    
    def get_is_bookmarked(self, obj):
        """Check if the current user has bookmarked this tweet."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.bookmarks.filter(user=request.user).exists()
        return False
    
    def validate_content(self, value):
        """Validate tweet content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Tweet content cannot be empty.")
        
        if len(value) > 280:
            raise serializers.ValidationError("Tweet content cannot exceed 280 characters.")
        
        return value.strip()
    
    def validate_parent_tweet(self, value):
        """Validate parent tweet for replies."""
        if value and value.is_deleted:
            raise serializers.ValidationError("Cannot reply to a deleted tweet.")
        return value


class TweetCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating tweets with media support.
    """
    media_files = serializers.ListField(
        child=serializers.FileField(),
        write_only=True,
        required=False,
        max_length=4,  # Maximum 4 media files per tweet
        help_text="Media files to attach to the tweet (max 4)"
    )
    
    class Meta:
        model = Tweet
        fields = ['content', 'parent_tweet', 'community', 'media_files']
    
    def validate_content(self, value):
        """Validate tweet content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Tweet content cannot be empty.")
        
        if len(value) > 280:
            raise serializers.ValidationError("Tweet content cannot exceed 280 characters.")
        
        return value.strip()
    
    def validate_parent_tweet(self, value):
        """Validate parent tweet for replies."""
        if value and value.is_deleted:
            raise serializers.ValidationError("Cannot reply to a deleted tweet.")
        return value
    
    def validate_community(self, value):
        """Validate community access."""
        if value:
            request = self.context.get('request')
            if request and request.user.is_authenticated:
                # Check if user is a member of the community
                from apps.communities.models import CommunityMember
                try:
                    membership = CommunityMember.objects.get(
                        community=value,
                        user=request.user,
                        is_active=True
                    )
                    # Check if user has permission to post content
                    if not membership.has_permission('post_content'):
                        raise serializers.ValidationError(
                            "You don't have permission to post in this community."
                        )
                except CommunityMember.DoesNotExist:
                    raise serializers.ValidationError(
                        "You must be a member of this community to post."
                    )
        return value
    
    def validate_media_files(self, value):
        """Validate media files."""
        if len(value) > 4:
            raise serializers.ValidationError("Maximum 4 media files allowed per tweet.")
        
        # Validate file sizes (max 5MB per file)
        max_size = 5 * 1024 * 1024  # 5MB
        for file in value:
            if file.size > max_size:
                raise serializers.ValidationError(f"File {file.name} is too large. Maximum size is 5MB.")
        
        return value
    
    def create(self, validated_data):
        """Create a new tweet with media attachments."""
        media_files = validated_data.pop('media_files', [])
        validated_data['author'] = self.context['request'].user
        
        tweet = super().create(validated_data)
        
        # Create media objects for uploaded files
        for media_file in media_files:
            Media.objects.create(
                tweet=tweet,
                file=media_file
            )
        
        return tweet


class TweetUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating tweets (only content can be updated).
    """
    class Meta:
        model = Tweet
        fields = ['content']
    
    def validate_content(self, value):
        """Validate tweet content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Tweet content cannot be empty.")
        
        if len(value) > 280:
            raise serializers.ValidationError("Tweet content cannot exceed 280 characters.")
        
        return value.strip()

class TweetReplySerializer(serializers.ModelSerializer):
    """
    Serializer specifically for creating replies to tweets.
    """
    parent_tweet_info = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = Tweet
        fields = ['content', 'parent_tweet', 'parent_tweet_info']
        
    def validate_parent_tweet(self, value):
        """Validate that parent tweet exists and is not deleted."""
        if not value:
            raise serializers.ValidationError("Parent tweet is required for replies.")
        
        if value.is_deleted:
            raise serializers.ValidationError("Cannot reply to a deleted tweet.")
        
        return value
    
    def validate_content(self, value):
        """Validate reply content."""
        if not value or not value.strip():
            raise serializers.ValidationError("Reply content cannot be empty.")
        
        if len(value) > 280:
            raise serializers.ValidationError("Reply content cannot exceed 280 characters.")
        
        return value.strip()
    
    def get_parent_tweet_info(self, obj):
        """Get parent tweet information."""
        if obj.parent_tweet and not obj.parent_tweet.is_deleted:
            return {
                'id': obj.parent_tweet.id,
                'content': obj.parent_tweet.content[:100] + "..." if len(obj.parent_tweet.content) > 100 else obj.parent_tweet.content,
                'author': UserBasicSerializer(obj.parent_tweet.author).data
            }
        return None
    
    def create(self, validated_data):
        """Create a reply tweet."""
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)