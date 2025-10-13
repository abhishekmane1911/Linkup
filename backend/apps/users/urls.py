from django.urls import path
from . import views

app_name = 'users'

urlpatterns = [
    # User profile and relationships
    path('<int:user_id>/', views.user_profile, name='user_profile'),
    path('<int:user_id>/followers/', views.user_followers, name='user_followers'),
    path('<int:user_id>/following/', views.user_following, name='user_following'),
    
    # User search
    path('search/', views.search_users, name='search_users'),
]