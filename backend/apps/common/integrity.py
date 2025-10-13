"""
Data integrity and consistency checks for the Linkup backend.
"""
from django.db import models, transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth import get_user_model
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class DataIntegrityMixin(models.Model):
    """
    Abstract mixin that provides data integrity checks for models.
    """
    
    class Meta:
        abstract = True
    
    def clean(self):
        """
        Perform model-level validation.
        """
        super().clean()
        self.validate_business_rules()
        self.validate_data_consistency()
    
    def validate_business_rules(self):
        """
        Override this method to implement business rule validation.
        """
        pass
    
    def validate_data_consistency(self):
        """
        Override this method to implement data consistency checks.
        """
        pass
    
    def save(self, *args, **kwargs):
        """
        Override save to ensure validation is always performed.
        """
        self.full_clean()
        super().save(*args, **kwargs)


class IntegrityChecker:
    """
    Class for performing comprehensive data integrity checks.
    """
    
    def __init__(self):
        self.errors = []
        self.warnings = []
    
    def check_all(self):
        """
        Run all integrity checks.
        """
        self.errors = []
        self.warnings = []
        
        self.check_user_integrity()
        self.check_tweet_integrity()
        self.check_social_integrity()
        self.check_community_integrity()
        self.check_messaging_integrity()
        self.check_count_consistency()
        
        return {
            'errors': self.errors,
            'warnings': self.warnings,
            'total_errors': len(self.errors),
            'total_warnings': len(self.warnings)
        }
    
    def check_user_integrity(self):
        """
        Check user data integrity.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        # Check for duplicate emails
        duplicate_emails = User.objects.values('email').annotate(
            count=models.Count('email')
        ).filter(count__gt=1)
        
        for item in duplicate_emails:
            self.errors.append(f"Duplicate email found: {item['email']}")
        
        # Check for duplicate usernames
        duplicate_usernames = User.objects.values('username').annotate(
            count=models.Count('username')
        ).filter(count__gt=1)
        
        for item in duplicate_usernames:
            self.errors.append(f"Duplicate username found: {item['username']}")
        
        # Check for invalid email formats
        invalid_emails = User.objects.exclude(
            email__regex=r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        )
        
        for user in invalid_emails:
            self.errors.append(f"Invalid email format for user {user.id}: {user.email}")
        
        # Check for users with empty required fields
        users_missing_data = User.objects.filter(
            models.Q(username__isnull=True) | 
            models.Q(username='') |
            models.Q(email__isnull=True) |
            models.Q(email='')
        )
        
        for user in users_missing_data:
            self.errors.append(f"User {user.id} missing required data")
    
    def check_tweet_integrity(self):
        """
        Check tweet data integrity.
        """
        from apps.tweets.models import Tweet, TweetHashtag, Hashtag
        
        # Check for tweets with invalid content length
        invalid_tweets = Tweet.objects.filter(
            models.Q(content__isnull=True) |
            models.Q(content='') |
            models.Q(content__length__gt=280)
        )
        
        for tweet in invalid_tweets:
            self.errors.append(f"Tweet {tweet.id} has invalid content")
        
        # Check for orphaned replies (parent tweet doesn't exist or is deleted)
        orphaned_replies = Tweet.objects.filter(
            parent_tweet__isnull=False,
            parent_tweet__is_deleted=True
        )
        
        for tweet in orphaned_replies:
            self.warnings.append(f"Tweet {tweet.id} is a reply to deleted tweet {tweet.parent_tweet.id}")
        
        # Check for circular references in tweet replies
        tweets_with_parents = Tweet.objects.filter(parent_tweet__isnull=False)
        for tweet in tweets_with_parents:
            if self._has_circular_reference(tweet):
                self.errors.append(f"Circular reference detected in tweet {tweet.id}")
        
        # Check hashtag consistency
        tweet_hashtags = TweetHashtag.objects.all()
        for th in tweet_hashtags:
            if th.tweet.is_deleted:
                self.warnings.append(f"TweetHashtag {th.id} references deleted tweet {th.tweet.id}")
        
        # Check hashtag usage counts
        for hashtag in Hashtag.objects.all():
            actual_count = TweetHashtag.objects.filter(
                hashtag=hashtag,
                tweet__is_deleted=False
            ).count()
            
            if hashtag.usage_count != actual_count:
                self.errors.append(
                    f"Hashtag {hashtag.id} usage count mismatch: "
                    f"stored={hashtag.usage_count}, actual={actual_count}"
                )
    
    def check_social_integrity(self):
        """
        Check social interaction data integrity.
        """
        from apps.interactions.models import Like, Retweet, Bookmark, Follow
        
        # Check for duplicate likes
        duplicate_likes = Like.objects.values('user', 'tweet').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for item in duplicate_likes:
            self.errors.append(
                f"Duplicate like found: user={item['user']}, tweet={item['tweet']}"
            )
        
        # Check for duplicate retweets
        duplicate_retweets = Retweet.objects.values('user', 'tweet').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for item in duplicate_retweets:
            self.errors.append(
                f"Duplicate retweet found: user={item['user']}, tweet={item['tweet']}"
            )
        
        # Check for self-follows
        self_follows = Follow.objects.filter(follower=models.F('following'))
        
        for follow in self_follows:
            self.errors.append(f"Self-follow detected: user {follow.follower.id}")
        
        # Check for duplicate follows
        duplicate_follows = Follow.objects.values('follower', 'following').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for item in duplicate_follows:
            self.errors.append(
                f"Duplicate follow found: follower={item['follower']}, following={item['following']}"
            )
    
    def check_community_integrity(self):
        """
        Check community data integrity.
        """
        from apps.communities.models import Community, CommunityMember
        
        # Check for communities without owners
        communities_without_owners = Community.objects.filter(owner__isnull=True)
        
        for community in communities_without_owners:
            self.errors.append(f"Community {community.id} has no owner")
        
        # Check for duplicate community memberships
        duplicate_memberships = CommunityMember.objects.values('user', 'community').annotate(
            count=models.Count('id')
        ).filter(count__gt=1)
        
        for item in duplicate_memberships:
            self.errors.append(
                f"Duplicate community membership: user={item['user']}, community={item['community']}"
            )
        
        # Check that community owners are also members
        communities = Community.objects.all()
        for community in communities:
            if not CommunityMember.objects.filter(
                community=community,
                user=community.owner
            ).exists():
                self.warnings.append(
                    f"Community {community.id} owner is not a member"
                )
    
    def check_messaging_integrity(self):
        """
        Check messaging data integrity.
        """
        from apps.messaging.models import Conversation, ConversationParticipant, DirectMessage
        
        # Check for conversations without participants
        conversations_without_participants = Conversation.objects.annotate(
            participant_count=models.Count('participants')
        ).filter(participant_count=0)
        
        for conversation in conversations_without_participants:
            self.errors.append(f"Conversation {conversation.id} has no participants")
        
        # Check for messages in conversations where sender is not a participant
        invalid_messages = DirectMessage.objects.exclude(
            conversation__participants__user=models.F('sender')
        )
        
        for message in invalid_messages:
            self.errors.append(
                f"Message {message.id} sender is not a participant in conversation {message.conversation.id}"
            )
        
        # Check for duplicate conversation participants
        duplicate_participants = ConversationParticipant.objects.values(
            'conversation', 'user'
        ).annotate(count=models.Count('id')).filter(count__gt=1)
        
        for item in duplicate_participants:
            self.errors.append(
                f"Duplicate conversation participant: conversation={item['conversation']}, user={item['user']}"
            )
    
    def check_count_consistency(self):
        """
        Check consistency of cached counts.
        """
        # Check follower counts
        for user in User.objects.all():
            actual_followers = user.followers.count()
            # If there's a cached follower count field, check it
            # stored_followers = user.followers_count
            # if stored_followers != actual_followers:
            #     self.errors.append(f"User {user.id} follower count mismatch")
        
        # Check tweet counts for users
        for user in User.objects.all():
            actual_tweets = user.tweets.filter(is_deleted=False).count()
            # If there's a cached tweet count field, check it
            # stored_tweets = user.tweets_count
            # if stored_tweets != actual_tweets:
            #     self.errors.append(f"User {user.id} tweet count mismatch")
    
    def _has_circular_reference(self, tweet, visited=None):
        """
        Check if a tweet has circular references in its parent chain.
        """
        if visited is None:
            visited = set()
        
        if tweet.id in visited:
            return True
        
        if tweet.parent_tweet is None:
            return False
        
        visited.add(tweet.id)
        return self._has_circular_reference(tweet.parent_tweet, visited)


class DataConsistencyValidator:
    """
    Validator for ensuring data consistency across operations.
    """
    
    @staticmethod
    def validate_tweet_creation(user, content, parent_tweet=None, community=None):
        """
        Validate tweet creation parameters.
        """
        errors = []
        
        # Check content
        if not content or not content.strip():
            errors.append("Tweet content cannot be empty")
        
        if len(content) > 280:
            errors.append("Tweet content cannot exceed 280 characters")
        
        # Check parent tweet
        if parent_tweet:
            if parent_tweet.is_deleted:
                errors.append("Cannot reply to deleted tweet")
            
            # Check reply depth (prevent too deep nesting)
            if parent_tweet.get_conversation_depth() >= 10:
                errors.append("Reply depth limit exceeded")
        
        # Check community permissions
        if community:
            from apps.communities.models import CommunityMember
            if not CommunityMember.objects.filter(
                community=community,
                user=user
            ).exists():
                errors.append("User is not a member of the specified community")
        
        if errors:
            raise ValidationError(errors)
    
    @staticmethod
    def validate_follow_action(follower, following):
        """
        Validate follow action.
        """
        errors = []
        
        # Check self-follow
        if follower == following:
            errors.append("Users cannot follow themselves")
        
        # Check if already following
        from apps.interactions.models import Follow
        if Follow.objects.filter(follower=follower, following=following).exists():
            errors.append("Already following this user")
        
        # Check privacy settings
        if following.is_private:
            # In a real implementation, you might need to create a follow request
            pass
        
        if errors:
            raise ValidationError(errors)
    
    @staticmethod
    def validate_community_membership(user, community, role=None):
        """
        Validate community membership.
        """
        errors = []
        
        # Check if already a member
        from apps.communities.models import CommunityMember
        if CommunityMember.objects.filter(user=user, community=community).exists():
            errors.append("User is already a member of this community")
        
        # Check community capacity (if there's a limit)
        current_members = CommunityMember.objects.filter(community=community).count()
        if hasattr(community, 'max_members') and current_members >= community.max_members:
            errors.append("Community has reached maximum member capacity")
        
        if errors:
            raise ValidationError(errors)
    
    @staticmethod
    def validate_message_sending(sender, conversation):
        """
        Validate message sending.
        """
        errors = []
        
        # Check if sender is a participant
        from apps.messaging.models import ConversationParticipant
        if not ConversationParticipant.objects.filter(
            conversation=conversation,
            user=sender
        ).exists():
            errors.append("Sender is not a participant in this conversation")
        
        if errors:
            raise ValidationError(errors)


def run_integrity_check():
    """
    Run a comprehensive integrity check and return results.
    """
    checker = IntegrityChecker()
    results = checker.check_all()
    
    # Log results
    if results['total_errors'] > 0:
        logger.error(f"Data integrity check found {results['total_errors']} errors")
        for error in results['errors']:
            logger.error(f"Integrity Error: {error}")
    
    if results['total_warnings'] > 0:
        logger.warning(f"Data integrity check found {results['total_warnings']} warnings")
        for warning in results['warnings']:
            logger.warning(f"Integrity Warning: {warning}")
    
    return results


def fix_count_inconsistencies():
    """
    Fix count inconsistencies in the database.
    """
    from apps.tweets.models import Hashtag
    from apps.interactions.models import Follow
    
    fixed_count = 0
    
    # Fix hashtag usage counts
    for hashtag in Hashtag.objects.all():
        actual_count = hashtag.tweet_hashtags.filter(
            tweet__is_deleted=False
        ).count()
        
        if hashtag.usage_count != actual_count:
            hashtag.usage_count = actual_count
            hashtag.save(update_fields=['usage_count'])
            fixed_count += 1
    
    logger.info(f"Fixed {fixed_count} count inconsistencies")
    return fixed_count