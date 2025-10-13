from django.db import models
from django.db.models import Q
from django.core.validators import MaxLengthValidator, FileExtensionValidator
from django.contrib.auth import get_user_model
from django.utils import timezone
import os
import re

User = get_user_model()


class Tweet(models.Model):
    """
    Tweet model for storing user tweets with content validation.
    """
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='tweets',
        help_text="The user who created this tweet"
    )
    content = models.TextField(
        max_length=280,
        validators=[MaxLengthValidator(280, "Tweet content cannot exceed 280 characters")],
        help_text="Tweet content (max 280 characters)"
    )
    parent_tweet = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        help_text="Parent tweet if this is a reply"
    )
    community = models.ForeignKey(
        'communities.Community',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tweets',
        help_text="Community this tweet belongs to (optional)"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete functionality
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'tweets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent_tweet']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_deleted']),
        ]
    
    def __str__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"@{self.author.username}: {content_preview}"
    
    def save(self, *args, **kwargs):
        """Override save to handle content validation and timestamps."""
        if len(self.content.strip()) == 0:
            raise ValueError("Tweet content cannot be empty")
        
        # Update timestamp on edit
        if self.pk:
            self.updated_at = timezone.now()
        
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Extract and link hashtags for new tweets
        if is_new:
            self.extract_and_link_hashtags()
    
    def extract_hashtags(self):
        """Extract hashtags from tweet content."""
        hashtag_pattern = r'#(\w+)'
        hashtags = re.findall(hashtag_pattern, self.content, re.IGNORECASE)
        return [hashtag.lower() for hashtag in hashtags]
    
    def extract_and_link_hashtags(self):
        """Extract hashtags from content and create relationships."""
        hashtags = self.extract_hashtags()
        
        for i, hashtag_name in enumerate(hashtags):
            # Get or create hashtag
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_name)
            
            # Create tweet-hashtag relationship if it doesn't exist
            tweet_hashtag, created = TweetHashtag.objects.get_or_create(
                tweet=self,
                hashtag=hashtag,
                defaults={'position': i}
            )
            
            # Increment usage count if this is a new relationship
            if created:
                hashtag.increment_usage()
    
    def get_hashtags(self):
        """Get all hashtags associated with this tweet."""
        return Hashtag.objects.filter(tweet_hashtags__tweet=self)
    
    def get_root_tweet(self):
        """Get the root tweet of the conversation thread."""
        root = self
        while root.parent_tweet and not root.parent_tweet.is_deleted:
            root = root.parent_tweet
        return root
    
    def get_thread_tweets(self):
        """Get all tweets in the same conversation thread."""
        root = self.get_root_tweet()
        return Tweet.objects.filter(
            Q(id=root.id) |
            Q(parent_tweet=root) |
            Q(parent_tweet__parent_tweet=root)
        ).filter(is_deleted=False).order_by('created_at')
    
    def get_direct_replies(self):
        """Get direct replies to this tweet."""
        return self.replies.filter(is_deleted=False).order_by('created_at')
    
    def get_conversation_depth(self):
        """Get the depth of this tweet in the conversation (0 for root)."""
        depth = 0
        current = self
        while current.parent_tweet and not current.parent_tweet.is_deleted:
            depth += 1
            current = current.parent_tweet
        return depth
    
    def soft_delete(self):
        """Soft delete the tweet."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def is_reply(self):
        """Check if this tweet is a reply to another tweet."""
        return self.parent_tweet is not None
    
    @property
    def reply_count(self):
        """Get the count of replies to this tweet."""
        return self.replies.filter(is_deleted=False).count()
    
    @property
    def likes_count(self):
        """Get the count of likes for this tweet."""
        return self.likes.count()
    
    @property
    def retweets_count(self):
        """Get the count of retweets for this tweet."""
        return self.retweets.count()
    
    @property
    def bookmarks_count(self):
        """Get the count of bookmarks for this tweet."""
        return self.bookmarks.count()


class Media(models.Model):
    """
    Media model for storing tweet attachments (images, videos, etc.).
    """
    MEDIA_TYPES = [
        ('image', 'Image'),
        ('video', 'Video'),
        ('gif', 'GIF'),
    ]
    
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
        related_name='media',
        help_text="The tweet this media belongs to"
    )
    media_type = models.CharField(
        max_length=10,
        choices=MEDIA_TYPES,
        help_text="Type of media file"
    )
    file = models.FileField(
        upload_to='tweet_media/',
        validators=[
            FileExtensionValidator(
                allowed_extensions=['jpg', 'jpeg', 'png', 'gif', 'mp4', 'mov', 'avi', 'webm']
            )
        ],
        help_text="Media file (image or video)"
    )
    alt_text = models.CharField(
        max_length=420,
        blank=True,
        null=True,
        help_text="Alternative text for accessibility"
    )
    
    # File metadata
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="File size in bytes"
    )
    width = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Media width in pixels"
    )
    height = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Media height in pixels"
    )
    duration = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Video duration in seconds"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'tweet_media'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['tweet']),
            models.Index(fields=['media_type']),
        ]
    
    def __str__(self):
        return f"{self.media_type} for tweet {self.tweet.id}"
    
    def save(self, *args, **kwargs):
        """Override save to set media type and file size."""
        if self.file:
            # Set file size
            self.file_size = self.file.size
            
            # Determine media type from file extension
            file_extension = os.path.splitext(self.file.name)[1].lower()
            if file_extension in ['.jpg', '.jpeg', '.png']:
                self.media_type = 'image'
            elif file_extension == '.gif':
                self.media_type = 'gif'
            elif file_extension in ['.mp4', '.mov', '.avi', '.webm']:
                self.media_type = 'video'
        
        super().save(*args, **kwargs)
    
    def get_file_url(self):
        """Get the file URL."""
        if self.file:
            return self.file.url
        return None
    
    @property
    def is_image(self):
        """Check if media is an image."""
        return self.media_type in ['image', 'gif']
    
    @property
    def is_video(self):
        """Check if media is a video."""
        return self.media_type == 'video'


class Hashtag(models.Model):
    """
    Hashtag model for storing unique hashtags.
    """
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Hashtag name without the # symbol"
    )
    
    # Statistics
    usage_count = models.PositiveIntegerField(
        default=0,
        help_text="Number of times this hashtag has been used"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'hashtags'
        ordering = ['-usage_count', 'name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['-usage_count']),
        ]
    
    def __str__(self):
        return f"#{self.name}"
    
    def save(self, *args, **kwargs):
        """Override save to normalize hashtag name."""
        # Remove # symbol and convert to lowercase
        self.name = self.name.lstrip('#').lower()
        super().save(*args, **kwargs)
    
    def increment_usage(self):
        """Increment the usage count for this hashtag."""
        self.usage_count += 1
        self.save(update_fields=['usage_count', 'updated_at'])
    
    def decrement_usage(self):
        """Decrement the usage count for this hashtag."""
        if self.usage_count > 0:
            self.usage_count -= 1
            self.save(update_fields=['usage_count', 'updated_at'])


class TweetHashtag(models.Model):
    """
    Through model for Tweet-Hashtag many-to-many relationship.
    """
    tweet = models.ForeignKey(
        Tweet,
        on_delete=models.CASCADE,
        related_name='tweet_hashtags'
    )
    hashtag = models.ForeignKey(
        Hashtag,
        on_delete=models.CASCADE,
        related_name='tweet_hashtags'
    )
    
    # Position of hashtag in tweet content
    position = models.PositiveIntegerField(
        help_text="Position of hashtag in tweet content"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'tweet_hashtags'
        unique_together = ['tweet', 'hashtag']
        indexes = [
            models.Index(fields=['tweet']),
            models.Index(fields=['hashtag']),
        ]
    
    def __str__(self):
        return f"{self.tweet.id} - #{self.hashtag.name}"
