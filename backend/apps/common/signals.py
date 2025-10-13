"""
Django signals for maintaining data consistency and integrity.
"""
from django.db.models.signals import post_save, post_delete, pre_save, pre_delete
from django.dispatch import receiver
from django.db import transaction
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


@receiver(pre_save)
def validate_model_before_save(sender, instance, **kwargs):
    """
    Validate model instance before saving.
    """
    # Skip validation for certain models or during migrations
    if hasattr(instance, '_skip_validation'):
        return
    
    try:
        instance.full_clean()
    except Exception as e:
        logger.error(f"Validation error before save for {sender.__name__}: {e}")
        raise


@receiver(post_save)
def log_model_changes(sender, instance, created, **kwargs):
    """
    Log model changes for audit purposes.
    """
    # Skip logging for certain models
    skip_models = ['Session', 'LogEntry', 'ContentType', 'Permission']
    if sender.__name__ in skip_models:
        return
    
    action = 'created' if created else 'updated'
    logger.info(
        f"Model {action}: {sender.__name__} {instance.pk}",
        extra={
            'model': sender.__name__,
            'instance_id': instance.pk,
            'action': action,
            'timestamp': instance.updated_at if hasattr(instance, 'updated_at') else None
        }
    )


@receiver(post_delete)
def log_model_deletions(sender, instance, **kwargs):
    """
    Log model deletions for audit purposes.
    """
    # Skip logging for certain models
    skip_models = ['Session', 'LogEntry', 'ContentType', 'Permission']
    if sender.__name__ in skip_models:
        return
    
    logger.info(
        f"Model deleted: {sender.__name__} {instance.pk}",
        extra={
            'model': sender.__name__,
            'instance_id': instance.pk,
            'action': 'deleted'
        }
    )


# Tweet-specific signals
@receiver(post_save, sender='tweets.Tweet')
def handle_tweet_creation(sender, instance, created, **kwargs):
    """
    Handle tweet creation and updates.
    """
    if created:
        # Clear user's tweet count cache
        cache_key = f"user_tweets_count_{instance.author.id}"
        cache.delete(cache_key)
        
        # Update user's last activity
        instance.author.updated_at = instance.created_at
        instance.author.save(update_fields=['updated_at'])


@receiver(post_delete, sender='tweets.Tweet')
def handle_tweet_deletion(sender, instance, **kwargs):
    """
    Handle tweet deletion.
    """
    # Clear user's tweet count cache
    cache_key = f"user_tweets_count_{instance.author.id}"
    cache.delete(cache_key)
    
    # Decrement hashtag usage counts
    for tweet_hashtag in instance.tweet_hashtags.all():
        tweet_hashtag.hashtag.decrement_usage()


# Hashtag-specific signals
@receiver(post_save, sender='tweets.TweetHashtag')
def handle_hashtag_usage_increment(sender, instance, created, **kwargs):
    """
    Handle hashtag usage increment.
    """
    if created:
        # Clear trending hashtags cache
        cache.delete('trending_hashtags')


@receiver(post_delete, sender='tweets.TweetHashtag')
def handle_hashtag_usage_decrement(sender, instance, **kwargs):
    """
    Handle hashtag usage decrement.
    """
    # Clear trending hashtags cache
    cache.delete('trending_hashtags')


# Social interaction signals
@receiver(post_save, sender='interactions.Like')
def handle_like_creation(sender, instance, created, **kwargs):
    """
    Handle like creation.
    """
    if created:
        # Clear tweet likes count cache
        cache_key = f"tweet_likes_count_{instance.tweet.id}"
        cache.delete(cache_key)
        
        # Clear user's liked tweets cache
        user_cache_key = f"user_liked_tweets_{instance.user.id}"
        cache.delete(user_cache_key)


@receiver(post_delete, sender='interactions.Like')
def handle_like_deletion(sender, instance, **kwargs):
    """
    Handle like deletion.
    """
    # Clear tweet likes count cache
    cache_key = f"tweet_likes_count_{instance.tweet.id}"
    cache.delete(cache_key)
    
    # Clear user's liked tweets cache
    user_cache_key = f"user_liked_tweets_{instance.user.id}"
    cache.delete(user_cache_key)


@receiver(post_save, sender='interactions.Follow')
def handle_follow_creation(sender, instance, created, **kwargs):
    """
    Handle follow relationship creation.
    """
    if created:
        # Clear follower/following count caches
        follower_cache_key = f"user_followers_count_{instance.following.id}"
        following_cache_key = f"user_following_count_{instance.follower.id}"
        cache.delete(follower_cache_key)
        cache.delete(following_cache_key)
        
        # Clear user's timeline cache
        timeline_cache_key = f"user_timeline_{instance.follower.id}"
        cache.delete(timeline_cache_key)


@receiver(post_delete, sender='interactions.Follow')
def handle_follow_deletion(sender, instance, **kwargs):
    """
    Handle follow relationship deletion.
    """
    # Clear follower/following count caches
    follower_cache_key = f"user_followers_count_{instance.following.id}"
    following_cache_key = f"user_following_count_{instance.follower.id}"
    cache.delete(follower_cache_key)
    cache.delete(following_cache_key)
    
    # Clear user's timeline cache
    timeline_cache_key = f"user_timeline_{instance.follower.id}"
    cache.delete(timeline_cache_key)


# Community signals
@receiver(post_save, sender='communities.CommunityMember')
def handle_community_membership_creation(sender, instance, created, **kwargs):
    """
    Handle community membership creation.
    """
    if created:
        # Clear community member count cache
        cache_key = f"community_members_count_{instance.community.id}"
        cache.delete(cache_key)
        
        # Clear user's communities cache
        user_cache_key = f"user_communities_{instance.user.id}"
        cache.delete(user_cache_key)


@receiver(post_delete, sender='communities.CommunityMember')
def handle_community_membership_deletion(sender, instance, **kwargs):
    """
    Handle community membership deletion.
    """
    # Clear community member count cache
    cache_key = f"community_members_count_{instance.community.id}"
    cache.delete(cache_key)
    
    # Clear user's communities cache
    user_cache_key = f"user_communities_{instance.user.id}"
    cache.delete(user_cache_key)


# Messaging signals
@receiver(post_save, sender='messaging.DirectMessage')
def handle_message_creation(sender, instance, created, **kwargs):
    """
    Handle message creation.
    """
    if created:
        # Update conversation's last message timestamp
        conversation = instance.conversation
        conversation.updated_at = instance.created_at
        conversation.save(update_fields=['updated_at'])
        
        # Clear conversation cache for all participants
        for participant in conversation.participants.all():
            cache_key = f"user_conversations_{participant.user.id}"
            cache.delete(cache_key)


@receiver(post_save, sender='messaging.ConversationParticipant')
def handle_conversation_participant_creation(sender, instance, created, **kwargs):
    """
    Handle conversation participant creation.
    """
    if created:
        # Clear user's conversations cache
        cache_key = f"user_conversations_{instance.user.id}"
        cache.delete(cache_key)


# Cache invalidation signals - temporarily disabled to fix user creation
# @receiver(post_save)
# def invalidate_related_caches(sender, instance, **kwargs):
#     """
#     Invalidate related caches when models are updated.
#     """
#     try:
#         # Define cache patterns to invalidate based on model
#         if sender.__name__ == 'User':
#             patterns = [
#                 f"user_profile_{instance.id}",
#                 f"user_stats_{instance.id}",
#             ]
#         elif sender.__name__ == 'Tweet':
#             patterns = [
#                 f"tweet_detail_{instance.id}",
#                 f"user_tweets_{instance.author.id}",
#                 f"tweet_thread_{instance.get_root_tweet().id if instance.parent_tweet else instance.id}",
#             ]
#         elif sender.__name__ == 'Community':
#             patterns = [
#                 f"community_detail_{instance.id}",
#                 f"community_stats_{instance.id}",
#             ]
#         else:
#             patterns = []
#         
#         for pattern in patterns:
#             cache.delete(pattern)
#     except Exception as e:
#         # Log the error but don't break the save operation
#         import logging
#         logger = logging.getLogger(__name__)
#         logger.error(f"Error invalidating cache for {sender.__name__}: {e}")


# Data consistency signals
@receiver(pre_delete, sender='tweets.Tweet')
def handle_tweet_soft_delete(sender, instance, **kwargs):
    """
    Handle tweet soft delete to maintain data consistency.
    """
    # If this is a soft delete (setting is_deleted=True), don't actually delete
    if hasattr(instance, '_soft_delete') and instance._soft_delete:
        # Mark as deleted instead of actually deleting
        instance.is_deleted = True
        instance.deleted_at = timezone.now()
        instance.save(update_fields=['is_deleted', 'deleted_at'])
        
        # Prevent actual deletion
        return False


@receiver(pre_save, sender='interactions.Follow')
def prevent_self_follow(sender, instance, **kwargs):
    """
    Prevent users from following themselves.
    """
    if instance.follower == instance.following:
        raise ValueError("Users cannot follow themselves")


@receiver(pre_save, sender='interactions.Like')
def prevent_duplicate_likes(sender, instance, **kwargs):
    """
    Prevent duplicate likes.
    """
    if not instance.pk:  # Only check for new instances
        existing = sender.objects.filter(
            user=instance.user,
            tweet=instance.tweet
        ).exists()
        
        if existing:
            raise ValueError("User has already liked this tweet")


@receiver(pre_save, sender='communities.CommunityMember')
def prevent_duplicate_membership(sender, instance, **kwargs):
    """
    Prevent duplicate community memberships.
    """
    if not instance.pk:  # Only check for new instances
        existing = sender.objects.filter(
            user=instance.user,
            community=instance.community
        ).exists()
        
        if existing:
            raise ValueError("User is already a member of this community")