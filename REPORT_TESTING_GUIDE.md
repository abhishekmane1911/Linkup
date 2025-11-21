# Report Functionality Testing Guide

## Prerequisites
- Backend server running
- Frontend development server running
- At least 2 user accounts for testing
- Some tweets posted by different users

## Test Scenarios

### 1. Report a Tweet

#### Steps:
1. Log in to the application
2. Navigate to the home feed or any page with tweets
3. Find a tweet from another user (not your own)
4. Click the three-dot menu (⋯) on the tweet
5. Click "Report Tweet"
6. In the dialog that opens:
   - Select a report type (e.g., "Spam")
   - Enter a description (required, max 1000 characters)
   - Click "Submit Report"

#### Expected Results:
- ✅ Report dialog opens with tweet preview
- ✅ All 9 report types are visible
- ✅ Description field is required
- ✅ Character counter shows (0/1000)
- ✅ Submit button is disabled until description is entered
- ✅ Success toast appears: "Report submitted"
- ✅ Dialog closes automatically
- ✅ Report is saved in database

#### Edge Cases to Test:
- Try to submit without description → Should show error
- Try to report the same tweet again → Should show error "You have already reported this content"
- Try to report your own tweet → Report option should not appear in menu
- Enter 1001 characters → Should be limited to 1000

---

### 2. Report a User

#### Steps:
1. Log in to the application
2. Navigate to another user's profile (not your own)
3. Look for the flag icon button next to Follow/Message buttons
4. Click the flag icon
5. In the dialog that opens:
   - Select a report type (e.g., "Harassment")
   - Enter a description
   - Click "Submit Report"

#### Expected Results:
- ✅ Report dialog opens with username shown
- ✅ All 9 report types are visible
- ✅ Success toast appears after submission
- ✅ Dialog closes automatically
- ✅ Report is saved in database

#### Edge Cases to Test:
- Visit your own profile → Flag button should not appear
- Try to report the same user again → Should show error
- Try to report without description → Should show error

---

### 3. View My Reports

#### Steps:
1. Log in to the application
2. Navigate to `/reports` (or add a link in navigation)
3. View the list of your submitted reports

#### Expected Results:
- ✅ All your submitted reports are displayed
- ✅ Each report shows:
  - Content type (tweet/user) and ID
  - Report type badge
  - Description
  - Status badge with appropriate color
  - Submission date
  - Resolution date (if resolved)
- ✅ Tabs for filtering work correctly:
  - All
  - Pending
  - Under Review
  - Resolved
  - Dismissed
- ✅ Empty state shows when no reports match filter
- ✅ Loading spinner shows while fetching

#### Test Different Filters:
1. Click "Pending" tab → Should show only pending reports
2. Click "Under Review" tab → Should show only under review reports
3. Click "Resolved" tab → Should show only resolved reports
4. Click "Dismissed" tab → Should show only dismissed reports
5. Click "All" tab → Should show all reports

---

### 4. Status Badge Colors

Verify the status badges have correct colors:
- **Pending** → Yellow badge with clock icon ⏰
- **Under Review** → Blue badge with alert icon ⚠️
- **Resolved** → Green badge with checkmark icon ✓
- **Dismissed** → Gray badge with X icon ✗
- **Escalated** → Red badge with warning icon ⚠️

---

### 5. Backend Validation

#### Test Duplicate Prevention:
1. Report a tweet
2. Try to report the same tweet again
3. Expected: Error message "You have already reported this content"

#### Test Content Validation:
1. Try to report a non-existent tweet ID (via API)
2. Expected: Error message "Object with ID X does not exist"

#### Test Authentication:
1. Log out
2. Try to access `/reports` page
3. Expected: Redirect to login or error

---

## API Testing (Optional)

### Using curl or Postman:

#### Create a Report:
```bash
curl -X POST http://localhost:8000/api/v1/moderation/reports/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content_type": "tweet",
    "object_id": 1,
    "report_type": "spam",
    "description": "This is spam content"
  }'
```

#### Get My Reports:
```bash
curl -X GET http://localhost:8000/api/v1/moderation/my-reports/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Database Verification

### Check Reports Table:
```sql
SELECT * FROM reports ORDER BY created_at DESC LIMIT 10;
```

### Check for Duplicates:
```sql
SELECT reporter_id, content_type_id, object_id, COUNT(*) 
FROM reports 
GROUP BY reporter_id, content_type_id, object_id 
HAVING COUNT(*) > 1;
```
Expected: No results (duplicates prevented)

---

## Common Issues & Solutions

### Issue: "Report feature coming soon" toast appears
**Solution:** Make sure you've updated TweetCard.tsx with the new code

### Issue: Report dialog doesn't open
**Solution:** Check browser console for errors, ensure ReportDialog component is imported

### Issue: "Failed to submit report" error
**Solution:** 
- Check backend is running
- Verify authentication token is valid
- Check network tab for API response

### Issue: My Reports page is empty
**Solution:**
- Submit at least one report first
- Check API endpoint `/api/v1/moderation/my-reports/` is working
- Verify authentication

### Issue: Cannot report own content
**Solution:** This is expected behavior - users cannot report their own content

---

## Success Criteria

✅ Users can report tweets from other users
✅ Users can report other users from their profiles
✅ Users cannot report their own content
✅ Duplicate reports are prevented
✅ All 9 report types are available
✅ Description is required and limited to 1000 characters
✅ Success/error feedback is shown
✅ Users can view all their submitted reports
✅ Reports can be filtered by status
✅ Status badges show correct colors and icons
✅ Report details are displayed correctly
✅ Loading and empty states work properly

---

## Next Steps After Testing

1. **Add Navigation Link**
   - Add "My Reports" link to sidebar or user menu
   - Make it easily accessible

2. **Moderator Testing** (if implementing moderator UI)
   - Test report review workflow
   - Test status updates
   - Test moderation actions

3. **Performance Testing**
   - Test with many reports
   - Check pagination
   - Verify loading times

4. **Mobile Testing**
   - Test on mobile devices
   - Verify responsive design
   - Check touch interactions

---

## Reporting Bugs

If you find any issues during testing, please note:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Browser and version
- Console errors (if any)
- Network errors (if any)
