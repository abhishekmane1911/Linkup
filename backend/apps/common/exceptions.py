"""
Custom exception classes for the Linkup backend.
"""
from rest_framework import status
from rest_framework.views import exception_handler
from rest_framework.response import Response
from django.utils import timezone
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import Http404
from django.db import IntegrityError
import logging

logger = logging.getLogger(__name__)


class LinkupException(Exception):
    """Base exception class for Linkup-specific errors."""
    default_message = "An error occurred"
    default_code = "LINKUP_ERROR"
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self, message=None, code=None, status_code=None):
        self.message = message or self.default_message
        self.code = code or self.default_code
        self.status_code = status_code or self.status_code
        super().__init__(self.message)


class ValidationException(LinkupException):
    """Exception for validation errors."""
    default_message = "Validation failed"
    default_code = "VALIDATION_ERROR"
    status_code = status.HTTP_400_BAD_REQUEST


class AuthenticationException(LinkupException):
    """Exception for authentication errors."""
    default_message = "Authentication failed"
    default_code = "AUTHENTICATION_ERROR"
    status_code = status.HTTP_401_UNAUTHORIZED


class AuthorizationException(LinkupException):
    """Exception for authorization errors."""
    default_message = "Permission denied"
    default_code = "AUTHORIZATION_ERROR"
    status_code = status.HTTP_403_FORBIDDEN


class ResourceNotFoundException(LinkupException):
    """Exception for resource not found errors."""
    default_message = "Resource not found"
    default_code = "RESOURCE_NOT_FOUND"
    status_code = status.HTTP_404_NOT_FOUND


class ConflictException(LinkupException):
    """Exception for conflict errors."""
    default_message = "Resource conflict"
    default_code = "CONFLICT_ERROR"
    status_code = status.HTTP_409_CONFLICT


class RateLimitException(LinkupException):
    """Exception for rate limiting errors."""
    default_message = "Rate limit exceeded"
    default_code = "RATE_LIMIT_EXCEEDED"
    status_code = status.HTTP_429_TOO_MANY_REQUESTS


class BusinessLogicException(LinkupException):
    """Exception for business logic violations."""
    default_message = "Business rule violation"
    default_code = "BUSINESS_LOGIC_ERROR"
    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY


def get_error_code(exc):
    """Get error code from exception."""
    if hasattr(exc, 'code'):
        return exc.code
    elif isinstance(exc, DjangoValidationError):
        return "VALIDATION_ERROR"
    elif isinstance(exc, Http404):
        return "RESOURCE_NOT_FOUND"
    elif isinstance(exc, IntegrityError):
        return "DATA_INTEGRITY_ERROR"
    elif isinstance(exc, PermissionError):
        return "AUTHORIZATION_ERROR"
    else:
        return "INTERNAL_SERVER_ERROR"


def get_error_message(exc):
    """Get error message from exception."""
    if hasattr(exc, 'message'):
        return exc.message
    elif hasattr(exc, 'detail'):
        return str(exc.detail)
    else:
        return str(exc)


def custom_exception_handler(exc, context):
    """
    Custom exception handler that returns standardized error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # Log the exception
    logger.error(f"Exception occurred: {exc}", exc_info=True, extra={
        'request': context.get('request'),
        'view': context.get('view'),
    })
    
    # Handle custom Linkup exceptions
    if isinstance(exc, LinkupException):
        custom_response_data = {
            'error': {
                'code': exc.code,
                'message': exc.message,
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        return Response(custom_response_data, status=exc.status_code)
    
    # Handle Django validation errors
    elif isinstance(exc, DjangoValidationError):
        custom_response_data = {
            'error': {
                'code': 'VALIDATION_ERROR',
                'message': 'Validation failed',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)],
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        return Response(custom_response_data, status=status.HTTP_400_BAD_REQUEST)
    
    # Handle database integrity errors
    elif isinstance(exc, IntegrityError):
        custom_response_data = {
            'error': {
                'code': 'DATA_INTEGRITY_ERROR',
                'message': 'Data integrity constraint violation',
                'details': str(exc),
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        return Response(custom_response_data, status=status.HTTP_409_CONFLICT)
    
    # Handle 404 errors
    elif isinstance(exc, Http404):
        custom_response_data = {
            'error': {
                'code': 'RESOURCE_NOT_FOUND',
                'message': 'The requested resource was not found',
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        return Response(custom_response_data, status=status.HTTP_404_NOT_FOUND)
    
    # Handle DRF exceptions with custom format
    elif response is not None:
        custom_response_data = {
            'error': {
                'code': get_error_code(exc),
                'message': get_error_message(exc),
                'details': response.data,
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        response.data = custom_response_data
        return response
    
    # Handle unexpected errors
    else:
        custom_response_data = {
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': 'An unexpected error occurred',
                'timestamp': timezone.now().isoformat(),
                'path': context['request'].path if context.get('request') else None
            }
        }
        return Response(custom_response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)