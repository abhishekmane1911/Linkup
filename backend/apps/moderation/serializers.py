from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import Report, ModerationAction

User = get_user_model()


class ReportCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new reports.
    """
    content_type = serializers.CharField(write_only=True)
    object_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = Report
        fields = [
            'content_type', 'object_id', 'report_type', 'description'
        ]
    
    def validate_content_type(self, value):
        """Validate that the content type is allowed for reporting."""
        allowed_types = ['tweet', 'user']  # Add more as needed
        if value not in allowed_types:
            raise serializers.ValidationError(
                f"Content type '{value}' is not allowed for reporting. "
                f"Allowed types: {', '.join(allowed_types)}"
            )
        return value
    
    def validate(self, attrs):
        """Validate that the reported object exists and can be reported."""
        content_type_name = attrs['content_type']
        object_id = attrs['object_id']
        
        # Map content type names to actual models
        content_type_mapping = {
            'tweet': 'tweets.tweet',
            'user': 'authentication.user',
        }
        
        try:
            content_type = ContentType.objects.get(
                app_label=content_type_mapping[content_type_name].split('.')[0],
                model=content_type_mapping[content_type_name].split('.')[1]
            )
            attrs['content_type'] = content_type
        except ContentType.DoesNotExist:
            raise serializers.ValidationError(f"Invalid content type: {content_type_name}")
        
        # Check if the object exists
        model_class = content_type.model_class()
        try:
            reported_object = model_class.objects.get(id=object_id)
            
            # Additional validation for specific content types
            if content_type_name == 'tweet' and hasattr(reported_object, 'is_deleted'):
                if reported_object.is_deleted:
                    raise serializers.ValidationError("Cannot report deleted content.")
            
        except model_class.DoesNotExist:
            raise serializers.ValidationError(f"Object with ID {object_id} does not exist.")
        
        return attrs
    
    def create(self, validated_data):
        """Create a new report with the current user as reporter."""
        validated_data['reporter'] = self.context['request'].user
        return super().create(validated_data)


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for report responses."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class ReportListSerializer(serializers.ModelSerializer):
    """
    Serializer for listing reports with basic information.
    """
    reporter = UserBasicSerializer(read_only=True)
    assigned_moderator = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    reported_content_preview = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'content_type_name', 'object_id',
            'report_type', 'status', 'assigned_moderator',
            'resolved_by', 'resolved_at', 'created_at',
            'reported_content_preview'
        ]
    
    def get_content_type_name(self, obj):
        """Get human-readable content type name."""
        return obj.content_type.model


class ReportDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for individual report views.
    """
    reporter = UserBasicSerializer(read_only=True)
    assigned_moderator = UserBasicSerializer(read_only=True)
    resolved_by = UserBasicSerializer(read_only=True)
    reported_content_preview = serializers.ReadOnlyField()
    content_type_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Report
        fields = [
            'id', 'reporter', 'content_type_name', 'object_id',
            'report_type', 'description', 'status',
            'assigned_moderator', 'resolution_notes',
            'resolved_by', 'resolved_at', 'created_at',
            'updated_at', 'reported_content_preview'
        ]
    
    def get_content_type_name(self, obj):
        """Get human-readable content type name."""
        return obj.content_type.model


class ReportStatusUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating report status and resolution.
    """
    
    class Meta:
        model = Report
        fields = ['status', 'resolution_notes']
    
    def validate_status(self, value):
        """Validate status transitions."""
        if self.instance:
            current_status = self.instance.status
            
            # Define allowed status transitions
            allowed_transitions = {
                'pending': ['under_review', 'dismissed'],
                'under_review': ['resolved', 'dismissed', 'escalated'],
                'escalated': ['resolved', 'dismissed'],
                'resolved': [],  # Final state
                'dismissed': [],  # Final state
            }
            
            if value not in allowed_transitions.get(current_status, []):
                raise serializers.ValidationError(
                    f"Cannot transition from '{current_status}' to '{value}'"
                )
        
        return value
    
    def update(self, instance, validated_data):
        """Update report with proper status handling."""
        status = validated_data.get('status')
        resolution_notes = validated_data.get('resolution_notes')
        
        # Get the current user from context
        user = self.context['request'].user
        
        if status == 'resolved':
            instance.resolve(user, resolution_notes)
        elif status == 'dismissed':
            instance.dismiss(user, resolution_notes)
        elif status == 'under_review':
            instance.assign_moderator(user)
        elif status == 'escalated':
            instance.escalate()
        else:
            # For other status changes, use regular update
            instance.status = status
            if resolution_notes:
                instance.resolution_notes = resolution_notes
            instance.save()
        
        return instance


class ModerationActionSerializer(serializers.ModelSerializer):
    """
    Serializer for moderation actions.
    """
    moderator = UserBasicSerializer(read_only=True)
    severity_display = serializers.ReadOnlyField()
    
    class Meta:
        model = ModerationAction
        fields = [
            'id', 'action_type', 'description', 'moderator',
            'severity_level', 'severity_display', 'is_automated',
            'additional_data', 'created_at'
        ]


class ModerationActionCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating moderation actions.
    """
    
    class Meta:
        model = ModerationAction
        fields = [
            'action_type', 'description', 'severity_level', 'additional_data'
        ]
    
    def create(self, validated_data):
        """Create moderation action with current user as moderator."""
        validated_data['moderator'] = self.context['request'].user
        validated_data['report'] = self.context['report']
        return super().create(validated_data)


class ReportWithActionsSerializer(ReportDetailSerializer):
    """
    Extended report serializer that includes moderation actions.
    """
    moderation_actions = ModerationActionSerializer(many=True, read_only=True)
    
    class Meta(ReportDetailSerializer.Meta):
        fields = ReportDetailSerializer.Meta.fields + ['moderation_actions']