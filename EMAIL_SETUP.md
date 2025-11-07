# Email Setup Guide

This guide explains how to configure email sending for the Contact Us form.

## ⚠️ Important: Railway Deployment

**If you're deploying on Railway**, SMTP ports (587, 465) are often blocked. Use **Resend API** instead (see below).

## Resend API Setup (Recommended for Railway)

Resend is an HTTP-based email API that works reliably on Railway and other cloud platforms.

### Step 1: Create Resend Account
1. Go to https://resend.com
2. Sign up for a free account (100 emails/day free)
3. Verify your email address

### Step 2: Get API Key
1. Go to https://resend.com/api-keys
2. Click **Create API Key**
3. Give it a name (e.g., "FoodTracker")
4. Copy the API key (starts with `re_`)

### Step 3: Add Domain (Optional but Recommended)
1. Go to https://resend.com/domains
2. Click **Add Domain**
3. Follow the DNS verification steps
4. Once verified, you can use `noreply@yourdomain.com` as the sender

**Note:** If you don't add a domain, you can use Resend's test domain, but emails may go to spam.

### Step 4: Set Environment Variables

Add these to your Railway environment variables:

```env
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=your-verified-email@yourdomain.com
CONTACT_EMAIL=gagankothari6@gmail.com
```

**Important:**
- `RESEND_API_KEY`: Your Resend API key (starts with `re_`)
- `RESEND_FROM_EMAIL`: Your verified email address or domain email
- `CONTACT_EMAIL`: Where contact form submissions will be sent

The system will automatically use Resend API if `RESEND_API_KEY` is set, otherwise it will fall back to SMTP.

## Gmail Setup (For Local Development or Non-Railway Deployments)

### Step 1: Enable 2-Step Verification
1. Go to your Google Account settings
2. Navigate to Security
3. Enable 2-Step Verification (if not already enabled)

### Step 2: Generate App Password
1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", click **2-Step Verification**
4. Scroll down and click **App passwords**
5. Select "Mail" as the app and "Other (Custom name)" as the device
6. Enter "FoodTracker" as the name
7. Click **Generate**
8. Copy the 16-character password (it will look like: `abcd efgh ijkl mnop`)

### Step 3: Set Environment Variables

Add these to your `.env` file or Railway environment variables:

```env
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-16-character-app-password
CONTACT_EMAIL=gagankothari6@gmail.com
```

**Important Notes:**
- `SMTP_USERNAME`: Your Gmail address (e.g., `your-email@gmail.com`)
- `SMTP_PASSWORD`: The 16-character app password (remove spaces if any)
- `CONTACT_EMAIL`: The email where contact form submissions will be sent (`gagankothari6@gmail.com`)

## Alternative: Other Email Providers

### Outlook/Hotmail
```env
SMTP_SERVER=smtp-mail.outlook.com
SMTP_PORT=587
SMTP_USERNAME=your-email@outlook.com
SMTP_PASSWORD=your-password
```

### Yahoo
```env
SMTP_SERVER=smtp.mail.yahoo.com
SMTP_PORT=587
SMTP_USERNAME=your-email@yahoo.com
SMTP_PASSWORD=your-app-password
```

### Custom SMTP Server
```env
SMTP_SERVER=your-smtp-server.com
SMTP_PORT=587
SMTP_USERNAME=your-username
SMTP_PASSWORD=your-password
```

## Testing

After setting up the environment variables:
1. Restart your backend server
2. Go to the Contact Us page
3. Fill out and submit the form
4. Check `gagankothari6@gmail.com` for the email

## Troubleshooting

### "[Errno 101] Network is unreachable" or SMTP Connection Errors on Railway
**Solution:** Railway blocks SMTP ports. Use Resend API instead:
1. Set up Resend API (see above)
2. Add `RESEND_API_KEY` and `RESEND_FROM_EMAIL` to Railway
3. The system will automatically use Resend instead of SMTP

### "SMTP authentication failed"
- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-Step Verification is enabled
- Check that the password doesn't have spaces

### "Connection refused" or "Connection timeout"
- Check your firewall settings
- Verify SMTP server and port are correct
- Some networks/cloud platforms block SMTP ports (587, 465)
- **For Railway:** Use Resend API instead

### Emails not received
- Check spam/junk folder
- Verify `CONTACT_EMAIL` is set correctly
- Check backend logs for error messages
- For Resend: Check Resend dashboard for delivery status

### Resend API Errors
- Verify your API key is correct
- Make sure your domain is verified (if using custom domain)
- Check Resend dashboard for rate limits (100 emails/day on free tier)

