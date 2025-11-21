# Image Upload Troubleshooting Guide

## Issue
Images appear to upload successfully (success message shows) but are not actually saved to the database or displayed.

## Changes Made to Fix

### 1. Removed Manual Content-Type Headers
**Problem**: Setting `Content-Type: multipart/form-data` manually prevents axios from adding the required boundary parameter.

**Fix**: Let axios automatically set the Content-Type header with the correct boundary.

```typescript
// BEFORE (WRONG)
const response = await api.patch('/auth/profile/', formData, {
  headers: {
    'Content-Type': 'multipart/form-data',  // ❌ Missing boundary
  },
});

// AFTER (CORRECT)
const response = await api.patch('/auth/profile/', formData);  // ✅ Axios adds boundary automatically
```

### 2. Added Debug Logging
Added console.log statements to track the upload process:
- File information (name, size, type)
- FormData contents
- API response
- Error details

## How to Test

### 1. Open Browser Console
Press F12 or right-click → Inspect → Console tab

### 2. Upload an Image
1. Go to your profile
2. Click "Edit Profile"
3. Click on profile or banner image
4. Select an image file

### 3. Check Console Output
You should see:
```
Uploading file: example.jpg Size: 123456 Type: image/jpeg
updateProfileImage called with file: File {...}
FormData entries:
profile_image File {...}
Profile image update response: {...}
Upload successful
```

### 4. Check Network Tab
1. Open Network tab in browser dev tools
2. Upload an image
3. Find the PATCH request to `/api/v1/auth/profile/`
4. Check:
   - Request Headers: Should have `Content-Type: multipart/form-data; boundary=----...`
   - Request Payload: Should show the image file
   - Response: Should return updated user object with image URLs

## Common Issues & Solutions

### Issue 1: "Profile updated" but no image
**Cause**: Content-Type header was set manually without boundary
**Solution**: ✅ Fixed - removed manual header

### Issue 2: CORS errors
**Cause**: Backend not configured to accept multipart requests
**Solution**: Check Django CORS settings

### Issue 3: 413 Request Entity Too Large
**Cause**: File size exceeds server limit
**Solution**: 
- Frontend validates max 5MB
- Check nginx/server config for upload limits

### Issue 4: 400 Bad Request
**Possible Causes**:
1. FormData not properly formatted
2. Field name mismatch (profile_image vs profileImage)
3. Backend serializer not accepting files

**Debug Steps**:
1. Check console logs for FormData contents
2. Verify field names match backend expectations
3. Check backend logs for validation errors

### Issue 5: Image uploads but doesn't display
**Possible Causes**:
1. MEDIA_URL not configured correctly
2. Media files not being served in development
3. Image URL not being returned in API response

**Solution**:
```python
# backend/linkup_backend/urls.py
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

## Backend Verification

### 1. Check Media Configuration
```python
# backend/linkup_backend/settings/base.py
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"
```

### 2. Check URL Configuration
```python
# backend/linkup_backend/urls.py
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 3. Check Model Fields
```python
# backend/apps/authentication/models.py
profile_image = models.ImageField(upload_to='profile_images/', ...)
banner_image = models.ImageField(upload_to='banner_images/', ...)
```

### 4. Check Serializer
```python
# backend/apps/authentication/serializers.py
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        fields = (..., 'profile_image', 'banner_image', ...)
```

### 5. Check Pillow Installation
```bash
cd backend
pip list | grep Pillow
# Should show: Pillow==10.1.0
```

### 6. Check Media Directory Permissions
```bash
cd backend
ls -la media/
# Should show writable directories
```

## Testing the Fix

### Test 1: Profile Image Upload
1. Go to your profile
2. Click "Edit Profile"
3. Upload a profile image
4. Check console for logs
5. Refresh page - image should display
6. Check database - profile_image field should have value

### Test 2: Banner Image Upload
1. Go to your profile
2. Click "Edit Profile"
3. Upload a banner image
4. Check console for logs
5. Refresh page - banner should display
6. Check database - banner_image field should have value

### Test 3: Community Banner Upload
1. Go to a community you own
2. Click settings icon
3. Upload a banner image
4. Check console for logs
5. Refresh page - banner should display
6. Check database - banner_image field should have value

## Expected API Response

After successful upload, the API should return:
```json
{
  "id": 1,
  "username": "john_doe",
  "profile_image": "profile_images/example_abc123.jpg",
  "profile_image_url": "http://localhost:8000/media/profile_images/example_abc123.jpg",
  "banner_image": "banner_images/banner_xyz789.jpg",
  "banner_image_url": "http://localhost:8000/media/banner_images/banner_xyz789.jpg",
  ...
}
```

## If Still Not Working

### 1. Check Backend Logs
```bash
cd backend
python manage.py runserver
# Watch for errors when uploading
```

### 2. Test with cURL
```bash
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "profile_image=@/path/to/image.jpg"
```

### 3. Check File System
```bash
cd backend/media/profile_images
ls -la
# Should see uploaded files
```

### 4. Check Database
```sql
SELECT id, username, profile_image, banner_image FROM authentication_user WHERE id = YOUR_USER_ID;
```

## Success Indicators

✅ Console shows "Upload successful"
✅ Network tab shows 200 OK response
✅ Response includes image URLs
✅ Image file exists in media directory
✅ Database field is updated
✅ Image displays on page refresh
✅ No errors in browser console
✅ No errors in backend logs

## Next Steps

After verifying the fix works:
1. Remove debug console.log statements
2. Test on different browsers
3. Test with different image formats (JPG, PNG, GIF)
4. Test with different file sizes
5. Test error cases (invalid files, too large, etc.)
