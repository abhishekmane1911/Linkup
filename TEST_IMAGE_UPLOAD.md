# Image Upload Testing Guide

## Current Status
- ✅ Media directories exist (`media/profile_images/`, `media/banner_images/`)
- ✅ Files are being saved to disk (found existing uploads)
- ✅ Serializer includes `profile_image` and `banner_image` fields
- ✅ Model has ImageField for both fields
- ✅ MEDIA_URL and MEDIA_ROOT configured
- ✅ Media files served in development mode
- ⚠️ Frontend removed manual Content-Type header (axios sets it automatically)

## Testing Steps

### 1. Check Browser Console
When you upload an image, check for these logs:
```
Uploading file: example.jpg Size: 123456 Type: image/jpeg
updateProfileImage called with file: File {...}
FormData entries:
profile_image File {...}
```

### 2. Check Network Tab
Look for the PATCH request to `/api/v1/auth/profile/`:
- **Request Headers**: Should have `Content-Type: multipart/form-data; boundary=----...`
- **Request Payload**: Should show the image file
- **Response Status**: Should be 200 OK
- **Response Body**: Should include updated user object with image URLs

### 3. Check Backend Logs
In your Django server terminal, you should see:
```
"PATCH /api/v1/auth/profile/ HTTP/1.1" 200
```

### 4. Check Database
After upload, verify the database has the image path:
```sql
SELECT id, username, profile_image, banner_image 
FROM authentication_user 
WHERE id = YOUR_USER_ID;
```

Should show something like:
```
profile_image: profile_images/example_abc123.jpg
banner_image: banner_images/banner_xyz789.jpg
```

### 5. Check File System
```bash
ls -la backend/media/profile_images/
ls -la backend/media/banner_images/
```

Should show your uploaded files with recent timestamps.

## Common Issues & Solutions

### Issue 1: "Profile updated" but image not saved

**Possible Causes**:
1. FormData not being sent correctly
2. Backend not parsing multipart data
3. Serializer not saving the file
4. File permissions issue

**Debug Steps**:
```javascript
// In browser console after upload attempt:
// 1. Check what was sent
console.log('FormData was sent with profile_image field');

// 2. Check response
console.log('Response:', response.data);
console.log('Profile image in response:', response.data.profile_image);
console.log('Profile image URL:', response.data.profile_image_url);
```

### Issue 2: Image uploads but doesn't display

**Possible Causes**:
1. MEDIA_URL not configured correctly
2. Image URL not being returned
3. CORS issue with media files
4. Image path incorrect

**Check**:
```python
# In Django shell
from apps.authentication.models import User
user = User.objects.get(id=YOUR_ID)
print(f"Profile image field: {user.profile_image}")
print(f"Profile image URL: {user.get_profile_image_url()}")
print(f"File exists: {user.profile_image.storage.exists(user.profile_image.name)}")
```

### Issue 3: 400 Bad Request

**Possible Causes**:
1. Field name mismatch
2. File too large
3. Invalid file type
4. Missing CSRF token

**Solution**:
- Check field names match: `profile_image` and `banner_image`
- Check file size < 5MB (frontend validation)
- Check file type is image/*
- Ensure auth token is being sent

## Manual Testing with cURL

### Test Profile Image Upload
```bash
# Get your auth token first
TOKEN="your_jwt_token_here"

# Upload profile image
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "profile_image=@/path/to/your/image.jpg"
```

### Test Banner Image Upload
```bash
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "banner_image=@/path/to/your/banner.jpg"
```

### Expected Response
```json
{
  "id": 1,
  "username": "john_doe",
  "profile_image": "profile_images/image_abc123.jpg",
  "profile_image_url": "http://localhost:8000/media/profile_images/image_abc123.jpg",
  "banner_image": "banner_images/banner_xyz789.jpg",
  "banner_image_url": "http://localhost:8000/media/banner_images/banner_xyz789.jpg",
  ...
}
```

## Debugging Checklist

### Frontend
- [ ] File is selected correctly
- [ ] FormData is created with correct field name
- [ ] No manual Content-Type header (let axios set it)
- [ ] Auth token is included in request
- [ ] Request reaches the server (check Network tab)
- [ ] Response is received (check console logs)

### Backend
- [ ] Endpoint receives the request
- [ ] User is authenticated
- [ ] Multipart data is parsed
- [ ] File is saved to disk
- [ ] Database is updated
- [ ] Response includes image URLs
- [ ] Media files are accessible

### Configuration
- [ ] MEDIA_URL = "/media/"
- [ ] MEDIA_ROOT = BASE_DIR / "media"
- [ ] urlpatterns includes static() for media
- [ ] Pillow is installed
- [ ] Media directories exist and are writable

## What to Check Next

1. **Open browser DevTools**
2. **Go to Network tab**
3. **Try uploading an image**
4. **Find the PATCH request to `/api/v1/auth/profile/`**
5. **Check:**
   - Request Headers (Content-Type should have boundary)
   - Request Payload (should show the file)
   - Response Status (should be 200)
   - Response Body (should have image URLs)

6. **Share the following**:
   - Console logs
   - Network request details
   - Response body
   - Any error messages

## Expected Working Flow

```
1. User selects image file
   ↓
2. Frontend creates FormData with file
   ↓
3. Axios sends PATCH request (auto-sets Content-Type with boundary)
   ↓
4. Django receives multipart request
   ↓
5. DRF parses the file
   ↓
6. Serializer validates and saves
   ↓
7. File saved to media/profile_images/
   ↓
8. Database updated with file path
   ↓
9. Response returns with image URLs
   ↓
10. Frontend updates UI
   ↓
11. Image displays on page
```

## Next Steps

Please try uploading an image and share:
1. **Browser console output** (all the logs)
2. **Network tab details** (request and response)
3. **Any error messages**

This will help me identify exactly where the issue is occurring!
