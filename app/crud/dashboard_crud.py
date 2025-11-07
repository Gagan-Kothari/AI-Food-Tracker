from sqlalchemy.orm import Session
from app.models import models
from sqlalchemy import func


def get_dashboard_stats(db: Session, user_id: int):
    """
    Get dashboard statistics for a user:
    - Items donated: Count of items with status 'donated' in FoodStatusLog
    - Recipes tried: Count of unique recipes tried by user
    - Items scanned: Count of items in Inventory for user
    
    Args:
        db: Database session
        user_id: User ID
        
    Returns:
        dict: Dashboard statistics
    """
    try:
        # Items donated: Count items with status 'donated' in FoodStatusLog
        # Join with Inventory to ensure items belong to this user
        items_donated = db.query(func.count(models.FoodStatusLog.id)).join(
            models.Inventory,
            models.FoodStatusLog.inventory_id == models.Inventory.id
        ).filter(
            models.Inventory.u_id == user_id,
            models.FoodStatusLog.status == "donated"
        ).scalar() or 0
        
        # Recipes tried: Count unique recipes tried by user
        recipes_tried = db.query(func.count(func.distinct(models.RecipesTried.recipe_id))).filter(
            models.RecipesTried.user_id == user_id
        ).scalar() or 0
        
        # Items scanned: Count of items in Inventory for user
        items_scanned = db.query(func.count(models.Inventory.id)).filter(
            models.Inventory.u_id == user_id
        ).scalar() or 0
        
        return {
            "status": True,
            "items_donated": items_donated,
            "recipes_tried": recipes_tried,
            "items_scanned": items_scanned
        }
    except Exception as e:
        return {
            "status": False,
            "message": f"Failed to get dashboard stats: {str(e)}",
            "items_donated": 0,
            "recipes_tried": 0,
            "items_scanned": 0
        }

