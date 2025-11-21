# Soft Delete Fix - Bookmarks Showing Deleted Tweets

## Issue Identified
Deleted tweets were appearing in the bookmarks list because the `user_bookmarks` endpoint wasn't filtering out soft-deleted tweets (where `is_deleted=True`).

## Root Cause
The application uses **soft deletes** for tweets:
- When a tweet is deleted, `is_deleted` is set to `True`
- The tweet record remains in the database
- Most endpoints filter `is_deleted=False` to hide deleted tweets
- **BUT** the bookmarks endpoint was missing this filter

## The Problem Flow
```
1. User bookmarks a tweet
2. Tweet author deletes the tweet (is_deleted=True)
3. User views their bookmarks
4. Deleted tweet still appears in the list
5. User tries to delete it → 404 error (tweet already deleted)
```

## Fix Applied

### Backend Change
**File**: `backend/apps/interactions/views.py`

**Before**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """
    Get user's bookmarked tweets.
    """
    bookmarks = Bookmark.objects.filter(
        user=request.user,
        # Missing is_deleted filter!
    ).select_related(
        'tweet__author'
    ).prefetch_related(
        'tweet__media'
    )
    ...
```

**After**:
```python
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_bookmarks(request):
    """
    Get user's bookmarked tweets.
    """
    bookmarks = Bookmark.objects.filter(
        user=request.user,
        tweet__is_deleted=False  # ✅ Exclude deleted tweets
    ).select_related(
        'tweet__author'
    ).prefetch_related(
        'tweet__media'
    )
    ...
```

## Verification

### Other Endpoints Checked
All other tweet-related endpoints properly filter `is_deleted=False`:

✅ **Tweet List/Create** - `Tweet.objects.filter(is_deleted=False)`
✅ **Tweet Detail** - `Tweet.objects.filter(is_deleted=False)`
✅ **User Tweets** - `is_deleted=False`
✅ **User Replies** - `is_deleted=False`
✅ **User Media** - `is_deleted=False`
✅ **User Likes** - `is_deleted=False`
✅ **Tweet Replies** - `is_deleted=False`
✅ **Hashtag Tweets** - `is_deleted=False`
✅ **Home Feed** - `is_deleted=False`
✅ **Explore Feed** - `is_deleted=False`
✅ **Search** - `is_deleted=False`
✅ **Trending** - `is_deleted=False`

❌ **User Bookmarks** - Was missing the filter (NOW FIXED)

## Testing

### Test Case 1: Bookmark Deleted Tweet
1. User A creates a tweet
2. User B bookmarks the tweet
3. User A deletes the tweet
4. User B views bookmarks
5. **Expected**: Deleted tweet should NOT appear
6. **Result**: ✅ Tweet is filtered out

### Test Case 2: Delete Own Bookmarked Tweet
1. User creates and bookmarks their own tweet
2. User deletes the tweet
3. User views bookmarks
4. **Expected**: Tweet should NOT appear
5. **Result**: ✅ Tweet is filtered out

### Test Case 3: Normal Bookmarks
1. User bookmarks several tweets
2. None are deleted
3. User views bookmarks
4. **Expected**: All bookmarks appear
5. **Result**: ✅ All bookmarks visible

## Why Soft Deletes?

### Advantages
1. **Data Integrity**: Maintains referential integrity
2. **Analytics**: Can analyze deleted content
3. **Audit Trail**: Track what was deleted and when
4. **Recovery**: Possible to restore if needed
5. **Cascading Issues**: Prevents breaking replies/threads

### Implementation
```python
# In Tweet model
is_deleted = models.BooleanField(default=False)

# When deleting
def perform_destroy(self, instance):
    instance.is_deleted = True
    instance.save()
```

## Best Practices for Soft Deletes

### 1. Always Filter in Queries
```python
# ✅ Good
Tweet.objects.filter(is_deleted=False)

# ❌ Bad
Tweet.objects.all()  # Includes deleted tweets
```

### 2. Use Model Manager
Consider creating a custom manager:
```python
class TweetManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class Tweet(models.Model):
    objects = TweetManager()
    all_objects = models.Manager()  # For admin access
```

### 3. Related Object Queries
When querying through relationships:
```python
# ✅ Good
Bookmark.objects.filter(
    user=user,
    tweet__is_deleted=False  # Filter through relationship
)

# ❌ Bad
Bookmark.objects.filter(user=user)  # Includes deleted tweets
```

### 4. Consistent Filtering
Every endpoint that returns tweets should filter:
- Direct queries: `Tweet.objects.filter(is_deleted=False)`
- Related queries: `model__tweet__is_deleted=False`
- Prefetch queries: Include filter in Prefetch object

## Related Issues Fixed

### Frontend Error Handling
Also improved error handling in `TweetCard.tsx`:
- Better error message extraction
- Specific messages for 404 (already deleted)
- Specific messages for 403 (no permission)
- Prevents React rendering errors with object responses

## Monitoring

### Check for Similar Issues
Run this query to find other potential issues:
```sql
-- Find bookmarks of deleted tweets
SELECT b.id, b.user_id, t.id as tweet_id, t.is_deleted
FROM interactions_bookmark b
JOIN tweets_tweet t ON b.tweet_id = t.id
WHERE t.is_deleted = TRUE;

-- Find likes of deleted tweets
SELECT l.id, l.user_id, t.id as tweet_id, t.is_deleted
FROM interactions_like l
JOIN tweets_tweet t ON l.tweet_id = t.id
WHERE t.is_deleted = TRUE;

-- Find retweets of deleted tweets
SELECT r.id, r.user_id, t.id as tweet_id, t.is_deleted
FROM interactions_retweet r
JOIN tweets_tweet t ON r.tweet_id = t.id
WHERE t.is_deleted = TRUE;
```

## Future Improvements

### 1. Cleanup Job
Create a periodic task to remove old soft-deleted records:
```python
# Delete tweets that have been soft-deleted for > 30 days
from django.utils import timezone
from datetime import timedelta

thirty_days_ago = timezone.now() - timedelta(days=30)
Tweet.objects.filter(
    is_deleted=True,
    updated_at__lt=thirty_days_ago
).delete()
```

### 2. Cascade Cleanup
When deleting a tweet, also clean up:
- Remove from bookmarks
- Remove likes
- Remove retweets
- Notify users who interacted

### 3. Admin Interface
Add admin view to:
- See deleted tweets
- Restore deleted tweets
- Permanently delete tweets
- View deletion statistics

## Success Criteria

✅ Deleted tweets don't appear in bookmarks
✅ No 404 errors when viewing bookmarks
✅ Consistent behavior across all endpoints
✅ Proper error messages
✅ No React rendering errors
✅ Database integrity maintained

---

**Status**: ✅ **FIXED**

The bookmarks endpoint now properly filters out soft-deleted tweets, preventing 404 errors and ensuring a consistent user experience.
