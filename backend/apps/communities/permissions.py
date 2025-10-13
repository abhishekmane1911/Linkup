from rest_framework import permissions
from .models import CommunityMember


class IsCommunityMember(permissions.BasePermission):
    """
    Permission to check if user is a member of the community.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # For Community objects
        if hasattr(obj, 'members'):
            return CommunityMember.objects.filter(
                community=obj,
                user=request.user,
                is_active=True
            ).exists()
        
        # For objects that have a community attribute
        if hasattr(obj, 'community'):
            return CommunityMember.objects.filter(
                community=obj.community,
                user=request.user,
                is_active=True
            ).exists()
        
        return False


class IsCommunityOwner(permissions.BasePermission):
    """
    Permission to check if user is the owner of the community.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        # For Community objects
        if hasattr(obj, 'owner'):
            return obj.owner == request.user
        
        # For objects that have a community attribute
        if hasattr(obj, 'community'):
            return obj.community.owner == request.user
        
        return False


class IsCommunityAdmin(permissions.BasePermission):
    """
    Permission to check if user is an admin or owner of the community.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        community = obj if hasattr(obj, 'members') else getattr(obj, 'community', None)
        if not community:
            return False
        
        try:
            membership = CommunityMember.objects.get(
                community=community,
                user=request.user,
                is_active=True
            )
            return membership.role in ['owner', 'admin']
        except CommunityMember.DoesNotExist:
            return False


class IsCommunityModerator(permissions.BasePermission):
    """
    Permission to check if user is a moderator, admin, or owner of the community.
    """
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        community = obj if hasattr(obj, 'members') else getattr(obj, 'community', None)
        if not community:
            return False
        
        try:
            membership = CommunityMember.objects.get(
                community=community,
                user=request.user,
                is_active=True
            )
            return membership.role in ['owner', 'admin', 'moderator']
        except CommunityMember.DoesNotExist:
            return False


class HasCommunityPermission(permissions.BasePermission):
    """
    Permission to check if user has a specific permission in the community.
    """
    
    def __init__(self, permission_codename):
        self.permission_codename = permission_codename
    
    def has_object_permission(self, request, view, obj):
        if not request.user.is_authenticated:
            return False
        
        community = obj if hasattr(obj, 'members') else getattr(obj, 'community', None)
        if not community:
            return False
        
        try:
            membership = CommunityMember.objects.get(
                community=community,
                user=request.user,
                is_active=True
            )
            return membership.has_permission(self.permission_codename)
        except CommunityMember.DoesNotExist:
            return False


def has_community_permission(permission_codename):
    """
    Factory function to create permission classes for specific permissions.
    """
    class CommunityPermission(permissions.BasePermission):
        def has_object_permission(self, request, view, obj):
            if not request.user.is_authenticated:
                return False
            
            community = obj if hasattr(obj, 'members') else getattr(obj, 'community', None)
            if not community:
                return False
            
            try:
                membership = CommunityMember.objects.get(
                    community=community,
                    user=request.user,
                    is_active=True
                )
                return membership.has_permission(permission_codename)
            except CommunityMember.DoesNotExist:
                return False
    
    return CommunityPermission


# Specific permission classes for common use cases
class CanManageCommunity(permissions.BasePermission):
    """Permission to manage community settings."""
    
    def has_object_permission(self, request, view, obj):
        return has_community_permission('manage_community')().has_object_permission(request, view, obj)


class CanManageMembers(permissions.BasePermission):
    """Permission to manage community members."""
    
    def has_object_permission(self, request, view, obj):
        return has_community_permission('manage_members')().has_object_permission(request, view, obj)


class CanModerateContent(permissions.BasePermission):
    """Permission to moderate community content."""
    
    def has_object_permission(self, request, view, obj):
        return has_community_permission('moderate_content')().has_object_permission(request, view, obj)


class CanPostContent(permissions.BasePermission):
    """Permission to post content in community."""
    
    def has_object_permission(self, request, view, obj):
        return has_community_permission('post_content')().has_object_permission(request, view, obj)


class CanManageRoles(permissions.BasePermission):
    """Permission to manage community roles."""
    
    def has_object_permission(self, request, view, obj):
        return has_community_permission('manage_roles')().has_object_permission(request, view, obj)