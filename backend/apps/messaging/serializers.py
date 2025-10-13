from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Conversation, ConversationParticipant, DirectMessage

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user serializer for messaging contexts."""
    full_name = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'profile_image_url', 'is_verified']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'profile_image_url', 'is_verified']
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()


class DirectMessageSerializer(serializers.ModelSerializer):
    """Serializer for direct messages."""
    message_id = serializers.IntegerField(source='id', read_only=True)
    conversation_id = serializers.IntegerField(source='conversation.id', read_only=True)
    sender_user_id = serializers.IntegerField(source='sender.id', read_only=True)
    sent_at = serializers.DateTimeField(source='created_at', read_only=True)
    sender = UserBasicSerializer(read_only=True)
    is_read = serializers.SerializerMethodField()
    
    class Meta:
        model = DirectMessage
        fields = [
            'message_id', 'conversation_id', 'sender_user_id', 'content', 
            'sent_at', 'is_read', 'sender'
        ]
        read_only_fields = ['message_id', 'conversation_id', 'sender_user_id', 'sent_at', 'sender']
    
    def get_is_read(self, obj):
        """Check if message is read by the requesting user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_read_by_user(request.user)
        return False


class DirectMessageCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating direct messages."""
    recipient_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = DirectMessage
        fields = ['content', 'recipient_id']
    
    def validate_content(self, value):
        """Validate message content."""
        if not value.strip():
            raise serializers.ValidationError("Message content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Message content cannot exceed 1000 characters.")
        return value.strip()
    
    def validate_recipient_id(self, value):
        """Validate recipient exists and is not the sender."""
        try:
            recipient = User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Recipient does not exist.")
        
        request = self.context.get('request')
        if request and request.user.id == value:
            raise serializers.ValidationError("Cannot send message to yourself.")
        
        # Check privacy settings
        if request and not Conversation.objects.can_users_message(request.user, recipient):
            raise serializers.ValidationError(
                "You cannot send messages to this user due to privacy settings."
            )
        
        return value
    
    def create(self, validated_data):
        """Create a new direct message."""
        recipient_id = validated_data.pop('recipient_id')
        sender = self.context['request'].user
        recipient = User.objects.get(id=recipient_id)
        
        # Get or create conversation
        conversation, created = Conversation.objects.get_or_create_conversation(sender, recipient)
        
        # Create the message
        message = conversation.add_message(sender, validated_data['content'])
        
        return message


class ConversationParticipantSerializer(serializers.ModelSerializer):
    """Serializer for conversation participants."""
    user = UserBasicSerializer(read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = ConversationParticipant
        fields = ['user', 'joined_at', 'last_read_at', 'unread_count']
        read_only_fields = ['joined_at', 'last_read_at']
    
    def get_unread_count(self, obj):
        """Get unread message count for this participant."""
        return obj.get_unread_count()


class ConversationSerializer(serializers.ModelSerializer):
    """Serializer for conversations."""
    participants = ConversationParticipantSerializer(many=True, read_only=True)
    last_message = DirectMessageSerializer(read_only=True)
    other_participant = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = [
            'id', 'created_at', 'updated_at', 'participants', 
            'last_message', 'other_participant', 'unread_count'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_other_participant(self, obj):
        """Get the other participant in the conversation."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            other_participant = obj.get_other_participant(request.user)
            if other_participant:
                return UserBasicSerializer(other_participant.user).data
        return None
    
    def get_unread_count(self, obj):
        """Get unread message count for the requesting user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.participants.filter(user=request.user).first()
            if participant:
                return participant.get_unread_count()
        return 0


class ConversationListSerializer(serializers.ModelSerializer):
    """Simplified serializer for conversation lists."""
    conversation_id = serializers.IntegerField(source='id', read_only=True)
    participants = serializers.SerializerMethodField()
    last_message = DirectMessageSerializer(read_only=True)
    last_message_at = serializers.DateTimeField(source='updated_at', read_only=True)
    unread_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'last_message', 'created_at', 'last_message_at', 'unread_count']
        read_only_fields = ['conversation_id', 'created_at', 'last_message_at']
    
    def get_participants(self, obj):
        """Get participants excluding the current user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Return all participants except the current user
            participants = obj.participants.exclude(user=request.user)
            return [UserBasicSerializer(p.user).data for p in participants]
        return []
    
    def get_unread_count(self, obj):
        """Get unread message count for the requesting user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            participant = obj.participants.filter(user=request.user).first()
            if participant:
                return participant.get_unread_count()
        return 0
        if request and request.user.is_authenticated:
            participant = obj.participants.filter(user=request.user).first()
            if participant:
                return participant.get_unread_count()
        return 0