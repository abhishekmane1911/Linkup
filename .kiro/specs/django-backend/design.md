# Design Document

## Overview

The Django backend for Linkup will be built as a REST API using Django REST Framework (DRF). The architecture follows a modular approach with separate Django apps for different feature domains. The system will use JWT authentication, implement proper caching strategies, and provide comprehensive API endpoints for the React frontend.

## Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   React Frontend │────│  Django REST API │────│   MySQL Database│
│                 │    │                 │    │                 │
│  - Components   │    │  - Authentication│    │  - User Data    │
│  - State Mgmt   │    │  - Business Logic│    │  - Tweets       │
│  - API Calls    │    │  - Serialization │    │  - Relationships│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Django Project Structure

```
linkup_backend/
├── manage.py
├── requirements.txt
├── linkup_backend/
│   ├── __init__.py
│   ├── settings/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── development.py
│   │   └── production.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── authentication/
│   ├── users/
│   ├── tweets/
│   ├── social/
│   ├── messaging/
│   ├── communities/
│   ├── moderation/
│   └── common/
└── media/
    ├── profile_images/
    ├── banner_images/
    └── tweet_media/
```

## Components and Interfaces

### Django Apps Architecture

#### 1. Authentication App (`apps/authentication/`)
- **Purpose**: Handle user authentication, JWT tokens, password management
- **Models**: Custom User model extending AbstractUser
- **Key Features**:
  - JWT token authentication
  - Password reset functionality
  - Email verification
  - Rate limiting for auth endpoints

#### 2. Users App (`apps/users/`)
- **Purpose**: User profile management, follow relationships
- **Models**: UserProfile, Follow relationships
- **Key Features**:
  - Profile CRUD operations
  - Follow/unfollow functionality
  - User search and discovery
  - Profile image/banner upload

#### 3. Tweets App (`apps/tweets/`)
- **Purpose**: Tweet creation, management, and retrieval
- **Models**: Tweet, Media, Hashtag, TweetHashtag
- **Key Features**:
  - Tweet CRUD operations
  - Media attachment handling
  - Hashtag extraction and linking
  - Reply threading
  - Feed generation

#### 4. Social App (`apps/social/`)
- **Purpose**: Social interactions (likes, retweets, bookmarks)
- **Models**: Like, Retweet, Bookmark
- **Key Features**:
  - Like/unlike functionality
  - Retweet operations
  - Bookmark management
  - Interaction analytics

#### 5. Messaging App (`apps/messaging/`)
- **Purpose**: Direct messaging system
- **Models**: Conversation, ConversationParticipant, DirectMessage
- **Key Features**:
  - Conversation management
  - Message sending/receiving
  - Read status tracking
  - Message history

#### 6. Communities App (`apps/communities/`)
- **Purpose**: Community features and management
- **Models**: Community, CommunityMember, Role, Permission
- **Key Features**:
  - Community CRUD operations
  - Member management
  - Role-based permissions
  - Community feeds

#### 7. Moderation App (`apps/moderation/`)
- **Purpose**: Content moderation and reporting
- **Models**: Report, ModerationAction
- **Key Features**:
  - Report submission
  - Moderation workflows
  - Content flagging
  - Admin tools

#### 8. Common App (`apps/common/`)
- **Purpose**: Shared utilities and base classes
- **Components**:
  - Base serializers
  - Common mixins
  - Utility functions
  - Custom permissions

### API Endpoint Structure

```
/api/v1/
├── auth/
│   ├── register/
│   ├── login/
│   ├── logout/
│   ├── refresh/
│   └── password-reset/
├── users/
│   ├── profile/
│   ├── {user_id}/
│   ├── {user_id}/follow/
│   ├── {user_id}/followers/
│   ├── {user_id}/following/
│   └── search/
├── tweets/
│   ├── /
│   ├── {tweet_id}/
│   ├── {tweet_id}/like/
│   ├── {tweet_id}/retweet/
│   ├── {tweet_id}/bookmark/
│   ├── {tweet_id}/replies/
│   ├── feed/
│   └── hashtags/{hashtag}/
├── messaging/
│   ├── conversations/
│   ├── conversations/{conversation_id}/
│   └── conversations/{conversation_id}/messages/
├── communities/
│   ├── /
│   ├── {community_id}/
│   ├── {community_id}/members/
│   ├── {community_id}/join/
│   └── {community_id}/posts/
└── moderation/
    ├── reports/
    └── reports/{report_id}/
```

## Data Models

### Core Model Relationships

The Django models will closely mirror the provided database schema with these key relationships:

1. **User Model** (extends AbstractUser)
   - One-to-many with Tweet (author)
   - Many-to-many with User (follows)
   - One-to-many with Community (owner)

2. **Tweet Model**
   - Foreign key to User (author)
   - Self-referencing foreign key (parent_tweet)
   - Many-to-many with User through Like, Retweet, Bookmark
   - One-to-many with Media

3. **Community Model**
   - Foreign key to User (owner)
   - Many-to-many with User through CommunityMember
   - Many-to-many with Topic

### Model Serializers

Each app will have dedicated serializers:

```python
# Example serializer structure
class TweetSerializer(serializers.ModelSerializer):
    author = UserBasicSerializer(read_only=True)
    likes_count = serializers.IntegerField(read_only=True)
    retweets_count = serializers.IntegerField(read_only=True)
    replies_count = serializers.IntegerField(read_only=True)
    is_liked = serializers.SerializerMethodField()
    is_retweeted = serializers.SerializerMethodField()
    is_bookmarked = serializers.SerializerMethodField()
    media = MediaSerializer(many=True, read_only=True)
    
    class Meta:
        model = Tweet
        fields = '__all__'
```

## Error Handling

### Standardized Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "field_name": ["This field is required."]
    },
    "timestamp": "2024-01-15T10:30:00Z"
  }
}
```

### Error Categories

1. **Authentication Errors** (401)
   - Invalid credentials
   - Expired tokens
   - Missing authentication

2. **Authorization Errors** (403)
   - Insufficient permissions
   - Resource access denied

3. **Validation Errors** (400)
   - Invalid input data
   - Business rule violations

4. **Not Found Errors** (404)
   - Resource not found
   - Invalid endpoints

5. **Server Errors** (500)
   - Database connection issues
   - Unexpected exceptions

### Custom Exception Handler

```python
def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    
    if response is not None:
        custom_response_data = {
            'error': {
                'code': get_error_code(exc),
                'message': get_error_message(exc),
                'details': response.data,
                'timestamp': timezone.now().isoformat()
            }
        }
        response.data = custom_response_data
    
    return response
```

## Testing Strategy

### Testing Pyramid

1. **Unit Tests** (70%)
   - Model methods and properties
   - Serializer validation
   - Utility functions
   - Business logic methods

2. **Integration Tests** (20%)
   - API endpoint functionality
   - Database interactions
   - Authentication flows
   - Permission checks

3. **End-to-End Tests** (10%)
   - Complete user workflows
   - Cross-app interactions
   - Performance scenarios

### Test Organization

```
tests/
├── unit/
│   ├── test_models.py
│   ├── test_serializers.py
│   └── test_utils.py
├── integration/
│   ├── test_auth_api.py
│   ├── test_tweets_api.py
│   └── test_social_api.py
└── e2e/
    ├── test_user_journey.py
    └── test_social_interactions.py
```

### Testing Tools

- **pytest-django**: Test framework
- **factory-boy**: Test data generation
- **pytest-cov**: Coverage reporting
- **django-test-plus**: Enhanced testing utilities

## Security Considerations

### Authentication & Authorization

1. **JWT Implementation**
   - Access tokens (15 minutes expiry)
   - Refresh tokens (7 days expiry)
   - Token blacklisting on logout

2. **Permission System**
   - Custom permission classes
   - Object-level permissions
   - Role-based access control

### Data Protection

1. **Input Validation**
   - Serializer validation
   - Custom validators
   - SQL injection prevention

2. **File Upload Security**
   - File type validation
   - Size limitations
   - Virus scanning integration

3. **Rate Limiting**
   - Per-user rate limits
   - Endpoint-specific limits
   - IP-based throttling

### CORS Configuration

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev server
    "https://linkup.example.com",  # Production frontend
]

CORS_ALLOW_CREDENTIALS = True
```

## Performance Optimization

### Database Optimization

1. **Query Optimization**
   - Select_related for foreign keys
   - Prefetch_related for many-to-many
   - Database indexing strategy

2. **Session Management**
   - Django's default session framework
   - Database-backed sessions
   - Simple in-memory caching for development

### API Performance

1. **Pagination**
   - Cursor-based pagination for feeds
   - Limit-offset for search results
   - Configurable page sizes

2. **Response Optimization**
   - Field selection
   - Minimal serializers for lists
   - Compressed responses

### Monitoring

1. **Performance Metrics**
   - Response time tracking
   - Database query monitoring
   - Cache hit rates

2. **Error Tracking**
   - Sentry integration
   - Custom logging
   - Alert systems

## Development Setup

### Local Development Environment

1. **Database Setup**
   - Local MySQL installation
   - Database creation using provided schema
   - Django migrations for model sync

2. **Django Configuration**
   - Virtual environment setup
   - Requirements installation
   - Settings configuration for development

3. **Media Handling**
   - Local file storage for development
   - Simple file upload handling

### Future Enhancements

After the core functionality is working:

1. **Performance Optimization**
   - Redis caching implementation
   - Database query optimization
   - CDN integration for media

2. **Deployment**
   - Docker containerization
   - Production environment setup
   - CI/CD pipeline

3. **Advanced Features**
   - Real-time notifications
   - Advanced search
   - Analytics and reporting