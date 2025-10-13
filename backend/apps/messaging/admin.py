from django.contrib import admin
from .models import Conversation, ConversationParticipant, DirectMessage


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'participant_count', 'created_at', 'updated_at', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['participants__user__username', 'participants__user__email']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ConversationParticipant)
class ConversationParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'joined_at', 'last_read_at', 'is_active']
    list_filter = ['is_active', 'joined_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['joined_at']


@admin.register(DirectMessage)
class DirectMessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'conversation', 'content_preview', 'created_at', 'is_deleted']
    list_filter = ['is_deleted', 'created_at']
    search_fields = ['sender__username', 'content']
    readonly_fields = ['created_at', 'updated_at']
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
