# WhatsApp Notification Troubleshooting Guide

## Quick Test

I've added a test endpoint to help debug WhatsApp notifications. Use this to test if notifications are working:

### Test Endpoint

**POST** `/user/test-whatsapp`

**Request Body:**
```json
{
  "userid": 1
}
```

**Response:**
```json
{
  "status": true/false,
  "message": "Result message",
  "user_phone": "+919943434...",
  "whatsapp_result": {...}
}
```

## Debug Logging

I've added comprehensive debug logging. Check your **Railway logs** or **console output** to see:

1. **Phone Number Formatting:**
   - `DEBUG: Formatting phone number. Original: '+919943434...'`
   - `DEBUG: Formatted phone number: '+919943434...'`

2. **Message Sending:**
   - `DEBUG: Sending WhatsApp message to: +919943434...`
   - `DEBUG: WhatsApp API URL: ...`
   - `DEBUG: Response status code: 200`
   - `SUCCESS: WhatsApp message sent. Message ID: ...`

3. **Errors:**
   - `ERROR: Failed to send WhatsApp message. Status: 400, Error: ...`
   - `EXCEPTION: Error sending WhatsApp message: ...`

## Common Issues & Solutions

### Issue 1: Phone Number Not in Database

**Symptom:** No notification sent, logs show "User has no phone number"

**Solution:**
1. Check your database - ensure the user has a `phone_number` field set
2. Phone number should be in E.164 format: `+919943434...` (with country code)
3. Update the user's phone number in the database

**SQL Query to Check:**
```sql
SELECT id, name, email, phone_number FROM users WHERE id = YOUR_USER_ID;
```

**SQL Query to Update:**
```sql
UPDATE users SET phone_number = '+919943434...' WHERE id = YOUR_USER_ID;
```

### Issue 2: Phone Number Format Wrong

**Symptom:** Error message about invalid phone number

**Solution:**
- Phone number must be in **E.164 format**: `+[country code][number]`
- For India: `+91` followed by 10 digits (e.g., `+919876543210`)
- Remove spaces, dashes, parentheses
- Must start with `+`

**Examples:**
- ✅ Correct: `+919876543210`
- ✅ Correct: `+1234567890`
- ❌ Wrong: `919876543210` (missing +)
- ❌ Wrong: `+91 9876543210` (has space)
- ❌ Wrong: `9876543210` (missing country code)

### Issue 3: API Returns Success But No Message Received

**Symptom:** Logs show `SUCCESS: WhatsApp message sent` with status 200, but no message on phone

**This is the most common issue!** The API accepts the message, but WhatsApp can't deliver it.

**Solution:**
1. **Verify test number in Meta:**
   - Go to Meta for Developers → WhatsApp → API Setup
   - Scroll to "To" section (or "Test phone numbers")
   - Check if your phone number `+919811546101` is listed there
   - If not, click "Add phone number" → "Add test number"
   - Enter: `+919811546101` (exactly as in database)
   - Verify with code sent to WhatsApp

2. **Check phone number format:**
   - Database: `+919811546101` ✅ (correct format)
   - Must match test number in Meta exactly
   - No spaces, dashes, or extra characters

3. **Verify the number is registered with WhatsApp:**
   - The phone number must be registered with WhatsApp
   - You should be able to receive messages on this number normally

4. **Check Meta Business Suite:**
   - Go to https://business.facebook.com/
   - Check message logs to see delivery status
   - Look for any error messages

**Common causes:**
- Phone number not added as test number in Meta
- Phone number format mismatch (database vs Meta)
- Phone number not registered with WhatsApp
- Test number verification expired (re-verify if needed)

### Issue 4: Credentials Not Set

**Symptom:** Logs show "WhatsApp credentials not configured"

**Solution:**
1. Check Railway environment variables:
   - `WHATSAPP_ACCESS_TOKEN` - Your access token
   - `WHATSAPP_PHONE_NUMBER_ID` - Your phone number ID
2. Verify they're set correctly (no extra spaces)
3. Redeploy after adding variables

### Issue 5: Access Token Expired

**Symptom:** Error code 190 or "Invalid OAuth access token"

**Solution:**
1. Temporary tokens expire in 24 hours
2. Go to Meta for Developers → WhatsApp → API Setup
3. Generate a new temporary access token
4. Update `WHATSAPP_ACCESS_TOKEN` in Railway
5. Redeploy

## How to Check Logs

### On Railway:
1. Go to your Railway project
2. Click on your service
3. Go to **Deployments** tab
4. Click on the latest deployment
5. View **Logs** tab
6. Look for `DEBUG:` messages

### On Local:
- Check your terminal/console output
- Look for `DEBUG:`, `ERROR:`, `SUCCESS:` messages

## Step-by-Step Verification

1. **Check Database:**
   ```sql
   SELECT id, name, phone_number FROM users WHERE email = 'your@email.com';
   ```
   - Verify `phone_number` is set
   - Verify format is `+919943434...` (E.164)

2. **Check Environment Variables:**
   - Railway → Service → Variables
   - Verify `WHATSAPP_ACCESS_TOKEN` exists
   - Verify `WHATSAPP_PHONE_NUMBER_ID` exists

3. **Check Test Number in Meta:**
   - Meta for Developers → WhatsApp → API Setup
   - Verify your phone number is listed under "To" section
   - Must match database phone number exactly

4. **Test with Test Endpoint:**
   - Use Postman or your frontend
   - POST to `/user/test-whatsapp` with your userid
   - Check response and logs

5. **Check Logs:**
   - Look for `DEBUG:` messages
   - Check for any `ERROR:` messages
   - Verify phone number formatting

## Expected Log Output (Success)

```
DEBUG: User found with phone number: +919943434...
DEBUG: Formatting phone number. Original: '+919943434...'
DEBUG: Formatted phone number: '+919943434...'
DEBUG: Sending WhatsApp message to: +919943434...
DEBUG: WhatsApp API URL: https://graph.facebook.com/v21.0/...
DEBUG: Response status code: 200
SUCCESS: WhatsApp message sent. Message ID: wamid.xxx...
SUCCESS: WhatsApp ID (wa_id): 919943434...
SUCCESS: Contact info: {'input': '+919943434...', 'wa_id': '919943434...'}
```

**Important:** If you see `SUCCESS` but no `wa_id`, it means:
- The API accepted the message
- But WhatsApp couldn't deliver it (number not registered or not added as test number)

## Expected Log Output (Error)

```
DEBUG: User found with phone number: +919943434...
DEBUG: Formatting phone number. Original: '+919943434...'
ERROR: Failed to send WhatsApp message. Status: 400, Error: Invalid recipient phone number, Code: 1008
ERROR: Full error data: {...}
```

## Next Steps

1. **Test the endpoint** - Use `/user/test-whatsapp` to verify basic functionality
2. **Check logs** - Look for debug messages to see what's happening
3. **Verify phone number** - Ensure it's in E.164 format and added as test number
4. **Try a donation or recipe cook** - These will trigger notifications automatically

## Still Not Working?

If you're still having issues after checking all the above:

1. Share the **exact error message** from logs
2. Share the **phone number format** in your database (mask sensitive digits)
3. Share the **response from test endpoint**
4. Verify the phone number is **exactly the same** in:
   - Database
   - Meta test numbers
   - No extra spaces or characters

