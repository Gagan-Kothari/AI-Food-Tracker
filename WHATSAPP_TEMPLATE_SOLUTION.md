# WhatsApp Template Solution - Why Text Messages Don't Work

## The Problem

You discovered that:
- ✅ **Test template works** (hello_world template)
- ❌ **Text messages don't work** (even though API returns 200 OK)

## Why This Happens

In **development mode**, WhatsApp has restrictions:
- ✅ **Template messages** work for business-initiated messages
- ❌ **Text messages** only work within 24-hour window (after user messages you)
- ❌ **Text messages** for business-initiated alerts are blocked

Since your expiry alerts are **business-initiated** (you're sending them, not responding to user), they need templates!

## Solution: Create Custom Templates

You need to create custom message templates for your alerts. Here's how:

### Step 1: Create Template for Expiry Alerts

1. **Go to Meta for Developers:**
   - Visit: https://developers.facebook.com/
   - Select your app → WhatsApp → Message Templates
   - Click "Create Template"

2. **Template Details:**
   - **Name:** `expiry_alert` (or `food_expiry_alert`)
   - **Category:** Utility
   - **Language:** English (US)

3. **Template Body:**
   ```
   {{1}}
   ```
   - This is a variable that will contain your alert message
   - Click "Add variable" → Add one variable

4. **Submit for Approval:**
   - Click "Submit"
   - Wait for approval (usually instant for utility templates in development)

### Step 2: Create Template for Donation Notifications

1. **Create another template:**
   - **Name:** `donation_notification`
   - **Category:** Utility
   - **Language:** English (US)
   - **Body:** `{{1}}` (one variable)

### Step 3: Create Template for Recipe Cooked Notifications

1. **Create another template:**
   - **Name:** `recipe_cooked`
   - **Category:** Utility
   - **Language:** English (US)
   - **Body:** `{{1}}` (one variable)

### Step 4: Update Code to Use Templates

I'll update the code to use templates instead of text messages. The code will:
- Use `expiry_alert` template for expiry alerts
- Use `donation_notification` template for donations
- Use `recipe_cooked` template for recipe notifications

## Quick Test (Using hello_world)

For now, I've updated the code to use the `hello_world` template format. This will:
- ✅ Send messages successfully (since test template works)
- ⚠️ But only send "Hello World!" message (not your custom content)

**This confirms the template approach works**, then we'll switch to custom templates.

## Next Steps

1. **Test with hello_world first:**
   - Deploy the updated code
   - Try sending an alert
   - You should receive "Hello World!" message
   - This confirms templates work

2. **Create custom templates:**
   - Follow Step 1-3 above
   - Create templates for each message type

3. **Update code with template names:**
   - I'll update the code to use your custom template names
   - Messages will then contain your actual content

## Why This Is Necessary

WhatsApp Business API in development mode:
- Allows **template messages** for business-initiated communication
- Blocks **text messages** for business-initiated communication (only works in 24-hour window)

This is a **WhatsApp policy**, not a code issue. Templates are required for business-initiated messages.

## Template Format

Once you create templates, the code will send:
```json
{
  "messaging_product": "whatsapp",
  "to": "919811546101",
  "type": "template",
  "template": {
    "name": "expiry_alert",
    "language": {
      "code": "en_US"
    },
    "components": [
      {
        "type": "body",
        "parameters": [
          {
            "type": "text",
            "text": "🔴 RED ALERT: Items expiring in 3 days:\n• Item 1\n• Item 2"
          }
        ]
      }
    ]
  }
}
```

This will work because it's a template message!

