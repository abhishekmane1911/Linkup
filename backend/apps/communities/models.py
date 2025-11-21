from django.db import models
from django.conf import settings
from django.core.validators import MinLengthValidator
from django.utils import timezone


class Community(models.Model):
    """
    Model representing a community where users can gather around specific topics.
    """
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    name = models.CharField(
        max_length=100,
        unique=True,
        validators=[MinLengthValidator(3)],
        help_text="Community name (3-100 characters)"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        help_text="Community description"
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_communities',
        help_text="Community owner"
    )
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='public',
        help_text="Community privacy setting"
    )
    banner_image = models.ImageField(
        upload_to='community_banners/',
        blank=True,
        null=True,
        help_text="Community banner image"
    )
    rules = models.TextField(
        blank=True,
        null=True,
        help_text="Community rules and guidelines"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the community is active"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communities_community'
        verbose_name = 'Community'
        verbose_name_plural = 'Communities'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def members_count(self):
        """Get the count of community members."""
        return self.members.filter(is_active=True).count()
    
    @property
    def posts_count(self):
        """Get the count of posts in this community."""
        return self.tweets.filter(is_deleted=False).count()
    
    def get_banner_image_url(self):
        """Return banner image URL or None."""
        if self.banner_image:
            try:
                return self.banner_image.url
            except ValueError:
                # Handle case where file doesn't exist
                return None
        return None


class CommunityMember(models.Model):
    """
    Model representing membership of users in communities.
    """
    ROLE_CHOICES = [
        ('member', 'Member'),
        ('moderator', 'Moderator'),
        ('admin', 'Admin'),
        ('owner', 'Owner'),
    ]
    
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='members'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='community_memberships'
    )
    role = models.CharField(
        max_length=10,
        choices=ROLE_CHOICES,
        default='member'
    )
    custom_role = models.ForeignKey(
        'Role',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text="Custom role with specific permissions"
    )
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communities_communitymember'
        verbose_name = 'Community Member'
        verbose_name_plural = 'Community Members'
        unique_together = ['community', 'user']
        ordering = ['-joined_at']
    
    def __str__(self):
        return f"{self.user.username} in {self.community.name} ({self.get_effective_role()})"
    
    def get_effective_role(self):
        """Get the effective role name (custom role or default role)."""
        if self.custom_role:
            return self.custom_role.name
        return self.get_role_display()
    
    def has_permission(self, permission_codename):
        """Check if the member has a specific permission."""
        # Check custom role permissions first
        if self.custom_role:
            return self.custom_role.has_permission(permission_codename)
        
        # Fall back to default role permissions
        default_role_permissions = {
            'owner': [
                'manage_community', 'manage_members', 'manage_roles',
                'moderate_content', 'post_content', 'delete_posts',
                'ban_members', 'view_reports'
            ],
            'admin': [
                'manage_members', 'manage_roles', 'moderate_content',
                'post_content', 'delete_posts', 'ban_members', 'view_reports'
            ],
            'moderator': [
                'moderate_content', 'post_content', 'delete_posts', 'view_reports'
            ],
            'member': ['post_content'],
        }
        return permission_codename in default_role_permissions.get(self.role, [])


class Permission(models.Model):
    """
    Model representing permissions that can be assigned to community roles.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Permission name"
    )
    codename = models.CharField(
        max_length=50,
        unique=True,
        help_text="Permission codename for programmatic use"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Permission description"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'communities_permission'
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Model representing roles within communities with specific permissions.
    """
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Role name"
    )
    codename = models.CharField(
        max_length=50,
        unique=True,
        help_text="Role codename for programmatic use"
    )
    description = models.TextField(
        blank=True,
        null=True,
        help_text="Role description"
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        related_name='roles',
        help_text="Permissions assigned to this role"
    )
    is_default = models.BooleanField(
        default=False,
        help_text="Whether this is a default system role"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'communities_role'
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    def has_permission(self, permission_codename):
        """Check if this role has a specific permission."""
        return self.permissions.filter(codename=permission_codename).exists()


class CommunityRole(models.Model):
    """
    Model representing custom roles within specific communities.
    """
    community = models.ForeignKey(
        Community,
        on_delete=models.CASCADE,
        related_name='custom_roles'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='community_assignments'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'communities_communityrole'
        verbose_name = 'Community Role'
        verbose_name_plural = 'Community Roles'
        unique_together = ['community', 'role']
    
    def __str__(self):
        return f"{self.role.name} in {self.community.name}"
