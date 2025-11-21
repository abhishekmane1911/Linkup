from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Community, CommunityMember, Role, Permission

User = get_user_model()


class CommunityOwnerSerializer(serializers.ModelSerializer):
    """Serializer for community owner information."""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']
        read_only_fields = ['id', 'username', 'first_name', 'last_name', 'profile_image']


class CommunityMemberSerializer(serializers.ModelSerializer):
    """Serializer for community member information."""
    user = CommunityOwnerSerializer(read_only=True)
    
    class Meta:
        model = CommunityMember
        fields = ['id', 'user', 'role', 'is_active', 'joined_at']
        read_only_fields = ['id', 'joined_at']


class CommunitySerializer(serializers.ModelSerializer):
    """Serializer for Community model."""
    owner = CommunityOwnerSerializer(read_only=True)
    members_count = serializers.ReadOnlyField()
    posts_count = serializers.ReadOnlyField()
    banner_image_url = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    user_role = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'name', 'description', 'owner', 'privacy', 'banner_image',
            'banner_image_url', 'rules', 'is_active', 'created_at', 'updated_at',
            'members_count', 'posts_count', 'is_member', 'user_role'
        ]
        read_only_fields = ['id', 'owner', 'created_at', 'updated_at', 'banner_image_url']
        extra_kwargs = {
            'banner_image': {'write_only': True}
        }
    
    def get_banner_image_url(self, obj):
        """Get the banner image URL."""
        url = obj.get_banner_image_url()
        if url and not url.startswith('http'):
            # Build absolute URL if needed
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
        return url
    
    def get_is_member(self, obj):
        """Check if the current user is a member of this community."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommunityMember.objects.filter(
                community=obj,
                user=request.user,
                is_active=True
            ).exists()
        return False
    
    def get_user_role(self, obj):
        """Get the current user's role in this community."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                membership = CommunityMember.objects.get(
                    community=obj,
                    user=request.user,
                    is_active=True
                )
                return membership.role
            except CommunityMember.DoesNotExist:
                pass
        return None


class CommunityCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating communities."""
    
    class Meta:
        model = Community
        fields = ['name', 'description', 'privacy', 'banner_image', 'rules']
    
    def create(self, validated_data):
        """Create a new community and make the creator the owner."""
        request = self.context.get('request')
        validated_data['owner'] = request.user
        community = Community.objects.create(**validated_data)
        
        # Create owner membership
        CommunityMember.objects.create(
            community=community,
            user=request.user,
            role='owner'
        )
        
        return community


class CommunityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for community lists."""
    owner = CommunityOwnerSerializer(read_only=True)
    members_count = serializers.ReadOnlyField()
    banner_image_url = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()
    
    class Meta:
        model = Community
        fields = [
            'id', 'name', 'description', 'owner', 'privacy',
            'banner_image_url', 'is_active', 'created_at',
            'members_count', 'is_member'
        ]
    
    def get_banner_image_url(self, obj):
        """Get the banner image URL."""
        url = obj.get_banner_image_url()
        if url and not url.startswith('http'):
            # Build absolute URL if needed
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(url)
        return url
    
    def get_is_member(self, obj):
        """Check if the current user is a member of this community."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return CommunityMember.objects.filter(
                community=obj,
                user=request.user,
                is_active=True
            ).exists()
        return False


class JoinCommunitySerializer(serializers.Serializer):
    """Serializer for joining a community."""
    pass  # No fields needed, just the action


class CommunityMemberManagementSerializer(serializers.ModelSerializer):
    """Serializer for managing community members."""
    
    class Meta:
        model = CommunityMember
        fields = ['role', 'is_active']
    
    def validate_role(self, value):
        """Validate role changes."""
        request = self.context.get('request')
        community = self.instance.community
        
        # Check if the requesting user has permission to change roles
        try:
            requester_membership = CommunityMember.objects.get(
                community=community,
                user=request.user,
                is_active=True
            )
            
            # Only owners and admins can change roles
            if requester_membership.role not in ['owner', 'admin']:
                raise serializers.ValidationError(
                    "You don't have permission to change member roles."
                )
            
            # Owners cannot be demoted by others
            if self.instance.role == 'owner' and requester_membership.role != 'owner':
                raise serializers.ValidationError(
                    "Cannot change the role of the community owner."
                )
            
            # Only owners can assign admin role
            if value == 'admin' and requester_membership.role != 'owner':
                raise serializers.ValidationError(
                    "Only community owners can assign admin roles."
                )
                
        except CommunityMember.DoesNotExist:
            raise serializers.ValidationError(
                "You are not a member of this community."
            )
        
        return value


class PermissionSerializer(serializers.ModelSerializer):
    """Serializer for Permission model."""
    
    class Meta:
        model = Permission
        fields = ['id', 'name', 'codename', 'description']
        read_only_fields = ['id']


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for Role model."""
    permissions = PermissionSerializer(many=True, read_only=True)
    permissions_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Role
        fields = ['id', 'name', 'codename', 'description', 'permissions', 'permissions_count', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']
    
    def get_permissions_count(self, obj):
        return obj.permissions.count()


class RoleCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating custom roles."""
    permission_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = Role
        fields = ['name', 'codename', 'description', 'permission_ids']
    
    def validate_codename(self, value):
        """Ensure codename is unique and follows naming convention."""
        if Role.objects.filter(codename=value).exists():
            raise serializers.ValidationError("A role with this codename already exists.")
        
        # Ensure it's not a reserved codename
        reserved_codenames = ['community_owner', 'community_admin', 'community_moderator', 'community_member']
        if value in reserved_codenames:
            raise serializers.ValidationError("This codename is reserved for system roles.")
        
        return value
    
    def create(self, validated_data):
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role


class AssignRoleSerializer(serializers.Serializer):
    """Serializer for assigning roles to community members."""
    role_id = serializers.IntegerField(required=False, allow_null=True)
    default_role = serializers.ChoiceField(
        choices=CommunityMember.ROLE_CHOICES,
        required=False,
        allow_null=True
    )
    
    def validate(self, data):
        """Ensure either role_id or default_role is provided, but not both."""
        role_id = data.get('role_id')
        default_role = data.get('default_role')
        
        if role_id and default_role:
            raise serializers.ValidationError(
                "Cannot assign both custom role and default role."
            )
        
        if not role_id and not default_role:
            raise serializers.ValidationError(
                "Must provide either role_id or default_role."
            )
        
        # Validate role exists if role_id is provided
        if role_id:
            try:
                Role.objects.get(id=role_id)
            except Role.DoesNotExist:
                raise serializers.ValidationError("Invalid role_id.")
        
        return data