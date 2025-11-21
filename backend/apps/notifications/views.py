from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from .models import Notification
from .serializers import NotificationSerializer, NotificationMarkReadSerializer


class NotificationPagination(PageNumberPagination):
    """Custom pagination for notifications."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationListView(generics.ListAPIView):
    """
    List notifications for the current user.
    """
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """Get notifications for the current user."""
        user = self.request.user
        queryset = Notification.objects.filter(
            recipient=user
        ).select_related('actor', 'content_type')
        
        # Filter by read status if specified
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() == 'true'
            queryset = queryset.filter(is_read=is_read_bool)
        
        return queryset


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def mark_notifications_read(request):
    """
    Mark notifications as read.
    If notification_ids is provided, mark those specific notifications.
    Otherwise, mark all unread notifications as read.
    """
    serializer = NotificationMarkReadSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    
    notification_ids = serializer.validated_data.get('notification_ids', [])
    user = request.user
    
    if notification_ids:
        # Mark specific notifications as read
        notifications = Notification.objects.filter(
            id__in=notification_ids,
            recipient=user,
            is_read=False
        )
    else:
        # Mark all unread notifications as read
        notifications = Notification.objects.filter(
            recipient=user,
            is_read=False
        )
    
    # Update notifications
    count = notifications.update(
        is_read=True,
        read_at=timezone.now()
    )
    
    return Response({
        'message': f'{count} notification(s) marked as read',
        'count': count
    })


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def notification_count(request):
    """
    Get count of unread notifications for the current user.
    """
    user = request.user
    unread_count = Notification.objects.filter(
        recipient=user,
        is_read=False
    ).count()
    
    return Response({
        'unread_count': unread_count
    })


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def delete_notification(request, pk):
    """
    Delete a specific notification.
    """
    try:
        notification = Notification.objects.get(
            id=pk,
            recipient=request.user
        )
        notification.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Notification.DoesNotExist:
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def clear_all_notifications(request):
    """
    Clear all notifications for the current user.
    """
    count = Notification.objects.filter(recipient=request.user).delete()[0]
    return Response({
        'message': f'{count} notification(s) deleted',
        'count': count
    })
