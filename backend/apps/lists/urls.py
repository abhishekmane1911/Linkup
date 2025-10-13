from django.urls import path
from . import views

app_name = 'lists'

urlpatterns = [
    # List CRUD operations
    path('', views.ListListCreateView.as_view(), name='list-list-create'),
    path('<int:id>/', views.ListDetailView.as_view(), name='list-detail'),
    
    # List member management
    path('<int:list_id>/members/', views.ListMembersView.as_view(), name='list-members'),
    path('<int:list_id>/members/add/', views.add_member_to_list, name='add-member'),
    path('<int:list_id>/members/<int:user_id>/remove/', views.remove_member_from_list, name='remove-member'),
    
    # List timeline functionality
    path('<int:list_id>/timeline/', views.ListTimelineView.as_view(), name='list-timeline'),
    
    # List discovery
    path('public/', views.PublicListsView.as_view(), name='public-lists'),
    path('users/<int:user_id>/', views.UserListsView.as_view(), name='user-lists'),
    path('discover/', views.list_discovery, name='list-discovery'),
    path('suggestions/', views.list_suggestions, name='list-suggestions'),
    
    # User search for adding to lists
    path('search-users/', views.search_users_for_list, name='search-users'),
]