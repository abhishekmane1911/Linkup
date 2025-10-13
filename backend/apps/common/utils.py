"""
Utility functions for the Linkup backend.
"""
from django.core.exceptions import ValidationError
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from .exceptions import (
    ValidationException, 
    ResourceNotFoundException, 
    ConflictException,
    BusinessLogicException
)
import logging

logger = logging.getLogger(__name__)


def handle_validation_error(func):
    """
    Decorator to handle validation errors and convert them to custom exceptions.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            raise ValidationException(
                message=str(e),
                code="VALIDATION_ERROR"
            )
    return wrapper


def safe_get_object(model_class, **kwargs):
    """
    Safely get an object or raise ResourceNotFoundException.
    """
    try:
        return model_class.objects.get(**kwargs)
    except model_class.DoesNotExist:
        raise ResourceNotFoundException(
            message=f"{model_class.__name__} not found",
            code="RESOURCE_NOT_FOUND"
        )


def safe_create_object(model_class, **kwargs):
    """
    Safely create an object with proper error handling.
    """
    try:
        with transaction.atomic():
            return model_class.objects.create(**kwargs)
    except ValidationError as e:
        raise ValidationException(
            message=str(e),
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"Error creating {model_class.__name__}: {e}")
        raise ConflictException(
            message=f"Could not create {model_class.__name__}",
            code="CREATION_ERROR"
        )


def safe_update_object(instance, **kwargs):
    """
    Safely update an object with proper error handling.
    """
    try:
        with transaction.atomic():
            for key, value in kwargs.items():
                setattr(instance, key, value)
            instance.full_clean()
            instance.save()
            return instance
    except ValidationError as e:
        raise ValidationException(
            message=str(e),
            code="VALIDATION_ERROR"
        )
    except Exception as e:
        logger.error(f"Error updating {instance.__class__.__name__}: {e}")
        raise ConflictException(
            message=f"Could not update {instance.__class__.__name__}",
            code="UPDATE_ERROR"
        )


def safe_delete_object(instance):
    """
    Safely delete an object with proper error handling.
    """
    try:
        with transaction.atomic():
            instance.delete()
    except Exception as e:
        logger.error(f"Error deleting {instance.__class__.__name__}: {e}")
        raise ConflictException(
            message=f"Could not delete {instance.__class__.__name__}",
            code="DELETION_ERROR"
        )


def validate_business_rule(condition, message, code="BUSINESS_RULE_VIOLATION"):
    """
    Validate a business rule and raise BusinessLogicException if violated.
    """
    if not condition:
        raise BusinessLogicException(
            message=message,
            code=code
        )


def create_success_response(data=None, message="Success", status_code=status.HTTP_200_OK):
    """
    Create a standardized success response.
    """
    response_data = {
        "success": True,
        "message": message,
        "data": data
    }
    return Response(response_data, status=status_code)


def create_error_response(message, code="ERROR", status_code=status.HTTP_400_BAD_REQUEST, details=None):
    """
    Create a standardized error response.
    """
    response_data = {
        "error": {
            "code": code,
            "message": message,
            "details": details
        }
    }
    return Response(response_data, status=status_code)


def paginate_queryset(queryset, request, paginator_class=None):
    """
    Paginate a queryset with proper error handling.
    """
    from rest_framework.pagination import PageNumberPagination
    
    if paginator_class is None:
        paginator_class = PageNumberPagination
    
    paginator = paginator_class()
    try:
        page = paginator.paginate_queryset(queryset, request)
        return page, paginator
    except Exception as e:
        logger.error(f"Pagination error: {e}")
        raise ValidationException(
            message="Invalid pagination parameters",
            code="PAGINATION_ERROR"
        )


def check_object_permissions(user, obj, permission):
    """
    Check if user has permission for an object.
    """
    if not user.has_perm(permission, obj):
        from .exceptions import AuthorizationException
        raise AuthorizationException(
            message=f"You don't have permission to {permission} this resource",
            code="INSUFFICIENT_PERMISSIONS"
        )


def log_user_action(user, action, resource_type, resource_id=None, details=None):
    """
    Log user actions for audit purposes.
    """
    logger.info(
        f"User action: {user.username} performed {action} on {resource_type}",
        extra={
            'user_id': user.id,
            'username': user.username,
            'action': action,
            'resource_type': resource_type,
            'resource_id': resource_id,
            'details': details
        }
    )