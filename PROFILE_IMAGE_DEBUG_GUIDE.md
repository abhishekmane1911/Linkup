# Profile Image Upload & Display - Debug Guide

## Issues Reported
1. Profile picture not visible in Edit Profile modal
2. Uploading new banner and profile pic not working

## Debug Steps Added

### 1. Console Logging
Added comprehensive logging to track the data flow:

**EditProfileModal.tsx:**
```typescript
console.log('EditProfileModal - User data:', user);
console.log('Profile image URL:', user.profile_image_url);
console.log('Banner image URL:', user.banner_image_url);
```

**ImageUpload.tsx:**
```typescript
console.log(`ImageUpload (${type}) - currentImage:`, currentImage);
```

**userService.ts** (already has):
```typescript
console.log('updateProfileImage called with file:', imageFile);
console.log('FormData entries:', ...);
console.log('Profile image update response:', response.data);
```

### 2. What to Check

#### Open Browser Console and Check:

1. **When Edit Profile Modal Opens:**
   ```
   EditProfileModal - User data: {id: 5, username: "abhishek123", ...}
   Profile image URL: http://localhost:8000/media/profile_images/...
   Banner image URL: null
   ImageUpload (profile) - currentImage: http://localhost:8000/media/...
   ImageUpload (banner) - currentImage: null
   ```

2. **When Uploading Image:**
   ```
   Uploading file: image.jpg Size: 123456 Type: image/jpeg
   Uploading profile image...
   updateProfileImage called with file: File {...}
   FormData entries: profile_image File {...}
   Profile image update response: {...}
   Upload successful
   Profile image uploaded, response: {...}
   ```

## Possible Issues & Solutions

### Issue 1: Images Not Displaying

**Symptom:** Modal opens but images don't show

**Possible Causes:**
1. `user.profile_image_url` is undefined or null
2. URL is incorrect or inaccessible
3. CORS issue

**Check:**
```javascript
// In console when modal opens
console.log(user.profile_image_url);
// Should show: "http://localhost:8000/media/profile_images/..."
```

**Solution:**
- If undefined: Backend not returning `profile_image_url`
- If null: User has no image (expected)
- If URL exists but image doesn't load: Check if URL is accessible

### Issue 2: Upload Not Working

**Symptom:** Click upload, select file, but nothing happens

**Possible Causes:**
1. FormData not being sent correctly
2. Backend not accepting the upload
3. Response not being handled

**Check Console For:**
```
Uploading profile image...
updateProfileImage called with file: File {...}
```

**If you see an error:**
- Check the error message
- Check Network tab for the request
- Check response status and body

### Issue 3: Upload Success But Image Not Updating

**Symptom:** Upload succeeds but image doesn't change

**Possible Causes:**
1. Response doesn't include updated image URL
2. State not updating correctly
3. Component not re-rendering

**Check:**
```javascript
// After upload
console.log('Profile image update response:', response.data);
// Should include: profile_image_url: "http://..."
```

## Testing Checklist

### Test 1: Check User Data
```
1. Open Edit Profile modal
2. Check console for user data
3. Verify profile_image_url and banner_image_url are present
4. If null, that's OK (no image uploaded yet)
5. If undefined, there's a problem with the API response
```

### Test 2: Check Image Display
```
1. If user has images, they should display in the modal
2. If no images, should show camera icon placeholder
3. Hover over image area - should show "Change" button
```

### Test 3: Upload Profile Image
```
1. Click on profile image area
2. Select an image file
3. Check console for upload logs
4. Should see "Upload successful"
5. Should see success toast
6. Image should update immediately
```

### Test 4: Upload Banner Image
```
1. Click on banner image area
2. Select an image file
3. Check console for upload logs
4. Should see "Upload successful"
5. Should see success toast
6. Image should update immediately
```

## Network Tab Inspection

### Check the PATCH Request

1. **Open Network tab**
2. **Upload an image**
3. **Find request to `/api/v1/auth/profile/`**
4. **Check:**

**Request Headers:**
```
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary...
Authorization: Bearer eyJ...
```

**Request Payload:**
```
------WebKitFormBoundary...
Content-Disposition: form-data; name="profile_image"; filename="image.jpg"
Content-Type: image/jpeg

[binary data]
------WebKitFormBoundary...
```

**Response (200 OK):**
```json
{
  "id": 5,
  "username": "abhishek123",
  "profile_image_url": "http://localhost:8000/media/profile_images/image_new.jpg",
  "banner_image_url": null,
  ...
}
```

## Common Problems

### Problem 1: "profile_image_url is undefined"

**Cause:** Backend not returning the field

**Solution:**
1. Restart Django server
2. Check serializer includes `profile_image_url` in fields
3. Check model has `get_profile_image_url()` method

### Problem 2: "Upload says success but image doesn't change"

**Cause:** Response not updating state

**Solution:**
Check if response includes the new URL:
```javascript
console.log('Response:', response.data);
console.log('New URL:', response.data.profile_image_url);
```

### Problem 3: "Image shows broken/404"

**Cause:** URL is wrong or file doesn't exist

**Solution:**
1. Check if file exists: `ls backend/media/profile_images/`
2. Check if URL is correct
3. Check if media files are being served

### Problem 4: "CORS error"

**Cause:** Media files not accessible from frontend

**Solution:**
1. Check Django is serving media files
2. Check CORS settings
3. Try accessing image URL directly in browser

## What to Share for Debugging

Please share:

1. **Console Output:**
   - All logs when opening modal
   - All logs when uploading image
   - Any error messages

2. **Network Tab:**
   - Screenshot of the PATCH request
   - Request headers
   - Request payload
   - Response status
   - Response body

3. **Current Behavior:**
   - What happens when you open Edit Profile?
   - What happens when you click to upload?
   - What happens after selecting a file?
   - Do you see any error messages?

4. **Expected vs Actual:**
   - What you expect to see
   - What you actually see

## Quick Fixes to Try

### Fix 1: Clear Browser Cache
```
1. Hard refresh: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
2. Clear cache and reload
```

### Fix 2: Restart Django Server
```bash
cd backend
python manage.py runserver
```

### Fix 3: Check File Permissions
```bash
cd backend
ls -la media/profile_images/
# Should be writable
```

### Fix 4: Test Upload with cURL
```bash
TOKEN="your_jwt_token"
curl -X PATCH http://localhost:8000/api/v1/auth/profile/ \
  -H "Authorization: Bearer $TOKEN" \
  -F "profile_image=@/path/to/test.jpg"
```

## Next Steps

1. **Open Edit Profile modal**
2. **Open Browser Console (F12)**
3. **Copy all console output**
4. **Try uploading an image**
5. **Copy all console output after upload**
6. **Share the output**

This will help identify exactly where the issue is!
