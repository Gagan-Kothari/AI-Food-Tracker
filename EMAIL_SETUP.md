# Email Setup Guide

This guide explains how to configure email sending for the Contact Us form.

## Gmail Setup (Recommended)

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

### "SMTP authentication failed"
- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-Step Verification is enabled
- Check that the password doesn't have spaces

### "Connection refused" or "Connection timeout"
- Check your firewall settings
- Verify SMTP server and port are correct
- Some networks block SMTP ports (587, 465)

### Emails not received
- Check spam/junk folder
- Verify `CONTACT_EMAIL` is set correctly
- Check backend logs for error messages

