from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.contenttypes.models import ContentType
from apps.interactions.models import Like, Retweet, Follow
from apps.tweets.models import Tweet
from .models import Notification


@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes a tweet."""
    if created and not instance.tweet.is_deleted:
        Notification.create_notification(
            recipient=instance.tweet.author,
            actor=instance.user,
            notification_type='like',
            content_object=instance.tweet
        )


@receiver(post_save, sender=Retweet)
def create_retweet_notification(sender, instance, created, **kwargs):
    """Create notification when someone retweets a tweet."""
    if created and not instance.tweet.is_deleted:
        Notification.create_notification(
            recipient=instance.tweet.author,
            actor=instance.user,
            notification_type='retweet',
            content_object=instance.tweet
        )


@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when someone follows a user."""
    if created:
        Notification.create_notification(
            recipient=instance.following,
            actor=instance.follower,
            notification_type='follow',
            content_object=None
        )


@receiver(post_save, sender=Tweet)
def create_reply_notification(sender, instance, created, **kwargs):
    """Create notification when someone replies to a tweet."""
    if created and instance.parent_tweet and not instance.is_deleted:
        Notification.create_notification(
            recipient=instance.parent_tweet.author,
            actor=instance.author,
            notification_type='reply',
            content_object=instance
        )
