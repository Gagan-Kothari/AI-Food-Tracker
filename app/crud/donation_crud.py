from sqlalchemy.orm import Session
from app.models import models
from datetime import datetime
from app.whatsapp_alerts import send_whatsapp_message


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
        
        for inventory_id in inventory_ids:
            # Check if the item belongs to the user
            inventory_item = db.query(models.Inventory).filter(
                models.Inventory.id == inventory_id,
                models.Inventory.u_id == user_id
            ).first()
            
            if not inventory_item:
                continue
            
            # Check if this item is already in FoodStatusLog
            existing_log = db.query(models.FoodStatusLog).filter(
                models.FoodStatusLog.inventory_id == inventory_id
            ).first()
            
            if not existing_log:
                # Move to FoodStatusLog with 'donated' status
                food_status_log = models.FoodStatusLog(
                    inventory_id=inventory_id,
                    status="donated",
                    notes="Donated to NGO",
                    timestamp=datetime.now()
                )
                db.add(food_status_log)
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
                donation_message = f"❤️ Thank you for your generous donation!\n\n"
                donation_message += f"You've donated {donated_count} item{'s' if donated_count > 1 else ''}:\n"
                for item_name in donated_items_details[:5]:  # Limit to first 5 items
                    donation_message += f"• {item_name}\n"
                if len(donated_items_details) > 5:
                    donation_message += f"• ... and {len(donated_items_details) - 5} more\n"
                donation_message += f"\n🎉 You've earned {points_earned} points!\n"
                donation_message += f"Total points: {user.points}\n\n"
                donation_message += f"Your kindness helps reduce food waste and feeds families in need. Thank you for making a difference! 🌟"
                
                send_whatsapp_message(user.phone_number, donation_message)
            
            return {
                "message": f"Successfully donated {donated_count} items", 
                "donated_count": donated_count, 
                "points_earned": points_earned,
                "total_points": user.points if user else 0,
                "status": True
            }
        else:
            return {"message": "No items were donated", "donated_count": 0, "status": False}
            
    except Exception as e:
        return {"message": "Failed to donate items", "error": str(e), "status": False}
