from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Community, CommunityMember, Role, Permission
from .serializers import (
    CommunitySerializer, CommunityCreateSerializer, CommunityListSerializer,
    CommunityMemberSerializer, JoinCommunitySerializer, CommunityMemberManagementSerializer,
    RoleSerializer, RoleCreateSerializer, PermissionSerializer, AssignRoleSerializer
)
from .permissions import IsCommunityAdmin, CanManageMembers, CanManageRoles


class CommunityListCreateView(generics.ListCreateAPIView):
    """
    List all communities or create a new community.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CommunityCreateSerializer
        return CommunityListSerializer
    
    def get_queryset(self):
        """
        Return communities based on privacy settings and user membership.
        """
        user = self.request.user
        queryset = Community.objects.filter(is_active=True)
        
        # Filter by search query if provided
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) | Q(description__icontains=search)
            )
        
        # Filter by privacy - show public communities and private ones user is member of
        public_communities = queryset.filter(privacy='public')
        private_communities = queryset.filter(
            privacy='private',
            members__user=user,
            members__is_active=True
        )
        
        return (public_communities | private_communities).distinct().order_by('-created_at')


class CommunityDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update or delete a community.
    """
    serializer_class = CommunitySerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return communities the user can access.
        """
        user = self.request.user
        return Community.objects.filter(
            Q(privacy='public') | 
            Q(members__user=user, members__is_active=True)
        ).distinct()
    
    def perform_update(self, serializer):
        """
        Only allow community owners to update the community.
        """
        community = self.get_object()
        if community.owner != self.request.user:
            # Check if user is admin
            try:
                membership = CommunityMember.objects.get(
                    community=community,
                    user=self.request.user,
                    is_active=True
                )
                if membership.role not in ['owner', 'admin']:
                    raise permissions.PermissionDenied(
                        "Only community owners and admins can update community details."
                    )
            except CommunityMember.DoesNotExist:
                raise permissions.PermissionDenied(
                    "You don't have permission to update this community."
                )
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """
        Only allow community owners to delete the community.
        """
        if instance.owner != self.request.user:
            raise permissions.PermissionDenied(
                "Only community owners can delete the community."
            )
        instance.delete()


class CommunityMembersView(generics.ListAPIView):
    """
    List all members of a community.
    """
    serializer_class = CommunityMemberSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Return members of the specified community.
        """
        community_id = self.kwargs['community_id']
        community = get_object_or_404(Community, id=community_id)
        
        # Check if user can view members (public community or is a member)
        user = self.request.user
        if community.privacy == 'private':
            if not CommunityMember.objects.filter(
                community=community,
                user=user,
                is_active=True
            ).exists():
                raise permissions.PermissionDenied(
                    "You must be a member to view community members."
                )
        
        return CommunityMember.objects.filter(
            community=community,
            is_active=True
        ).order_by('-joined_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def join_community(request, community_id):
    """
    Join a community.
    """
    community = get_object_or_404(Community, id=community_id, is_active=True)
    user = request.user
    
    # Check if user is already a member
    existing_membership = CommunityMember.objects.filter(
        community=community,
        user=user
    ).first()
    
    if existing_membership:
        if existing_membership.is_active:
            return Response(
                {'detail': 'You are already a member of this community.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        else:
            # Reactivate membership
            existing_membership.is_active = True
            existing_membership.save()
            return Response(
                {'detail': 'Successfully rejoined the community.'},
                status=status.HTTP_200_OK
            )
    
    # Create new membership
    CommunityMember.objects.create(
        community=community,
        user=user,
        role='member'
    )
    
    return Response(
        {'detail': 'Successfully joined the community.'},
        status=status.HTTP_201_CREATED
    )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def leave_community(request, community_id):
    """
    Leave a community.
    """
    community = get_object_or_404(Community, id=community_id)
    user = request.user
    
    # Check if user is the owner
    if community.owner == user:
        return Response(
            {'detail': 'Community owners cannot leave their own community.'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        membership = CommunityMember.objects.get(
            community=community,
            user=user,
            is_active=True
        )
        membership.is_active = False
        membership.save()
        
        return Response(
            {'detail': 'Successfully left the community.'},
            status=status.HTTP_200_OK
        )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def manage_member(request, community_id, member_id):
    """
    Manage a community member (change role, remove, etc.).
    """
    community = get_object_or_404(Community, id=community_id)
    member = get_object_or_404(CommunityMember, id=member_id, community=community)
    
    # Check if requesting user has permission to manage members
    try:
        requester_membership = CommunityMember.objects.get(
            community=community,
            user=request.user,
            is_active=True
        )
        
        if requester_membership.role not in ['owner', 'admin']:
            return Response(
                {'detail': 'You don\'t have permission to manage members.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = CommunityMemberManagementSerializer(
        member,
        data=request.data,
        partial=True,
        context={'request': request}
    )
    
    if serializer.is_valid():
        serializer.save()
        return Response(CommunityMemberSerializer(member).data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_communities(request):
    """
    Get communities that the current user is a member of.
    """
    user = request.user
    memberships = CommunityMember.objects.filter(
        user=user,
        is_active=True
    ).select_related('community')
    
    communities = [membership.community for membership in memberships]
    serializer = CommunityListSerializer(
        communities,
        many=True,
        context={'request': request}
    )
    
    return Response(serializer.data)


# Role and Permission Management Views

class PermissionListView(generics.ListAPIView):
    """
    List all available permissions.
    """
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]


class RoleListCreateView(generics.ListCreateAPIView):
    """
    List all roles or create a new custom role.
    """
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return RoleCreateSerializer
        return RoleSerializer
    
    def get_queryset(self):
        """Return all roles, with option to filter by community."""
        queryset = Role.objects.all()
        
        # Filter by community if specified
        community_id = self.request.query_params.get('community_id')
        if community_id:
            # Check if user has permission to view community roles
            try:
                community = Community.objects.get(id=community_id)
                membership = CommunityMember.objects.get(
                    community=community,
                    user=self.request.user,
                    is_active=True
                )
                if membership.role not in ['owner', 'admin']:
                    # Return only default roles for non-admin members
                    queryset = queryset.filter(is_default=True)
            except (Community.DoesNotExist, CommunityMember.DoesNotExist):
                queryset = queryset.filter(is_default=True)
        
        return queryset.order_by('name')


class RoleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a role.
    """
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def perform_update(self, serializer):
        """Only allow updates to non-default roles."""
        role = self.get_object()
        if role.is_default:
            raise permissions.PermissionDenied(
                "Cannot modify default system roles."
            )
        serializer.save()
    
    def perform_destroy(self, instance):
        """Only allow deletion of non-default roles."""
        if instance.is_default:
            raise permissions.PermissionDenied(
                "Cannot delete default system roles."
            )
        instance.delete()


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def assign_role_to_member(request, community_id, member_id):
    """
    Assign a role to a community member.
    """
    community = get_object_or_404(Community, id=community_id)
    member = get_object_or_404(CommunityMember, id=member_id, community=community)
    
    # Check if requesting user has permission to manage members
    try:
        requester_membership = CommunityMember.objects.get(
            community=community,
            user=request.user,
            is_active=True
        )
        
        if not requester_membership.has_permission('manage_members'):
            return Response(
                {'detail': 'You don\'t have permission to manage member roles.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    serializer = AssignRoleSerializer(data=request.data)
    if serializer.is_valid():
        role_id = serializer.validated_data.get('role_id')
        default_role = serializer.validated_data.get('default_role')
        
        if role_id:
            # Assign custom role
            role = get_object_or_404(Role, id=role_id)
            member.custom_role = role
            member.role = 'member'  # Reset to default when using custom role
        else:
            # Assign default role
            member.role = default_role
            member.custom_role = None
        
        member.save()
        
        return Response(
            CommunityMemberSerializer(member).data,
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_roles(request, community_id):
    """
    Get all roles available in a community.
    """
    community = get_object_or_404(Community, id=community_id)
    
    # Check if user is a member
    try:
        membership = CommunityMember.objects.get(
            community=community,
            user=request.user,
            is_active=True
        )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get default roles and community-specific custom roles
    default_roles = Role.objects.filter(is_default=True)
    custom_roles = Role.objects.filter(
        is_default=False,
        community_assignments__community=community,
        community_assignments__is_active=True
    )
    
    all_roles = (default_roles | custom_roles).distinct()
    serializer = RoleSerializer(all_roles, many=True)
    
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def member_permissions(request, community_id, member_id):
    """
    Get all permissions for a specific community member.
    """
    community = get_object_or_404(Community, id=community_id)
    member = get_object_or_404(CommunityMember, id=member_id, community=community)
    
    # Check if requesting user can view member permissions
    try:
        requester_membership = CommunityMember.objects.get(
            community=community,
            user=request.user,
            is_active=True
        )
        
        # Members can view their own permissions, admins can view all
        if (member.user != request.user and 
            not requester_membership.has_permission('manage_members')):
            return Response(
                {'detail': 'You don\'t have permission to view member permissions.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    # Get all available permissions and check which ones the member has
    all_permissions = Permission.objects.all()
    member_permissions = []
    
    for permission in all_permissions:
        has_permission = member.has_permission(permission.codename)
        member_permissions.append({
            'permission': PermissionSerializer(permission).data,
            'has_permission': has_permission
        })
    
    return Response({
        'member': CommunityMemberSerializer(member).data,
        'permissions': member_permissions,
        'effective_role': member.get_effective_role()
    })


# Community Content and Feed Views

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_feed(request, community_id):
    """
    Get tweets from a specific community.
    """
    from apps.tweets.models import Tweet
    from apps.tweets.serializers import TweetSerializer
    
    community = get_object_or_404(Community, id=community_id, is_active=True)
    
    # Check if user can view community content
    if community.privacy == 'private':
        try:
            CommunityMember.objects.get(
                community=community,
                user=request.user,
                is_active=True
            )
        except CommunityMember.DoesNotExist:
            return Response(
                {'detail': 'You must be a member to view this community\'s content.'},
                status=status.HTTP_403_FORBIDDEN
            )
    
    # Get tweets from this community
    tweets = Tweet.objects.filter(
        community=community,
        is_deleted=False
    ).select_related('author', 'community').prefetch_related(
        'media', 'tweet_hashtags__hashtag'
    ).order_by('-created_at')
    
    # Pagination
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_tweets = paginator.paginate_queryset(tweets, request)
    
    serializer = TweetSerializer(
        paginated_tweets,
        many=True,
        context={'request': request}
    )
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_discovery(request):
    """
    Discover communities based on activity and user interests.
    """
    # Get trending communities (most active in the last 7 days)
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    
    week_ago = timezone.now() - timedelta(days=7)
    
    trending_communities = Community.objects.filter(
        is_active=True,
        privacy='public'
    ).annotate(
        recent_posts=Count(
            'tweets',
            filter=Q(tweets__created_at__gte=week_ago, tweets__is_deleted=False)
        ),
        total_members=Count('members', filter=Q(members__is_active=True))
    ).filter(
        recent_posts__gt=0
    ).order_by('-recent_posts', '-total_members')[:10]
    
    # Get suggested communities (communities with similar interests)
    user_communities = Community.objects.filter(
        members__user=request.user,
        members__is_active=True
    )
    
    # Simple suggestion: communities that other members of user's communities have joined
    suggested_communities = Community.objects.filter(
        is_active=True,
        privacy='public'
    ).exclude(
        id__in=user_communities.values_list('id', flat=True)
    ).annotate(
        common_members=Count(
            'members',
            filter=Q(
                members__user__in=user_communities.values_list('members__user', flat=True),
                members__is_active=True
            )
        )
    ).filter(common_members__gt=0).order_by('-common_members')[:10]
    
    trending_serializer = CommunityListSerializer(
        trending_communities,
        many=True,
        context={'request': request}
    )
    
    suggested_serializer = CommunityListSerializer(
        suggested_communities,
        many=True,
        context={'request': request}
    )
    
    return Response({
        'trending': trending_serializer.data,
        'suggested': suggested_serializer.data
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_search(request):
    """
    Search for communities by name or description.
    """
    query = request.query_params.get('q', '').strip()
    if not query:
        return Response({'results': []})
    
    # Search public communities and private communities user is member of
    public_communities = Community.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
        privacy='public'
    )
    
    private_communities = Community.objects.filter(
        Q(name__icontains=query) | Q(description__icontains=query),
        is_active=True,
        privacy='private',
        members__user=request.user,
        members__is_active=True
    )
    
    communities = (public_communities | private_communities).distinct().order_by('name')
    
    # Pagination
    from rest_framework.pagination import PageNumberPagination
    paginator = PageNumberPagination()
    paginator.page_size = 20
    paginated_communities = paginator.paginate_queryset(communities, request)
    
    serializer = CommunityListSerializer(
        paginated_communities,
        many=True,
        context={'request': request}
    )
    
    return paginator.get_paginated_response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def community_stats(request, community_id):
    """
    Get community statistics and analytics.
    """
    community = get_object_or_404(Community, id=community_id)
    
    # Check if user can view community stats
    try:
        membership = CommunityMember.objects.get(
            community=community,
            user=request.user,
            is_active=True
        )
        
        # Only admins and owners can view detailed stats
        if membership.role not in ['owner', 'admin']:
            return Response(
                {'detail': 'You don\'t have permission to view community statistics.'},
                status=status.HTTP_403_FORBIDDEN
            )
    except CommunityMember.DoesNotExist:
        return Response(
            {'detail': 'You are not a member of this community.'},
            status=status.HTTP_403_FORBIDDEN
        )
    
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Count
    from apps.tweets.models import Tweet
    
    # Calculate various statistics
    now = timezone.now()
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)
    
    stats = {
        'total_members': community.members.filter(is_active=True).count(),
        'total_posts': Tweet.objects.filter(community=community, is_deleted=False).count(),
        'posts_this_week': Tweet.objects.filter(
            community=community,
            is_deleted=False,
            created_at__gte=week_ago
        ).count(),
        'posts_this_month': Tweet.objects.filter(
            community=community,
            is_deleted=False,
            created_at__gte=month_ago
        ).count(),
        'new_members_this_week': community.members.filter(
            is_active=True,
            joined_at__gte=week_ago
        ).count(),
        'new_members_this_month': community.members.filter(
            is_active=True,
            joined_at__gte=month_ago
        ).count(),
        'top_contributors': list(
            Tweet.objects.filter(
                community=community,
                is_deleted=False,
                created_at__gte=month_ago
            ).values('author__username').annotate(
                post_count=Count('id')
            ).order_by('-post_count')[:5]
        )
    }
    
    return Response(stats)
