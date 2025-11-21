# Counter Fields Migration Guide

## Current Situation

Your backend currently uses **@property methods** that calculate counts dynamically:

```python
@property
def likes_count(self):
    return self.likes.count()  # Queries database every time
```

This means:
- ✅ Always accurate
- ❌ Slower performance (queries DB each time)
- ❌ Higher database load
- ❌ Triggers won't work (no counter columns exist)

## Migration to Counter Fields

To use database triggers, you need to:
1. Add counter columns to models
2. Update existing code to use fields instead of properties
3. Sync existing data
4. Apply triggers

---

## Step 1: Create Django Migration

### 1.1 Create migration file:

```bash
cd backend
python manage.py makemigrations tweets --empty --name add_counter_fields
```

### 1.2 Edit the migration file:

**File:** `backend/apps/tweets/migrations/XXXX_add_counter_fields.py`

```python
from django.db import migrations, models


def sync_tweet_counters(apps, schema_editor):
    """Sync counter fields with actual counts"""
    Tweet = apps.get_model('tweets', 'Tweet')
    
    for tweet in Tweet.objects.all():
        tweet.likes_count_field = tweet.likes.count()
        tweet.retweets_count_field = tweet.retweets.count()
        tweet.bookmarks_count_field = tweet.bookmarks.count()
        tweet.reply_count_field = tweet.replies.filter(is_deleted=False).count()
        tweet.save(update_fields=[
            'likes_count_field', 
            'retweets_count_field', 
            'bookmarks_count_field',
            'reply_count_field'
        ])


def sync_user_counters(apps, schema_editor):
    """Sync user counter fields"""
    User = apps.get_model('authentication', 'User')
    
    for user in User.objects.all():
        user.followers_count_field = user.followers.count()
        user.following_count_field = user.following.count()
        user.save(update_fields=['followers_count_field', 'following_count_field'])


def sync_community_counters(apps, schema_editor):
    """Sync community counter fields"""
    Community = apps.get_model('communities', 'Community')
    
    for community in Community.objects.all():
        community.members_count_field = community.members.count()
        community.save(update_fields=['members_count_field'])


class Migration(migrations.Migration):

    dependencies = [
        ('tweets', 'XXXX_previous_migration'),  # Update this
    ]

    operations = [
        # Add counter fields to Tweet model
        migrations.AddField(
            model_name='tweet',
            name='likes_count_field',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='retweets_count_field',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='bookmarks_count_field',
            field=models.IntegerField(default=0, db_index=True),
        ),
        migrations.AddField(
            model_name='tweet',
            name='reply_count_field',
            field=models.IntegerField(default=0, db_index=True),
        ),
        
        # Sync existing data
        migrations.RunPython(sync_tweet_counters, migrations.RunPython.noop),
    ]
```

### 1.3 Create migration for User model:

```bash
python manage.py makemigrations authentication --empty --name add_counter_fields
```

Edit the file similarly to add `followers_count_field` and `following_count_field`.

### 1.4 Create migration for Community model:

```bash
python manage.py makemigrations communities --empty --name add_counter_fields
```

Edit to add `members_count_field`.

---

## Step 2: Update Models

### 2.1 Update Tweet Model

**File:** `backend/apps/tweets/models.py`

```python
class Tweet(models.Model):
    # ... existing fields ...
    
    # Counter fields (managed by triggers)
    likes_count_field = models.IntegerField(default=0, db_index=True)
    retweets_count_field = models.IntegerField(default=0, db_index=True)
    bookmarks_count_field = models.IntegerField(default=0, db_index=True)
    reply_count_field = models.IntegerField(default=0, db_index=True)
    
    # Keep properties for backward compatibility
    @property
    def likes_count(self):
        """Get likes count from field (updated by trigger)"""
        return self.likes_count_field
    
    @property
    def retweets_count(self):
        """Get retweets count from field (updated by trigger)"""
        return self.retweets_count_field
    
    @property
    def bookmarks_count(self):
        """Get bookmarks count from field (updated by trigger)"""
        return self.bookmarks_count_field
    
    @property
    def reply_count(self):
        """Get reply count from field (updated by trigger)"""
        return self.reply_count_field
```

### 2.2 Update User Model

**File:** `backend/apps/authentication/models.py`

```python
class User(AbstractUser):
    # ... existing fields ...
    
    # Counter fields (managed by triggers)
    followers_count_field = models.IntegerField(default=0, db_index=True)
    following_count_field = models.IntegerField(default=0, db_index=True)
    
    @property
    def followers_count(self):
        """Get followers count from field (updated by trigger)"""
        return self.followers_count_field
    
    @property
    def following_count(self):
        """Get following count from field (updated by trigger)"""
        return self.following_count_field
```

### 2.3 Update Community Model

**File:** `backend/apps/communities/models.py`

```python
class Community(models.Model):
    # ... existing fields ...
    
    # Counter field (managed by trigger)
    members_count_field = models.IntegerField(default=0, db_index=True)
    
    @property
    def members_count(self):
        """Get members count from field (updated by trigger)"""
        return self.members_count_field
```

---

## Step 3: Update Triggers SQL

Update the triggers to use the new field names:

**File:** `backend/sql/triggers_with_fields.sql`

```sql
-- Update likes_count_field instead of likes_count
DELIMITER $$

CREATE TRIGGER after_like_insert
AFTER INSERT ON likes
FOR EACH ROW
BEGIN
    UPDATE tweets 
    SET likes_count_field = likes_count_field + 1,
        updated_at = NOW()
    WHERE id = NEW.tweet_id;
END$$

CREATE TRIGGER after_like_delete
AFTER DELETE ON likes
FOR EACH ROW
BEGIN
    UPDATE tweets 
    SET likes_count_field = GREATEST(likes_count_field - 1, 0),
        updated_at = NOW()
    WHERE id = OLD.tweet_id;
END$$

-- Similar updates for other triggers...
DELIMITER ;
```

---

## Step 4: Migration Process

### Development Environment:

```bash
# 1. Run migrations
python manage.py migrate

# 2. Verify counter fields exist
python manage.py dbshell
> DESCRIBE tweets;
> SELECT id, likes_count_field, retweets_count_field FROM tweets LIMIT 5;

# 3. Apply triggers
mysql -u your_user -p linkup_db < sql/triggers_with_fields.sql

# 4. Test
python manage.py shell
>>> from apps.tweets.models import Tweet
>>> tweet = Tweet.objects.first()
>>> print(tweet.likes_count)  # Should show count from field
```

### Production Environment:

```bash
# 1. BACKUP DATABASE FIRST!
mysqldump -u user -p linkup_db > backup_before_counters.sql

# 2. Run during low-traffic period
python manage.py migrate

# 3. Apply triggers
mysql -u user -p linkup_db < sql/triggers_with_fields.sql

# 4. Monitor for issues
tail -f logs/linkup.log
```

---

## Step 5: Remove Old Code (Optional)

After confirming everything works, you can remove the old `.count()` queries:

```python
# OLD (remove this)
@property
def likes_count(self):
    return self.likes.count()

# NEW (keep this)
@property
def likes_count(self):
    return self.likes_count_field
```

---

## Verification Queries

### Check if counters match reality:

```sql
-- Check likes_count accuracy
SELECT 
    t.id,
    t.likes_count_field as stored,
    COUNT(l.id) as actual,
    (t.likes_count_field - COUNT(l.id)) as diff
FROM tweets t
LEFT JOIN likes l ON t.id = l.tweet_id
GROUP BY t.id
HAVING diff != 0
LIMIT 10;

-- Check retweets_count accuracy
SELECT 
    t.id,
    t.retweets_count_field as stored,
    COUNT(r.id) as actual,
    (t.retweets_count_field - COUNT(r.id)) as diff
FROM tweets t
LEFT JOIN retweets r ON t.id = r.tweet_id
GROUP BY t.id
HAVING diff != 0
LIMIT 10;

-- Check followers_count accuracy
SELECT 
    u.id,
    u.username,
    u.followers_count_field as stored,
    COUNT(f.id) as actual,
    (u.followers_count_field - COUNT(f.id)) as diff
FROM users u
LEFT JOIN follows f ON u.id = f.followed_id
GROUP BY u.id
HAVING diff != 0
LIMIT 10;
```

---

## Rollback Plan

If something goes wrong:

```bash
# 1. Drop triggers
mysql -u user -p linkup_db < sql/drop_triggers.sql

# 2. Restore backup
mysql -u user -p linkup_db < backup_before_counters.sql

# 3. Revert migrations
python manage.py migrate tweets XXXX_previous_migration
python manage.py migrate authentication XXXX_previous_migration
python manage.py migrate communities XXXX_previous_migration
```

---

## Performance Comparison

### Before (Properties):
```python
tweet.likes_count  # SELECT COUNT(*) FROM likes WHERE tweet_id = X
# ~10-50ms per query
```

### After (Fields + Triggers):
```python
tweet.likes_count  # Returns field value directly
# ~0.1ms per query
```

**Result:** 100-500x faster! 🚀

---

## Recommendation

For your current application size, I recommend:

### **Keep Properties for Now** if:
- You have < 10,000 tweets
- You have < 1,000 active users
- Performance is acceptable
- You want simplicity

### **Migrate to Counter Fields** if:
- You have > 10,000 tweets
- You notice slow page loads
- You want to scale
- You're comfortable with migrations

---

## Alternative: Hybrid Approach

Use cached properties:

```python
from django.core.cache import cache

@property
def likes_count(self):
    cache_key = f'tweet_likes_{self.id}'
    count = cache.get(cache_key)
    if count is None:
        count = self.likes.count()
        cache.set(cache_key, count, 300)  # Cache for 5 minutes
    return count
```

This gives you:
- ✅ Good performance
- ✅ Always accurate (eventually)
- ✅ No migrations needed
- ❌ Requires Redis/Memcached
- ❌ Cache invalidation complexity

---

## Conclusion

**Current State:** Your app uses properties (no triggers needed)

**To Use Triggers:** You must add counter fields first

**My Recommendation:** Keep properties until you need the performance boost, then migrate to counter fields + triggers.
