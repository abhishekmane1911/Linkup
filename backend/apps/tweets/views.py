from rest_framework import generics, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from django.contrib.auth import get_user_model
from .models import Tweet, Media, Hashtag, TweetHashtag
from .serializers import TweetSerializer, TweetCreateSerializer, TweetUpdateSerializer, HashtagSerializer, TweetReplySerializer

User = get_user_model()


class TweetPagination(PageNumberPagination):
    """Custom pagination for tweets."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class TweetListCreateView(generics.ListCreateAPIView):
    """
    List all tweets or create a new tweet.
    GET: Returns paginated list of all tweets (excluding deleted ones)
    POST: Create a new tweet with optional media attachments
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    parser_classes = [MultiPartParser, FormParser, JSONParser]
    
    def get_queryset(self):
        """Get all non-deleted tweets ordered by creation date."""
        return Tweet.objects.filter(is_deleted=False).select_related('author').prefetch_related('media').order_by('-created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return TweetCreateSerializer
        return TweetSerializer


class TweetDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, or delete a specific tweet.
    GET: Retrieve tweet details
    PUT/PATCH: Update tweet content (only author can update)
    DELETE: Soft delete tweet (only author can delete)
    """
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get non-deleted tweets."""
        return Tweet.objects.filter(is_deleted=False).select_related('author').prefetch_related('media')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method in ['PUT', 'PATCH']:
            return TweetUpdateSerializer
        return TweetSerializer
    
    def perform_update(self, serializer):
        """Only allow author to update their own tweets."""
        tweet = self.get_object()
        if tweet.author != self.request.user:
            raise permissions.PermissionDenied("You can only edit your own tweets.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete tweet (only author can delete)."""
        if instance.author != self.request.user:
            raise permissions.PermissionDenied("You can only delete your own tweets.")
        instance.soft_delete()


class UserTweetsView(generics.ListAPIView):
    """
    List tweets by a specific user.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get tweets by specific user."""
        user_id = self.kwargs.get('user_id')
        return Tweet.objects.filter(
            author_id=user_id, 
            is_deleted=False
        ).select_related('author').prefetch_related('media').order_by('-created_at')


class TweetRepliesView(generics.ListCreateAPIView):
    """
    List replies to a specific tweet or create a new reply.
    GET: List all replies to a tweet
    POST: Create a new reply to a tweet
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get replies to a specific tweet."""
        tweet_id = self.kwargs.get('tweet_id')
        return Tweet.objects.filter(
            parent_tweet_id=tweet_id,
            is_deleted=False
        ).select_related('author', 'parent_tweet').prefetch_related('media').order_by('created_at')
    
    def get_serializer_class(self):
        """Return appropriate serializer based on request method."""
        if self.request.method == 'POST':
            return TweetReplySerializer
        return TweetSerializer
    
    def perform_create(self, serializer):
        """Set the parent tweet when creating a reply."""
        tweet_id = self.kwargs.get('tweet_id')
        parent_tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
        serializer.save(parent_tweet=parent_tweet)


class HashtagTweetsView(generics.ListAPIView):
    """
    List tweets containing a specific hashtag.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get tweets containing the specified hashtag."""
        hashtag_name = self.kwargs.get('hashtag_name')
        return Tweet.objects.filter(
            tweet_hashtags__hashtag__name=hashtag_name.lower(),
            is_deleted=False
        ).select_related('author').prefetch_related('media').order_by('-created_at')


class TrendingHashtagsView(generics.ListAPIView):
    """
    List trending hashtags based on usage count.
    """
    serializer_class = HashtagSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = None  # Disable pagination for this view
    
    def get_queryset(self):
        """Get trending hashtags ordered by usage count."""
        # Temporarily remove the filter to debug
        queryset = Hashtag.objects.all().order_by('-usage_count')[:20]
        print(f"Queryset count: {queryset.count()}")
        for hashtag in queryset:
            print(f"Hashtag: {hashtag.name}, usage_count: {hashtag.usage_count}")
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tweet_stats(request, tweet_id):
    """
    Get statistics for a specific tweet.
    """
    tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
    
    stats = {
        'likes_count': tweet.likes_count,
        'retweets_count': tweet.retweets_count,
        'reply_count': tweet.reply_count,
        'hashtags_count': tweet.get_hashtags().count(),
        'created_at': tweet.created_at,
        'updated_at': tweet.updated_at,
    }
    
    return Response(stats, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def hashtag_search(request):
    """
    Search for hashtags by name.
    """
    query = request.GET.get('q', '').strip()
    if not query:
        return Response({'error': 'Query parameter "q" is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Remove # symbol if present
    query = query.lstrip('#').lower()
    
    hashtags = Hashtag.objects.filter(
        name__icontains=query
    ).order_by('-usage_count')[:10]
    
    serializer = HashtagSerializer(hashtags, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)


class TweetThreadView(generics.RetrieveAPIView):
    """
    Get a tweet with its full conversation thread.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'
    
    def get_queryset(self):
        """Get non-deleted tweets."""
        return Tweet.objects.filter(is_deleted=False).select_related('author', 'parent_tweet').prefetch_related('media')
    
    def retrieve(self, request, *args, **kwargs):
        """Get tweet with its conversation thread."""
        tweet = self.get_object()
        
        # Get the root tweet of the conversation
        root_tweet = tweet
        while root_tweet.parent_tweet:
            root_tweet = root_tweet.parent_tweet
        
        # Get all tweets in the conversation thread
        thread_tweets = Tweet.objects.filter(
            Q(id=root_tweet.id) |
            Q(parent_tweet=root_tweet) |
            Q(parent_tweet__parent_tweet=root_tweet)
        ).filter(is_deleted=False).select_related('author', 'parent_tweet').prefetch_related('media').order_by('created_at')
        
        # Serialize the main tweet
        tweet_serializer = self.get_serializer(tweet)
        
        # Serialize the thread
        thread_serializer = TweetSerializer(thread_tweets, many=True, context={'request': request})
        
        return Response({
            'tweet': tweet_serializer.data,
            'thread': thread_serializer.data,
            'thread_count': thread_tweets.count()
        }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def tweet_conversation(request, tweet_id):
    """
    Get the full conversation thread for a tweet.
    """
    tweet = get_object_or_404(Tweet, id=tweet_id, is_deleted=False)
    
    # Find the root tweet
    root_tweet = tweet
    while root_tweet.parent_tweet and not root_tweet.parent_tweet.is_deleted:
        root_tweet = root_tweet.parent_tweet
    
    # Get all tweets in the conversation
    conversation_tweets = []
    
    def get_replies(parent_tweet, level=0):
        """Recursively get all replies to build the conversation tree."""
        replies = Tweet.objects.filter(
            parent_tweet=parent_tweet,
            is_deleted=False
        ).select_related('author').prefetch_related('media').order_by('created_at')
        
        for reply in replies:
            conversation_tweets.append({
                'tweet': TweetSerializer(reply, context={'request': request}).data,
                'level': level
            })
            get_replies(reply, level + 1)
    
    # Start with root tweet
    conversation_tweets.append({
        'tweet': TweetSerializer(root_tweet, context={'request': request}).data,
        'level': 0
    })
    
    # Get all replies recursively
    get_replies(root_tweet, 1)
    
    return Response({
        'conversation': conversation_tweets,
        'total_tweets': len(conversation_tweets),
        'root_tweet_id': root_tweet.id
    }, status=status.HTTP_200_OK)


class HomeTimelineFeedView(generics.ListAPIView):
    """
    Home timeline feed showing tweets from followed users.
    Returns tweets from users that the current user follows, ordered by creation date.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get tweets from followed users for the home timeline."""
        user = self.request.user
        
        # Get users that the current user follows
        following_users = user.following.values_list('following_id', flat=True)
        
        # If user doesn't follow anyone, return empty queryset
        if not following_users:
            return Tweet.objects.none()
        
        # Get tweets from followed users (including retweets)
        queryset = Tweet.objects.filter(
            author_id__in=following_users,
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


class TweetSearchView(generics.ListAPIView):
    """
    Search tweets by content and hashtags.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Search tweets by content and hashtags."""
        query = self.request.GET.get('q', '').strip()
        
        if not query:
            return Tweet.objects.none()
        
        # Search in tweet content and hashtags
        queryset = Tweet.objects.filter(
            Q(content__icontains=query) |
            Q(tweet_hashtags__hashtag__name__icontains=query.lstrip('#')),
            is_deleted=False
        ).distinct().select_related(
            'author', 'parent_tweet'
        ).prefetch_related(
            'media',
            'likes',
            'retweets',
            'bookmarks',
            Prefetch('tweet_hashtags__hashtag')
        ).order_by('-created_at')
        
        return queryset


class UserSearchView(generics.ListAPIView):
    """
    Search users by username, first name, or last name.
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_serializer_class(self):
        """Import and return UserBasicSerializer."""
        from .serializers import UserBasicSerializer
        return UserBasicSerializer
    
    def get_queryset(self):
        """Search users by username and name."""
        query = self.request.GET.get('q', '').strip()
        
        if not query:
            return User.objects.none()
        
        # Search in username, first name, and last name
        queryset = User.objects.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query),
            is_active=True
        ).order_by('username')
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def global_search(request):
    """
    Global search endpoint that searches both tweets and users.
    """
    query = request.GET.get('q', '').strip()
    
    if not query:
        return Response({
            'error': 'Query parameter "q" is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Search tweets
    tweets = Tweet.objects.filter(
        Q(content__icontains=query) |
        Q(tweet_hashtags__hashtag__name__icontains=query.lstrip('#')),
        is_deleted=False
    ).distinct().select_related(
        'author', 'parent_tweet'
    ).prefetch_related(
        'media',
        'likes',
        'retweets',
        'bookmarks',
        Prefetch('tweet_hashtags__hashtag')
    ).order_by('-created_at')[:10]  # Limit to 10 results
    
    # Search users
    users = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query),
        is_active=True
    ).order_by('username')[:10]  # Limit to 10 results
    
    # Search hashtags
    hashtags = Hashtag.objects.filter(
        name__icontains=query.lstrip('#')
    ).order_by('-usage_count')[:10]  # Limit to 10 results
    
    # Serialize results
    from .serializers import UserBasicSerializer
    
    tweet_serializer = TweetSerializer(tweets, many=True, context={'request': request})
    user_serializer = UserBasicSerializer(users, many=True)
    hashtag_serializer = HashtagSerializer(hashtags, many=True)
    
    return Response({
        'query': query,
        'results': {
            'tweets': {
                'count': tweets.count(),
                'data': tweet_serializer.data
            },
            'users': {
                'count': users.count(),
                'data': user_serializer.data
            },
            'hashtags': {
                'count': hashtags.count(),
                'data': hashtag_serializer.data
            }
        }
    }, status=status.HTTP_200_OK)


class PopularTweetsView(generics.ListAPIView):
    """
    Get popular tweets based on engagement (likes + retweets + replies).
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get popular tweets ordered by engagement."""
        from django.db.models import Count, F
        from datetime import timedelta
        from django.utils import timezone
        
        # Get tweets from the last 7 days for trending
        week_ago = timezone.now() - timedelta(days=7)
        
        queryset = Tweet.objects.filter(
            is_deleted=False,
            created_at__gte=week_ago
        ).annotate(
            engagement_score=Count('likes') + Count('retweets') + Count('replies')
        ).filter(
            engagement_score__gt=0
        ).select_related(
            'author', 'parent_tweet'
        ).prefetch_related(
            'media',
            'likes',
            'retweets',
            'bookmarks',
            Prefetch('tweet_hashtags__hashtag')
        ).order_by('-engagement_score', '-created_at')
        
        return queryset


class ExploreFeedView(generics.ListAPIView):
    """
    Explore feed showing a mix of popular and recent tweets.
    """
    serializer_class = TweetSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = TweetPagination
    
    def get_queryset(self):
        """Get explore feed with mix of popular and recent tweets."""
        from django.db.models import Count
        from datetime import timedelta
        from django.utils import timezone
        
        # Get tweets from the last 3 days
        three_days_ago = timezone.now() - timedelta(days=3)
        
        # Get tweets with some engagement or very recent tweets
        queryset = Tweet.objects.filter(
            is_deleted=False,
            created_at__gte=three_days_ago
        ).annotate(
            engagement_score=Count('likes') + Count('retweets') + Count('replies')
        ).select_related(
            'author', 'parent_tweet'
        ).prefetch_related(
            'media',
            'likes',
            'retweets',
            'bookmarks',
            Prefetch('tweet_hashtags__hashtag')
        ).order_by('-engagement_score', '-created_at')
        
        return queryset


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_suggestions(request):
    """
    Get user discovery suggestions based on popular users and mutual connections.
    """
    from django.db.models import Count
    
    current_user = request.user
    
    # Get users that current user is not following
    following_ids = current_user.following.values_list('following_id', flat=True)
    excluded_ids = list(following_ids) + [current_user.id]
    
    # Get popular users (users with most followers)
    popular_users = User.objects.filter(
        is_active=True
    ).exclude(
        id__in=excluded_ids
    ).annotate(
        followers_count=Count('followers')
    ).filter(
        followers_count__gt=0
    ).order_by('-followers_count')[:10]
    
    # Get users followed by people you follow (mutual connections)
    mutual_suggestions = User.objects.filter(
        followers__follower__in=following_ids,
        is_active=True
    ).exclude(
        id__in=excluded_ids
    ).annotate(
        mutual_count=Count('followers__follower', filter=Q(followers__follower__in=following_ids))
    ).filter(
        mutual_count__gt=0
    ).order_by('-mutual_count')[:10]
    
    # Combine and deduplicate suggestions
    all_suggestions = list(popular_users) + list(mutual_suggestions)
    seen_ids = set()
    unique_suggestions = []
    
    for user in all_suggestions:
        if user.id not in seen_ids:
            unique_suggestions.append(user)
            seen_ids.add(user.id)
    
    # Limit to 15 suggestions
    suggestions = unique_suggestions[:15]
    
    # Serialize results
    from .serializers import UserBasicSerializer
    serializer = UserBasicSerializer(suggestions, many=True)
    
    return Response({
        'suggestions': serializer.data,
        'count': len(suggestions)
    }, status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def trending_content(request):
    """
    Get comprehensive trending content including hashtags, tweets, and users.
    """
    from django.db.models import Count
    from datetime import timedelta
    from django.utils import timezone
    
    # Get trending hashtags (last 24 hours)
    day_ago = timezone.now() - timedelta(days=1)
    trending_hashtags = Hashtag.objects.filter(
        tweet_hashtags__tweet__created_at__gte=day_ago,
        tweet_hashtags__tweet__is_deleted=False
    ).annotate(
        recent_usage=Count('tweet_hashtags')
    ).filter(
        recent_usage__gt=0
    ).order_by('-recent_usage')[:10]
    
    # Get trending tweets (last 3 days)
    three_days_ago = timezone.now() - timedelta(days=3)
    trending_tweets = Tweet.objects.filter(
        is_deleted=False,
        created_at__gte=three_days_ago
    ).annotate(
        engagement_score=Count('likes') + Count('retweets') + Count('replies')
    ).filter(
        engagement_score__gte=5  # Minimum engagement threshold
    ).select_related(
        'author', 'parent_tweet'
    ).prefetch_related(
        'media',
        'likes',
        'retweets',
        'bookmarks',
        Prefetch('tweet_hashtags__hashtag')
    ).order_by('-engagement_score')[:10]
    
    # Get trending users (most followed in last week)
    week_ago = timezone.now() - timedelta(days=7)
    trending_users = User.objects.filter(
        is_active=True,
        followers__created_at__gte=week_ago
    ).annotate(
        new_followers=Count('followers', filter=Q(followers__created_at__gte=week_ago))
    ).filter(
        new_followers__gt=0
    ).order_by('-new_followers')[:10]
    
    # Serialize results
    from .serializers import UserBasicSerializer
    
    hashtag_serializer = HashtagSerializer(trending_hashtags, many=True)
    tweet_serializer = TweetSerializer(trending_tweets, many=True, context={'request': request})
    user_serializer = UserBasicSerializer(trending_users, many=True)
    
    return Response({
        'trending': {
            'hashtags': {
                'count': trending_hashtags.count(),
                'data': hashtag_serializer.data
            },
            'tweets': {
                'count': trending_tweets.count(),
                'data': tweet_serializer.data
            },
            'users': {
                'count': trending_users.count(),
                'data': user_serializer.data
            }
        }
    }, status=status.HTTP_200_OK)
