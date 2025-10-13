from django.urls import path
from . import views

app_name = 'messaging'

urlpatterns = [
    # Conversation endpoints
    path('conversations/', views.ConversationListView.as_view(), name='conversation-list'),
    path('conversations/<int:pk>/', views.ConversationDetailView.as_view(), name='conversation-detail'),
    path('conversations/<int:conversation_id>/messages/', views.ConversationMessagesView.as_view(), name='conversation-messages'),
    path('conversations/<int:conversation_id>/messages/create/', views.ConversationMessageCreateView.as_view(), name='conversation-message-create'),
    path('conversations/<int:conversation_id>/mark-read/', views.mark_conversation_read, name='conversation-mark-read'),
    path('conversations/<int:conversation_id>/metadata/', views.conversation_metadata, name='conversation-metadata'),
    path('conversations/<int:conversation_id>/participants/', views.ConversationParticipantManagementView.as_view(), name='conversation-participants'),
    
    # Direct message endpoints
    path('messages/create/', views.DirectMessageCreateView.as_view(), name='message-create'),
    path('messages/<int:message_id>/delete/', views.delete_message, name='message-delete'),
    
    # Privacy and utility endpoints
    path('privacy/check/<int:user_id>/', views.check_messaging_privacy, name='messaging-privacy-check'),
]