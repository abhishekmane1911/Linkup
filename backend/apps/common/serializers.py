"""
Base serializers with enhanced validation for the Linkup backend.
"""
from rest_framework import serializers
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from .exceptions import ValidationException, BusinessLogicException
from .validators import (
    validate_username,
    validate_tweet_content,
    validate_bio_length,
    validate_community_name,
    validate_hashtag,
    validate_media_file
)
from .integrity import DataConsistencyValidator
import logging

logger = logging.getLogger(__name__)


class BaseModelSerializer(serializers.ModelSerializer):
    """
    Base serializer with enhanced validation and error handling.
    """
    
    def validate(self, attrs):
        """
        Enhanced validation with business rule checking.
        """
        attrs = super().validate(attrs)
        
        # Perform custom validation
        self.validate_business_rules(attrs)
        self.validate_data_consistency(attrs)
        
        return attrs
    
    def validate_business_rules(self, attrs):
        """
        Override this method to implement business rule validation.
        """
        pass
    
    def validate_data_consistency(self, attrs):
        """
        Override this method to implement data consistency validation.
        """
        pass
    
    def create(self, validated_data):
        """
        Create with enhanced error handling and logging.
        """
        try:
            with transaction.atomic():
                instance = super().create(validated_data)
                self.post_create_actions(instance)
                return instance
        except Exception as e:
            logger.error(f"Error creating {self.Meta.model.__name__}: {e}")
            raise ValidationException(
                message=f"Failed to create {self.Meta.model.__name__}",
                code="CREATION_ERROR"
            )
    
    def update(self, instance, validated_data):
        """
        Update with enhanced error handling and logging.
        """
        try:
            with transaction.atomic():
                instance = super().update(instance, validated_data)
                self.post_update_actions(instance)
                return instance
        except Exception as e:
            logger.error(f"Error updating {self.Meta.model.__name__}: {e}")
            raise ValidationException(
                message=f"Failed to update {self.Meta.model.__name__}",
                code="UPDATE_ERROR"
            )
    
    def post_create_actions(self, instance):
        """
        Override this method to perform actions after creation.
        """
        pass
    
    def post_update_actions(self, instance):
        """
        Override this method to perform actions after update.
        """
        pass
    
    def to_internal_value(self, data):
        """
        Enhanced data validation before serialization.
        """
        try:
            return super().to_internal_value(data)
        except serializers.ValidationError as e:
            # Convert DRF validation errors to our custom format
            raise ValidationException(
                message="Validation failed",
                code="VALIDATION_ERROR"
            )


class UserValidationMixin:
    """
    Mixin for user-related validation.
    """
    
    def validate_username(self, value):
        """
        Validate username format and uniqueness.
        """
        validate_username(value)
        
        # Check uniqueness (excluding current instance for updates)
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        queryset = User.objects.filter(username=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Username already exists")
        
        return value
    
    def validate_email(self, value):
        """
        Validate email format and uniqueness.
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        queryset = User.objects.filter(email=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Email already exists")
        
        return value
    
    def validate_bio(self, value):
        """
        Validate user bio.
        """
        if value:
            validate_bio_length(value)
        return value


class TweetValidationMixin:
    """
    Mixin for tweet-related validation.
    """
    
    def validate_content(self, value):
        """
        Validate tweet content.
        """
        validate_tweet_content(value)
        return value
    
    def validate_parent_tweet(self, value):
        """
        Validate parent tweet for replies.
        """
        if value and value.is_deleted:
            raise serializers.ValidationError("Cannot reply to deleted tweet")
        
        if value and value.get_conversation_depth() >= 10:
            raise serializers.ValidationError("Reply depth limit exceeded")
        
        return value
    
    def validate_business_rules(self, attrs):
        """
        Validate tweet business rules.
        """
        super().validate_business_rules(attrs)
        
        user = self.context['request'].user
        content = attrs.get('content')
        parent_tweet = attrs.get('parent_tweet')
        community = attrs.get('community')
        
        # Use consistency validator
        DataConsistencyValidator.validate_tweet_creation(
            user, content, parent_tweet, community
        )


class SocialValidationMixin:
    """
    Mixin for social interaction validation.
    """
    
    def validate_like_action(self, user, tweet):
        """
        Validate like action.
        """
        if tweet.is_deleted:
            raise serializers.ValidationError("Cannot like deleted tweet")
        
        from apps.interactions.models import Like
        if Like.objects.filter(user=user, tweet=tweet).exists():
            raise serializers.ValidationError("Tweet already liked")
    
    def validate_follow_action(self, follower, following):
        """
        Validate follow action.
        """
        DataConsistencyValidator.validate_follow_action(follower, following)
    
    def validate_retweet_action(self, user, tweet):
        """
        Validate retweet action.
        """
        if tweet.is_deleted:
            raise serializers.ValidationError("Cannot retweet deleted tweet")
        
        if tweet.author == user:
            raise serializers.ValidationError("Cannot retweet own tweet")
        
        from apps.interactions.models import Retweet
        if Retweet.objects.filter(user=user, tweet=tweet).exists():
            raise serializers.ValidationError("Tweet already retweeted")


class CommunityValidationMixin:
    """
    Mixin for community-related validation.
    """
    
    def validate_name(self, value):
        """
        Validate community name.
        """
        validate_community_name(value)
        
        # Check uniqueness
        from apps.communities.models import Community
        queryset = Community.objects.filter(name=value)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        
        if queryset.exists():
            raise serializers.ValidationError("Community name already exists")
        
        return value
    
    def validate_membership(self, user, community, role=None):
        """
        Validate community membership.
        """
        DataConsistencyValidator.validate_community_membership(user, community, role)


class MediaValidationMixin:
    """
    Mixin for media file validation.
    """
    
    def validate_file(self, value):
        """
        Validate uploaded media file.
        """
        validate_media_file(value)
        return value
    
    def validate_alt_text(self, value):
        """
        Validate alt text for accessibility.
        """
        if value and len(value) > 420:
            raise serializers.ValidationError("Alt text cannot exceed 420 characters")
        return value


class MessagingValidationMixin:
    """
    Mixin for messaging-related validation.
    """
    
    def validate_message_content(self, value):
        """
        Validate message content.
        """
        if not value or not value.strip():
            raise serializers.ValidationError("Message content cannot be empty")
        
        if len(value) > 1000:
            raise serializers.ValidationError("Message content cannot exceed 1000 characters")
        
        return value
    
    def validate_conversation_access(self, user, conversation):
        """
        Validate user access to conversation.
        """
        DataConsistencyValidator.validate_message_sending(user, conversation)


class PaginationValidationMixin:
    """
    Mixin for pagination validation.
    """
    
    def validate_page_size(self, value):
        """
        Validate page size parameter.
        """
        if value is not None:
            if value < 1:
                raise serializers.ValidationError("Page size must be at least 1")
            if value > 100:
                raise serializers.ValidationError("Page size cannot exceed 100")
        return value
    
    def validate_page_number(self, value):
        """
        Validate page number parameter.
        """
        if value is not None and value < 1:
            raise serializers.ValidationError("Page number must be at least 1")
        return value


class BulkOperationMixin:
    """
    Mixin for bulk operation validation.
    """
    
    def validate_bulk_data(self, data_list):
        """
        Validate bulk operation data.
        """
        if not isinstance(data_list, list):
            raise serializers.ValidationError("Data must be a list")
        
        if len(data_list) == 0:
            raise serializers.ValidationError("Data list cannot be empty")
        
        if len(data_list) > 100:
            raise serializers.ValidationError("Cannot process more than 100 items at once")
        
        return data_list
    
    def perform_bulk_create(self, validated_data_list):
        """
        Perform bulk create with validation.
        """
        try:
            with transaction.atomic():
                instances = []
                for validated_data in validated_data_list:
                    instance = self.Meta.model.objects.create(**validated_data)
                    instances.append(instance)
                return instances
        except Exception as e:
            logger.error(f"Error in bulk create: {e}")
            raise ValidationException(
                message="Bulk create operation failed",
                code="BULK_CREATE_ERROR"
            )


class SearchValidationMixin:
    """
    Mixin for search parameter validation.
    """
    
    def validate_search_query(self, value):
        """
        Validate search query.
        """
        if value is not None:
            if len(value.strip()) < 2:
                raise serializers.ValidationError("Search query must be at least 2 characters")
            if len(value) > 100:
                raise serializers.ValidationError("Search query cannot exceed 100 characters")
        return value
    
    def validate_search_filters(self, filters):
        """
        Validate search filters.
        """
        allowed_filters = getattr(self.Meta, 'allowed_search_filters', [])
        
        for filter_key in filters.keys():
            if filter_key not in allowed_filters:
                raise serializers.ValidationError(f"Invalid search filter: {filter_key}")
        
        return filters


class AuditMixin:
    """
    Mixin for audit trail functionality.
    """
    
    def create(self, validated_data):
        """
        Create with audit logging.
        """
        instance = super().create(validated_data)
        self.log_audit_event('create', instance)
        return instance
    
    def update(self, instance, validated_data):
        """
        Update with audit logging.
        """
        old_values = self.get_audit_fields(instance)
        instance = super().update(instance, validated_data)
        new_values = self.get_audit_fields(instance)
        
        self.log_audit_event('update', instance, {
            'old_values': old_values,
            'new_values': new_values
        })
        
        return instance
    
    def get_audit_fields(self, instance):
        """
        Get fields to include in audit log.
        """
        audit_fields = getattr(self.Meta, 'audit_fields', [])
        return {field: getattr(instance, field) for field in audit_fields}
    
    def log_audit_event(self, action, instance, details=None):
        """
        Log audit event.
        """
        logger.info(
            f"Audit: {action} {instance.__class__.__name__} {instance.pk}",
            extra={
                'action': action,
                'model': instance.__class__.__name__,
                'instance_id': instance.pk,
                'user_id': self.context['request'].user.id if 'request' in self.context else None,
                'details': details
            }
        )