from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q

from apps.authentication.models import User
from apps.authentication.serializers import UserProfileSerializer, UserBasicSerializer
from apps.interactions.models import Follow
from apps.interactions.serializers import FollowSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request, user_id):
    """
    Get user profile information.
    """
    user = get_object_or_404(User, id=user_id)
    serializer = UserProfileSerializer(user, context={'request': request})
    return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_followers(request, user_id):
    """
    Get list of user's followers.
    """
    user = get_object_or_404(User, id=user_id)
    followers = Follow.objects.filter(following=user).select_related('follower')
    
    # Extract follower users
    follower_users = [follow.follower for follow in followers]
    serializer = UserBasicSerializer(follower_users, many=True, context={'request': request})
    
    return Response({
        'followers': serializer.data,
        'count': len(follower_users)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_following(request, user_id):
    """
    Get list of users that this user is following.
    """
    user = get_object_or_404(User, id=user_id)
    following = Follow.objects.filter(follower=user).select_related('following')
    
    # Extract following users
    following_users = [follow.following for follow in following]
    serializer = UserBasicSerializer(following_users, many=True, context={'request': request})
    
    return Response({
        'following': serializer.data,
        'count': len(following_users)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def search_users(request):
    """
    Search for users by username, first name, or last name.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Search query is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Search users by username, first name, or last name
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    ).exclude(id=request.user.id)[:20]  # Limit to 20 results
    
    serializer = UserBasicSerializer(users, many=True, context={'request': request})
    
    return Response({
        'users': serializer.data,
        'count': len(users),
        'query': query
    }, status=status.HTTP_200_OK)
