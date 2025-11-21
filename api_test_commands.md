# Complete API Testing Commands for LinkUp Backend

This document contains comprehensive curl commands to test all features of the LinkUp social media backend API.

**Base URL:** `http://localhost:8000`

## Prerequisites

1. Start the Django development server: `python manage.py runserver`
2. Replace `{ACCESS_TOKEN}` with actual JWT access token after login
3. Replace `{USER_ID}`, `{TWEET_ID}`, etc. with actual IDs from your database

---

## 1. Authentication & User Management

### 1.1 User Registration
```bash
curl -X POST http://localhost:8000/api/v1/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123",
    "first_name": "Test",
    "last_name": "User"
  }'
```

### 1.2 User Login
```bash
 
```

### 1.3 Token Refresh
```bash
curl -X POST http://localhost:8000/api/v1/auth/token/refresh/ \
  -H "Content-Type: application/json" \
  -d '{
    "refresh": "{REFRESH_TOKEN}"
  }'
```

### 1.4 Get Current User Profile
```bash
curl -X GET http://localhost:8000/api/v1/auth/profile/me/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 1.5 Update User Profile
```bash
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "first_name": "Updated",
    "last_name": "Name",
    "bio": "Updated bio"
  }'
```

### 1.6 Change Password
```bash
curl -X POST http://localhost:8000/api/v1/auth/password/change/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "old_password": "securepassword123",
    "new_password": "newsecurepassword456"
  }'
```

### 1.7 Logout
```bash
curl -X POST http://localhost:8000/api/v1/auth/logout/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "{REFRESH_TOKEN}"
  }'
```

---

## 2. User Profiles & Relationships

### 2.1 Get User Profile by ID
```bash
curl -X GET http://localhost:8000/api/v1/users/{USER_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 2.2 Get User Followers
```bash
curl -X GET http://localhost:8000/api/v1/users/{USER_ID}/followers/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 2.3 Get User Following
```bash
curl -X GET http://localhost:8000/api/v1/users/{USER_ID}/following/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 2.4 Search Users
```bash
curl -X GET "http://localhost:8000/api/v1/users/search/?q=testuser" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 3. Tweet Management

### 3.1 Create Tweet (Text Only)
```bash
curl -X POST http://localhost:8000/api/v1/tweets/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is my first tweet! #hello #world"
  }'
```

### 3.2 Create Tweet with Media
```bash
curl -X POST http://localhost:8000/api/v1/tweets/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -F "content=Tweet with image! #photo" \
  -F "media_files=@/path/to/image.jpg"
```

### 3.3 Get All Tweets (Paginated)
```bash
curl -X GET "http://localhost:8000/api/v1/tweets/?page=1&page_size=20" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 3.4 Get Tweet by ID
```bash
curl -X GET http://localhost:8000/api/v1/tweets/{TWEET_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 3.5 Update Tweet
```bash
curl -X PATCH http://localhost:8000/api/v1/tweets/{TWEET_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated tweet content #updated"
  }'
```

### 3.6 Delete Tweet
```bash
curl -X DELETE http://localhost:8000/api/v1/tweets/{TWEET_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 3.7 Get User's Tweets
```bash
curl -X GET http://localhost:8000/api/v1/tweets/user/{USER_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 3.8 Get Tweet Statistics
```bash
curl -X GET http://localhost:8000/api/v1/tweets/{TWEET_ID}/stats/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 4. Tweet Replies & Threading

### 4.1 Get Tweet Replies
```bash
curl -X GET http://localhost:8000/api/v1/tweets/{TWEET_ID}/replies/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 4.2 Create Reply to Tweet
```bash
curl -X POST http://localhost:8000/api/v1/tweets/{TWEET_ID}/replies/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "This is a reply to the tweet!"
  }'
```

### 4.3 Get Tweet Thread
```bash
curl -X GET http://localhost:8000/api/v1/tweets/{TWEET_ID}/thread/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 4.4 Get Tweet Conversation
```bash
curl -X GET http://localhost:8000/api/v1/tweets/{TWEET_ID}/conversation/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 5. Tweet Interactions

### 5.1 Like Tweet
```bash
curl -X POST http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/like/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.2 Unlike Tweet
```bash
curl -X DELETE http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/like/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.3 Retweet
```bash
curl -X POST http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/retweet/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.4 Unretweet
```bash
curl -X DELETE http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/retweet/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.5 Bookmark Tweet
```bash
curl -X POST http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/bookmark/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.6 Unbookmark Tweet
```bash
curl -X DELETE http://localhost:8000/api/v1/interactions/tweets/{TWEET_ID}/bookmark/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 5.7 Get User Bookmarks
```bash
curl -X GET http://localhost:8000/api/v1/interactions/bookmarks/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 6. User Following

### 6.1 Follow User
```bash
curl -X POST http://localhost:8000/api/v1/interactions/users/{USER_ID}/follow/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 6.2 Unfollow User
```bash
curl -X DELETE http://localhost:8000/api/v1/interactions/users/{USER_ID}/follow/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 7. Feeds & Discovery

### 7.1 Home Timeline Feed
```bash
curl -X GET http://localhost:8000/api/v1/tweets/feed/home/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 7.2 Explore Feed
```bash
curl -X GET http://localhost:8000/api/v1/tweets/feed/explore/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 7.3 Popular Tweets
```bash
curl -X GET http://localhost:8000/api/v1/tweets/feed/popular/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 7.4 User Suggestions
```bash
curl -X GET http://localhost:8000/api/v1/tweets/discover/users/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 7.5 Trending Content
```bash
curl -X GET http://localhost:8000/api/v1/tweets/discover/trending/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 8. Search Functionality

### 8.1 Search Tweets
```bash
curl -X GET "http://localhost:8000/api/v1/tweets/search/?q=hello%20world" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 8.2 Search Users in Tweets
```bash
curl -X GET "http://localhost:8000/api/v1/tweets/search/users/?q=testuser" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 8.3 Global Search
```bash
curl -X GET "http://localhost:8000/api/v1/tweets/search/global/?q=hello" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 9. Hashtags

### 9.1 Get Tweets by Hashtag
```bash
curl -X GET http://localhost:8000/api/v1/tweets/hashtags/hello/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 9.2 Get Trending Hashtags
```bash
curl -X GET http://localhost:8000/api/v1/tweets/hashtags/trending/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 9.3 Search Hashtags
```bash
curl -X GET "http://localhost:8000/api/v1/tweets/hashtags/search/?q=hello" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 10. Messaging System

### 10.1 Get Conversations List
```bash
curl -X GET http://localhost:8000/api/v1/messaging/conversations/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.2 Get Conversation Details
```bash
curl -X GET http://localhost:8000/api/v1/messaging/conversations/{CONVERSATION_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.3 Get Conversation Messages
```bash
curl -X GET http://localhost:8000/api/v1/messaging/conversations/{CONVERSATION_ID}/messages/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.4 Send Message in Conversation
```bash
curl -X POST http://localhost:8000/api/v1/messaging/conversations/{CONVERSATION_ID}/messages/create/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Hello! This is a message."
  }'
```

### 10.5 Create Direct Message
```bash
curl -X POST http://localhost:8000/api/v1/messaging/messages/create/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "recipient_id": {USER_ID},
    "content": "Direct message content"
  }'
```

### 10.6 Mark Conversation as Read
```bash
curl -X POST http://localhost:8000/api/v1/messaging/conversations/{CONVERSATION_ID}/mark-read/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.7 Get Conversation Metadata
```bash
curl -X GET http://localhost:8000/api/v1/messaging/conversations/{CONVERSATION_ID}/metadata/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.8 Delete Message
```bash
curl -X DELETE http://localhost:8000/api/v1/messaging/messages/{MESSAGE_ID}/delete/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 10.9 Check Messaging Privacy
```bash
curl -X GET http://localhost:8000/api/v1/messaging/privacy/check/{USER_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 11. Communities

### 11.1 Get Communities List
```bash
curl -X GET http://localhost:8000/api/v1/communities/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.2 Create Community
```bash
curl -X POST http://localhost:8000/api/v1/communities/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Community",
    "description": "A test community for developers",
    "is_private": false
  }'
```

### 11.3 Get Community Details
```bash
curl -X GET http://localhost:8000/api/v1/communities/{COMMUNITY_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.4 Join Community
```bash
curl -X POST http://localhost:8000/api/v1/communities/{COMMUNITY_ID}/join/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.5 Leave Community
```bash
curl -X POST http://localhost:8000/api/v1/communities/{COMMUNITY_ID}/leave/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.6 Get Community Members
```bash
curl -X GET http://localhost:8000/api/v1/communities/{COMMUNITY_ID}/members/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.7 Get Community Feed
```bash
curl -X GET http://localhost:8000/api/v1/communities/{COMMUNITY_ID}/feed/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.8 Get User's Communities
```bash
curl -X GET http://localhost:8000/api/v1/communities/my-communities/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.9 Community Discovery
```bash
curl -X GET http://localhost:8000/api/v1/communities/discover/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 11.10 Search Communities
```bash
curl -X GET "http://localhost:8000/api/v1/communities/search/?q=developer" \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 12. Lists Management

### 12.1 Get User Lists
```bash
curl -X GET http://localhost:8000/api/v1/lists/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 12.2 Create List
```bash
curl -X POST http://localhost:8000/api/v1/lists/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Favorite Users",
    "description": "A list of my favorite users",
    "is_private": false
  }'
```

### 12.3 Get List Details
```bash
curl -X GET http://localhost:8000/api/v1/lists/{LIST_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 12.4 Get List Members
```bash
curl -X GET http://localhost:8000/api/v1/lists/{LIST_ID}/members/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 12.5 Add Member to List
```bash
curl -X POST http://localhost:8000/api/v1/lists/{LIST_ID}/members/add/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": {USER_ID}
  }'
```

### 12.6 Remove Member from List
```bash
curl -X DELETE http://localhost:8000/api/v1/lists/{LIST_ID}/members/{USER_ID}/remove/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 12.7 Get List Timeline
```bash
curl -X GET http://localhost:8000/api/v1/lists/{LIST_ID}/timeline/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 12.8 Get Public Lists
```bash
curl -X GET http://localhost:8000/api/v1/lists/public/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## 13. Moderation System

### 13.1 Create Report
```bash
curl -X POST http://localhost:8000/api/v1/moderation/reports/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "tweet",
    "object_id": {TWEET_ID},
    "reason": "spam",
    "description": "This tweet contains spam content"
  }'
```

### 13.2 Get User's Reports
```bash
curl -X GET http://localhost:8000/api/v1/moderation/my-reports/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 13.3 Get Reports List (Moderators Only)
```bash
curl -X GET http://localhost:8000/api/v1/moderation/reports/list/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 13.4 Get Report Details (Moderators Only)
```bash
curl -X GET http://localhost:8000/api/v1/moderation/reports/{REPORT_ID}/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

### 13.5 Moderator Dashboard (Moderators Only)
```bash
curl -X GET http://localhost:8000/api/v1/moderation/dashboard/ \
  -H "Authorization: Bearer {ACCESS_TOKEN}"
```

---

## Testing Workflow

### Step 1: Authentication Flow
1. Register a new user (1.1)
2. Login with credentials (1.2)
3. Save the access token for subsequent requests
4. Test token refresh (1.3)

### Step 2: Basic Tweet Operations
1. Create a text tweet (3.1)
2. Create a tweet with media (3.2)
3. Get all tweets (3.3)
4. Like/unlike the tweet (5.1, 5.2)
5. Retweet/unretweet (5.3, 5.4)

### Step 3: User Interactions
1. Search for users (2.4)
2. Follow/unfollow users (6.1, 6.2)
3. Get user profiles (2.1)

### Step 4: Advanced Features
1. Test messaging system (10.1-10.9)
2. Test communities (11.1-11.10)
3. Test lists (12.1-12.8)
4. Test search functionality (8.1-8.3)

### Step 5: Content Discovery
1. Test feeds (7.1-7.3)
2. Test hashtags (9.1-9.3)
3. Test trending content (7.5)

## Notes

- Replace all placeholder values (`{ACCESS_TOKEN}`, `{USER_ID}`, etc.) with actual values
- Some endpoints require specific permissions (moderator role, community membership, etc.)
- File uploads require actual file paths in the `-F` parameter
- All authenticated endpoints require the `Authorization: Bearer {ACCESS_TOKEN}` header
- Pagination parameters (`page`, `page_size`) can be added to list endpoints
- Search queries should be URL-encoded for special characters

## Postman Collection

You can import these commands into Postman by:
1. Creating a new collection
2. Adding each curl command as a new request
3. Setting up environment variables for `BASE_URL`, `ACCESS_TOKEN`, etc.
4. Using Postman's test scripts to automate token management