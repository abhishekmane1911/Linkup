# Database Triggers Implementation Guide

## Overview
This guide explains how to implement database triggers for the Linkup application that **won't conflict** with existing backend code.

## Important Note About Counter Fields

**Your backend currently uses `@property` methods to calculate counts dynamically** (likes_count, retweets_count, etc.). This means:
- Counts are calculated on-the-fly using `.count()` queries
- There are NO stored counter fields in the database
- Counter triggers would conflict with this approach

Therefore, the triggers provided focus on:
1. **Validation** - Prevent invalid data
2. **Audit Logging** - Track changes
3. **Data Integrity** - Enforce business rules

## Triggers Included (No Conflicts)

### 1. Validation Triggers
- **prevent_self_follow** - Users cannot follow themselves
- **prevent_self_like** - Users cannot like their own tweets

### 2. Audit Triggers
- **audit_tweet_changes** - Logs tweet content changes and deletions
- **audit_user_changes** - Logs username, email, and verification changes

### 3. Logging Triggers
- **log_report_status_change** - Tracks report status changes

### 4. Utility Triggers
- **update_tweet_timestamp** - Auto-updates `updated_at` field

## Implementation Steps

### Step 1: Create Audit Tables

First, create the required audit tables:

```bash
cd backend
mysql -u your_username -p linkup_db
```

Then run:

```sql
-- Create audit log table
CREATE TABLE IF NOT EXISTS audit_log (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    table_name VARCHAR(50) NOT NULL,
    record_id BIGINT NOT NULL,
    action_type VARCHAR(20) NOT NULL,
    old_value JSON,
    new_value JSON,
    changed_by BIGINT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_table_record (table_name, record_id),
    INDEX idx_changed_at (changed_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Create report status history table
CREATE TABLE IF NOT EXISTS report_status_history (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    report_id BIGINT NOT NULL,
    old_status VARCHAR(20),
    new_status VARCHAR(20) NOT NULL,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    changed_by BIGINT,
    INDEX idx_report (report_id),
    INDEX idx_changed_at (changed_at),
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Step 2: Install Triggers

Run the triggers SQL file:

```sql
SOURCE /path/to/backend/sql/triggers.sql;
```

Or copy and paste the trigger definitions from `backend/sql/triggers.sql`.

### Step 3: Verify Installation

```sql
-- Show all triggers
SHOW TRIGGERS;

-- Should show:
-- audit_tweet_changes
-- audit_user_changes
-- prevent_self_follow
-- prevent_self_like
-- log_report_status_change
-- update_tweet_timestamp
```

## Testing the Triggers

### Test 1: Prevent Self-Follow

```sql
-- This should FAIL with error: "Users cannot follow themselves"
INSERT INTO follows (follower_id, followed_id, created_at) 
VALUES (1, 1, NOW());
```

### Test 2: Prevent Self-Like

```sql
-- First, find a tweet by user 1
SELECT id FROM tweets WHERE author_id = 1 LIMIT 1;

-- Try to like it as user 1 (should FAIL)
INSERT INTO likes (user_id, tweet_id, created_at) 
VALUES (1, <tweet_id>, NOW());
```

### Test 3: Audit Logging

```sql
-- Update a tweet
UPDATE tweets SET content = 'Updated content' WHERE id = 1;

-- Check audit log
SELECT * FROM audit_log WHERE table_name = 'tweets' ORDER BY changed_at DESC LIMIT 5;
```

### Test 4: Report Status History

```sql
-- Update a report status
UPDATE reports SET status = 'resolved' WHERE id = 1;

-- Check history
SELECT * FROM report_status_history WHERE report_id = 1;
```

## Viewing Audit Data

### View Recent Tweet Changes
```sql
SELECT 
    al.*,
    t.content as current_content,
    u.username as changed_by_username
FROM audit_log al
JOIN tweets t ON al.record_id = t.id
JOIN users u ON al.changed_by = u.id
WHERE al.table_name = 'tweets'
ORDER BY al.changed_at DESC
LIMIT 20;
```

### View User Profile Changes
```sql
SELECT 
    al.*,
    u.username as current_username,
    u.email as current_email
FROM audit_log al
JOIN users u ON al.record_id = u.id
WHERE al.table_name = 'users'
ORDER BY al.changed_at DESC
LIMIT 20;
```

### View Report Status Timeline
```sql
SELECT 
    rsh.*,
    r.report_type,
    u.username as reporter
FROM report_status_history rsh
JOIN reports r ON rsh.report_id = r.id
JOIN users u ON r.reporter_id = u.id
ORDER BY rsh.changed_at DESC
LIMIT 20;
```

## Disabling Triggers (If Needed)

If you need to temporarily disable triggers:

```sql
-- Disable a specific trigger
DROP TRIGGER IF EXISTS prevent_self_follow;

-- Re-enable by recreating it
DELIMITER $$
CREATE TRIGGER prevent_self_follow
BEFORE INSERT ON follows
FOR EACH ROW
BEGIN
    IF NEW.follower_id = NEW.followed_id THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Users cannot follow themselves';
    END IF;
END$$
DELIMITER ;
```

## Removing All Triggers

```sql
DROP TRIGGER IF EXISTS audit_tweet_changes;
DROP TRIGGER IF EXISTS audit_user_changes;
DROP TRIGGER IF EXISTS prevent_self_follow;
DROP TRIGGER IF EXISTS prevent_self_like;
DROP TRIGGER IF EXISTS log_report_status_change;
DROP TRIGGER IF EXISTS update_tweet_timestamp;
```

## Benefits of These Triggers

### 1. Data Integrity
- Prevents invalid relationships (self-follow, self-like)
- Enforced at database level, can't be bypassed

### 2. Audit Trail
- Complete history of changes
- Useful for debugging and compliance
- Can track who changed what and when

### 3. Automatic Logging
- No application code needed
- Consistent across all data modifications
- Can't be forgotten or skipped

### 4. Performance
- Validation happens at database level
- No extra application queries needed
- Atomic operations

## Troubleshooting

### Error: "Trigger already exists"
```sql
DROP TRIGGER IF EXISTS trigger_name;
-- Then recreate it
```

### Error: "Access denied; you need TRIGGER privilege"
```sql
GRANT TRIGGER ON linkup_db.* TO 'your_username'@'localhost';
FLUSH PRIVILEGES;
```

### Error: "Table 'audit_log' doesn't exist"
Create the audit tables first (see Step 1 above).

### Trigger not firing
1. Check if trigger exists: `SHOW TRIGGERS;`
2. Check trigger definition: `SHOW CREATE TRIGGER trigger_name;`
3. Verify table names match your Django models
4. Check MySQL error log

## Alternative: Django Signals

If you prefer application-level logic instead of triggers, you can use Django signals:

```python
# In apps/common/signals.py

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.interactions.models import Follow, Like

@receiver(pre_save, sender=Follow)
def prevent_self_follow(sender, instance, **kwargs):
    if instance.follower == instance.followed:
        raise ValueError("Users cannot follow themselves")

@receiver(pre_save, sender=Like)
def prevent_self_like(sender, instance, **kwargs):
    if instance.user == instance.tweet.author:
        raise ValueError("Users cannot like their own tweets")
```

## Best Practices

1. **Test in Development First** - Never apply triggers directly to production
2. **Backup Before Changes** - Always backup your database
3. **Monitor Performance** - Watch for slow queries after adding triggers
4. **Document Everything** - Keep this guide updated
5. **Version Control** - Keep trigger SQL in git
6. **Review Audit Logs** - Regularly check audit_log table
7. **Clean Old Data** - Archive old audit logs periodically

## Maintenance

### Clean Old Audit Logs (Keep Last 90 Days)
```sql
DELETE FROM audit_log 
WHERE changed_at < DATE_SUB(NOW(), INTERVAL 90 DAY);
```

### Clean Old Report History (Keep Last 180 Days)
```sql
DELETE FROM report_status_history 
WHERE changed_at < DATE_SUB(NOW(), INTERVAL 180 DAY);
```

### Check Audit Log Size
```sql
SELECT 
    COUNT(*) as total_records,
    ROUND(SUM(LENGTH(old_value) + LENGTH(new_value)) / 1024 / 1024, 2) as size_mb
FROM audit_log;
```

## Conclusion

These triggers provide validation and audit logging without conflicting with your existing backend code. They focus on data integrity and tracking rather than counter management, which is already handled by your Django models.

For questions or issues, refer to:
- MySQL Trigger Documentation: https://dev.mysql.com/doc/refman/8.0/en/triggers.html
- Django Signals Documentation: https://docs.djangoproject.com/en/stable/topics/signals/
