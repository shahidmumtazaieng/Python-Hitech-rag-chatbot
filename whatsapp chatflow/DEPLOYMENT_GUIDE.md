# WhatsApp Cloud API Integration Guide - Hi-Tech Industrial Group Chatflow

## 📋 Quick Start

This document provides complete instructions for deploying the Hi-Tech chatflow to WhatsApp Business API.

---

## 🎯 Overview

**Flow Type:** Interactive Multi-Step Customer Support Chatflow
**Language Support:** English (en) & Arabic (ar)
**Structure:** Tree-based menu hierarchy with fallback handlers
**Categories:** 7 industrial product/service divisions
**Format:** JSON for WhatsApp Cloud API v18.0

---

## 📁 File Structure

```
chatflow_complete.json          # Main chatflow file (production-ready)
├── flow_metadata               # General flow information
├── webhook_config              # WhatsApp webhook configuration
├── global_settings             # Global behavior settings
├── business_hours              # Operating hours
└── steps                       # All conversation steps (47 total)
```

---

## 🔧 Configuration Setup

### 1. **Update Webhook Endpoint**

In `webhook_config` section, replace:
```json
"endpoint": "https://your-domain.com/webhook/whatsapp"
```

With your actual endpoint:
```json
"endpoint": "https://api.yourdomain.com/webhook/whatsapp"
```

### 2. **Set Verification Token**

Replace:
```json
"verify_token": "your_verify_token"
```

With a secure token (minimum 32 characters):
```json
"verify_token": "generate_random_32char_token_here"
```

### 3. **Update Contact Information**

Search and replace all instances of:
- `[YOUR-PHONE-NUMBER]` → Your business phone number
- `[YOUR-DOMAIN]` → Your business domain
- `sales@hitech-group.com` → Your actual email
- `support@hitech-group.com` → Your support email

---

## 🚀 Deployment Steps

### Step 1: Prepare Credentials
```
1. Go to WhatsApp Business API dashboard
2. Get your:
   - Phone Number ID
   - Business Account ID
   - API Access Token
   - Webhook Verify Token
```

### Step 2: Server Setup
```bash
# Your backend server should:
1. Listen on PORT 3000 (or your preferred port)
2. Have HTTPS enabled (required by WhatsApp)
3. Accept POST requests on /webhook/whatsapp
4. Validate webhook with verify_token
```

### Step 3: Deploy Chatflow JSON

**Option A: Direct API Deployment**
```bash
# Upload to your WhatsApp Business API directly
curl -X POST https://graph.instagram.com/v18.0/YOUR_PHONE_ID/messages \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d @chatflow_complete.json
```

**Option B: Application Integration**
Store the JSON in your application database:
```javascript
// Node.js Example
const chatflow = require('./chatflow_complete.json');
app.get('/api/chatflow', (req, res) => {
  res.json(chatflow);
});
```

### Step 4: Webhook Handler Implementation

**Basic Node.js/Express Example:**

```javascript
const express = require('express');
const app = express();

// Parse webhooks
app.use(express.json());

// Webhook Verification (GET)
app.get('/webhook/whatsapp', (req, res) => {
  const verify_token = req.query['hub.verify_token'];
  const challenge = req.query['hub.challenge'];

  if (verify_token === 'your_verify_token') {
    res.send(challenge);
  } else {
    res.status(403).send('Verification failed');
  }
});

// Incoming Messages (POST)
app.post('/webhook/whatsapp', (req, res) => {
  const body = req.body;

  // Handle different message types
  if (body.object && body.entry) {
    body.entry.forEach((entry) => {
      const changes = entry.changes[0];
      const value = changes.value;

      if (value.messages) {
        const message = value.messages[0];
        const sender_id = value.contacts[0].wa_id;
        
        // Process message based on text or button interaction
        handleMessage(sender_id, message);
      }
    });
  }
  res.status(200).send('OK');
});

app.listen(3000, () => {
  console.log('WhatsApp webhook listening on port 3000');
});
```

### Step 5: Message Handler Implementation

**Process Different Interaction Types:**

```javascript
function handleMessage(userId, message) {
  const chatflow = require('./chatflow_complete.json');

  // Interactive Button/List Selection
  if (message.interactive) {
    const selected = message.interactive.button_reply?.id ||
                    message.interactive.list_reply?.id;
    
    handleFlowNavigation(userId, selected, chatflow);
  }

  // Text Input
  if (message.text) {
    const text = message.text.body;
    handleTextInput(userId, text, chatflow);
  }
}

function handleFlowNavigation(userId, selectedId, chatflow) {
  // Find next step based on selectedId
  const currentStep = findCurrentStep(userId);
  const nextStep = currentStep.next_logic[selectedId];
  
  const stepContent = chatflow.steps[nextStep];
  sendMessage(userId, stepContent);
}
```

---

## 📤 Message Format

### Interactive Button Messages (WhatsApp Format)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "button",
    "body": {
      "text": "Button message text"
    },
    "action": {
      "buttons": [
        {
          "type": "reply",
          "reply": {
            "id": "button_id_1",
            "title": "Button 1"
          }
        },
        {
          "type": "reply",
          "reply": {
            "id": "button_id_2",
            "title": "Button 2"
          }
        }
      ]
    }
  }
}
```

### Interactive List Messages

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "interactive",
  "interactive": {
    "type": "list",
    "body": {
      "text": "List message text"
    },
    "action": {
      "button": "View Options",
      "sections": [
        {
          "title": "Section 1",
          "rows": [
            {
              "id": "row_id_1",
              "title": "Option 1",
              "description": "Description"
            }
          ]
        }
      ]
    }
  }
}
```

### Text Messages (Simple)

```json
{
  "messaging_product": "whatsapp",
  "to": "1234567890",
  "type": "text",
  "text": {
    "body": "Your message text here"
  }
}
```

---

## 🔄 Flow Navigation Logic

### Step Types Supported

1. **interactive_button** - Single/multiple button choices
2. **interactive_list** - Dropdown list selection
3. **text** - Simple text message (requires_human_followup = true)

### Next Logic Pattern

```json
"next_logic": {
  "button_id_1": "next_step_id_1",
  "button_id_2": "next_step_id_2"
}
```

### Flow State Management

Track user progress using:
```javascript
{
  user_id: "1234567890",
  current_step: "main_menu",
  language: "en",
  session_start: "2024-11-15T10:30:00Z",
  conversation_context: {
    selected_category: "fencing_submenu",
    selected_product: "fence_chainlink",
    quotation_data: {}
  }
}
```

---

## 📊 All 47 Steps Overview

| Step ID | Type | Purpose |
|---------|------|---------|
| welcome | button | Initial greeting + language selection |
| main_menu | list | Main category navigation (7 divisions) |
| about_submenu | button | Company information options |
| fencing_submenu | list | Fencing product types (5 options) |
| fencing_deep_dive | button | Fencing project details |
| fencing_quotation_form | text | Detailed quotation form |
| gabion_submenu | list | Gabion application types (5 options) |
| gabion_deep_dive | button | Gabion project details |
| gabion_quotation_form | text | Technical requirements form |
| upvc_submenu | list | UPVC product catalog |
| upvc_deep_dive | button | Assessment questions |
| upvc_quotation_form | text | UPVC quotation form |
| barrier_submenu | list | Barrier types (6 options) |
| barrier_deep_dive | button | Traffic analysis |
| barrier_quotation_form | text | Access control details |
| galvanizing_submenu | list | Galvanizing part types (6 options) |
| galvanizing_deep_dive | button | Process advantages |
| galvanizing_quotation_form | text | Part specifications |
| racks_submenu | list | Storage solutions |
| racks_deep_dive | button | Engineering assessment |
| racks_quotation_form | text | Warehouse details |
| smart_submenu | list | Smart toilet models |
| smart_deep_dive | button | Project assessment |
| smart_quotation_form | text | Smart toilet project form |
| quote_submitted | text | Confirmation + next steps |
| speak_engineer | text | Live engineer connection |
| other_support | text | Technical support channel |
| schedule_visit_form | text | Site survey scheduling |
| send_document | text | Document delivery |
| send_video | text | Video tour link |
| general_inquiry_form | text | Free-form inquiry |
| unrecognized_input | text | Fallback handler |
| session_timeout | text | Timeout handler |
| human_handoff_request | text | Human escalation |

---

## 🎓 User Journey Examples

### Example 1: Fencing Quote Request
```
1. welcome (language selection)
2. main_menu (select "Fencing Solutions")
3. fencing_submenu (select fence type)
4. fencing_deep_dive (choose "Request Quote")
5. fencing_quotation_form (fill form)
6. quote_submitted (confirmation)
```

### Example 2: Ask Engineer
```
1. welcome (language selection)
2. main_menu (select "Speak to Engineer")
3. speak_engineer (description + contact)
→ Human agent takes over
```

### Example 3: Galvanizing Parts
```
1. welcome (language)
2. main_menu (select "Spin Galvanizing")
3. galvanizing_submenu (select part type)
4. galvanizing_deep_dive (choose "Upload Parts")
5. galvanizing_quotation_form (submit specifications)
6. quote_submitted (confirmation)
```

---

## 🌐 Language Switching

All steps have both English and Arabic content:
- `body_en` - English message
- `body_ar` - Arabic message
- `message_en` / `message_ar` - Button messages

**Set User Language Preference:**
```javascript
const userLanguage = localStorage.getItem('language') || 'en';
const content = step[`body_${userLanguage}`];
```

---

## ✅ Testing Checklist

- [ ] Webhook endpoint publicly accessible (HTTPS)
- [ ] Verify token working correctly
- [ ] All steps properly linked in next_logic
- [ ] Button IDs match next_logic keys
- [ ] Arabic & English content loads correctly
- [ ] Form submissions captured
- [ ] Fallback handlers working
- [ ] Session timeout triggers after 30 minutes
- [ ] Human handoff escalation works
- [ ] Analytics logging enabled
- [ ] Rate limiting configured
- [ ] Security headers set (HSTS, CSP, etc.)

---

## 🔒 Security Best Practices

1. **Webhook Verification**
   - Always validate verify_token
   - Check origin of requests
   - Use HTTPS only

2. **Data Protection**
   - Encrypt PII in transit and at rest
   - Comply with GDPR/CCPA
   - Implement data retention policies

3. **Rate Limiting**
   - Limit messages per user per minute
   - Implement exponential backoff for API calls
   - Monitor for abuse patterns

4. **Access Control**
   - Use strong API tokens (32+ chars)
   - Rotate tokens regularly
   - Restrict API token permissions

---

## 📈 Analytics & Monitoring

**Track These Metrics:**
```javascript
{
  total_conversations: 0,
  conversations_by_category: {},
  average_conversation_length: 0,
  quote_requests_submitted: 0,
  human_handoff_rate: 0,
  average_response_time: 0,
  language_distribution: { en: 0, ar: 0 },
  drop_off_points: {},
  top_requested_features: {}
}
```

---

## 🚨 Error Handling

```javascript
function handleError(error, userId, step) {
  console.error(`Error in step ${step}:`, error);
  
  // Send fallback message
  sendFallbackMessage(userId, 'unrecognized_input');
  
  // Log for support team
  logError({
    user_id: userId,
    step: step,
    error: error.message,
    timestamp: new Date()
  });
  
  // Escalate if critical
  if (error.critical) {
    escalateToHuman(userId);
  }
}
```

---

## 📞 Support & Maintenance

- **Issue Tracker:** Log all chatflow errors
- **Monthly Review:** Analyze conversations for improvements
- **Quarterly Updates:** Refresh product details
- **Regular Testing:** Test all flows weekly
- **User Feedback:** Collect feedback for improvements

---

## 📄 Additional Resources

- [WhatsApp Business API Docs](https://developers.facebook.com/docs/whatsapp/cloud-api)
- [Interactive Messages Guide](https://developers.facebook.com/docs/whatsapp/cloud-api/reference/messages)
- [Webhook Reference](https://developers.facebook.com/docs/whatsapp/cloud-api/webhooks)

---

**Version:** 3.0  
**Last Updated:** November 2024  
**Status:** Production Ready ✅
