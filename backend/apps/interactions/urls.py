from django.urls import path
from . import views

app_name = 'interactions'

urlpatterns = [
    # Tweet interactions
    path('tweets/<int:tweet_id>/like/', views.like_tweet, name='like_tweet'),
    path('tweets/<int:tweet_id>/retweet/', views.retweet_tweet, name='retweet_tweet'),
    path('tweets/<int:tweet_id>/bookmark/', views.bookmark_tweet, name='bookmark_tweet'),
    
    # User interactions
    path('users/<int:user_id>/follow/', views.follow_user, name='follow_user'),
    
    # User's bookmarks
    path('bookmarks/', views.user_bookmarks, name='user_bookmarks'),
]