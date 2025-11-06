# WhatsApp Messages Not Received - Troubleshooting Guide

## ✅ Webhooks Are NOT Required

**Important:** Webhooks are **NOT needed** for sending messages. They're only required if you want to:
- Receive incoming messages from users
- Get delivery status updates

For sending expiry alerts, webhooks are **optional**.

## If Test Number is Added But Still Not Receiving Messages

### 1. Check WhatsApp Spam/Archived Messages

WhatsApp might have filtered the messages:
- Open WhatsApp on `+919811546101`
- Check **"Archived"** chats (swipe down in chat list)
- Check **"Spam"** or filtered messages
- Look for messages from an unknown number (Meta's WhatsApp Business number)

### 2. Verify Access Token Hasn't Expired

**Temporary access tokens expire in 24 hours!**

- Go to Meta for Developers → WhatsApp → API Setup
- Check if your token is still valid
- If expired, generate a new one:
  - Click "Generate access token" or "Temporary access token"
  - Copy the new token
  - Update `WHATSAPP_ACCESS_TOKEN` in Railway variables
  - Redeploy your service

### 3. Check Meta Business Suite for Delivery Status

1. Go to: https://business.facebook.com/
2. Select your business account
3. Navigate to **"Inbox"** or **"Messages"**
4. Look for your WhatsApp messages
5. Check delivery status:
   - ✅ **Delivered** = Message was sent successfully
   - ❌ **Failed** = There's an error (check error details)
   - ⏳ **Pending** = Still being processed

### 4. Verify Test Number Format

Make sure the test number in Meta matches exactly:
- Database: `+919811546101`
- Meta test number: `+919811546101`
- **No spaces, dashes, or extra characters**

### 5. Wait for Delivery

Sometimes there's a delay:
- Messages can take 1-2 minutes to arrive
- Try logging in again after a few minutes
- Check if messages arrive later

### 6. Check Railway Logs for Errors

Look for any new error messages in Railway logs:
- Check for authentication errors
- Check for rate limiting errors
- Check for any API errors

### 7. Test with Meta's Test Template

Try sending a message using Meta's test template in the API Setup page:
- This confirms your setup is correct
- If this works but your app doesn't, there's a code issue
- If this doesn't work, there's a Meta configuration issue

## Common Issues

### Issue: Access Token Expired
**Symptom:** Messages stop working after 24 hours
**Solution:** Generate a new temporary token or create a permanent token

### Issue: Rate Limiting
**Symptom:** Some messages work, others don't
**Solution:** Wait a few minutes between sending multiple messages

### Issue: Number Format Mismatch
**Symptom:** API accepts but no delivery
**Solution:** Ensure database and Meta test number match exactly

### Issue: Messages in Spam
**Symptom:** API shows success but no message visible
**Solution:** Check archived/spam folders in WhatsApp

## Quick Verification Steps

1. ✅ Test number added in Meta: `+919811546101`
2. ✅ Access token is valid (not expired)
3. ✅ Phone number in database: `+919811546101`
4. ✅ Checked WhatsApp spam/archived messages
5. ✅ Checked Meta Business Suite for delivery status
6. ✅ Waited 1-2 minutes for delivery

## Still Not Working?

If you've checked all the above:
1. Try the test endpoint: `POST /user/test-whatsapp` with your user ID
2. Check Meta Business Suite for specific error messages
3. Verify your WhatsApp Business account is active
4. Try removing and re-adding the test number
5. Generate a fresh access token

## Next Steps

Once messages are working:
- Consider setting up webhooks for delivery status (optional)
- Generate a permanent access token (instead of temporary)
- Add more test numbers for team members

