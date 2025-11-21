from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import IntegrityError

from apps.tweets.models import Tweet
from .models import Like, Retweet, Bookmark, Follow
from .serializers import LikeSerializer, RetweetSerializer, BookmarkSerializer, FollowSerializer
from apps.authentication.models import User


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def like_tweet(request, tweet_id):
    """
    Like or unlike a tweet.
    POST: Like a tweet
    DELETE: Unlike a tweet
    """
    tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
    
    if request.method == 'POST':
        try:
            like, created = Like.objects.get_or_create(
                user=request.user,
                tweet=tweet
            )
            if created:
                serializer = LikeSerializer(like)
                return Response({
                    'message': 'Tweet liked successfully',
                    'like': serializer.data,
                    'likes_count': tweet.likes_count
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Tweet already liked',
                    'likes_count': tweet.likes_count
                }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'Failed to like tweet'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            like = Like.objects.get(user=request.user, tweet=tweet)
            like.delete()
            return Response({
                'message': 'Tweet unliked successfully',
                'likes_count': tweet.likes_count
            }, status=status.HTTP_200_OK)
        except Like.DoesNotExist:
            return Response({
                'error': 'Like not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def retweet_tweet(request, tweet_id):
    """
    Retweet or unretweet a tweet.
    POST: Retweet a tweet
    DELETE: Unretweet a tweet
    """
    tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
    
    # Prevent users from retweeting their own tweets
    if tweet.author == request.user:
        return Response({
            'error': 'Cannot retweet your own tweet'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':
        try:
            retweet, created = Retweet.objects.get_or_create(
                user=request.user,
                tweet=tweet
            )
            if created:
                serializer = RetweetSerializer(retweet)
                return Response({
                    'message': 'Tweet retweeted successfully',
                    'retweet': serializer.data,
                    'retweets_count': tweet.retweets_count
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Tweet already retweeted',
                    'retweets_count': tweet.retweets_count
                }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'Failed to retweet'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            retweet = Retweet.objects.get(user=request.user, tweet=tweet)
            retweet.delete()
            return Response({
                'message': 'Tweet unretweeted successfully',
                'retweets_count': tweet.retweets_count
            }, status=status.HTTP_200_OK)
        except Retweet.DoesNotExist:
            return Response({
                'error': 'Retweet not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def bookmark_tweet(request, tweet_id):
    """
    Bookmark or unbookmark a tweet.
    POST: Bookmark a tweet
    DELETE: Unbookmark a tweet
    """
    tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
    
    if request.method == 'POST':
        try:
            bookmark, created = Bookmark.objects.get_or_create(
                user=request.user,
                tweet=tweet
            )
            if created:
                serializer = BookmarkSerializer(bookmark)
                return Response({
                    'message': 'Tweet bookmarked successfully',
                    'bookmark': serializer.data,
                    'bookmarks_count': tweet.bookmarks_count
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': 'Tweet already bookmarked',
                    'bookmarks_count': tweet.bookmarks_count
                }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'Failed to bookmark tweet'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            bookmark = Bookmark.objects.get(user=request.user, tweet=tweet)
            bookmark.delete()
            return Response({
                'message': 'Tweet unbookmarked successfully',
                'bookmarks_count': tweet.bookmarks_count
            }, status=status.HTTP_200_OK)
        except Bookmark.DoesNotExist:
            return Response({
                'error': 'Bookmark not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['POST', 'DELETE'])
@permission_classes([IsAuthenticated])
def follow_user(request, user_id):
    """
    Follow or unfollow a user.
    POST: Follow a user
    DELETE: Unfollow a user
    """
    user_to_follow = get_object_or_404(User, id=user_id)
    
    # Prevent users from following themselves
    if user_to_follow == request.user:
        return Response({
            'error': 'Cannot follow yourself'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if request.method == 'POST':
        try:
            follow, created = Follow.objects.get_or_create(
                follower=request.user,
                following=user_to_follow
            )
            if created:
                serializer = FollowSerializer(follow)
                return Response({
                    'message': f'Successfully followed {user_to_follow.username}',
                    'follow': serializer.data,
                    'followers_count': user_to_follow.followers.count(),
                    'following_count': request.user.following.count()
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({
                    'message': f'Already following {user_to_follow.username}',
                    'followers_count': user_to_follow.followers.count(),
                    'following_count': request.user.following.count()
                }, status=status.HTTP_200_OK)
        except IntegrityError:
            return Response({
                'error': 'Failed to follow user'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            follow = Follow.objects.get(follower=request.user, following=user_to_follow)
            follow.delete()
            return Response({
                'message': f'Successfully unfollowed {user_to_follow.username}',
                'followers_count': user_to_follow.followers.count(),
                'following_count': request.user.following.count()
            }, status=status.HTTP_200_OK)
        except Follow.DoesNotExist:
            return Response({
                'error': 'Follow relationship not found'
            }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """
    Get user's bookmarked tweets.
    """
    bookmarks = Bookmark.objects.filter(
        user=request.user,
        tweet__is_deleted=False  
    ).select_related(
        'tweet__author'
    ).prefetch_related(
        'tweet__media'
    )
    serializer = BookmarkSerializer(bookmarks, many=True, context={'request': request})
    return Response({
        'bookmarks': serializer.data,
        'count': bookmarks.count()
    }, status=status.HTTP_200_OK)
