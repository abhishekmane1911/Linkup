"""
Custom throttling classes for the Linkup backend.
"""
from rest_framework.throttling import UserRateThrottle, AnonRateThrottle
from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
import hashlib


class AuthenticationThrottle(UserRateThrottle):
    """
    Throttle for authentication endpoints (login, register, password reset).
    More restrictive to prevent brute force attacks.
    """
    scope = 'auth'
    rate = '5/min'  # 5 attempts per minute


class SocialActionThrottle(UserRateThrottle):
    """
    Throttle for social actions (like, retweet, follow).
    Prevents spam and abuse.
    """
    scope = 'social'
    rate = '100/hour'  # 100 social actions per hour


class TweetCreationThrottle(UserRateThrottle):
    """
    Throttle for tweet creation.
    Prevents spam posting.
    """
    scope = 'tweet_create'
    rate = '50/hour'  # 50 tweets per hour


class MessageThrottle(UserRateThrottle):
    """
    Throttle for direct messages.
    Prevents message spam.
    """
    scope = 'message'
    rate = '200/hour'  # 200 messages per hour


class SearchThrottle(UserRateThrottle):
    """
    Throttle for search endpoints.
    Prevents search abuse.
    """
    scope = 'search'
    rate = '300/hour'  # 300 searches per hour


class FileUploadThrottle(UserRateThrottle):
    """
    Throttle for file uploads.
    Prevents upload abuse.
    """
    scope = 'upload'
    rate = '20/hour'  # 20 uploads per hour


class BurstThrottle(UserRateThrottle):
    """
    Short-term burst protection.
    Prevents rapid-fire requests.
    """
    scope = 'burst'
    rate = '60/min'  # 60 requests per minute


class SustainedThrottle(UserRateThrottle):
    """
    Long-term sustained usage throttle.
    Prevents sustained abuse.
    """
    scope = 'sustained'
    rate = '10000/day'  # 10,000 requests per day


class IPBasedThrottle(AnonRateThrottle):
    """
    IP-based throttling for anonymous users.
    """
    scope = 'anon_ip'
    rate = '100/hour'  # 100 requests per hour per IP


class CustomUserRateThrottle(UserRateThrottle):
    """
    Custom user rate throttle with enhanced features.
    """
    
    def get_cache_key(self, request, view):
        """
        Create cache key based on user and endpoint.
        """
        if request.user.is_authenticated:
            ident = request.user.pk
        else:
            ident = self.get_ident(request)
        
        # Include view name in cache key for endpoint-specific throttling
        view_name = getattr(view, 'throttle_scope', self.scope)
        return self.cache_format % {
            'scope': view_name,
            'ident': ident
        }
    
    def allow_request(self, request, view):
        """
        Enhanced allow_request with custom logic.
        """
        # Skip throttling for superusers
        if request.user.is_authenticated and request.user.is_superuser:
            return True
        
        return super().allow_request(request, view)


class FailedLoginThrottle:
    """
    Custom throttle for failed login attempts.
    Implements progressive delays for repeated failures.
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
    
    def get_cache_key(self, identifier):
        """
        Get cache key for failed login attempts.
        """
        return f"failed_login:{hashlib.md5(identifier.encode()).hexdigest()}"
    
    def is_allowed(self, identifier):
        """
        Check if login attempt is allowed.
        """
        cache_key = self.get_cache_key(identifier)
        failed_attempts = cache.get(cache_key, 0)
        
        # Progressive delays: 1min, 5min, 15min, 30min, 1hour
        delay_minutes = [1, 5, 15, 30, 60]
        
        if failed_attempts >= len(delay_minutes):
            # Max delay reached
            return False
        
        if failed_attempts > 0:
            # Check if delay period has passed
            last_attempt_key = f"{cache_key}:last_attempt"
            last_attempt = cache.get(last_attempt_key)
            
            if last_attempt:
                delay = timedelta(minutes=delay_minutes[failed_attempts - 1])
                if timezone.now() - last_attempt < delay:
                    return False
        
        return True
    
    def record_failure(self, identifier):
        """
        Record a failed login attempt.
        """
        cache_key = self.get_cache_key(identifier)
        failed_attempts = cache.get(cache_key, 0) + 1
        
        cache.set(cache_key, failed_attempts, self.cache_timeout)
        cache.set(f"{cache_key}:last_attempt", timezone.now(), self.cache_timeout)
        
        return failed_attempts
    
    def clear_failures(self, identifier):
        """
        Clear failed login attempts (on successful login).
        """
        cache_key = self.get_cache_key(identifier)
        cache.delete(cache_key)
        cache.delete(f"{cache_key}:last_attempt")


class SuspiciousActivityThrottle:
    """
    Throttle for detecting and preventing suspicious activity patterns.
    """
    
    def __init__(self):
        self.cache_timeout = 3600  # 1 hour
        self.suspicious_threshold = 10  # Number of actions that trigger suspicion
    
    def get_cache_key(self, user_id, action_type):
        """
        Get cache key for tracking user actions.
        """
        return f"suspicious_activity:{user_id}:{action_type}"
    
    def record_action(self, user_id, action_type):
        """
        Record a user action and check for suspicious patterns.
        """
        cache_key = self.get_cache_key(user_id, action_type)
        current_count = cache.get(cache_key, 0) + 1
        
        cache.set(cache_key, current_count, self.cache_timeout)
        
        # Check if user has exceeded suspicious activity threshold
        if current_count > self.suspicious_threshold:
            self._flag_suspicious_activity(user_id, action_type, current_count)
            return False
        
        return True
    
    def _flag_suspicious_activity(self, user_id, action_type, count):
        """
        Flag suspicious activity for review.
        """
        import logging
        logger = logging.getLogger(__name__)
        
        logger.warning(
            f"Suspicious activity detected: User {user_id} performed {action_type} {count} times in 1 hour",
            extra={
                'user_id': user_id,
                'action_type': action_type,
                'count': count,
                'timestamp': timezone.now().isoformat()
            }
        )
        
        # Could also create a database record for admin review
        # or send alerts to monitoring systems


# Throttle decorator for views
def throttle_classes(*throttle_classes):
    """
    Decorator to apply multiple throttle classes to a view.
    """
    def decorator(view_class):
        if hasattr(view_class, 'throttle_classes'):
            view_class.throttle_classes = list(view_class.throttle_classes) + list(throttle_classes)
        else:
            view_class.throttle_classes = list(throttle_classes)
        return view_class
    return decorator


# Throttle mixin for views
class ThrottleMixin:
    """
    Mixin that provides enhanced throttling capabilities.
    """
    
    def check_throttles(self, request):
        """
        Check throttles with enhanced error messages.
        """
        throttle_durations = []
        for throttle in self.get_throttles():
            if not throttle.allow_request(request, self):
                throttle_durations.append(throttle.wait())
        
        if throttle_durations:
            # Get the longest wait time
            duration = max(throttle_durations) if throttle_durations else None
            from .exceptions import RateLimitException
            
            wait_time = int(duration) if duration else 60
            raise RateLimitException(
                message=f"Rate limit exceeded. Try again in {wait_time} seconds.",
                code="RATE_LIMIT_EXCEEDED"
            )