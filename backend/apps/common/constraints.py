"""
Database constraints and indexes for data integrity.
"""
from django.db import models
from django.db.models import Q, CheckConstraint, UniqueConstraint


class DatabaseConstraints:
    """
    Class containing database constraint definitions.
    """
    
    @staticmethod
    def get_user_constraints():
        """
        Get constraints for User model.
        """
        return [
            # Ensure username is not empty
            CheckConstraint(
                check=~Q(username=''),
                name='user_username_not_empty'
            ),
            # Ensure email is not empty
            CheckConstraint(
                check=~Q(email=''),
                name='user_email_not_empty'
            ),
            # Ensure bio length is reasonable
            CheckConstraint(
                check=Q(bio__isnull=True) | Q(bio__length__lte=500),
                name='user_bio_length_check'
            ),
        ]
    
    @staticmethod
    def get_tweet_constraints():
        """
        Get constraints for Tweet model.
        """
        return [
            # Ensure content is not empty
            CheckConstraint(
                check=~Q(content=''),
                name='tweet_content_not_empty'
            ),
            # Ensure content length is within limits
            CheckConstraint(
                check=Q(content__length__lte=280),
                name='tweet_content_length_check'
            ),
            # Ensure deleted tweets have deleted_at timestamp
            CheckConstraint(
                check=Q(is_deleted=False) | Q(deleted_at__isnull=False),
                name='tweet_deleted_timestamp_check'
            ),
            # Prevent self-replies (tweet cannot be its own parent)
            CheckConstraint(
                check=~Q(id=models.F('parent_tweet')),
                name='tweet_no_self_reply'
            ),
        ]
    
    @staticmethod
    def get_hashtag_constraints():
        """
        Get constraints for Hashtag model.
        """
        return [
            # Ensure hashtag name is not empty
            CheckConstraint(
                check=~Q(name=''),
                name='hashtag_name_not_empty'
            ),
            # Ensure usage count is non-negative
            CheckConstraint(
                check=Q(usage_count__gte=0),
                name='hashtag_usage_count_positive'
            ),
        ]
    
    @staticmethod
    def get_media_constraints():
        """
        Get constraints for Media model.
        """
        return [
            # Ensure file size is positive
            CheckConstraint(
                check=Q(file_size__isnull=True) | Q(file_size__gt=0),
                name='media_file_size_positive'
            ),
            # Ensure dimensions are positive
            CheckConstraint(
                check=Q(width__isnull=True) | Q(width__gt=0),
                name='media_width_positive'
            ),
            CheckConstraint(
                check=Q(height__isnull=True) | Q(height__gt=0),
                name='media_height_positive'
            ),
            # Ensure duration is positive for videos
            CheckConstraint(
                check=Q(duration__isnull=True) | Q(duration__gt=0),
                name='media_duration_positive'
            ),
        ]
    
    @staticmethod
    def get_community_constraints():
        """
        Get constraints for Community model.
        """
        return [
            # Ensure community name is not empty
            CheckConstraint(
                check=~Q(name=''),
                name='community_name_not_empty'
            ),
            # Ensure member count is non-negative
            CheckConstraint(
                check=Q(member_count__gte=0),
                name='community_member_count_positive'
            ),
        ]
    
    @staticmethod
    def get_follow_constraints():
        """
        Get constraints for Follow model.
        """
        return [
            # Prevent self-follows
            CheckConstraint(
                check=~Q(follower=models.F('following')),
                name='follow_no_self_follow'
            ),
        ]
    
    @staticmethod
    def get_like_constraints():
        """
        Get constraints for Like model.
        """
        return [
            # Unique constraint for user-tweet combination
            UniqueConstraint(
                fields=['user', 'tweet'],
                name='unique_user_tweet_like'
            ),
        ]
    
    @staticmethod
    def get_retweet_constraints():
        """
        Get constraints for Retweet model.
        """
        return [
            # Unique constraint for user-tweet combination
            UniqueConstraint(
                fields=['user', 'tweet'],
                name='unique_user_tweet_retweet'
            ),
        ]
    
    @staticmethod
    def get_bookmark_constraints():
        """
        Get constraints for Bookmark model.
        """
        return [
            # Unique constraint for user-tweet combination
            UniqueConstraint(
                fields=['user', 'tweet'],
                name='unique_user_tweet_bookmark'
            ),
        ]
    
    @staticmethod
    def get_conversation_participant_constraints():
        """
        Get constraints for ConversationParticipant model.
        """
        return [
            # Unique constraint for user-conversation combination
            UniqueConstraint(
                fields=['user', 'conversation'],
                name='unique_user_conversation_participant'
            ),
        ]
    
    @staticmethod
    def get_community_member_constraints():
        """
        Get constraints for CommunityMember model.
        """
        return [
            # Unique constraint for user-community combination
            UniqueConstraint(
                fields=['user', 'community'],
                name='unique_user_community_member'
            ),
        ]


class DatabaseIndexes:
    """
    Class containing database index definitions.
    """
    
    @staticmethod
    def get_user_indexes():
        """
        Get indexes for User model.
        """
        return [
            models.Index(fields=['username']),
            models.Index(fields=['email']),
            models.Index(fields=['is_verified']),
            models.Index(fields=['is_private']),
            models.Index(fields=['created_at']),
        ]
    
    @staticmethod
    def get_tweet_indexes():
        """
        Get indexes for Tweet model.
        """
        return [
            models.Index(fields=['author', '-created_at']),
            models.Index(fields=['parent_tweet']),
            models.Index(fields=['community', '-created_at']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['author', 'is_deleted', '-created_at']),
        ]
    
    @staticmethod
    def get_hashtag_indexes():
        """
        Get indexes for Hashtag model.
        """
        return [
            models.Index(fields=['name']),
            models.Index(fields=['-usage_count']),
            models.Index(fields=['name', '-usage_count']),
        ]
    
    @staticmethod
    def get_media_indexes():
        """
        Get indexes for Media model.
        """
        return [
            models.Index(fields=['tweet']),
            models.Index(fields=['media_type']),
            models.Index(fields=['tweet', 'media_type']),
        ]
    
    @staticmethod
    def get_social_indexes():
        """
        Get indexes for social interaction models.
        """
        return {
            'like': [
                models.Index(fields=['user', 'tweet']),
                models.Index(fields=['tweet', '-created_at']),
                models.Index(fields=['user', '-created_at']),
            ],
            'retweet': [
                models.Index(fields=['user', 'tweet']),
                models.Index(fields=['tweet', '-created_at']),
                models.Index(fields=['user', '-created_at']),
            ],
            'bookmark': [
                models.Index(fields=['user', 'tweet']),
                models.Index(fields=['user', '-created_at']),
            ],
            'follow': [
                models.Index(fields=['follower', 'following']),
                models.Index(fields=['following', '-created_at']),
                models.Index(fields=['follower', '-created_at']),
            ],
        }
    
    @staticmethod
    def get_community_indexes():
        """
        Get indexes for Community model.
        """
        return [
            models.Index(fields=['name']),
            models.Index(fields=['owner']),
            models.Index(fields=['is_private']),
            models.Index(fields=['created_at']),
        ]
    
    @staticmethod
    def get_messaging_indexes():
        """
        Get indexes for messaging models.
        """
        return {
            'conversation': [
                models.Index(fields=['created_at']),
                models.Index(fields=['updated_at']),
            ],
            'conversation_participant': [
                models.Index(fields=['user', 'conversation']),
                models.Index(fields=['conversation', 'joined_at']),
            ],
            'direct_message': [
                models.Index(fields=['conversation', '-created_at']),
                models.Index(fields=['sender', '-created_at']),
                models.Index(fields=['conversation', 'is_read']),
            ],
        }


def apply_constraints_to_model(model_class, constraints):
    """
    Apply constraints to a model class.
    """
    if hasattr(model_class._meta, 'constraints'):
        model_class._meta.constraints.extend(constraints)
    else:
        model_class._meta.constraints = constraints


def apply_indexes_to_model(model_class, indexes):
    """
    Apply indexes to a model class.
    """
    if hasattr(model_class._meta, 'indexes'):
        model_class._meta.indexes.extend(indexes)
    else:
        model_class._meta.indexes = indexes