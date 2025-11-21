# Notification 500 Error Fix

## Problem
When opening the notifications page, you got:
- **500 Internal Server Error** from backend
- **React error**: "Objects are not valid as a React child"

## Root Cause

### Backend Issue
The `NotificationUserSerializer` was trying to access `profile_image_url` and `full_name` as model fields, but:
- `full_name` is a `@property` method
- `profile_image_url` doesn't exist (it's `get_profile_image_url()` method)

This caused the serializer to fail when trying to serialize user data in notifications.

### Frontend Issue
The error handling was trying to render an error object directly in the toast description instead of extracting the error message string.

## Fixes Applied

### 1. Backend Fix - Notification Serializer
**File:** `backend/apps/notifications/serializers.py`

```python
class NotificationUserSerializer(serializers.ModelSerializer):
    """Serializer for user in notifications."""
    full_name = serializers.ReadOnlyField()  # ✅ Added as ReadOnlyField
    profile_image_url = serializers.SerializerMethodField()  # ✅ Added as SerializerMethodField
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'full_name', 'profile_image_url']
    
    def get_profile_image_url(self, obj):
        """Get profile image URL."""
        return obj.get_profile_image_url()  # ✅ Call the method
```

### 2. Frontend Fix - Error Handling
**File:** `frontend/src/pages/Notifications.tsx`

```typescript
const fetchNotifications = async () => {
  setIsLoading(true);
  try {
    const response = await notificationService.getNotifications();
    setNotifications(response.results);
  } catch (error: any) {
    console.error('Failed to fetch notifications:', error);
    // ✅ Properly extract error message
    const errorMessage = typeof error.response?.data?.error === 'string' 
      ? error.response.data.error 
      : error.response?.data?.message || error.message || 'Please try again later';
    
    toast({
      title: 'Failed to load notifications',
      description: errorMessage,  // ✅ Always a string now
      variant: 'destructive',
    });
  } finally {
    setIsLoading(false);
  }
};
```

## Testing

### 1. Restart Backend
```bash
cd backend
python manage.py runserver
```

### 2. Test Notifications Page
1. Open the app in browser
2. Navigate to `/notifications`
3. Should load without errors
4. Notifications should display properly

### 3. Verify User Data
Check that each notification shows:
- User's full name
- User's profile image (if they have one)
- Notification content
- Timestamp

## What Was Wrong

### Before (Broken):
```python
# Serializer tried to access fields that don't exist
fields = ['full_name', 'profile_image_url']
# Django couldn't find these as model fields → 500 error
```

### After (Fixed):
```python
# Properly defined as computed fields
full_name = serializers.ReadOnlyField()  # Uses @property
profile_image_url = serializers.SerializerMethodField()  # Uses method
```

## Related Files Modified

1. `backend/apps/notifications/serializers.py` - Fixed serializer
2. `frontend/src/pages/Notifications.tsx` - Fixed error handling

## Prevention

To avoid similar issues in the future:

1. **Always check if a field is a property or method** before adding to serializer
2. **Use `SerializerMethodField` for computed values**
3. **Use `ReadOnlyField` for `@property` methods**
4. **Test serializers with actual data** before deploying
5. **Handle errors properly in frontend** - never render objects directly

## Verification Checklist

- [ ] Backend starts without errors
- [ ] Notifications page loads
- [ ] User data displays correctly
- [ ] Profile images show (if user has one)
- [ ] No console errors
- [ ] Error messages display properly if API fails

## If Still Having Issues

1. **Check backend logs:**
   ```bash
   # Look for Python errors
   tail -f backend/logs/linkup.log
   ```

2. **Check browser console:**
   - Look for network errors
   - Check API response in Network tab

3. **Verify database:**
   ```sql
   -- Check if notifications exist
   SELECT * FROM notifications LIMIT 5;
   ```

4. **Test API directly:**
   ```bash
   curl -H "Authorization: Bearer YOUR_TOKEN" \
        http://localhost:8000/api/v1/notifications/
   ```

## Summary

✅ Fixed serializer to properly handle user properties
✅ Fixed frontend error handling to display strings only
✅ Notifications page should now work correctly
