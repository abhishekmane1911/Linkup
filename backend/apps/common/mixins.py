"""
Common mixins for views and serializers.
"""
from rest_framework import status
from rest_framework.response import Response
from django.db import transaction
from .exceptions import (
    ValidationException,
    ResourceNotFoundException,
    AuthorizationException,
    BusinessLogicException
)
from .utils import (
    safe_get_object,
    safe_create_object,
    safe_update_object,
    safe_delete_object,
    create_success_response,
    log_user_action
)
import logging

logger = logging.getLogger(__name__)


class ErrorHandlingMixin:
    """
    Mixin that provides consistent error handling for views.
    """
    
    def handle_exception(self, exc):
        """
        Handle exceptions with proper logging and response formatting.
        """
        logger.error(f"Exception in {self.__class__.__name__}: {exc}", exc_info=True)
        return super().handle_exception(exc)
    
    def get_object_or_404(self, model_class, **kwargs):
        """
        Get object or raise 404 with proper error handling.
        """
        return safe_get_object(model_class, **kwargs)
    
    def check_object_permissions(self, request, obj):
        """
        Check object permissions with proper error handling.
        """
        try:
            super().check_object_permissions(request, obj)
        except Exception as e:
            raise AuthorizationException(
                message="You don't have permission to access this resource",
                code="INSUFFICIENT_PERMISSIONS"
            )


class CRUDMixin(ErrorHandlingMixin):
    """
    Mixin that provides safe CRUD operations with error handling.
    """
    
    def perform_create(self, serializer):
        """
        Create object with proper error handling and logging.
        """
        try:
            with transaction.atomic():
                instance = serializer.save()
                log_user_action(
                    user=self.request.user,
                    action='create',
                    resource_type=instance.__class__.__name__,
                    resource_id=instance.pk
                )
                return instance
        except Exception as e:
            logger.error(f"Error creating {self.get_serializer_class().Meta.model.__name__}: {e}")
            raise ValidationException(
                message="Failed to create resource",
                code="CREATION_ERROR"
            )
    
    def perform_update(self, serializer):
        """
        Update object with proper error handling and logging.
        """
        try:
            with transaction.atomic():
                instance = serializer.save()
                log_user_action(
                    user=self.request.user,
                    action='update',
                    resource_type=instance.__class__.__name__,
                    resource_id=instance.pk
                )
                return instance
        except Exception as e:
            logger.error(f"Error updating {self.get_serializer_class().Meta.model.__name__}: {e}")
            raise ValidationException(
                message="Failed to update resource",
                code="UPDATE_ERROR"
            )
    
    def perform_destroy(self, instance):
        """
        Delete object with proper error handling and logging.
        """
        try:
            with transaction.atomic():
                log_user_action(
                    user=self.request.user,
                    action='delete',
                    resource_type=instance.__class__.__name__,
                    resource_id=instance.pk
                )
                instance.delete()
        except Exception as e:
            logger.error(f"Error deleting {instance.__class__.__name__}: {e}")
            raise ValidationException(
                message="Failed to delete resource",
                code="DELETION_ERROR"
            )


class ValidationMixin:
    """
    Mixin that provides enhanced validation for serializers.
    """
    
    def validate(self, attrs):
        """
        Enhanced validation with business rule checking.
        """
        attrs = super().validate(attrs)
        
        # Perform custom validation
        self.validate_business_rules(attrs)
        
        return attrs
    
    def validate_business_rules(self, attrs):
        """
        Override this method to implement business rule validation.
        """
        pass
    
    def run_validation(self, data):
        """
        Run validation with proper error handling.
        """
        try:
            return super().run_validation(data)
        except Exception as e:
            logger.error(f"Validation error in {self.__class__.__name__}: {e}")
            raise ValidationException(
                message="Validation failed",
                code="VALIDATION_ERROR"
            )


class PermissionMixin:
    """
    Mixin that provides enhanced permission checking.
    """
    
    def check_permissions(self, request):
        """
        Check permissions with proper error handling.
        """
        try:
            super().check_permissions(request)
        except Exception as e:
            raise AuthorizationException(
                message="You don't have permission to perform this action",
                code="INSUFFICIENT_PERMISSIONS"
            )
    
    def check_object_permissions(self, request, obj):
        """
        Check object permissions with proper error handling.
        """
        try:
            super().check_object_permissions(request, obj)
        except Exception as e:
            raise AuthorizationException(
                message="You don't have permission to access this resource",
                code="INSUFFICIENT_PERMISSIONS"
            )


class ResponseMixin:
    """
    Mixin that provides standardized response formatting.
    """
    
    def create_response(self, data=None, message="Success", status_code=status.HTTP_200_OK):
        """
        Create standardized success response.
        """
        return create_success_response(data, message, status_code)
    
    def list(self, request, *args, **kwargs):
        """
        List with standardized response format.
        """
        response = super().list(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': response.data
        })
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve with standardized response format.
        """
        response = super().retrieve(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Data retrieved successfully',
            'data': response.data
        })
    
    def create(self, request, *args, **kwargs):
        """
        Create with standardized response format.
        """
        response = super().create(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Resource created successfully',
            'data': response.data
        }, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """
        Update with standardized response format.
        """
        response = super().update(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Resource updated successfully',
            'data': response.data
        })
    
    def destroy(self, request, *args, **kwargs):
        """
        Delete with standardized response format.
        """
        super().destroy(request, *args, **kwargs)
        return Response({
            'success': True,
            'message': 'Resource deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)