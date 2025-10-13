from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MaxLengthValidator
from django.utils import timezone

User = get_user_model()


class List(models.Model):
    """
    List model for user-created lists to organize and follow specific groups of accounts.
    """
    PRIVACY_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_lists',
        help_text="The user who created and owns this list"
    )
    name = models.CharField(
        max_length=100,
        validators=[MaxLengthValidator(100, "List name cannot exceed 100 characters")],
        help_text="Name of the list"
    )
    description = models.TextField(
        max_length=500,
        blank=True,
        null=True,
        validators=[MaxLengthValidator(500, "List description cannot exceed 500 characters")],
        help_text="Optional description of the list"
    )
    privacy = models.CharField(
        max_length=10,
        choices=PRIVACY_CHOICES,
        default='public',
        help_text="Privacy setting for the list"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Soft delete functionality
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'lists'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['owner', '-created_at']),
            models.Index(fields=['privacy']),
            models.Index(fields=['is_deleted']),
            models.Index(fields=['name']),
        ]
        unique_together = ['owner', 'name']  # User cannot have duplicate list names
    
    def __str__(self):
        return f"{self.name} by @{self.owner.username}"
    
    def save(self, *args, **kwargs):
        """Override save to handle validation and timestamps."""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("List name cannot be empty")
        
        # Update timestamp on edit
        if self.pk:
            self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)
    
    def soft_delete(self):
        """Soft delete the list."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save(update_fields=['is_deleted', 'deleted_at'])
    
    def is_public(self):
        """Check if the list is public."""
        return self.privacy == 'public'
    
    def is_private(self):
        """Check if the list is private."""
        return self.privacy == 'private'
    
    def can_view(self, user):
        """Check if a user can view this list."""
        if self.is_deleted:
            return False
        
        # Owner can always view
        if self.owner == user:
            return True
        
        # Public lists can be viewed by anyone
        if self.is_public():
            return True
        
        # Private lists can only be viewed by owner
        return False
    
    def can_edit(self, user):
        """Check if a user can edit this list."""
        if self.is_deleted:
            return False
        
        # Only owner can edit
        return self.owner == user
    
    @property
    def members_count(self):
        """Get the count of members in this list."""
        return self.members.filter(is_active=True).count()
    
    def get_members(self):
        """Get all active members of this list."""
        return User.objects.filter(
            list_memberships__list=self,
            list_memberships__is_active=True
        ).order_by('list_memberships__created_at')
    
    def add_member(self, user):
        """Add a user to this list."""
        list_member, created = ListMember.objects.get_or_create(
            list=self,
            user=user,
            defaults={'is_active': True}
        )
        
        # If member was previously removed, reactivate them
        if not created and not list_member.is_active:
            list_member.is_active = True
            list_member.save(update_fields=['is_active', 'updated_at'])
        
        return list_member, created
    
    def remove_member(self, user):
        """Remove a user from this list."""
        try:
            list_member = ListMember.objects.get(list=self, user=user)
            list_member.is_active = False
            list_member.save(update_fields=['is_active', 'updated_at'])
            return True
        except ListMember.DoesNotExist:
            return False
    
    def is_member(self, user):
        """Check if a user is a member of this list."""
        return ListMember.objects.filter(
            list=self,
            user=user,
            is_active=True
        ).exists()


class ListMember(models.Model):
    """
    Through model for List-User many-to-many relationship representing list membership.
    """
    list = models.ForeignKey(
        List,
        on_delete=models.CASCADE,
        related_name='members',
        help_text="The list this membership belongs to"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='list_memberships',
        help_text="The user who is a member of the list"
    )
    
    # Membership status
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this membership is currently active"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'list_members'
        unique_together = ['list', 'user']
        indexes = [
            models.Index(fields=['list', 'is_active']),
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        status = "active" if self.is_active else "inactive"
        return f"@{self.user.username} in '{self.list.name}' ({status})"
    
    def save(self, *args, **kwargs):
        """Override save to handle timestamps."""
        if self.pk:
            self.updated_at = timezone.now()
        
        super().save(*args, **kwargs)