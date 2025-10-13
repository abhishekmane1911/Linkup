from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import List, ListMember
from .serializers import (
    ListSerializer, ListBasicSerializer, ListCreateSerializer, 
    ListUpdateSerializer, ListMemberSerializer, AddMemberSerializer,
    UserBasicSerializer
)

User = get_user_model()


class ListPagination(PageNumberPagination):
    """
    Custom pagination for lists.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ListListCreateView(generics.ListCreateAPIView):
    """
    List all lists for the authenticated user or create a new list.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ListPagination
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListCreateSerializer
        return ListBasicSerializer
    
    def get_queryset(self):
        """Get lists owned by the authenticated user."""
        return List.objects.filter(
            owner=self.request.user,
            is_deleted=False
        ).select_related('owner').order_by('-created_at')
    
    def perform_create(self, serializer):
        """Create a new list with the current user as owner."""
        serializer.save(owner=self.request.user)


class ListDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific list.
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return ListUpdateSerializer
        return ListSerializer
    
    def get_queryset(self):
        """Get lists that the user can access."""
        user = self.request.user
        return List.objects.filter(
            Q(owner=user) | Q(privacy='public'),
            is_deleted=False
        ).select_related('owner')
    
    def get_object(self):
        """Get the list object with permission checking."""
        obj = super().get_object()
        
        # Check if user can view this list
        if not obj.can_view(self.request.user):
            self.permission_denied(
                self.request,
                message="You don't have permission to access this list."
            )
        
        return obj
    
    def update(self, request, *args, **kwargs):
        """Update a list (only owner can update)."""
        obj = self.get_object()
        
        # Check if user can edit this list
        if not obj.can_edit(request.user):
            return Response(
                {"error": "You don't have permission to edit this list."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        """Soft delete a list (only owner can delete)."""
        obj = self.get_object()
        
        # Check if user can edit this list
        if not obj.can_edit(request.user):
            return Response(
                {"error": "You don't have permission to delete this list."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Perform soft delete
        obj.soft_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ListMembersView(generics.ListAPIView):
    """
    List all members of a specific list.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListMemberSerializer
    pagination_class = ListPagination
    
    def get_queryset(self):
        """Get members of the specified list."""
        list_id = self.kwargs['list_id']
        list_obj = get_object_or_404(
            List.objects.select_related('owner'),
            id=list_id,
            is_deleted=False
        )
        
        # Check if user can view this list
        if not list_obj.can_view(self.request.user):
            return ListMember.objects.none()
        
        return ListMember.objects.filter(
            list=list_obj,
            is_active=True
        ).select_related('user').order_by('created_at')


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def add_member_to_list(request, list_id):
    """
    Add a member to a list.
    """
    # Get the list
    list_obj = get_object_or_404(
        List.objects.select_related('owner'),
        id=list_id,
        is_deleted=False
    )
    
    # Check if user can edit this list
    if not list_obj.can_edit(request.user):
        return Response(
            {"error": "You don't have permission to modify this list."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Validate the request data
    serializer = AddMemberSerializer(
        data=request.data,
        context={'list': list_obj}
    )
    
    if serializer.is_valid():
        user_to_add = serializer.validated_data['user_id']
        
        # Add the member
        list_member, created = list_obj.add_member(user_to_add)
        
        if created:
            return Response(
                {
                    "message": f"@{user_to_add.username} has been added to the list.",
                    "member": ListMemberSerializer(list_member).data
                },
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"message": f"@{user_to_add.username} is already a member of this list."},
                status=status.HTTP_200_OK
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@permission_classes([permissions.IsAuthenticated])
def remove_member_from_list(request, list_id, user_id):
    """
    Remove a member from a list.
    """
    # Get the list
    list_obj = get_object_or_404(
        List.objects.select_related('owner'),
        id=list_id,
        is_deleted=False
    )
    
    # Check if user can edit this list
    if not list_obj.can_edit(request.user):
        return Response(
            {"error": "You don't have permission to modify this list."},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get the user to remove
    user_to_remove = get_object_or_404(User, id=user_id)
    
    # Remove the member
    removed = list_obj.remove_member(user_to_remove)
    
    if removed:
        return Response(
            {"message": f"@{user_to_remove.username} has been removed from the list."},
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {"error": f"@{user_to_remove.username} is not a member of this list."},
            status=status.HTTP_404_NOT_FOUND
        )


class PublicListsView(generics.ListAPIView):
    """
    List public lists for discovery.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListBasicSerializer
    pagination_class = ListPagination
    
    def get_queryset(self):
        """Get public lists ordered by creation date."""
        queryset = List.objects.filter(
            privacy='public',
            is_deleted=False
        ).select_related('owner').order_by('-created_at')
        
        # Optional search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(description__icontains=search) |
                Q(owner__username__icontains=search)
            )
        
        return queryset


class UserListsView(generics.ListAPIView):
    """
    List public lists owned by a specific user.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ListBasicSerializer
    pagination_class = ListPagination
    
    def get_queryset(self):
        """Get public lists owned by the specified user."""
        user_id = self.kwargs['user_id']
        user = get_object_or_404(User, id=user_id)
        
        return List.objects.filter(
            owner=user,
            privacy='public',
            is_deleted=False
        ).select_related('owner').order_by('-created_at')


class ListTimelineView(generics.ListAPIView):
    """
    Get timeline feed for a specific list showing tweets from list members.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = ListPagination
    
    def get_serializer_class(self):
        """Import and return TweetSerializer from tweets app."""
        from apps.tweets.serializers import TweetSerializer
        return TweetSerializer
    
    def get_queryset(self):
        """Get tweets from list members."""
        list_id = self.kwargs['list_id']
        list_obj = get_object_or_404(
            List.objects.select_related('owner'),
            id=list_id,
            is_deleted=False
        )
        
        # Check if user can view this list
        if not list_obj.can_view(self.request.user):
            from apps.tweets.models import Tweet
            return Tweet.objects.none()
        
        # Get active list members
        member_user_ids = list_obj.members.filter(
            is_active=True
        ).values_list('user_id', flat=True)
        
        if not member_user_ids:
            from apps.tweets.models import Tweet
            return Tweet.objects.none()
        
        # Get tweets from list members
        from apps.tweets.models import Tweet
        from django.db.models import Prefetch
        
        queryset = Tweet.objects.filter(
            author_id__in=member_user_ids,
            is_deleted=False
        ).select_related(
            'author', 'parent_tweet', 'parent_tweet__author'
        ).prefetch_related(
            'media',
            'likes',
            'retweets',
            'bookmarks',
            Prefetch('tweet_hashtags__hashtag')
        ).order_by('-created_at')
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def search_users_for_list(request):
    """
    Search users to add to a list.
    """
    query = request.query_params.get('q', '').strip()
    
    if not query or len(query) < 2:
        return Response(
            {"error": "Search query must be at least 2 characters long."},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Search users by username, first name, or last name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]  # Limit to 20 results
    
    serializer = UserBasicSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_discovery(request):
    """
    Discover popular and trending lists.
    """
    from django.db.models import Count
    from datetime import timedelta
    from django.utils import timezone
    
    # Get popular public lists (most members)
    popular_lists = List.objects.filter(
        privacy='public',
        is_deleted=False
    ).annotate(
        active_members_count=Count('members', filter=Q(members__is_active=True))
    ).filter(
        active_members_count__gt=0
    ).select_related('owner').order_by('-active_members_count')[:10]
    
    # Get recently created public lists
    week_ago = timezone.now() - timedelta(days=7)
    recent_lists = List.objects.filter(
        privacy='public',
        is_deleted=False,
        created_at__gte=week_ago
    ).select_related('owner').order_by('-created_at')[:10]
    
    # Get lists with recent activity (new members)
    active_lists = List.objects.filter(
        privacy='public',
        is_deleted=False,
        members__created_at__gte=week_ago,
        members__is_active=True
    ).annotate(
        new_members_count=Count('members', filter=Q(
            members__created_at__gte=week_ago,
            members__is_active=True
        ))
    ).filter(
        new_members_count__gt=0
    ).select_related('owner').order_by('-new_members_count')[:10]
    
    # Optional search functionality
    search = request.query_params.get('search', None)
    if search:
        popular_lists = popular_lists.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(owner__username__icontains=search)
        )
        recent_lists = recent_lists.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(owner__username__icontains=search)
        )
        active_lists = active_lists.filter(
            Q(name__icontains=search) |
            Q(description__icontains=search) |
            Q(owner__username__icontains=search)
        )
    
    # Serialize results
    popular_serializer = ListBasicSerializer(popular_lists, many=True, context={'request': request})
    recent_serializer = ListBasicSerializer(recent_lists, many=True, context={'request': request})
    active_serializer = ListBasicSerializer(active_lists, many=True, context={'request': request})
    
    return Response({
        'discovery': {
            'popular': {
                'count': popular_lists.count(),
                'data': popular_serializer.data
            },
            'recent': {
                'count': recent_lists.count(),
                'data': recent_serializer.data
            },
            'active': {
                'count': active_lists.count(),
                'data': active_serializer.data
            }
        }
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def list_suggestions(request):
    """
    Get list suggestions based on user's following and interests.
    """
    from django.db.models import Count
    
    current_user = request.user
    
    # Get users that current user follows
    following_ids = current_user.following.values_list('following_id', flat=True)
    
    if not following_ids:
        # If user doesn't follow anyone, return popular lists
        suggested_lists = List.objects.filter(
            privacy='public',
            is_deleted=False
        ).annotate(
            members_count=Count('members', filter=Q(members__is_active=True))
        ).filter(
            members_count__gt=0
        ).select_related('owner').order_by('-members_count')[:10]
    else:
        # Get lists that contain users the current user follows
        suggested_lists = List.objects.filter(
            privacy='public',
            is_deleted=False,
            members__user_id__in=following_ids,
            members__is_active=True
        ).exclude(
            owner=current_user  # Exclude user's own lists
        ).annotate(
            mutual_members_count=Count('members', filter=Q(
                members__user_id__in=following_ids,
                members__is_active=True
            ))
        ).filter(
            mutual_members_count__gt=0
        ).select_related('owner').order_by('-mutual_members_count')[:10]
    
    serializer = ListBasicSerializer(suggested_lists, many=True, context={'request': request})
    
    return Response({
        'suggestions': serializer.data,
        'count': len(suggested_lists)
    }, status=status.HTTP_200_OK)