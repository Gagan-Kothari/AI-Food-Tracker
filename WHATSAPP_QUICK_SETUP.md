# WhatsApp Notification Service - Quick Setup Guide

## What You Need to Provide

To enable WhatsApp notifications for expiry alerts, you need to add the following environment variables to your `.env` file (or Railway environment variables):

### Required Environment Variables

```env
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
```

### Optional Environment Variables

```env
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_API_VERSION=v21.0
```

## How to Get These Values

### 1. WhatsApp Access Token (`WHATSAPP_ACCESS_TOKEN`)

**Steps:**
1. Go to https://developers.facebook.com/apps/
2. Select your app (or create a new one)
3. Navigate to **WhatsApp** → **API Setup**
4. Copy the **"Temporary access token"** for testing
   - ⚠️ Temporary tokens expire in 24 hours
5. For production, click **"Generate access token"** to create a permanent token

### 2. Phone Number ID (`WHATSAPP_PHONE_NUMBER_ID`)

**Steps:**
1. In the same **WhatsApp** → **API Setup** page
2. Look for **"Phone number ID"** or **"From"** field
3. Copy the numeric ID (e.g., `123456789012345`)

### 3. Business Account ID (`WHATSAPP_BUSINESS_ACCOUNT_ID`) - Optional

**Steps:**
1. In **WhatsApp** → **API Setup**
2. Look for **"Business Account ID"**
3. Copy the ID (only needed for certain operations)

## Prerequisites

Before you can get these credentials, you need:

1. **Meta Business Account**
   - Go to https://business.facebook.com/
   - Create or sign in to your account

2. **WhatsApp Business API Setup**
   - Go to https://developers.facebook.com/
   - Create a new app or use existing one
   - Add **"WhatsApp"** product to your app
   - Follow the setup wizard

3. **Test Phone Number** (for testing)
   - In WhatsApp → API Setup
   - Add a test phone number
   - This allows you to test without production verification

## Development Mode vs Production

### ✅ For Development/Testing (Current Setup)

**YES! You can skip payment and use test numbers only.**

You **DO NOT need** to complete all 6 steps. Here's what you need:

- ✅ **Step 1-2**: Basic setup (already done)
- ✅ **Step 4**: Learn API (code is already written)
- ✅ **Step 5**: Add test phone number (use Meta's test numbers)
- ❌ **Step 3 (Webhooks)**: **NOT REQUIRED** - Only needed if you want to receive incoming messages or status callbacks
- ❌ **Step 6 (Payment)**: **SKIP IT** - Test numbers work completely free without payment

**For development, you only need:**
1. Access Token (temporary is fine)
2. Phone Number ID
3. Test phone numbers (add them in Meta for Developers)

**Important:** With test numbers, you can only send messages to phone numbers you've added as test numbers. 

**Perfect for development:** Add your own phone number as a test number, and you can receive all the expiry alerts on your WhatsApp - completely free, no payment method needed!

### 🚀 For Production (Later)

When you're ready to go live, you'll need:

- ✅ **Step 3 (Webhooks)**: Set up if you want delivery status updates
- ✅ **Step 5**: Verify your business phone number
- ✅ **Step 6**: Add payment method (required for sending messages at scale)
- ✅ Business verification from Meta

## Where to Add These Variables

### For Local Development:
Add to your `.env` file in the project root:
```env
WHATSAPP_ACCESS_TOKEN=your_token
WHATSAPP_PHONE_NUMBER_ID=your_id
```

### For Railway Deployment:
1. Go to your Railway project dashboard
2. Navigate to your service → **Variables** tab
3. Add each variable:
   - `WHATSAPP_ACCESS_TOKEN` = your token
   - `WHATSAPP_PHONE_NUMBER_ID` = your ID
4. **Redeploy** your service (Railway will automatically redeploy when you add variables, or you can manually trigger it)
5. ✅ WhatsApp API will now work in deployment!

**Note:** The same test number limitations apply in deployment - you can only send to test numbers you've added in Meta for Developers.

## User Phone Number Format

Users in your database must have phone numbers in **E.164 format**:
- Format: `+[country code][number]`
- Examples:
  - US: `+1234567890`
  - India: `+919876543210`
- **No spaces, dashes, or parentheses**

## How It Works

Once configured, the system will:

1. **Check expiry dates** for all inventory items
2. **Categorize items** into:
   - 🟡 **YELLOW**: Expiring in 7 days
   - 🔴 **RED**: Expiring in 3 days
   - ⚫ **GREY**: Already expired

3. **Send WhatsApp alerts** to users with:
   - Valid phone numbers in database
   - Items that are NOT consumed/donated

## Testing (Development Mode)

1. **Add test phone number** in Meta for Developers
   - Go to WhatsApp → API Setup
   - Click "Add phone number" → "Add test number"
   - Enter your WhatsApp number and verify with code
2. **Ensure a user** in your database has a phone number in E.164 format
   - Example: `+1234567890` or `+919876543210`
3. **Use Admin Dashboard** to trigger test alerts
   - Navigate to Admin Dashboard
   - Use the "Send Expiry Alerts" feature
4. **Check Meta Business Suite** for message delivery status
   - Go to https://business.facebook.com/
   - Check message logs

**Important Notes About Test Numbers:**
- ✅ **Completely FREE** - No payment method needed
- ✅ **No credit card required** - Skip Step 6 entirely
- ✅ **Works for development** - Perfect for testing your app
- ⚠️ **Limited recipients** - Can only send to phone numbers you've added as test numbers
- ⚠️ **Not for production** - When you go live, you'll need to add payment and verify your business number

**⚠️ Important Limitation:**
The system automatically reads phone numbers from your database and tries to send alerts to all users with expiring items. However, with **test numbers**, messages will **only be delivered** to phone numbers you've added as test numbers in Meta for Developers.

**What this means:**
- ✅ System will attempt to send to all users in database (automatic)
- ✅ Messages will be delivered to test numbers you've added
- ❌ Messages will **fail** for numbers not added as test numbers
- 💡 **Solution**: Add all user phone numbers as test numbers, OR use production mode with payment

**To add your own phone number as a test number (Recommended):**
1. Go to WhatsApp → API Setup
2. Scroll to "To" section (or look for "Test phone numbers")
3. Click "Add phone number" → "Add test number"
4. Enter **YOUR OWN phone number** (in E.164 format: `+1234567890` or `+919876543210`)
5. You'll receive a verification code on WhatsApp
6. Enter the code to verify
7. ✅ Done! You can now send messages to your own number without payment

**Pro Tip:** Add your own number first, then add other test numbers (friends, team members) if needed. All test numbers work completely free!

**How the System Works:**
1. The system automatically reads phone numbers from your database
2. It checks which users have items expiring soon
3. It attempts to send WhatsApp alerts to all those users
4. **With test numbers**: Only messages to added test numbers will be delivered
5. **With production**: Messages to any WhatsApp number will be delivered

**For Testing:**
- Add your own number + any test users' numbers as test numbers
- The system will automatically send alerts to all of them
- Messages to numbers not added will fail (but won't break the system)

## Current Implementation

The WhatsApp notification service is already integrated in:
- `app/whatsapp_alerts.py` - Core notification functions
- `app/routes/routes.py` - API endpoints for sending alerts
- Admin Dashboard - UI to trigger alerts

## Next Steps

### For Development (Right Now):

1. ✅ Get your WhatsApp credentials from Meta for Developers
   - Go to WhatsApp → API Setup
   - Copy **Temporary access token** (works for 24 hours)
   - Copy **Phone number ID**
2. ✅ Add them to your `.env` file (local) or Railway variables (deployment)
3. ✅ **Add YOUR OWN phone number as a test number** (This lets you skip payment!)
   - Go to WhatsApp → API Setup
   - Click "Add phone number" → "Add test number"
   - Enter **YOUR phone number** in E.164 format (e.g., `+1234567890` or `+919876543210`)
   - Verify with the code sent to your WhatsApp
   - ✅ **No payment needed!** You can now send messages to your own number
4. ✅ Ensure users in your database have phone numbers in E.164 format
   - For testing, make sure at least one user has your test phone number
5. ✅ Test using the Admin Dashboard
6. ❌ **Skip Steps 3 (Webhooks), 5 (Business number), and 6 (Payment)** - not needed for development

### For Production (Later - When Ready to Go Live):

When you're ready to send messages to real users (not just test numbers):

1. ✅ Complete Meta's business verification
2. ✅ Set up webhooks (Step 3) if you want delivery status updates
3. ✅ Verify your business phone number (Step 5) - This replaces test numbers
4. ✅ **Add payment method (Step 6)** - Required for sending to real users at scale
5. ✅ Generate permanent access token (instead of temporary)

**Key Difference:**
- **Test Numbers**: Free, no payment, limited to added test numbers
- **Production**: Requires payment, can send to any WhatsApp number, needs business verification

## Troubleshooting

### "WhatsApp credentials not configured"
- Check that variables are set correctly
- Verify variable names match exactly (case-sensitive)

### "Invalid OAuth access token"
- Temporary tokens expire in 24 hours
- Generate a new token from Meta for Developers

### "Invalid phone number"
- Verify phone numbers are in E.164 format
- Ensure phone number is registered with WhatsApp

### No alerts received
- Check user has phone number in database
- Verify items are not consumed/donated
- Check Meta Business Suite for delivery status

## Resources

- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Cloud API Guide](https://developers.facebook.com/docs/whatsapp/cloud-api)

