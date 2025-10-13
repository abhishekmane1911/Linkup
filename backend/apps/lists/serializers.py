from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import List, ListMember

User = get_user_model()


class UserBasicSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for list member information.
    """
    profile_image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'profile_image_url', 'is_verified']
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()


class ListMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for ListMember model.
    """
    user = UserBasicSerializer(read_only=True)
    
    class Meta:
        model = ListMember
        fields = ['id', 'user', 'is_active', 'created_at']


class ListSerializer(serializers.ModelSerializer):
    """
    Serializer for List model with full details.
    """
    owner = UserBasicSerializer(read_only=True)
    members_count = serializers.ReadOnlyField()
    is_member = serializers.SerializerMethodField()
    can_edit = serializers.SerializerMethodField()
    
    class Meta:
        model = List
        fields = [
            'id', 'name', 'description', 'privacy', 'owner', 
            'members_count', 'is_member', 'can_edit', 
            'created_at', 'updated_at'
        ]
        read_only_fields = ['owner', 'created_at', 'updated_at']
    
    def get_is_member(self, obj):
        """Check if the current user is a member of this list."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_member(request.user)
        return False
    
    def get_can_edit(self, obj):
        """Check if the current user can edit this list."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.can_edit(request.user)
        return False
    
    def validate_name(self, value):
        """Validate list name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("List name cannot be empty.")
        
        # Check for duplicate names for the same user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            existing_lists = List.objects.filter(
                owner=request.user,
                name__iexact=value.strip(),
                is_deleted=False
            )
            
            # Exclude current instance if updating
            if self.instance:
                existing_lists = existing_lists.exclude(id=self.instance.id)
            
            if existing_lists.exists():
                raise serializers.ValidationError("You already have a list with this name.")
        
        return value.strip()
    
    def create(self, validated_data):
        """Create a new list with the current user as owner."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class ListBasicSerializer(serializers.ModelSerializer):
    """
    Basic list serializer for minimal list information.
    """
    owner = UserBasicSerializer(read_only=True)
    members_count = serializers.ReadOnlyField()
    
    class Meta:
        model = List
        fields = ['id', 'name', 'description', 'privacy', 'owner', 'members_count', 'created_at']


class ListCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating new lists.
    """
    class Meta:
        model = List
        fields = ['name', 'description', 'privacy']
    
    def validate_name(self, value):
        """Validate list name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("List name cannot be empty.")
        
        # Check for duplicate names for the same user
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            existing_lists = List.objects.filter(
                owner=request.user,
                name__iexact=value.strip(),
                is_deleted=False
            )
            
            if existing_lists.exists():
                raise serializers.ValidationError("You already have a list with this name.")
        
        return value.strip()
    
    def create(self, validated_data):
        """Create a new list with the current user as owner."""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            validated_data['owner'] = request.user
        return super().create(validated_data)


class ListUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating existing lists.
    """
    class Meta:
        model = List
        fields = ['name', 'description', 'privacy']
    
    def validate_name(self, value):
        """Validate list name."""
        if not value or len(value.strip()) == 0:
            raise serializers.ValidationError("List name cannot be empty.")
        
        # Check for duplicate names for the same user
        request = self.context.get('request')
        if request and request.user.is_authenticated and self.instance:
            existing_lists = List.objects.filter(
                owner=request.user,
                name__iexact=value.strip(),
                is_deleted=False
            ).exclude(id=self.instance.id)
            
            if existing_lists.exists():
                raise serializers.ValidationError("You already have a list with this name.")
        
        return value.strip()


class AddMemberSerializer(serializers.Serializer):
    """
    Serializer for adding members to a list.
    """
    user_id = serializers.IntegerField()
    
    def validate_user_id(self, value):
        """Validate that the user exists."""
        try:
            user = User.objects.get(id=value)
            return user
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found.")
    
    def validate(self, attrs):
        """Additional validation for adding members."""
        user = attrs['user_id']
        list_instance = self.context.get('list')
        
        if not list_instance:
            raise serializers.ValidationError("List not found.")
        
        # Check if user is already a member
        if list_instance.is_member(user):
            raise serializers.ValidationError("User is already a member of this list.")
        
        return attrs