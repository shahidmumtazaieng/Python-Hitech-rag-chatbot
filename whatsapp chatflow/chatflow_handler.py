"""
Hi-Tech Industrial Group - WhatsApp Chatflow Handler
Python Implementation for WhatsApp Cloud API v18.0

This module provides complete webhook handling and chatflow management
for the Hi-Tech chatflow deployed on WhatsApp Business API.
"""

import json
import requests
import hashlib
import hmac
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# =============================================================================
# CONFIGURATION
# =============================================================================

WHATSAPP_API_URL = "https://graph.instagram.com/v18.0/"
PHONE_NUMBER_ID = "YOUR_PHONE_NUMBER_ID"  # Get from WhatsApp Dashboard
BUSINESS_ACCOUNT_ID = "YOUR_BUSINESS_ACCOUNT_ID"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"  # From WhatsApp Business Account
VERIFY_TOKEN = "your_verify_token"  # Must match chatflow config

# Load chatflow
with open('chatflow_complete.json', 'r', encoding='utf-8') as f:
    CHATFLOW = json.load(f)

# Store for user sessions (in production, use database)
user_sessions = {}

# =============================================================================
# FLASK APP SETUP
# =============================================================================

app = Flask(__name__)

@app.route('/webhook/whatsapp', methods=['GET', 'POST'])
def webhook():
    """
    Main webhook endpoint for WhatsApp messages
    Handles verification and incoming messages
    """
    if request.method == 'GET':
        return verify_webhook(request)
    elif request.method == 'POST':
        return handle_message(request)

# =============================================================================
# WEBHOOK VERIFICATION
# =============================================================================

def verify_webhook(req):
    """
    Verify the webhook endpoint with WhatsApp
    Called with hub.verify_token and hub.challenge
    """
    verify_token = req.args.get('hub.verify_token')
    challenge = req.args.get('hub.challenge')

    logger.info(f"Webhook verification attempt with token: {verify_token}")

    if verify_token == VERIFY_TOKEN:
        logger.info("Webhook verification successful!")
        return challenge, 200
    else:
        logger.warning(f"Invalid verification token: {verify_token}")
        return jsonify({"error": "Invalid verification token"}), 403

# =============================================================================
# MESSAGE HANDLING
# =============================================================================

def handle_message(req):
    """
    Process incoming messages from WhatsApp
    Handles button replies, list selections, and text input
    """
    try:
        body = req.get_json()
        
        # Validate webhook signature (optional but recommended)
        # validate_webhook_signature(req)
        
        # Check if this is a valid WhatsApp message event
        if body.get('object') != 'whatsapp_business_account':
            return jsonify({"error": "Invalid object"}), 400

        entry = body.get('entry', [])[0]
        changes = entry.get('changes', [])[0]
        value = changes.get('value', {})

        # Handle incoming messages
        if 'messages' in value:
            message = value['messages'][0]
            contact_id = value['contacts'][0]['wa_id']
            contact_name = value['contacts'][0]['profile']['name']
            
            logger.info(f"Message from {contact_name} ({contact_id}): {message}")
            
            # Route message to appropriate handler
            process_incoming_message(contact_id, contact_name, message)
            
        # Handle message status updates
        elif 'statuses' in value:
            status = value['statuses'][0]
            logger.info(f"Message status update: {status}")
            
        return jsonify({"status": "ok"}), 200

    except Exception as e:
        logger.error(f"Error handling message: {str(e)}")
        return jsonify({"error": str(e)}), 500

# =============================================================================
# MESSAGE PROCESSING
# =============================================================================

def process_incoming_message(user_id: str, user_name: str, message: Dict[str, Any]):
    """
    Route incoming message to appropriate handler based on type
    """
    
    # Initialize user session if new
    if user_id not in user_sessions:
        user_sessions[user_id] = {
            'user_id': user_id,
            'user_name': user_name,
            'current_step': 'welcome',
            'language': 'en',
            'session_start': datetime.now().isoformat(),
            'conversation_data': {},
            'messages_sent': 0,
            'messages_received': 0
        }
    
    session = user_sessions[user_id]
    session['messages_received'] += 1
    
    # Handle different message types
    if 'interactive' in message:
        handle_interactive_message(user_id, session, message['interactive'])
    elif 'text' in message:
        handle_text_message(user_id, session, message['text']['body'])
    elif 'location' in message:
        handle_location_message(user_id, session, message['location'])
    else:
        send_fallback_message(user_id, session, 'unrecognized_input')

# =============================================================================
# INTERACTIVE MESSAGE HANDLER (Buttons & Lists)
# =============================================================================

def handle_interactive_message(user_id: str, session: Dict, interactive: Dict):
    """
    Handle button clicks and list selections
    """
    
    # Extract selected option ID
    selected_id = None
    
    if 'button_reply' in interactive:
        selected_id = interactive['button_reply']['id']
        logger.info(f"User {user_id} clicked button: {selected_id}")
        
    elif 'list_reply' in interactive:
        selected_id = interactive['list_reply']['id']
        logger.info(f"User {user_id} selected list item: {selected_id}")
    
    if not selected_id:
        send_fallback_message(user_id, session, 'unrecognized_input')
        return
    
    # Handle specific selections
    if selected_id in ['lang_en', 'lang_ar']:
        handle_language_selection(user_id, session, selected_id)
    else:
        navigate_flow(user_id, session, selected_id)

# =============================================================================
# TEXT MESSAGE HANDLER
# =============================================================================

def handle_text_message(user_id: str, session: Dict, text: str):
    """
    Handle free-form text input
    Used for quotation forms and inquiries
    """
    
    logger.info(f"User {user_id} sent text: {text}")
    
    current_step_id = session['current_step']
    current_step = CHATFLOW['steps'].get(current_step_id)
    
    if not current_step:
        send_fallback_message(user_id, session, 'unrecognized_input')
        return
    
    # If current step expects text input (requires_human_followup)
    if current_step.get('requires_human_followup'):
        # Save the message data
        session['conversation_data']['last_message'] = text
        session['conversation_data']['message_received_at'] = datetime.now().isoformat()
        
        # Show confirmation
        lang = session['language']
        next_step_id = current_step.get('next', 'quote_submitted')
        show_step(user_id, session, next_step_id)
        
        # Queue for human followup
        queue_for_human_followup(user_id, session, text)
    else:
        send_fallback_message(user_id, session, 'unrecognized_input')

# =============================================================================
# FLOW NAVIGATION
# =============================================================================

def navigate_flow(user_id: str, session: Dict, selected_id: str):
    """
    Navigate to next step based on user selection
    """
    
    current_step_id = session['current_step']
    current_step = CHATFLOW['steps'].get(current_step_id)
    
    if not current_step:
        logger.error(f"Current step {current_step_id} not found in chatflow")
        send_fallback_message(user_id, session, 'unrecognized_input')
        return
    
    # Get next step from next_logic
    next_logic = current_step.get('next_logic', {})
    next_step_id = next_logic.get(selected_id)
    
    if not next_step_id:
        logger.warning(f"No next step found for {selected_id} in {current_step_id}")
        send_fallback_message(user_id, session, 'unrecognized_input')
        return
    
    # Update session and show next step
    session['current_step'] = next_step_id
    session['conversation_data'][current_step_id] = {
        'selected': selected_id,
        'timestamp': datetime.now().isoformat()
    }
    
    show_step(user_id, session, next_step_id)

# =============================================================================
# LANGUAGE SELECTION
# =============================================================================

def handle_language_selection(user_id: str, session: Dict, lang_id: str):
    """
    Handle language selection (en/ar)
    """
    
    if lang_id == 'lang_en':
        session['language'] = 'en'
    elif lang_id == 'lang_ar':
        session['language'] = 'ar'
    
    logger.info(f"User {user_id} selected language: {session['language']}")
    
    # Move to main menu
    session['current_step'] = 'main_menu'
    show_step(user_id, session, 'main_menu')

# =============================================================================
# STEP DISPLAY
# =============================================================================

def show_step(user_id: str, session: Dict, step_id: str):
    """
    Display a conversation step to the user
    """
    
    step = CHATFLOW['steps'].get(step_id)
    
    if not step:
        logger.error(f"Step {step_id} not found in chatflow")
        send_fallback_message(user_id, session, 'unrecognized_input')
        return
    
    lang = session['language']
    step_type = step.get('type')
    
    logger.info(f"Showing step {step_id} to user {user_id} ({lang})")
    
    # Get message content based on language
    if step_type == 'interactive_button':
        send_button_message(user_id, session, step)
    elif step_type == 'interactive_list':
        send_list_message(user_id, session, step)
    elif step_type == 'text':
        send_text_message(user_id, session, step)
    else:
        logger.error(f"Unknown step type: {step_type}")
        send_text_message(user_id, session, step)

# =============================================================================
# MESSAGE SENDING FUNCTIONS
# =============================================================================

def send_button_message(user_id: str, session: Dict, step: Dict):
    """
    Send interactive button message
    """
    
    lang = session['language']
    
    try:
        # Build message
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": user_id,
            "type": "interactive",
            "interactive": {
                "type": "button",
                "body": {
                    "text": step.get(f'body_{lang}', step.get('body_en', 'Select an option'))
                },
                "action": {
                    "buttons": []
                }
            }
        }
        
        # Add buttons
        for button in step.get('buttons', []):
            message_data['interactive']['action']['buttons'].append({
                "type": "reply",
                "reply": {
                    "id": button.get('id'),
                    "title": button.get(f'title_{lang}', button.get('title_en', 'Button'))[:20]  # WhatsApp limit
                }
            })
        
        # Send message
        send_whatsapp_message(message_data)
        session['messages_sent'] += 1
        
    except Exception as e:
        logger.error(f"Error sending button message: {str(e)}")
        send_text_message(user_id, session, step)

def send_list_message(user_id: str, session: Dict, step: Dict):
    """
    Send interactive list message
    """
    
    lang = session['language']
    
    try:
        # Build message
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": user_id,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": step.get(f'header_{lang}', step.get('header_en', 'Options'))
                },
                "body": {
                    "text": step.get(f'body_{lang}', step.get('body_en', 'Please select an option'))
                },
                "footer": {
                    "text": step.get(f'footer_{lang}', step.get('footer_en', 'Hi-Tech Industrial Group')) 
                },
                "action": {
                    "button": step.get(f'button_text_{lang}', step.get('button_text_en', 'Select')),
                    "sections": []
                }
            }
        }
        
        # Add sections and rows
        for section in step.get('sections', []):
            section_data = {
                "title": section.get(f'title_{lang}', section.get('title_en', 'Section')),
                "rows": []
            }
            
            for row in section.get('rows', []):
                section_data['rows'].append({
                    "id": row.get('id'),
                    "title": row.get(f'title_{lang}', row.get('title_en', 'Option'))[:24],
                    "description": row.get(f'description_{lang}', row.get('description_en', ''))[:72]
                })
            
            message_data['interactive']['action']['sections'].append(section_data)
        
        # Send message
        send_whatsapp_message(message_data)
        session['messages_sent'] += 1
        
    except Exception as e:
        logger.error(f"Error sending list message: {str(e)}")
        send_text_message(user_id, session, step)

def send_text_message(user_id: str, session: Dict, step: Dict):
    """
    Send simple text message
    """
    
    lang = session['language']
    
    try:
        message_data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": user_id,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": step.get(f'body_{lang}', step.get('body_en', 'Please try again'))
            }
        }
        
        send_whatsapp_message(message_data)
        session['messages_sent'] += 1
        
    except Exception as e:
        logger.error(f"Error sending text message: {str(e)}")

def send_whatsapp_message(message_data: Dict) -> bool:
    """
    Send message via WhatsApp Business API
    """
    
    try:
        headers = {
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        url = f"{WHATSAPP_API_URL}{PHONE_NUMBER_ID}/messages"
        
        response = requests.post(url, json=message_data, headers=headers)
        response.raise_for_status()
        
        logger.info(f"Message sent successfully: {response.json()}")
        return True
        
    except requests.exceptions.RequestException as e:
        logger.error(f"Error sending WhatsApp message: {str(e)}")
        return False

# =============================================================================
# FALLBACK & ERROR HANDLING
# =============================================================================

def send_fallback_message(user_id: str, session: Dict, fallback_type: str):
    """
    Send fallback message for unrecognized input
    """
    
    fallback = CHATFLOW['fallback_handlers'].get(fallback_type)
    
    if fallback:
        send_text_message(user_id, session, fallback)
    else:
        # Generic fallback
        lang = session['language']
        default_msg = {
            'body_en': "I'm sorry, I didn't understand that. Please select from the available options or type 'help'.",
            'body_ar': "أعتذر، لم أفهم ذلك. يرجى الاختيار من الخيارات المتاحة أو اكتب 'help'."
        }
        send_text_message(user_id, session, default_msg)

# =============================================================================
# HUMAN HANDOFF
# =============================================================================

def queue_for_human_followup(user_id: str, session: Dict, last_message: str):
    """
    Queue conversation for human agent followup
    """
    
    # In production, save to database or queue system
    followup_data = {
        'user_id': user_id,
        'user_name': session['user_name'],
        'current_step': session['current_step'],
        'language': session['language'],
        'last_message': last_message,
        'queued_at': datetime.now().isoformat(),
        'priority': 'normal'
    }
    
    logger.info(f"Queued for human followup: {json.dumps(followup_data, indent=2)}")
    
    # TODO: Save to database/queue (e.g., Retool, Airtable, Firebase)
    # save_to_queue(followup_data)

# =============================================================================
# LOCATION MESSAGE HANDLER
# =============================================================================

def handle_location_message(user_id: str, session: Dict, location: Dict):
    """
    Handle location shared by user
    """
    
    lat = location.get('latitude')
    lon = location.get('longitude')
    
    logger.info(f"User {user_id} shared location: {lat}, {lon}")
    
    # Save location for later use
    session['conversation_data']['location'] = {
        'latitude': lat,
        'longitude': lon,
        'timestamp': datetime.now().isoformat()
    }
    
    # Continue with current flow
    show_step(user_id, session, session['current_step'])

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def validate_webhook_signature(req) -> bool:
    """
    Validate webhook signature (optional but recommended)
    """
    # TODO: Implement signature validation
    # See: https://developers.facebook.com/docs/graph-api/webhooks/getting-started
    return True

# =============================================================================
# SESSION MANAGEMENT
# =============================================================================

@app.route('/api/session/<user_id>', methods=['GET'])
def get_session(user_id):
    """
    Get user session data (for debugging)
    """
    if user_id in user_sessions:
        return jsonify(user_sessions[user_id])
    return jsonify({"error": "Session not found"}), 404

@app.route('/api/sessions/count', methods=['GET'])
def count_sessions():
    """
    Get total active sessions
    """
    return jsonify({"active_sessions": len(user_sessions)})

# =============================================================================
# STATIC CONTENT
# =============================================================================

@app.route('/api/chatflow', methods=['GET'])
def get_chatflow():
    """
    Get complete chatflow (for development/debugging)
    """
    return jsonify(CHATFLOW)

@app.route('/api/steps/<step_id>', methods=['GET'])
def get_step(step_id):
    """
    Get specific step details
    """
    step = CHATFLOW['steps'].get(step_id)
    if step:
        return jsonify(step)
    return jsonify({"error": "Step not found"}), 404

# =============================================================================
# MAIN
# =============================================================================

if __name__ == '__main__':
    print("""
    ╔══════════════════════════════════════════════════════════════╗
    ║  Hi-Tech Industrial Group - WhatsApp Chatflow Handler        ║
    ║  Flask Server Starting...                                    ║
    ║  Endpoint: http://localhost:5000/webhook/whatsapp           ║
    ║  Status: DEVELOPMENT (Use production WSGI server in live)    ║
    ║  Docs: DEPLOYMENT_GUIDE.md                                   ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True  # Set to False in production
    )
