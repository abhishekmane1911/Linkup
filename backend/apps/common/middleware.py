"""
Custom middleware for security and abuse prevention.
"""
from django.core.cache import cache
from django.http import JsonResponse
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
import hashlib
import json
import logging

logger = logging.getLogger(__name__)


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request, response):
        """
        Add security headers to response.
        """
        # Prevent clickjacking
        response['X-Frame-Options'] = 'DENY'
        
        # Prevent MIME type sniffing
        response['X-Content-Type-Options'] = 'nosniff'
        
        # Enable XSS protection
        response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer policy
        response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Content Security Policy (basic)
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline';"
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log API requests for monitoring and debugging.
    """
    
    def process_request(self, request):
        """
        Log incoming requests.
        """
        # Skip logging for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Log request details
        logger.info(
            f"API Request: {request.method} {request.path}",
            extra={
                'method': request.method,
                'path': request.path,
                'user_id': request.user.id if hasattr(request, 'user') and request.user.is_authenticated else None,
                'ip_address': self.get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'timestamp': timezone.now().isoformat()
            }
        )
        
        return None
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AbusePreventionMiddleware(MiddlewareMixin):
    """
    Middleware to detect and prevent various forms of abuse.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.suspicious_patterns = [
            # Patterns that might indicate bot activity
            'bot', 'crawler', 'spider', 'scraper',
            # Common attack tools
            'sqlmap', 'nikto', 'nmap', 'burp'
        ]
        super().__init__(get_response)
    
    def process_request(self, request):
        """
        Check for suspicious activity patterns.
        """
        # Check user agent for suspicious patterns
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        if any(pattern in user_agent for pattern in self.suspicious_patterns):
            logger.warning(
                f"Suspicious user agent detected: {user_agent}",
                extra={
                    'ip_address': self.get_client_ip(request),
                    'user_agent': user_agent,
                    'path': request.path
                }
            )
            # Could block the request here if needed
            # return JsonResponse({'error': 'Access denied'}, status=403)
        
        # Check for rapid requests from same IP
        ip_address = self.get_client_ip(request)
        if self.is_rapid_requests(ip_address):
            logger.warning(
                f"Rapid requests detected from IP: {ip_address}",
                extra={
                    'ip_address': ip_address,
                    'path': request.path
                }
            )
            # Could implement temporary IP blocking here
        
        return None
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_rapid_requests(self, ip_address):
        """
        Check if IP is making rapid requests.
        """
        cache_key = f"rapid_requests:{hashlib.md5(ip_address.encode()).hexdigest()}"
        current_count = cache.get(cache_key, 0)
        
        # Allow up to 10 requests per minute from same IP
        if current_count > 10:
            return True
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 60)  # 1 minute timeout
        return False


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning.
    """
    
    def process_request(self, request):
        """
        Add API version to request.
        """
        # Default to v1 if no version specified
        if request.path.startswith('/api/'):
            if not any(request.path.startswith(f'/api/v{i}/') for i in range(1, 10)):
                # No version specified, redirect to v1
                request.path_info = request.path.replace('/api/', '/api/v1/', 1)
        
        return None


class MaintenanceModeMiddleware(MiddlewareMixin):
    """
    Middleware to handle maintenance mode.
    """
    
    def process_request(self, request):
        """
        Check if site is in maintenance mode.
        """
        maintenance_mode = getattr(settings, 'MAINTENANCE_MODE', False)
        
        if maintenance_mode:
            # Allow access to admin and superusers
            if (request.path.startswith('/admin/') or 
                (hasattr(request, 'user') and request.user.is_authenticated and request.user.is_superuser)):
                return None
            
            # Return maintenance response for all other requests
            return JsonResponse({
                'error': {
                    'code': 'MAINTENANCE_MODE',
                    'message': 'The service is currently under maintenance. Please try again later.',
                    'timestamp': timezone.now().isoformat()
                }
            }, status=503)
        
        return None


class CORSMiddleware(MiddlewareMixin):
    """
    Custom CORS middleware with enhanced security.
    """
    
    def process_response(self, request, response):
        """
        Add CORS headers with security considerations.
        """
        # Only add CORS headers for API endpoints
        if request.path.startswith('/api/'):
            origin = request.META.get('HTTP_ORIGIN')
            
            # Check if origin is allowed
            allowed_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
            
            if origin in allowed_origins:
                response['Access-Control-Allow-Origin'] = origin
                response['Access-Control-Allow-Credentials'] = 'true'
                response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                response['Access-Control-Allow-Headers'] = 'Accept, Authorization, Content-Type, X-CSRFToken'
                response['Access-Control-Max-Age'] = '86400'  # 24 hours
        
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Global rate limiting middleware as a fallback.
    """
    
    def process_request(self, request):
        """
        Apply global rate limiting.
        """
        # Skip for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        # Get client identifier
        if hasattr(request, 'user') and request.user.is_authenticated:
            identifier = f"user:{request.user.id}"
        else:
            identifier = f"ip:{self.get_client_ip(request)}"
        
        # Check global rate limit
        cache_key = f"global_rate_limit:{hashlib.md5(identifier.encode()).hexdigest()}"
        current_count = cache.get(cache_key, 0)
        
        # Global limit: 1000 requests per hour
        if current_count > 1000:
            logger.warning(
                f"Global rate limit exceeded for {identifier}",
                extra={
                    'identifier': identifier,
                    'count': current_count,
                    'path': request.path
                }
            )
            return JsonResponse({
                'error': {
                    'code': 'GLOBAL_RATE_LIMIT_EXCEEDED',
                    'message': 'Global rate limit exceeded. Please try again later.',
                    'timestamp': timezone.now().isoformat()
                }
            }, status=429)
        
        # Increment counter
        cache.set(cache_key, current_count + 1, 3600)  # 1 hour timeout
        return None
    
    def get_client_ip(self, request):
        """
        Get client IP address from request.
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip