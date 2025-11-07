# WhatsApp Template Form Fields - Complete Guide

When creating a template in Meta for Developers, you'll see several fields. Here's what to fill in for each:

## Template Creation Form Fields

### 1. Template Name
**Field:** Template Name  
**Value:** `expiry_alert` (or `donation_notification` or `recipe_cooked`)  
**Notes:**
- Must be lowercase
- Use underscores, no spaces
- Must match exactly what your code uses

### 2. Category
**Field:** Category  
**Value:** Select **"Utility"** from dropdown  
**Why:** Fastest approval, best for notifications

### 3. Language
**Field:** Language  
**Value:** Select **"English (US)"** or **"English"**  
**Why:** Matches your message language

---

## Template Structure Sections

### Header Section
**Field:** Header  
**Action:** **LEAVE EMPTY** or **SKIP**  
**Why:** 
- Not needed for simple text messages
- Only use if you want an image/video at the top
- For your use case, skip this

**If you want to add a header (optional):**
- Choose "Text" or "Media"
- Text header: Limited characters, appears at top
- Media header: Image/video/document
- **For your templates, skip this - not needed**

### Body Section
**Field:** Body  
**Value:** `Alert: {{1}}` or `{{1}}` (with text around it)  
**Action:** 
1. Click in the Body text area
2. Type: `{{1}}` (the variable)
3. **IMPORTANT:** Meta requires text before or after the variable
4. You can use: `Alert: {{1}}` or just `{{1}}` with sample text

**IMPORTANT - Meta Requirements:**
- Variables **CANNOT** be at the start or end alone
- You need some text around the variable
- Use format: `Alert: {{1}}` or add text after: `{{1}} - Food Tracker`

**Correct Format Options:**
- Option 1: `Alert: {{1}}` ✅
- Option 2: `{{1}}` (but add sample text when prompted) ✅
- Option 3: `{{1}}\n\n- Food Tracker` ✅

**Variable Sample (Required):**
When Meta asks for "Enter content for {{1}}", enter sample text like:
```
🔴 RED ALERT: Items expiring in 3 days:
• Item 1 - Expires: 2025-11-08 (2 days left)
• Item 2 - Expires: 2025-11-09 (3 days left)
```

**Explanation:**
- `{{1}}` = First variable
- Your code will pass the entire alert message as this variable
- The sample text is just for Meta's review (not sent to users)
- The actual message will replace `{{1}}` when sent

### Footer Section
**Field:** Footer  
**Action:** **LEAVE EMPTY** or **SKIP**  
**Why:**
- Optional text that appears at bottom
- Limited to 60 characters
- Not needed for your templates
- **Skip this section**

### Buttons Section
**Field:** Buttons  
**Action:** **LEAVE EMPTY** or **SKIP**  
**Why:**
- Optional interactive buttons
- Not needed for simple notifications
- **Skip this section**

---

## Type of Variable

When you type `{{1}}` in the Body, Meta will automatically:
1. Recognize it as a variable
2. Show you variable options
3. You'll see "Type of variable" or "Variable type"

**What to select:**
- **Type:** `Text` (or `String`)
- This is the default and correct choice
- Your messages are text, not numbers or dates

**Variable Options:**
- `Text` ✅ (Select this)
- `Number` ❌ (Not needed)
- `Currency` ❌ (Not needed)
- `DateTime` ❌ (Not needed)

---

## Media Sample

**Field:** Media Sample (if shown)  
**Action:** **SKIP** or **LEAVE EMPTY**  
**Why:**
- Only needed if you're using media (images/videos)
- Your templates are text-only
- **Not required for your templates**

---

## Complete Form Example

Here's exactly what to fill in for each template:

### Template: `expiry_alert`

```
Template Name: expiry_alert
Category: Utility
Language: English (US)

Header: [LEAVE EMPTY - Skip]
Body: Alert: {{1}}
  - Variable Type: Text
  - Sample for {{1}}: 🔴 RED ALERT: Items expiring in 3 days:
    • Item 1 - Expires: 2025-11-08 (2 days left)
    • Item 2 - Expires: 2025-11-09 (3 days left)
Footer: [LEAVE EMPTY - Skip]
Buttons: [LEAVE EMPTY - Skip]
Media Sample: [LEAVE EMPTY - Skip]
```

### Template: `donation_notification`

```
Template Name: donation_notification
Category: Utility
Language: English (US)

Header: [LEAVE EMPTY - Skip]
Body: Alert: {{1}}
  - Variable Type: Text
  - Sample for {{1}}: 🎉 Thank you for your donation! You've earned 10 points.
Footer: [LEAVE EMPTY - Skip]
Buttons: [LEAVE EMPTY - Skip]
Media Sample: [LEAVE EMPTY - Skip]
```

### Template: `recipe_cooked`

```
Template Name: recipe_cooked
Category: Utility
Language: English (US)

Header: [LEAVE EMPTY - Skip]
Body: Alert: {{1}}
  - Variable Type: Text
  - Sample for {{1}}: 🍳 Great job cooking! You saved 3 items from expiring.
Footer: [LEAVE EMPTY - Skip]
Buttons: [LEAVE EMPTY - Skip]
Media Sample: [LEAVE EMPTY - Skip]
```

---

## Step-by-Step: What You'll See

### Step 1: Basic Info
- **Template Name:** Type `expiry_alert`
- **Category:** Select "Utility"
- **Language:** Select "English (US)"
- Click "Next" or "Continue"

### Step 2: Template Structure
You'll see sections for:
- **Header:** Click "Skip" or leave empty
- **Body:** 
  1. Click in the text area
  2. Type: `Alert: {{1}}` (or `{{1}}` with text around it)
  3. Meta will highlight `{{1}}` as a variable
  4. If asked for variable type, select "Text"
  5. **IMPORTANT:** When asked for "Enter content for {{1}}", enter sample text:
     ```
     🔴 RED ALERT: Items expiring in 3 days:
     • Item 1 - Expires: 2025-11-08 (2 days left)
     • Item 2 - Expires: 2025-11-09 (3 days left)
     ```
  6. Click "Add sample text" or "Save sample"
- **Footer:** Click "Skip" or leave empty
- **Buttons:** Click "Skip" or leave empty

### Step 3: Review
- Check that Body shows: `{{1}}`
- Verify template name is correct
- Click "Submit"

---

## Visual Guide

```
┌─────────────────────────────────────┐
│ Template Name: expiry_alert         │
│ Category: [Utility ▼]                │
│ Language: [English (US) ▼]          │
├─────────────────────────────────────┤
│                                     │
│ Header: [Skip]                      │
│                                     │
│ Body:                               │
│ ┌─────────────────────────────────┐ │
│ │ {{1}}                            │ │
│ └─────────────────────────────────┘ │
│ Variable Type: [Text ▼]             │
│                                     │
│ Footer: [Skip]                      │
│                                     │
│ Buttons: [Skip]                      │
│                                     │
│ Media Sample: [Skip]                │
│                                     │
│ [Cancel]  [Submit]                  │
└─────────────────────────────────────┘
```

---

## Common Questions

### Q: Do I need to fill Header?
**A:** No, skip it. Only needed for images/videos at the top.

### Q: What if I see "Media Sample"?
**A:** Skip it. Only needed if using images/videos.

### Q: What about Footer?
**A:** Skip it. Optional text at bottom, not needed.

### Q: Should I add Buttons?
**A:** No, skip it. Buttons are for interactive messages.

### Q: Variable Type - which one?
**A:** Select "Text" - your messages are text strings.

### Q: Can I add more variables?
**A:** Yes, but not needed. `{{1}}` contains your entire message.

### Q: What if the form looks different?
**A:** Meta updates their UI, but the fields are the same:
- Template Name (required)
- Category (required)
- Language (required)
- Body with `{{1}}` (required)
- Everything else: Skip/Leave empty

---

## Important Reminders

✅ **Fill In:**
- Template Name
- Category (Utility)
- Language (English US)
- Body: `{{1}}` with variable type "Text"

❌ **Skip/Leave Empty:**
- Header
- Footer
- Buttons
- Media Sample

---

## After Submission

1. Template will be reviewed
2. Status will show "Pending" then "Approved"
3. Approval is usually instant for Utility templates
4. Once approved, your code will automatically use it!

---

## Troubleshooting

### "Variable not defined" error
- Make sure you typed `{{1}}` exactly (with double curly braces)
- Select variable type as "Text"

### "Template name already exists"
- Delete the old template first
- Or use a different name (but update your code too)

### Can't find "Skip" button
- Just leave the field empty
- Some fields are optional and can be left blank

### Form looks different
- Meta updates their UI frequently
- Look for: Name, Category, Language, Body fields
- Skip everything else

---

## Summary

**For all three templates, you only need to fill:**
1. Template Name (expiry_alert, donation_notification, recipe_cooked)
2. Category (Utility)
3. Language (English US)
4. Body (`{{1}}` with type "Text")

**Everything else: Skip or leave empty!**

