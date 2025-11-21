from django.urls import path
from . import views

app_name = 'tweets'

urlpatterns = [
    # Tweet CRUD operations
    path('', views.TweetListCreateView.as_view(), name='tweet-list-create'),
    path('<int:id>/', views.TweetDetailView.as_view(), name='tweet-detail'),
    path('<int:tweet_id>/stats/', views.tweet_stats, name='tweet-stats'),
    
    # Feed endpoints
    path('feed/home/', views.HomeTimelineFeedView.as_view(), name='home-timeline-feed'),
    path('feed/explore/', views.ExploreFeedView.as_view(), name='explore-feed'),
    path('feed/popular/', views.PopularTweetsView.as_view(), name='popular-tweets'),
    
    # Search endpoints
    path('search/', views.TweetSearchView.as_view(), name='tweet-search'),
    path('search/users/', views.UserSearchView.as_view(), name='user-search'),
    path('search/global/', views.global_search, name='global-search'),
    
    # Discovery endpoints
    path('discover/users/', views.user_suggestions, name='user-suggestions'),
    path('discover/trending/', views.trending_content, name='trending-content'),
    
    # User tweets
    path('user/<int:user_id>/', views.UserTweetsView.as_view(), name='user-tweets'),
    path('user/<int:user_id>/replies/', views.UserRepliesView.as_view(), name='user-replies'),
    path('user/<int:user_id>/media/', views.UserMediaView.as_view(), name='user-media'),
    path('user/<int:user_id>/likes/', views.UserLikesView.as_view(), name='user-likes'),
    path('user/<int:user_id>/retweets/', views.UserRetweetsView.as_view(), name='user-retweets'),
    
    # Tweet replies and threading
    path('<int:tweet_id>/replies/', views.TweetRepliesView.as_view(), name='tweet-replies'),
    path('<int:id>/thread/', views.TweetThreadView.as_view(), name='tweet-thread'),
    path('<int:tweet_id>/conversation/', views.tweet_conversation, name='tweet-conversation'),
    
    # Hashtag-related endpoints
    path('hashtags/<str:hashtag_name>/', views.HashtagTweetsView.as_view(), name='hashtag-tweets'),
    path('hashtags/trending/', views.TrendingHashtagsView.as_view(), name='trending-hashtags'),
    path('hashtags/search/', views.hashtag_search, name='hashtag-search'),
]