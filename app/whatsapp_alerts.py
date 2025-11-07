"""
WhatsApp expiry alerts using Official WhatsApp Business API (Meta)
"""
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models import models
import requests

load_dotenv()

# WhatsApp Business API credentials - set these in your .env file
WHATSAPP_ACCESS_TOKEN = os.getenv("WHATSAPP_ACCESS_TOKEN")
WHATSAPP_PHONE_NUMBER_ID = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
WHATSAPP_BUSINESS_ACCOUNT_ID = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID")  # Optional
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v24.0")  # Default to v24.0 (v21.0 is deprecated)

# WhatsApp Cloud API base URL
WHATSAPP_API_BASE_URL = f"https://graph.facebook.com/{WHATSAPP_API_VERSION}"


def format_phone_number(phone: str) -> str:
    """
    Format phone number for WhatsApp API
    Phone should be in E.164 format: +1234567890
    """
    if not phone:
        print("WARNING: Empty phone number provided")
        return ""
    phone = phone.strip()
    print(f"DEBUG: Formatting phone number. Original: '{phone}'")
    
    # Remove any existing whatsapp: prefix
    if phone.startswith("whatsapp:"):
        phone = phone.replace("whatsapp:", "")
    
    # Remove any spaces, dashes, or parentheses
    phone = phone.replace(" ", "").replace("-", "").replace("(", "").replace(")", "")
    
    # Ensure it starts with +
    if not phone.startswith("+"):
        # If it starts with 0, remove it (common in some countries)
        if phone.startswith("0"):
            phone = phone[1:]
        # Add + prefix
        phone = "+" + phone
    
    print(f"DEBUG: Formatted phone number: '{phone}'")
    return phone


def send_whatsapp_message(to_phone: str, message: str, template_name: str = None) -> dict:
    """
    Send WhatsApp message via Official WhatsApp Business API
    
    Args:
        to_phone: Recipient phone number (format: +1234567890)
        message: Message to send
        
    Returns:
        dict: Success/failure status
    """
    try:
        # Debug: Check if credentials are loaded
        print(f"DEBUG: ========== WhatsApp API Call Debug ==========")
        print(f"DEBUG: WHATSAPP_ACCESS_TOKEN present: {bool(WHATSAPP_ACCESS_TOKEN)}")
        print(f"DEBUG: WHATSAPP_ACCESS_TOKEN length: {len(WHATSAPP_ACCESS_TOKEN) if WHATSAPP_ACCESS_TOKEN else 0}")
        print(f"DEBUG: WHATSAPP_ACCESS_TOKEN first 20 chars: {WHATSAPP_ACCESS_TOKEN[:20] if WHATSAPP_ACCESS_TOKEN else 'None'}...")
        print(f"DEBUG: WHATSAPP_PHONE_NUMBER_ID: {WHATSAPP_PHONE_NUMBER_ID}")
        print(f"DEBUG: WHATSAPP_API_VERSION: {WHATSAPP_API_VERSION}")
        
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print("ERROR: WhatsApp credentials not configured")
            print(f"ERROR: WHATSAPP_ACCESS_TOKEN = {WHATSAPP_ACCESS_TOKEN}")
            print(f"ERROR: WHATSAPP_PHONE_NUMBER_ID = {WHATSAPP_PHONE_NUMBER_ID}")
            return {
                "status": False,
                "message": "WhatsApp credentials not configured. Set WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env"
            }
        
        formatted_phone = format_phone_number(to_phone)
        
        # WhatsApp API expects phone number WITHOUT the + sign
        # Remove + if present (format: 919811546101 instead of +919811546101)
        whatsapp_phone = formatted_phone.lstrip('+')
        
        print(f"DEBUG: Sending WhatsApp message to: {whatsapp_phone}")
        print(f"DEBUG: Original phone number: {to_phone}")
        print(f"DEBUG: Formatted (with +): {formatted_phone}")
        print(f"DEBUG: WhatsApp format (no +): {whatsapp_phone}")
        print(f"DEBUG: Message preview: {message[:50]}...")
        
        # WhatsApp Cloud API endpoint
        url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Request payload - Use template format since test template works but text messages don't
        # In development mode, business-initiated messages require templates (text messages only work in 24-hour window)
        # Try to use custom template if available, otherwise fall back to hello_world for testing
        # Note: WhatsApp API expects phone number WITHOUT + sign (e.g., "919811546101" not "+919811546101")
        
        # Check if we have a custom template name (parameter, then environment variable, then default)
        if template_name is None:
            template_name = os.getenv("WHATSAPP_TEMPLATE_NAME", "hello_world")
        
        # Build template payload
        # For hello_world: no components needed (fixed message)
        # For custom templates: include components with message body
        if template_name == "hello_world":
            # Use hello_world template (fixed message, no custom content)
            payload = {
                "messaging_product": "whatsapp",
                "to": whatsapp_phone,
                "type": "template",
                "template": {
                    "name": "hello_world",
                    "language": {
                        "code": "en_US"
                    }
                }
            }
            print(f"DEBUG: Using hello_world template (test template - will send 'Hello World!' message)")
            print(f"DEBUG: Original message was: {message[:100]}...")
            print(f"WARNING: hello_world template has fixed content. Create custom templates for actual messages.")
        else:
            # Use custom template with message body as parameter
            payload = {
                "messaging_product": "whatsapp",
                "to": whatsapp_phone,
                "type": "template",
                "template": {
                    "name": template_name,
                    "language": {
                        "code": "en_US"
                    },
                    "components": [
                        {
                            "type": "body",
                            "parameters": [
                                {
                                    "type": "text",
                                    "text": message
                                }
                            ]
                        }
                    ]
                }
            }
            print(f"DEBUG: Using custom template: {template_name}")
            print(f"DEBUG: Message content: {message[:100]}...")
        
        print(f"DEBUG: WhatsApp API URL: {url}")
        print(f"DEBUG: Full URL matches test template format: https://graph.facebook.com/{WHATSAPP_API_VERSION}/{WHATSAPP_PHONE_NUMBER_ID}/messages")
        print(f"DEBUG: Payload (JSON): {payload}")
        print(f"DEBUG: Headers (Authorization): Bearer {WHATSAPP_ACCESS_TOKEN[:20]}...")
        
        # Send request
        print(f"DEBUG: ========== Sending Request ==========")
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=10)
        except requests.exceptions.RequestException as e:
            print(f"ERROR: Request failed: {str(e)}")
            return {
                "status": False,
                "message": f"Failed to send request: {str(e)}"
            }
        
        print(f"DEBUG: Response status code: {response.status_code}")
        print(f"DEBUG: Response headers: {dict(response.headers)}")
        print(f"DEBUG: Response content: {response.text}")
        
        # Check for token expiration warnings
        if 'x-ad-api-version-warning' in response.headers:
            warning = response.headers.get('x-ad-api-version-warning', '')
            print(f"WARNING: API version warning: {warning}")
            print(f"WARNING: Consider updating WHATSAPP_API_VERSION environment variable to v24.0")
        
        # Check for authentication errors in response
        if response.status_code == 401:
            print(f"ERROR: Authentication failed. Access token may be expired or invalid.")
            print(f"ERROR: Generate a new access token from Meta for Developers and update Railway variables.")
            return {
                "status": False,
                "message": "Authentication failed. Access token may be expired. Please generate a new token.",
                "error_code": 401
            }
        
        # Check for rate limiting
        if response.status_code == 429:
            print(f"ERROR: Rate limit exceeded. Wait before sending more messages.")
            return {
                "status": False,
                "message": "Rate limit exceeded. Please wait before sending more messages."
            }
        
        # Compare with test template
        print(f"DEBUG: ========== Comparison with Test Template ==========")
        print(f"DEBUG: Test template URL: https://graph.facebook.com/v22.0/903484642839290/messages")
        print(f"DEBUG: Our URL: {url}")
        print(f"DEBUG: Test template 'to': '919811546101'")
        print(f"DEBUG: Our 'to': '{whatsapp_phone}'")
        print(f"DEBUG: Match: {'✅ MATCH' if whatsapp_phone == '919811546101' else '❌ MISMATCH'}")
        
        if response.status_code == 200:
            response_data = response.json()
            message_id = response_data.get("messages", [{}])[0].get("id", "")
            contact_info = response_data.get("contacts", [{}])[0] if response_data.get("contacts") else {}
            wa_id = contact_info.get("wa_id", "")
            
            print(f"SUCCESS: WhatsApp message sent. Message ID: {message_id}")
            print(f"SUCCESS: WhatsApp ID (wa_id): {wa_id}")
            print(f"SUCCESS: Contact info: {contact_info}")
            
            # Check if the phone number was recognized by WhatsApp
            if not wa_id:
                print(f"ERROR: WhatsApp did not return a wa_id. This means:")
                print(f"  - The number is NOT registered with WhatsApp")
                print(f"  - The number is NOT added as a test number in Meta")
                print(f"  - The phone number format is incorrect")
                return {
                    "status": False,
                    "message": "Phone number not recognized by WhatsApp. Verify the number is added as a test number in Meta.",
                    "wa_id": None
                }
            else:
                print(f"INFO: Message accepted by WhatsApp API (Message ID: {message_id})")
                print(f"INFO: WhatsApp ID (wa_id): {wa_id} - Number is recognized ✅")
                print(f"INFO: If message not received, check in this order:")
                print(f"  1. Meta Business Suite: https://business.facebook.com/inbox (check delivery status)")
                print(f"  2. Access token expiration (temporary tokens expire in 24 hours)")
                print(f"  3. WhatsApp spam/archived messages on your phone")
                print(f"  4. Wait 1-2 minutes for delivery (can be delayed)")
                print(f"  5. Verify test number is correctly added in Meta for Developers")
            
            return {
                "status": True,
                "message": "WhatsApp alert sent successfully",
                "message_id": message_id,
                "wa_id": wa_id,
                "contact_info": contact_info,
                "note": "If message not received, check WhatsApp spam/archived or verify access token hasn't expired"
            }
        else:
            error_data = response.json() if response.content else {}
            error_message = error_data.get("error", {}).get("message", "Unknown error")
            error_code = error_data.get("error", {}).get("code", "Unknown")
            print(f"ERROR: Failed to send WhatsApp message. Status: {response.status_code}, Error: {error_message}, Code: {error_code}")
            print(f"ERROR: Full error data: {error_data}")
            return {
                "status": False,
                "message": f"Failed to send WhatsApp alert: {error_message}",
                "error_code": response.status_code,
                "whatsapp_error_code": error_code,
                "error_details": error_data
            }
    except Exception as e:
        print(f"EXCEPTION: Error sending WhatsApp message: {str(e)}")
        import traceback
        print(f"EXCEPTION: Traceback: {traceback.format_exc()}")
        return {
            "status": False,
            "message": f"Failed to send WhatsApp alert: {str(e)}"
        }


def get_items_for_alerts(db: Session, user_id: int = None):
    """
    Get items that need expiry alerts, excluding consumed/donated items
    
    Args:
        db: Database session
        user_id: Optional user ID to filter by specific user
        
    Returns:
        dict: Items categorized by alert type (yellow, red, grey)
    """
    try:
        today = datetime.now().date()
        yellow_threshold = today + timedelta(days=7)  # 7 days from now
        red_threshold = today + timedelta(days=3)    # 3 days from now
        
        # Get all inventory items
        query = db.query(models.Inventory).join(models.Food_Items)
        
        if user_id:
            query = query.filter(models.Inventory.u_id == user_id)
        
        all_items = query.all()
        
        # Get inventory IDs that are already consumed or donated
        consumed_donated_ids_query = db.query(models.FoodStatusLog.inventory_id).filter(
            models.FoodStatusLog.status.in_(["consumed", "donated"])
        ).all()
        consumed_donated_ids = {row[0] for row in consumed_donated_ids_query}
        
        # Filter out consumed/donated items
        items_to_check = [
            item for item in all_items 
            if item.id not in consumed_donated_ids
        ]
        
        yellow_items = []  # Expiring in 7 days
        red_items = []      # Expiring in 3 days
        grey_items = []     # Expired
        
        for item in items_to_check:
            expiry_date = item.expiry_date.date() if item.expiry_date else None
            if not expiry_date:
                continue
            
            days_until_expiry = (expiry_date - today).days
            
            if expiry_date < today:
                # Expired
                grey_items.append(item)
            elif expiry_date <= red_threshold:
                # Expiring in 3 days or less
                red_items.append(item)
            elif expiry_date <= yellow_threshold:
                # Expiring in 7 days or less (but more than 3)
                yellow_items.append(item)
        
        return {
            "yellow": yellow_items,
            "red": red_items,
            "grey": grey_items
        }
    except Exception as e:
        return {
            "error": str(e),
            "yellow": [],
            "red": [],
            "grey": []
        }


def send_expiry_alerts(db: Session, user_id: int = None) -> dict:
    """
    Check expiry dates and send WhatsApp alerts to users
    
    Args:
        db: Database session
        user_id: Optional user ID to send alerts for specific user
        
    Returns:
        dict: Summary of alerts sent
    """
    try:
        print(f"DEBUG: send_expiry_alerts called for user_id: {user_id}")
        items_by_alert = get_items_for_alerts(db, user_id)
        
        print(f"DEBUG: Items by alert type - Yellow: {len(items_by_alert.get('yellow', []))}, Red: {len(items_by_alert.get('red', []))}, Grey: {len(items_by_alert.get('grey', []))}")
        
        if "error" in items_by_alert:
            print(f"ERROR: Error getting items for alerts: {items_by_alert['error']}")
            return {"status": False, "message": items_by_alert["error"]}
        
        alerts_sent = {
            "yellow": 0,
            "red": 0,
            "grey": 0,
            "failed": 0
        }
        
        # Group items by user
        user_items = {}
        for alert_type in ["yellow", "red", "grey"]:
            for item in items_by_alert[alert_type]:
                if item.u_id not in user_items:
                    user_items[item.u_id] = {"yellow": [], "red": [], "grey": []}
                user_items[item.u_id][alert_type].append(item)
        
        print(f"DEBUG: Found {len(user_items)} user(s) with items needing alerts")
        
        # Send alerts to each user
        for uid, items in user_items.items():
            user = db.query(models.Users).filter(models.Users.id == uid).first()
            if not user:
                print(f"DEBUG: User {uid} not found in database")
                continue
            if not user.phone_number:
                print(f"DEBUG: User {uid} has no phone number. Phone: {user.phone_number}")
                continue
            
            print(f"DEBUG: Sending alerts to user {uid} (phone: {user.phone_number})")
            print(f"DEBUG: Alert counts - Yellow: {len(items['yellow'])}, Red: {len(items['red'])}, Grey: {len(items['grey'])}")
            
            # Build messages for each alert type
            messages = []
            
            if items["yellow"]:
                yellow_msg = "🟡 YELLOW ALERT: Items expiring in 7 days:\n"
                for item in items["yellow"]:
                    # Get food item details using relationship
                    food_item = item.food_item if hasattr(item, 'food_item') else None
                    if not food_item:
                        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == item.f_id).first()
                    expiry_date = item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else "N/A"
                    days_left = (item.expiry_date.date() - datetime.now().date()).days if item.expiry_date else 0
                    food_name = food_item.f_name if food_item and food_item.f_name else "Unknown"
                    yellow_msg += f"• {food_name} - Expires: {expiry_date} ({days_left} days left)\n"
                messages.append(("yellow", yellow_msg))
            
            if items["red"]:
                red_msg = "🔴 RED ALERT: Items expiring in 3 days:\n"
                for item in items["red"]:
                    # Get food item details using relationship
                    food_item = item.food_item if hasattr(item, 'food_item') else None
                    if not food_item:
                        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == item.f_id).first()
                    expiry_date = item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else "N/A"
                    days_left = (item.expiry_date.date() - datetime.now().date()).days if item.expiry_date else 0
                    food_name = food_item.f_name if food_item and food_item.f_name else "Unknown"
                    red_msg += f"• {food_name} - Expires: {expiry_date} ({days_left} days left)\n"
                messages.append(("red", red_msg))
            
            if items["grey"]:
                grey_msg = "⚫ GREY ALERT: Items have expired:\n"
                for item in items["grey"]:
                    # Get food item details using relationship
                    food_item = item.food_item if hasattr(item, 'food_item') else None
                    if not food_item:
                        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == item.f_id).first()
                    expiry_date = item.expiry_date.strftime("%Y-%m-%d") if item.expiry_date else "N/A"
                    food_name = food_item.f_name if food_item and food_item.f_name else "Unknown"
                    grey_msg += f"• {food_name} - Expired: {expiry_date}\n"
                messages.append(("grey", grey_msg))
            
            # Send all messages for this user
            for alert_type, message in messages:
                # Use expiry_alert template for all expiry alerts
                result = send_whatsapp_message(user.phone_number, message, template_name="expiry_alert")
                if result["status"]:
                    alerts_sent[alert_type] += 1
                else:
                    alerts_sent["failed"] += 1
        
        return {
            "status": True,
            "alerts_sent": alerts_sent,
            "message": f"Sent {sum(alerts_sent.values()) - alerts_sent['failed']} alerts"
        }
    except Exception as e:
        return {
            "status": False,
            "message": f"Failed to send expiry alerts: {str(e)}"
        }
