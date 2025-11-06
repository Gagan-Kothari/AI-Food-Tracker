# WhatsApp Business API Setup Guide

This guide explains how to set up the Official WhatsApp Business API (Meta) for sending expiry alerts.

## Prerequisites

1. A Meta (Facebook) Business Account
2. A WhatsApp Business Account
3. Access to Meta Business Suite or Meta for Developers

## Step 1: Create Meta Business Account

1. Go to https://business.facebook.com/
2. Create or sign in to your Meta Business Account
3. Complete the business verification process if required

## Step 2: Set Up WhatsApp Business API

### Option A: WhatsApp Cloud API (Recommended - Free Tier Available)

1. Go to https://developers.facebook.com/
2. Create a new app or use an existing one
3. Add "WhatsApp" product to your app
4. Follow the setup wizard to configure WhatsApp Business API

### Option B: WhatsApp Business Platform (via Business Provider)

If you're using a Business Solution Provider (BSP), follow their specific setup instructions.

## Step 3: Get Your Credentials


1. **Access Token** (`WHATSAPP_ACCESS_TOKEN`)
   - Go to your app → WhatsApp → API Setup
   - Copy the temporary access token (for testing)
   - For production, generate a permanent token with proper permissions

2. **Phone Number ID** (`WHATSAPP_PHONE_NUMBER_ID`)
   - Found in WhatsApp → API Setup
   - This is the ID of your WhatsApp Business phone number

3. **Business Account ID** (`WHATSAPP_BUSINESS_ACCOUNT_ID`) - Optional
   - Found in WhatsApp → API Setup
   - Only needed for certain operations

4. **API Version** (`WHATSAPP_API_VERSION`) - Optional
   - Default is `v21.0`
   - Check Meta's documentation for the latest version

## Step 4: Configure Environment Variables

Add the following to your `.env` file:

```env
WHATSAPP_ACCESS_TOKEN=your_access_token_here
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id_here
WHATSAPP_BUSINESS_ACCOUNT_ID=your_business_account_id_here
WHATSAPP_API_VERSION=v21.0
```

### Getting Your Access Token

1. Go to https://developers.facebook.com/apps/
2. Select your app
3. Navigate to WhatsApp → API Setup
4. Copy the "Temporary access token" for testing
5. For production, click "Generate access token" and follow the process

### Getting Your Phone Number ID

1. In the same API Setup page
2. Look for "Phone number ID" or "From" field
3. Copy the numeric ID (e.g., `123456789012345`)

## Step 5: Test Phone Number Setup

For testing, you can use Meta's test phone numbers:

1. In WhatsApp → API Setup
2. Add a test phone number
3. Send a test message to verify the setup

## Step 6: Phone Number Format

User phone numbers in the database should be in E.164 format:
- Format: `+[country code][number]`
- Example: `+1234567890` (US), `+919876543210` (India)
- No spaces, dashes, or parentheses

## Alert Types

The system sends three types of alerts:

- **🟡 YELLOW ALERT**: Items expiring in 7 days
- **🔴 RED ALERT**: Items expiring in 3 days  
- **⚫ GREY ALERT**: Items that have expired

## Important Notes

- Alerts are **NOT** sent for items that are already marked as "consumed" or "donated"
- Users must have a valid `phone_number` in the database to receive alerts
- The admin can trigger alerts manually from the Admin Dashboard
- Alerts can be sent to all users or a specific user
- For production use, you need to complete Meta's business verification
- Free tier allows limited messages per month (check current limits)

## Testing

1. Make sure your `.env` file has the correct WhatsApp credentials
2. Ensure at least one user has a phone number in the database
3. Use the Admin Dashboard to send test alerts
4. Check Meta Business Suite for message logs and delivery status

## Troubleshooting

### "WhatsApp credentials not configured"
- Check your `.env` file has `WHATSAPP_ACCESS_TOKEN` and `WHATSAPP_PHONE_NUMBER_ID`
- Verify the variable names match exactly

### "Failed to send WhatsApp alert: Invalid OAuth access token"
- Your access token may have expired (temporary tokens expire in 24 hours)
- Generate a new access token from Meta for Developers
- For production, use a permanent token with proper permissions

### "Failed to send WhatsApp alert: Invalid phone number"
- Verify phone numbers are in E.164 format: `+[country code][number]`
- Ensure the phone number is registered with WhatsApp
- For testing, use Meta's test phone numbers

### "Failed to send WhatsApp alert: Rate limit exceeded"
- You've exceeded the free tier message limit
- Wait for the limit to reset or upgrade your plan
- Check your usage in Meta Business Suite

### No alerts received
- Check that users have phone numbers in the database
- Verify items are not consumed/donated
- Check Meta Business Suite for message delivery status
- Ensure your WhatsApp Business Account is approved

## API Rate Limits

- Free tier: Limited messages per month (check current limits)
- Paid tier: Higher limits based on your plan
- Check Meta's documentation for current rate limits

## Production Considerations

1. **Permanent Access Token**: Generate a permanent token with proper scopes
2. **Webhook Setup**: Set up webhooks to receive message status updates
3. **Business Verification**: Complete Meta's business verification process
4. **Phone Number Verification**: Verify your business phone number
5. **Message Templates**: For production, use approved message templates

## Resources

- [WhatsApp Business API Documentation](https://developers.facebook.com/docs/whatsapp)
- [Meta for Developers](https://developers.facebook.com/)
- [WhatsApp Cloud API Guide](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [API Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/reference)

