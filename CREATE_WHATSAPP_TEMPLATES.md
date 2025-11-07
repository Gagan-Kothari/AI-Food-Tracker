# How to Create WhatsApp Message Templates - Step by Step Guide

This guide will walk you through creating the three templates needed for your Food Tracker app.

## Prerequisites

- Access to Meta for Developers account
- Your WhatsApp app already set up
- Test number added (you've already done this)

## Template 1: Expiry Alert Template

### Step 1: Navigate to Message Templates

1. Go to: https://developers.facebook.com/
2. Select your app from the dropdown (top left)
3. In the left sidebar, click **"WhatsApp"**
4. Click **"Message Templates"** (under Configuration)

### Step 2: Create New Template

1. Click the **"+ Create Template"** button (usually top right)
2. You'll see a form to fill out

### Step 3: Fill in Template Details

**Template Name:**
```
expiry_alert
```
- Must be lowercase
- Use underscores, no spaces
- This is the exact name your code will use

**Category:**
- Select **"Utility"** from the dropdown
- This is the fastest to get approved

**Language:**
- Select **"English (US)"** or **"English"**

### Step 4: Add Template Body

1. In the **"Body"** section, you'll see a text editor
2. Type: `{{1}}`
3. This creates a variable that will contain your alert message
4. The `{{1}}` will be replaced with your actual message content

**Important:** The body should look exactly like this:
```
{{1}}
```

### Step 5: Submit Template

1. Review your template details
2. Click **"Submit"** button
3. For Utility templates in development mode, approval is usually **instant** (within seconds)
4. Wait for status to show **"Approved"** (green checkmark)

### Step 6: Verify Template

1. Once approved, you'll see it in your templates list
2. Note the exact name: `expiry_alert` (must match exactly)
3. Status should show "Approved"

---

## Template 2: Donation Notification Template

### Step 1: Create Another Template

1. Go back to **"Message Templates"** page
2. Click **"+ Create Template"** again

### Step 2: Fill in Template Details

**Template Name:**
```
donation_notification
```
- Lowercase, underscores, no spaces

**Category:**
- Select **"Utility"**

**Language:**
- Select **"English (US)"** or **"English"**

### Step 3: Add Template Body

1. In the **"Body"** section, type: `{{1}}`
2. This is the same format - one variable for the message

**Body:**
```
{{1}}
```

### Step 4: Submit Template

1. Click **"Submit"**
2. Wait for approval (usually instant for Utility templates)

---

## Template 3: Recipe Cooked Template

### Step 1: Create Third Template

1. Go to **"Message Templates"** page
2. Click **"+ Create Template"** again

### Step 2: Fill in Template Details

**Template Name:**
```
recipe_cooked
```
- Lowercase, underscores, no spaces

**Category:**
- Select **"Utility"**

**Language:**
- Select **"English (US)"** or **"English"**

### Step 3: Add Template Body

1. In the **"Body"** section, type: `{{1}}`
2. Same format - one variable for the message

**Body:**
```
{{1}}
```

### Step 4: Submit Template

1. Click **"Submit"**
2. Wait for approval (usually instant for Utility templates)

---

## Summary of All Three Templates

| Template Name | Category | Language | Body | Purpose |
|--------------|----------|----------|------|---------|
| `expiry_alert` | Utility | English (US) | `{{1}}` | Expiry alerts (yellow, red, grey) |
| `donation_notification` | Utility | English (US) | `{{1}}` | Donation notifications |
| `recipe_cooked` | Utility | English (US) | `{{1}}` | Recipe cooked notifications |

## Important Notes

### Template Names Must Match Exactly

Your code uses these exact names:
- `expiry_alert` ✅
- `donation_notification` ✅
- `recipe_cooked` ✅

**Don't use:**
- `Expiry_Alert` ❌ (wrong case)
- `expiry-alert` ❌ (use underscores, not dashes)
- `expiry alert` ❌ (no spaces)

### Template Body Format

All templates use the same simple format:
```
{{1}}
```

This means:
- `{{1}}` = First variable (your message content)
- The entire message will be passed as this one variable
- No need for multiple variables or complex formatting

### Approval Time

- **Utility templates in development mode:** Usually approved instantly (seconds to minutes)
- **Marketing templates:** Can take 24-48 hours
- **Production mode:** May require additional review

### After Creating Templates

1. **Wait for approval** (check status in templates list)
2. **Verify names match exactly** (case-sensitive)
3. **No code changes needed** - your code will automatically use them
4. **Test by logging in** - you should receive actual alert messages instead of "Hello World!"

## Troubleshooting

### Template Not Showing Up

- Refresh the page
- Check if it's still "Pending" approval
- Make sure you're looking at the correct app

### Template Name Error

- Verify the name is exactly: `expiry_alert`, `donation_notification`, `recipe_cooked`
- Check for typos
- Make sure it's lowercase with underscores

### Template Not Approved

- Utility templates in development should approve instantly
- If stuck, try deleting and recreating
- Check for any error messages in Meta

### Still Getting "Hello World!" Messages

- Verify all three templates are **Approved** (green checkmark)
- Check Railway logs for template errors
- The code will automatically use custom templates once they're approved

## Quick Checklist

- [ ] Created `expiry_alert` template
- [ ] Created `donation_notification` template
- [ ] Created `recipe_cooked` template
- [ ] All templates show "Approved" status
- [ ] Template names match exactly (case-sensitive)
- [ ] All templates have `{{1}}` in the body
- [ ] All templates are Utility category
- [ ] All templates are English (US) language

Once all templates are approved, your WhatsApp notifications will work with your actual alert messages! 🎉

