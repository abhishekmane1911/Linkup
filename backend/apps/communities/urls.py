from django.urls import path
from . import views

app_name = 'communities'

urlpatterns = [
    # Community CRUD
    path('', views.CommunityListCreateView.as_view(), name='community-list-create'),
    path('<int:pk>/', views.CommunityDetailView.as_view(), name='community-detail'),
    
    # Community membership
    path('<int:community_id>/join/', views.join_community, name='join-community'),
    path('<int:community_id>/leave/', views.leave_community, name='leave-community'),
    path('<int:community_id>/members/', views.CommunityMembersView.as_view(), name='community-members'),
    path('<int:community_id>/members/<int:member_id>/', views.manage_member, name='manage-member'),
    
    # Role and permission management
    path('<int:community_id>/roles/', views.community_roles, name='community-roles'),
    path('<int:community_id>/members/<int:member_id>/assign-role/', views.assign_role_to_member, name='assign-role'),
    path('<int:community_id>/members/<int:member_id>/permissions/', views.member_permissions, name='member-permissions'),
    
    # Global roles and permissions
    path('roles/', views.RoleListCreateView.as_view(), name='role-list-create'),
    path('roles/<int:pk>/', views.RoleDetailView.as_view(), name='role-detail'),
    path('permissions/', views.PermissionListView.as_view(), name='permission-list'),
    
    # User communities
    path('my-communities/', views.user_communities, name='user-communities'),
    
    # Community content and feeds
    path('<int:community_id>/feed/', views.community_feed, name='community-feed'),
    path('<int:community_id>/stats/', views.community_stats, name='community-stats'),
    path('discover/', views.community_discovery, name='community-discovery'),
    path('search/', views.community_search, name='community-search'),
]