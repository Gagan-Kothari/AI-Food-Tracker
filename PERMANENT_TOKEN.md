# How to Create a Permanent Access Token (Development Mode)

## Yes, You Can Create a Permanent Token in Development!

Even in development mode, you can create a **long-lived access token** that lasts 60 days (instead of 24 hours). This is much better for development!

## Step-by-Step Guide

### Method 1: Using Access Token Tool (Easiest)

1. **Go to Access Token Tool:**
   - Visit: https://developers.facebook.com/tools/explorer/
   - Or go to: Meta for Developers → Tools → Graph API Explorer

2. **Select Your App:**
   - In the top right, click the dropdown next to "Meta App"
   - Select your WhatsApp app

3. **Get User Access Token:**
   - Click "Generate Access Token" button
   - Select permissions:
     - `whatsapp_business_messaging`
     - `whatsapp_business_management`
   - Click "Generate Access Token"
   - Copy the token (this is a short-lived token)

4. **Extend Token to Long-Lived:**
   - In the same tool, look for "Access Token" section
   - Click the "i" (info) icon next to your token
   - Look for "Extend Access Token" or "Make Long-Lived Token"
   - Click it to extend to 60 days
   - Copy the new long-lived token

5. **Update in Railway:**
   - Go to Railway → Your Service → Variables
   - Update `WHATSAPP_ACCESS_TOKEN` with the new long-lived token
   - Save (auto-redeploys)

### Method 2: Using Graph API (More Control)

1. **Get Short-Lived Token First:**
   - Go to Meta for Developers → WhatsApp → API Setup
   - Copy the "Temporary access token"

2. **Extend Token via API:**
   - Use this endpoint:
   ```
   GET https://graph.facebook.com/v21.0/oauth/access_token?
     grant_type=fb_exchange_token&
     client_id=YOUR_APP_ID&
     client_secret=YOUR_APP_SECRET&
     fb_exchange_token=YOUR_SHORT_LIVED_TOKEN
   ```

3. **Get Your App ID and Secret:**
   - Go to Meta for Developers → Your App → Settings → Basic
   - Copy "App ID" and "App Secret"

4. **Make the Request:**
   - Use curl, Postman, or browser:
   ```
   https://graph.facebook.com/v21.0/oauth/access_token?grant_type=fb_exchange_token&client_id=YOUR_APP_ID&client_secret=YOUR_APP_SECRET&fb_exchange_token=YOUR_TEMP_TOKEN
   ```

5. **Response:**
   ```json
   {
     "access_token": "LONG_LIVED_TOKEN",
     "token_type": "bearer",
     "expires_in": 5183944
   }
   ```
   - `expires_in` is in seconds (60 days = ~5,184,000 seconds)

6. **Update in Railway:**
   - Copy the `access_token` from response
   - Update `WHATSAPP_ACCESS_TOKEN` in Railway

### Method 3: Using Meta Business Suite (If You Have Business Account)

1. **Go to Meta Business Suite:**
   - Visit: https://business.facebook.com/
   - Select your business account

2. **Navigate to System Users:**
   - Settings → Business Settings → System Users
   - Create or select a system user

3. **Assign WhatsApp Permissions:**
   - Add WhatsApp permissions to the system user
   - Generate a token for the system user
   - This token can be long-lived

4. **Copy Token:**
   - Copy the generated token
   - Update in Railway

## Token Types Explained

### Short-Lived Token (Temporary)
- **Duration:** 1-2 hours (sometimes 24 hours)
- **Where:** Meta for Developers → WhatsApp → API Setup → "Temporary access token"
- **Use:** Quick testing
- **Problem:** Expires quickly, needs frequent renewal

### Long-Lived Token
- **Duration:** 60 days
- **How to get:** Extend short-lived token using methods above
- **Use:** Development and testing
- **Benefit:** Lasts 60 days, much more convenient

### Permanent Token (System User)
- **Duration:** Never expires (unless revoked)
- **How to get:** Create system user in Business Settings
- **Use:** Production
- **Requirement:** Business verification usually needed

## For Development: Use Long-Lived Token (60 Days)

**Recommended:** Use Method 1 (Graph API Explorer) - it's the easiest!

## Quick Steps (Recommended)

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app
3. Generate access token with WhatsApp permissions
4. Extend to long-lived (60 days)
5. Copy the token
6. Update `WHATSAPP_ACCESS_TOKEN` in Railway
7. Done! Token lasts 60 days

## Verify Token Expiration

After getting your token, you can check expiration:

```
GET https://graph.facebook.com/v21.0/debug_token?
  input_token=YOUR_TOKEN&
  access_token=YOUR_TOKEN
```

Response shows:
```json
{
  "data": {
    "expires_at": 1234567890,  // Unix timestamp
    "is_valid": true
  }
}
```

## Important Notes

1. **Token Still Expires:** Long-lived tokens expire in 60 days (not permanent)
2. **Refresh Before Expiry:** Set a reminder to refresh before 60 days
3. **Keep Token Secret:** Never commit tokens to Git
4. **Revoke if Compromised:** If token is exposed, revoke it immediately

## Troubleshooting

### "Token expired" error
- Generate a new long-lived token
- Update in Railway
- Redeploy

### "Invalid token" error
- Verify token is correct (no extra spaces)
- Check token has WhatsApp permissions
- Generate a new token

### "Insufficient permissions" error
- Make sure token has:
  - `whatsapp_business_messaging`
  - `whatsapp_business_management`

## After Creating Long-Lived Token

1. ✅ Update `WHATSAPP_ACCESS_TOKEN` in Railway
2. ✅ Wait for auto-redeploy (or manually redeploy)
3. ✅ Test by logging in
4. ✅ Check if messages arrive now
5. ✅ Set calendar reminder for 55 days to refresh token

## Next Steps

Once you have a long-lived token:
- Your WhatsApp notifications should work reliably
- No need to refresh every 24 hours
- Focus on testing your app features
- When ready for production, create a system user token

