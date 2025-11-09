from sqlalchemy.orm import Session
from app.models import models
from datetime import datetime
from app.whatsapp_alerts import send_whatsapp_message
from app.email_service import send_notification_email


def donate_items(db: Session, inventory_ids: list, user_id: int):
    """
    Mark selected items as donated by moving them to FoodStatusLog with 'donated' status.
    Also awards 50 points per donated item.
    
    Args:
        db: Database session
        inventory_ids: List of inventory item IDs to donate
        user_id: User ID
        
    Returns:
        dict: Success/failure message with donation details and points earned
    """
    try:
        donated_count = 0
        skipped_items = []
        
        for inventory_id in inventory_ids:
            # Check if the item belongs to the user
            inventory_item = db.query(models.Inventory).filter(
                models.Inventory.id == inventory_id,
                models.Inventory.u_id == user_id
            ).first()
            
            if not inventory_item:
                print(f"DEBUG: Item {inventory_id} not found or doesn't belong to user {user_id}")
                skipped_items.append(f"Item {inventory_id} not found")
                continue
            
            # Check if this item is already consumed or donated (but allow alert_sent items to be donated)
            existing_log = db.query(models.FoodStatusLog).filter(
                models.FoodStatusLog.inventory_id == inventory_id,
                models.FoodStatusLog.status.in_(["consumed", "donated"])
            ).first()
            
            if existing_log:
                print(f"DEBUG: Item {inventory_id} already has status '{existing_log.status}', skipping donation")
                skipped_items.append(f"Item {inventory_id} already {existing_log.status}")
                continue
            
            # Check if there's an alert_sent log - if so, update it to donated
            alert_log = db.query(models.FoodStatusLog).filter(
                models.FoodStatusLog.inventory_id == inventory_id,
                models.FoodStatusLog.status == "alert_sent"
            ).first()
            
            if alert_log:
                # Update existing alert_sent log to donated
                alert_log.status = "donated"
                alert_log.notes = "Donated to NGO (previously alerted)"
                alert_log.timestamp = datetime.now()
                print(f"DEBUG: Updated item {inventory_id} from alert_sent to donated")
                donated_count += 1
            else:
                # Create new log entry with 'donated' status
                food_status_log = models.FoodStatusLog(
                    inventory_id=inventory_id,
                    status="donated",
                    notes="Donated to NGO",
                    timestamp=datetime.now()
                )
                db.add(food_status_log)
                print(f"DEBUG: Created new donation log for item {inventory_id}")
                donated_count += 1
        
        if donated_count > 0:
            # Award points to the user (50 points per donated item)
            points_earned = donated_count * 50
            user = db.query(models.Users).filter(models.Users.id == user_id).first()
            if user:
                user.points += points_earned
            
            # Get donated items details for notification
            donated_items_details = []
            for inventory_id in inventory_ids:
                inventory_item = db.query(models.Inventory).filter(
                    models.Inventory.id == inventory_id,
                    models.Inventory.u_id == user_id
                ).first()
                if inventory_item:
                    food_item = db.query(models.Food_Items).filter(
                        models.Food_Items.f_id == inventory_item.f_id
                    ).first()
                    if food_item:
                        donated_items_details.append(food_item.f_name or "Unknown item")
            
            db.commit()
            
            # Send WhatsApp notification for donation
            if user and user.phone_number:
                print(f"DEBUG: User found with phone number: {user.phone_number}")
                donation_message = f"❤️ Thank you for your generous donation!\n\n"
                donation_message += f"You've donated {donated_count} item{'s' if donated_count > 1 else ''}:\n"
                for item_name in donated_items_details[:5]:  # Limit to first 5 items
                    donation_message += f"• {item_name}\n"
                if len(donated_items_details) > 5:
                    donation_message += f"• ... and {len(donated_items_details) - 5} more\n"
                donation_message += f"\n🎉 You've earned {points_earned} points!\n"
                donation_message += f"Total points: {user.points}\n\n"
                donation_message += f"Your kindness helps reduce food waste and feeds families in need. Thank you for making a difference! 🌟"
                
                result = send_whatsapp_message(user.phone_number, donation_message, template_name="donation_notification")
                print(f"DEBUG: Donation notification result: {result}")
            
            # Send email notification alongside WhatsApp
            if user and user.email:
                try:
                    email_subject = "FoodTracker - Thank You for Your Donation!"
                    email_result = send_notification_email(user.email, email_subject, donation_message)
                    if email_result.get("status"):
                        print(f"DEBUG: Donation notification email sent to {user.email}")
                except Exception as e:
                    print(f"ERROR: Failed to send donation email: {str(e)}")
            
            if not user or not user.phone_number:
                print(f"DEBUG: User not found or no phone number. User: {user}, Phone: {user.phone_number if user else 'No user'}")
            
            return {
                "message": f"Successfully donated {donated_count} items", 
                "donated_count": donated_count, 
                "points_earned": points_earned,
                "total_points": user.points if user else 0,
                "status": True
            }
        else:
            error_msg = "No items were donated"
            if skipped_items:
                error_msg += f". Reasons: {', '.join(skipped_items[:3])}"  # Show first 3 reasons
            print(f"DEBUG: Donation failed - {error_msg}")
            return {"message": error_msg, "donated_count": 0, "status": False, "skipped_items": skipped_items}
            
    except Exception as e:
        print(f"ERROR: Exception in donate_items: {str(e)}")
        import traceback
        print(f"ERROR: Traceback: {traceback.format_exc()}")
        return {"message": "Failed to donate items", "error": str(e), "status": False}
