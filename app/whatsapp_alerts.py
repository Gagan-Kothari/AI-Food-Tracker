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
WHATSAPP_API_VERSION = os.getenv("WHATSAPP_API_VERSION", "v21.0")  # Default to v21.0

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


def send_whatsapp_message(to_phone: str, message: str) -> dict:
    """
    Send WhatsApp message via Official WhatsApp Business API
    
    Args:
        to_phone: Recipient phone number (format: +1234567890)
        message: Message to send
        
    Returns:
        dict: Success/failure status
    """
    try:
        if not WHATSAPP_ACCESS_TOKEN or not WHATSAPP_PHONE_NUMBER_ID:
            print("ERROR: WhatsApp credentials not configured")
            return {
                "status": False,
                "message": "WhatsApp credentials not configured. Set WHATSAPP_ACCESS_TOKEN and WHATSAPP_PHONE_NUMBER_ID in .env"
            }
        
        formatted_phone = format_phone_number(to_phone)
        print(f"DEBUG: Sending WhatsApp message to: {formatted_phone}")
        print(f"DEBUG: Original phone number: {to_phone}")
        print(f"DEBUG: Message preview: {message[:50]}...")
        
        # WhatsApp Cloud API endpoint
        url = f"{WHATSAPP_API_BASE_URL}/{WHATSAPP_PHONE_NUMBER_ID}/messages"
        
        # Request headers
        headers = {
            "Authorization": f"Bearer {WHATSAPP_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        
        # Request payload
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": formatted_phone,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        
        print(f"DEBUG: WhatsApp API URL: {url}")
        print(f"DEBUG: Payload: {payload}")
        
        # Send request
        response = requests.post(url, json=payload, headers=headers)
        
        print(f"DEBUG: Response status code: {response.status_code}")
        print(f"DEBUG: Response content: {response.text}")
        
        if response.status_code == 200:
            response_data = response.json()
            print(f"SUCCESS: WhatsApp message sent. Message ID: {response_data.get('messages', [{}])[0].get('id', '')}")
            return {
                "status": True,
                "message": "WhatsApp alert sent successfully",
                "message_id": response_data.get("messages", [{}])[0].get("id", "")
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
        items_by_alert = get_items_for_alerts(db, user_id)
        
        if "error" in items_by_alert:
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
        
        # Send alerts to each user
        for uid, items in user_items.items():
            user = db.query(models.Users).filter(models.Users.id == uid).first()
            if not user or not user.phone_number:
                continue
            
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
                result = send_whatsapp_message(user.phone_number, message)
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
