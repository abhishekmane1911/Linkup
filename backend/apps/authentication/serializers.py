from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from .models import User


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Custom JWT token serializer that includes additional user information.
    """
    
    def validate(self, attrs):
        data = super().validate(attrs)
        
        # Add custom claims
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'email': self.user.email,
            'first_name': self.user.first_name,
            'last_name': self.user.last_name,
            'is_verified': self.user.is_verified,
            'profile_image': self.user.get_profile_image_url(),
        }
        
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    """
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        write_only=True,
        style={'input_type': 'password'}
    )
    
    class Meta:
        model = User
        fields = (
            'username', 'email', 'password', 'password_confirm',
            'first_name', 'last_name', 'bio', 'location', 'website',
            'birth_date', 'phone_number'
        )
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
        }
    
    def validate(self, attrs):
        """Validate password confirmation."""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': 'Password confirmation does not match.'
            })
        return attrs
    
    def validate_email(self, value):
        """Validate email uniqueness."""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError('A user with this email already exists.')
        return value
    
    def validate_username(self, value):
        """Validate username uniqueness and format."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError('A user with this username already exists.')
        
        # Username validation (alphanumeric and underscores only)
        if not value.replace('_', '').isalnum():
            raise serializers.ValidationError(
                'Username can only contain letters, numbers, and underscores.'
            )
        
        return value
    
    def create(self, validated_data):
        """Create new user with encrypted password."""
        validated_data.pop('password_confirm')
        password = validated_data.pop('password')
        
        user = User.objects.create_user(
            password=password,
            **validated_data
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile information.
    """
    full_name = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    banner_image_url = serializers.SerializerMethodField()
    followers_count = serializers.ReadOnlyField()
    following_count = serializers.ReadOnlyField()
    tweets_count = serializers.ReadOnlyField()
    is_following = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name', 'full_name',
            'bio', 'location', 'website', 'birth_date', 'phone_number',
            'profile_image', 'banner_image', 'profile_image_url', 'banner_image_url',
            'is_verified', 'is_private', 'date_joined', 'last_login',
            'followers_count', 'following_count', 'tweets_count', 'is_following'
        )
        read_only_fields = ('id', 'username', 'email', 'date_joined', 'last_login', 'is_verified',
                           'followers_count', 'following_count', 'tweets_count', 'is_following')
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()
    
    def get_banner_image_url(self, obj):
        """Get banner image URL."""
        return obj.get_banner_image_url()
    
    def get_is_following(self, obj):
        """Check if the current user is following this user."""
        request = self.context.get('request')
        if request and request.user.is_authenticated and request.user != obj:
            return obj.followers.filter(follower=request.user).exists()
        return False


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for nested representations.
    """
    full_name = serializers.ReadOnlyField()
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'full_name',
            'profile_image_url', 'is_verified'
        )
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()


class PasswordChangeSerializer(serializers.Serializer):
    """
    Serializer for password change.
    """
    old_password = serializers.CharField(style={'input_type': 'password'})
    new_password = serializers.CharField(
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(style={'input_type': 'password'})
    
    def validate_old_password(self, value):
        """Validate old password."""
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError('Old password is incorrect.')
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation."""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': 'New password confirmation does not match.'
            })
        return attrs
    
    def save(self):
        """Save new password."""
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user