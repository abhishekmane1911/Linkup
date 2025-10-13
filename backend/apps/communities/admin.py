from django.contrib import admin
from .models import Community, CommunityMember, Role, Permission, CommunityRole


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'privacy', 'is_active', 'members_count', 'created_at']
    list_filter = ['privacy', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at', 'members_count', 'posts_count']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'description', 'owner', 'privacy')
        }),
        ('Media', {
            'fields': ('banner_image',)
        }),
        ('Settings', {
            'fields': ('rules', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('members_count', 'posts_count'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunityMember)
class CommunityMemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'community', 'role', 'is_active', 'joined_at']
    list_filter = ['role', 'is_active', 'joined_at']
    search_fields = ['user__username', 'community__name']
    readonly_fields = ['joined_at', 'updated_at']
    
    fieldsets = (
        (None, {
            'fields': ('community', 'user', 'role', 'custom_role', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('joined_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'created_at']
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'codename', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['name', 'codename', 'is_default', 'permissions_count', 'created_at']
    list_filter = ['is_default', 'created_at']
    search_fields = ['name', 'codename', 'description']
    readonly_fields = ['created_at', 'updated_at', 'permissions_count']
    filter_horizontal = ['permissions']
    
    def permissions_count(self, obj):
        return obj.permissions.count()
    permissions_count.short_description = 'Permissions Count'
    
    fieldsets = (
        (None, {
            'fields': ('name', 'codename', 'description', 'is_default')
        }),
        ('Permissions', {
            'fields': ('permissions',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('permissions_count',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CommunityRole)
class CommunityRoleAdmin(admin.ModelAdmin):
    list_display = ['community', 'role', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['community__name', 'role__name']
    readonly_fields = ['created_at']
    
    fieldsets = (
        (None, {
            'fields': ('community', 'role', 'is_active')
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
