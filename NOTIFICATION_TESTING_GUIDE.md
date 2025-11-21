# Notification System Testing Guide

## Prerequisites
- Backend server running
- Frontend development server running
- At least 2 user accounts for testing
- Some tweets posted

## Quick Test Scenarios

### 1. Test Like Notification

**Steps:**
1. Log in as User A
2. Post a tweet
3. Log out and log in as User B
4. Like User A's tweet
5. Log out and log in as User A
6. Click on "Notifications" in sidebar
7. Check the notification badge (should show "1")

**Expected Results:**
- ✅ Notification appears: "User B liked your tweet"
- ✅ Badge shows "1" on Notifications nav item
- ✅ Notification has blue background (unread)
- ✅ Tweet preview is shown
- ✅ Heart icon is displayed

---

### 2. Test Retweet Notification

**Steps:**
1. Log in as User A
2. Post a tweet
3. Log out and log in as User B
4. Retweet User A's tweet
5. Log out and log in as User A
6. Check notifications

**Expected Results:**
- ✅ Notification appears: "User B retweeted your tweet"
- ✅ Badge count increases
- ✅ Retweet icon (arrows) is displayed
- ✅ Tweet preview is shown

---

### 3. Test Follow Notification

**Steps:**
1. Log in as User B
2. Go to User A's profile
3. Click "Follow" button
4. Log out and log in as User A
5. Check notifications

**Expected Results:**
- ✅ Notification appears: "User B followed you"
- ✅ Badge count increases
- ✅ User plus icon is displayed
- ✅ No tweet preview (follow doesn't relate to a tweet)

---

### 4. Test Reply Notification

**Steps:**
1. Log in as User A
2. Post a tweet
3. Log out and log in as User B
4. Click on User A's tweet
5. Write a reply and post it
6. Log out and log in as User A
7. Check notifications

**Expected Results:**
- ✅ Notification appears: "User B replied to your tweet"
- ✅ Badge count increases
- ✅ Message icon is displayed
- ✅ Original tweet preview is shown

---

### 5. Test Mark as Read

**Steps:**
1. Have some unread notifications
2. Click on an unread notification (blue background)

**Expected Results:**
- ✅ Blue background disappears (marked as read)
- ✅ Badge count decreases by 1
- ✅ Notification stays in list

**Alternative - Mark All as Read:**
1. Have multiple unread notifications
2. Click "Mark all read" button in header

**Expected Results:**
- ✅ All notifications lose blue background
- ✅ Badge disappears (count becomes 0)
- ✅ All notifications stay in list

---

### 6. Test Delete Notification

**Steps:**
1. Have at least one notification
2. Hover over a notification
3. Click the trash icon on the right

**Expected Results:**
- ✅ Notification is removed from list
- ✅ Badge count updates if it was unread
- ✅ Smooth animation on removal

---

### 7. Test Badge Updates

**Steps:**
1. Log in as User A
2. Note the current badge count
3. In another browser/incognito, log in as User B
4. Like one of User A's tweets
5. Wait 30 seconds (polling interval)
6. Check User A's sidebar

**Expected Results:**
- ✅ Badge count increases after ~30 seconds
- ✅ Badge appears if it was 0 before

---

### 8. Test No Self-Notifications

**Steps:**
1. Log in as User A
2. Like your own tweet
3. Check notifications

**Expected Results:**
- ✅ No notification created
- ✅ Badge count doesn't change

**Repeat for:**
- Retweet your own tweet → No notification
- Reply to your own tweet → No notification
- Follow yourself (if possible) → No notification

---

### 9. Test Duplicate Prevention

**Steps:**
1. Log in as User B
2. Like User A's tweet
3. Unlike the tweet
4. Like it again
5. Log in as User A
6. Check notifications

**Expected Results:**
- ✅ Only ONE notification exists
- ✅ Badge shows "1" not "2"
- ✅ No duplicate notifications

---

### 10. Test Empty State

**Steps:**
1. Create a new user account
2. Log in
3. Go to Notifications page

**Expected Results:**
- ✅ Empty state message: "No notifications yet"
- ✅ Heart icon displayed
- ✅ Helpful text about when notifications appear

---

## API Testing (Optional)

### Test Get Notifications
```bash
# Get all notifications
curl -X GET http://localhost:8000/api/v1/notifications/ \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only unread
curl -X GET "http://localhost:8000/api/v1/notifications/?is_read=false" \
  -H "Authorization: Bearer YOUR_TOKEN"

# Get only read
curl -X GET "http://localhost:8000/api/v1/notifications/?is_read=true" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Get Unread Count
```bash
curl -X GET http://localhost:8000/api/v1/notifications/count/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Mark as Read
```bash
# Mark all as read
curl -X POST http://localhost:8000/api/v1/notifications/mark-read/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{}'

# Mark specific notifications as read
curl -X POST http://localhost:8000/api/v1/notifications/mark-read/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notification_ids": [1, 2, 3]}'
```

### Test Delete Notification
```bash
curl -X DELETE http://localhost:8000/api/v1/notifications/1/delete/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Test Clear All
```bash
curl -X DELETE http://localhost:8000/api/v1/notifications/clear/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Verification

### Check Notifications Table
```sql
-- View all notifications
SELECT * FROM notifications ORDER BY created_at DESC LIMIT 10;

-- Count by type
SELECT notification_type, COUNT(*) as count 
FROM notifications 
GROUP BY notification_type;

-- Check for duplicates (should be 0)
SELECT recipient_id, actor_id, notification_type, content_type_id, object_id, COUNT(*) 
FROM notifications 
GROUP BY recipient_id, actor_id, notification_type, content_type_id, object_id 
HAVING COUNT(*) > 1;

-- Unread notifications per user
SELECT recipient_id, COUNT(*) as unread_count 
FROM notifications 
WHERE is_read = FALSE 
GROUP BY recipient_id;
```

---

## Performance Testing

### Test with Many Notifications

1. Create 100+ notifications for a user
2. Navigate to Notifications page
3. Check loading time
4. Scroll through notifications
5. Test pagination

**Expected Results:**
- ✅ Page loads in < 2 seconds
- ✅ Smooth scrolling
- ✅ Pagination works correctly
- ✅ Badge shows correct count

---

## Common Issues & Solutions

### Issue: Badge not updating
**Solution:** 
- Wait 30 seconds (polling interval)
- Refresh the page
- Check browser console for errors

### Issue: Notifications not appearing
**Solution:**
- Check backend logs for signal errors
- Verify migrations ran successfully
- Check if notification was created in database
- Ensure user is not triggering their own actions

### Issue: Duplicate notifications
**Solution:**
- Check unique constraint in database
- Verify `create_notification()` uses `get_or_create()`
- Check database for actual duplicates

### Issue: Badge shows wrong count
**Solution:**
- Refresh the page
- Check API response: `/api/v1/notifications/count/`
- Verify database count matches

---

## Success Criteria

✅ All notification types work (like, retweet, follow, reply)
✅ Badge shows correct unread count
✅ Badge updates automatically (within 30 seconds)
✅ Notifications can be marked as read
✅ Notifications can be deleted
✅ No self-notifications created
✅ No duplicate notifications
✅ Empty state displays correctly
✅ Loading states work properly
✅ Timestamps are accurate
✅ Icons match notification types
✅ Tweet previews display correctly
✅ Pagination works (if > 20 notifications)

---

## Instructor Demonstration

To demonstrate the database trigger functionality to your instructor:

1. **Show the Signal Handlers** (`backend/apps/notifications/signals.py`)
   - Explain how Django signals act as database triggers
   - Show the `@receiver(post_save, sender=Like)` decorator
   - Explain it fires automatically when a Like is created

2. **Live Demonstration:**
   - Open Django admin or database viewer
   - Show empty notifications table
   - Perform an action (like a tweet)
   - Refresh database view
   - Show notification was automatically created

3. **Show the Unique Constraint:**
   - Show the `unique_together` in model
   - Try to create duplicate notification
   - Show it's prevented at database level

4. **Show the Indexes:**
   - Explain the indexes for performance
   - Show query execution plans (if needed)

---

## Additional Notes

- Notifications are created in real-time via Django signals
- Signals fire automatically when database records are created
- This is Django's implementation of database triggers
- The system prevents duplicates at the database level
- Badge updates every 30 seconds via polling
- All notifications are paginated for performance
- Soft-deleted tweets don't trigger notifications
