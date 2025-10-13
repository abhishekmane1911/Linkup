from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Conversation, ConversationParticipant, DirectMessage
from .serializers import (
    ConversationSerializer, ConversationListSerializer,
    DirectMessageSerializer, DirectMessageCreateSerializer
)


class ConversationListView(generics.ListAPIView):
    """
    List all conversations for the authenticated user.
    """
    serializer_class = ConversationListSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get conversations for the authenticated user."""
        return Conversation.objects.get_user_conversations(self.request.user)


class ConversationDetailView(generics.RetrieveAPIView):
    """
    Retrieve a specific conversation with full details.
    """
    serializer_class = ConversationSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get conversations for the authenticated user."""
        return Conversation.objects.get_user_conversations(self.request.user)
    
    def retrieve(self, request, *args, **kwargs):
        """Mark conversation as read when retrieved."""
        conversation = self.get_object()
        
        # Mark conversation as read for the current user
        participant = conversation.participants.filter(user=request.user).first()
        if participant:
            participant.mark_as_read()
        
        return super().retrieve(request, *args, **kwargs)


class ConversationMessagesView(generics.ListAPIView):
    """
    List all messages in a specific conversation.
    """
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get messages for the specified conversation."""
        conversation_id = self.kwargs['conversation_id']
        
        # Verify user is participant in this conversation
        conversation = get_object_or_404(
            Conversation.objects.get_user_conversations(self.request.user),
            id=conversation_id
        )
        
        return DirectMessage.objects.filter(
            conversation=conversation,
            is_deleted=False
        ).order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        """Mark conversation as read when messages are retrieved."""
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(
            Conversation.objects.get_user_conversations(request.user),
            id=conversation_id
        )
        
        # Mark conversation as read for the current user
        participant = conversation.participants.filter(user=request.user).first()
        if participant:
            participant.mark_as_read()
        
        return super().list(request, *args, **kwargs)


class DirectMessageCreateView(generics.CreateAPIView):
    """
    Create a new direct message.
    """
    serializer_class = DirectMessageCreateSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create a new message and return the created message."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = serializer.save()
        
        # Return the created message with full details
        response_serializer = DirectMessageSerializer(message, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ConversationMessageCreateView(generics.CreateAPIView):
    """
    Create a new message in a specific conversation.
    """
    serializer_class = DirectMessageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get the conversation for message creation."""
        conversation_id = self.kwargs['conversation_id']
        return Conversation.objects.get_user_conversations(self.request.user)
    
    def create(self, request, *args, **kwargs):
        """Create a new message in the specified conversation."""
        conversation_id = self.kwargs['conversation_id']
        conversation = get_object_or_404(
            self.get_queryset(),
            id=conversation_id
        )
        
        # Validate content
        content = request.data.get('content', '').strip()
        if not content:
            return Response(
                {'error': 'Message content cannot be empty.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(content) > 1000:
            return Response(
                {'error': 'Message content cannot exceed 1000 characters.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create the message
        message = conversation.add_message(request.user, content)
        
        # Return the created message
        serializer = DirectMessageSerializer(message, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mark_conversation_read(request, conversation_id):
    """
    Mark a conversation as read for the authenticated user.
    """
    conversation = get_object_or_404(
        Conversation.objects.get_user_conversations(request.user),
        id=conversation_id
    )
    
    participant = conversation.participants.filter(user=request.user).first()
    if participant:
        participant.mark_as_read()
        return Response({'message': 'Conversation marked as read.'})
    
    return Response(
        {'error': 'You are not a participant in this conversation.'},
        status=status.HTTP_403_FORBIDDEN
    )


class ConversationParticipantManagementView(generics.GenericAPIView):
    """
    Manage conversation participants (leave conversation).
    """
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, conversation_id):
        """
        Leave a conversation (deactivate participation).
        """
        conversation = get_object_or_404(
            Conversation.objects.get_user_conversations(request.user),
            id=conversation_id
        )
        
        participant = conversation.participants.filter(user=request.user).first()
        if participant:
            participant.is_active = False
            participant.save(update_fields=['is_active'])
            return Response({'message': 'You have left the conversation.'})
        
        return Response(
            {'error': 'You are not a participant in this conversation.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    def post(self, request, conversation_id):
        """
        Rejoin a conversation (reactivate participation).
        """
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            return Response(
                {'error': 'Conversation not found.'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        participant = conversation.participants.filter(user=request.user).first()
        if participant:
            participant.is_active = True
            participant.save(update_fields=['is_active'])
            return Response({'message': 'You have rejoined the conversation.'})
        
        return Response(
            {'error': 'You are not a participant in this conversation.'},
            status=status.HTTP_403_FORBIDDEN
        )


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_message(request, message_id):
    """
    Delete a message (soft delete).
    """
    try:
        message = DirectMessage.objects.get(
            id=message_id,
            sender=request.user,
            is_deleted=False
        )
    except DirectMessage.DoesNotExist:
        return Response(
            {'error': 'Message not found or you do not have permission to delete it.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    message.delete_message()
    return Response({'message': 'Message deleted successfully.'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_messaging_privacy(request, user_id):
    """
    Check if the authenticated user can send messages to another user.
    This implements basic privacy controls.
    """
    from django.contrib.auth import get_user_model
    
    User = get_user_model()
    
    try:
        target_user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return Response(
            {'error': 'User not found.'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    # Basic privacy check - users can message each other if:
    # 1. Target user is not private, OR
    # 2. Users follow each other (if following system is implemented)
    
    can_message = True
    reason = "You can send messages to this user."
    
    # Check if target user has private account
    if hasattr(target_user, 'is_private') and target_user.is_private:
        # Check if users follow each other (assuming Follow model exists)
        try:
            from apps.interactions.models import Follow
            
            # Check if authenticated user follows target user
            follows_target = Follow.objects.filter(
                follower=request.user,
                following=target_user
            ).exists()
            
            # Check if target user follows authenticated user
            followed_by_target = Follow.objects.filter(
                follower=target_user,
                following=request.user
            ).exists()
            
            if not (follows_target and followed_by_target):
                can_message = False
                reason = "This user has a private account and you must follow each other to send messages."
        
        except ImportError:
            # If Follow model doesn't exist, allow messaging for now
            pass
    
    return Response({
        'can_message': can_message,
        'reason': reason,
        'user': {
            'id': target_user.id,
            'username': target_user.username,
            'is_private': getattr(target_user, 'is_private', False)
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def conversation_metadata(request, conversation_id):
    """
    Get conversation metadata including participant info and settings.
    """
    conversation = get_object_or_404(
        Conversation.objects.get_user_conversations(request.user),
        id=conversation_id
    )
    
    # Get current user's participant record
    current_participant = conversation.participants.filter(user=request.user).first()
    
    # Get other participants
    other_participants = conversation.participants.filter(is_active=True).exclude(user=request.user)
    
    metadata = {
        'conversation_id': conversation.id,
        'created_at': conversation.created_at,
        'updated_at': conversation.updated_at,
        'is_active': conversation.is_active,
        'participant_count': conversation.participant_count,
        'current_user_joined_at': current_participant.joined_at if current_participant else None,
        'current_user_last_read_at': current_participant.last_read_at if current_participant else None,
        'other_participants': [
            {
                'user_id': p.user.id,
                'username': p.user.username,
                'joined_at': p.joined_at,
                'is_active': p.is_active
            }
            for p in other_participants
        ],
        'message_count': conversation.messages.filter(is_deleted=False).count(),
        'unread_count': current_participant.get_unread_count() if current_participant else 0
    }
    
    return Response(metadata)
