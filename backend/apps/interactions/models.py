from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


class Like(models.Model):
    """
    Like model for storing user likes on tweets.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="The user who liked the tweet"
    )
    tweet = models.ForeignKey(
        'tweets.Tweet',
        on_delete=models.CASCADE,
        related_name='likes',
        help_text="The tweet that was liked"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'likes'
        unique_together = ['user', 'tweet']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tweet']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} likes tweet {self.tweet.id}"


class Retweet(models.Model):
    """
    Retweet model for storing user retweets.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='retweets',
        help_text="The user who retweeted"
    )
    tweet = models.ForeignKey(
        'tweets.Tweet',
        on_delete=models.CASCADE,
        related_name='retweets',
        help_text="The tweet that was retweeted"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'retweets'
        unique_together = ['user', 'tweet']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tweet']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} retweeted tweet {self.tweet.id}"


class Bookmark(models.Model):
    """
    Bookmark model for storing user bookmarks on tweets.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text="The user who bookmarked the tweet"
    )
    tweet = models.ForeignKey(
        'tweets.Tweet',
        on_delete=models.CASCADE,
        related_name='bookmarks',
        help_text="The tweet that was bookmarked"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'bookmarks'
        unique_together = ['user', 'tweet']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['tweet']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} bookmarked tweet {self.tweet.id}"


class Follow(models.Model):
    """
    Follow model for storing user follow relationships.
    """
    follower = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        help_text="The user who is following"
    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='followers',
        help_text="The user being followed"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'follows'
        unique_together = ['follower', 'following']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['follower']),
            models.Index(fields=['following']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"
    
    def save(self, *args, **kwargs):
        """Override save to prevent self-following."""
        if self.follower == self.following:
            raise ValueError("Users cannot follow themselves")
        super().save(*args, **kwargs)
