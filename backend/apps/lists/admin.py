from django.contrib import admin
from .models import List, ListMember


@admin.register(List)
class ListAdmin(admin.ModelAdmin):
    """
    Admin interface for List model.
    """
    list_display = ['name', 'owner', 'privacy', 'members_count', 'created_at', 'is_deleted']
    list_filter = ['privacy', 'is_deleted', 'created_at']
    search_fields = ['name', 'description', 'owner__username', 'owner__email']
    readonly_fields = ['created_at', 'updated_at', 'deleted_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'description', 'privacy')
        }),
        ('Status', {
            'fields': ('is_deleted', 'deleted_at')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def members_count(self, obj):
        """Display the number of active members in the list."""
        return obj.members_count
    members_count.short_description = 'Members'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('owner')


@admin.register(ListMember)
class ListMemberAdmin(admin.ModelAdmin):
    """
    Admin interface for ListMember model.
    """
    list_display = ['list', 'user', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'list__privacy']
    search_fields = ['list__name', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    fieldsets = (
        ('Membership', {
            'fields': ('list', 'user', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related('list', 'user')