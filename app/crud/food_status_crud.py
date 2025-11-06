from sqlalchemy.orm import Session
from app.models import models
from datetime import datetime, timedelta


def update_food_status(db: Session, foodstatus):
    """
    Update food status by adding a new entry to FoodStatusLog.
    
    Args:
        db: Database session
        foodstatus: Food status data containing inventory_id, status, and notes
        
    Returns:
        dict: Success/failure message
    """
    try:
        # Get user_id from inventory item before updating status
        inventory_item = db.query(models.Inventory).filter(
            models.Inventory.id == foodstatus.inventory_id
        ).first()
        user_id = inventory_item.u_id if inventory_item else None
        
        food_status_log = models.FoodStatusLog(
            inventory_id=foodstatus.inventory_id,
            status=foodstatus.status,
            notes=foodstatus.notes,
            timestamp=datetime.now()
        )
        db.add(food_status_log)
        db.commit()
        db.refresh(food_status_log)
        
        # Send expiry alerts automatically when item status changes
        if user_id:
            try:
                from app.whatsapp_alerts import send_expiry_alerts
                print(f"DEBUG: Item status changed for user {user_id}, checking for expiry alerts...")
                alert_result = send_expiry_alerts(db, user_id)
                print(f"DEBUG: Expiry alerts result after status change: {alert_result}")
            except Exception as e:
                print(f"DEBUG: Error sending expiry alerts after status change: {str(e)}")
                # Don't fail status update if alerts fail
        
        return {"message": "success"}
    except Exception as e:
        return {"message": "Failed to update food status", "error": str(e)}


def get_expiring_items(db: Session, user_id: int, days: int = 3):
    """
    Get items that are expiring within the specified number of days.
    
    Args:
        db: Database session
        user_id: User ID
        days: Number of days to check for expiration (default: 3)
        
    Returns:
        list: List of expiring inventory items
    """
    try:
        today = datetime.now().date()  # Get today's date only
        upcoming = today + timedelta(days=days)

        expiring_items = db.query(models.Inventory).filter(
            models.Inventory.u_id == user_id,
            models.Inventory.expiry_date >= datetime.combine(today, datetime.min.time()),
            models.Inventory.expiry_date <= datetime.combine(upcoming, datetime.max.time())
        ).all()

        return expiring_items
    
    except Exception as e:
        return {"message": e}
