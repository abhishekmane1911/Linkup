from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator


class User(AbstractUser):
    """
    Custom User model extending AbstractUser with additional fields for social media platform.
    """
    email = models.EmailField(unique=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    # Profile images
    profile_image = models.ImageField(
        upload_to='profile_images/', 
        blank=True, 
        null=True,
        help_text="Profile picture"
    )
    banner_image = models.ImageField(
        upload_to='banner_images/', 
        blank=True, 
        null=True,
        help_text="Profile banner image"
    )
    
    # Social media specific fields
    is_verified = models.BooleanField(default=False)
    is_private = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Phone number with validation
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone_number = models.CharField(
        validators=[phone_regex], 
        max_length=17, 
        blank=True, 
        null=True
    )
    
    # Make email the username field
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"@{self.username}"
    
    @property
    def full_name(self):
        """Return the user's full name."""
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    def get_profile_image_url(self):
        """Return profile image URL or None."""
        if self.profile_image:
            try:
                return self.profile_image.url
            except ValueError:
                # Handle case where file doesn't exist
                return None
        return None
    
    def get_banner_image_url(self):
        """Return banner image URL or None."""
        if self.banner_image:
            try:
                return self.banner_image.url
            except ValueError:
                # Handle case where file doesn't exist
                return None
        return None
    
    @property
    def followers_count(self):
        """Get the count of followers."""
        return self.followers.count()
    
    @property
    def following_count(self):
        """Get the count of users this user is following."""
        return self.following.count()
    
    @property
    def tweets_count(self):
        """Get the count of tweets by this user."""
        return self.tweets.filter(is_deleted=False).count()
