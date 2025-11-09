from sqlalchemy.orm import Session
from app.models import models
from datetime import datetime
from app.crud.barcode_crud import find_categories


def add_to_database(db: Session, data, expirydate, user_id):
    """
    Add a food item to the database and user's inventory.
    
    Args:
        db: Database session
        data: Food item data from API
        expirydate: Expiry date for the item
        user_id: User ID
        
    Returns:
        dict: Success/failure message
    """
    try:
        f_id = int(data.get("code"))

        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == f_id).first()

        if not food_item:
            food_item = models.Food_Items(
                f_id=f_id,
                f_name=data.get("product_name_en"),
                brands=data.get("brands"),
                quantity=data.get("quantity"),
                energy=data.get("energy_kcal_100g") or 0,
                category=data.get("category"),
                categorystatus=data.get("categorystatus"),
                imageurl=data.get("imageurl")
            )
            db.add(food_item)
            db.commit()
            db.refresh(food_item)

        inventory_item = models.Inventory(
            f_id=food_item.f_id,
            u_id=user_id,
            expiry_date=expirydate
        )
        db.add(inventory_item)
        db.commit()

        # Send expiry alerts automatically when new item is added
        try:
            from app.whatsapp_alerts import send_expiry_alerts
            print(f"DEBUG: New item added for user {user_id}, checking for expiry alerts...")
            alert_result = send_expiry_alerts(db, user_id)
            print(f"DEBUG: Expiry alerts result after adding item: {alert_result}")
        except Exception as e:
            print(f"DEBUG: Error sending expiry alerts after adding item: {str(e)}")
            # Don't fail item addition if alerts fail

        return {"message": "success"}

    except Exception as e:
        return {"message": "Failed to add item", "error": str(e)}


def user_inventory(userid: int, db, foodstatus, inventory):
    """
    Get user's inventory items that haven't been consumed, donated, or expired.
    Items with 'alert_sent' status are still shown in inventory.
    
    Args:
        userid: User ID
        db: Database session
        foodstatus: FoodStatusLog model
        inventory: Inventory model
        
    Returns:
        list: List of inventory items with food details
    """
    try:
        # First, check and move any expired items for this user
        expired_result = check_and_move_expired_items(db, userid)
        print(f"Expired items check: {expired_result}")
        
        # Subquery to get inventory IDs that are consumed, donated, or expired (these should be hidden)
        # Items with 'alert_sent' status should still be visible
        subquery = db.query(foodstatus.inventory_id).filter(
            foodstatus.status.in_(["consumed", "donated", "expired"])
        ).subquery()

        # Main query to fetch inventory items that are not consumed, donated, or expired
        results = (
            db.query(inventory, models.Food_Items)
            .join(models.Food_Items, inventory.f_id == models.Food_Items.f_id)
            .filter(
                inventory.u_id == userid,
                ~inventory.id.in_(subquery)
            )
            .all()
        )

        inventory_data = []
        for inventory_item, food_item in results:
            inventory_data.append({
                "inventory_id": inventory_item.id,
                "expiry_date": inventory_item.expiry_date.strftime("%Y-%m-%d"),
                "f_id": inventory_item.f_id,
                "f_name": food_item.f_name or "",
                "brands": food_item.brands or "",
                "quantity": food_item.quantity or "",
                "energy": food_item.energy or 0,
                "category": food_item.category or "",
                "categorystatus": food_item.categorystatus or False,
                "imageurl": food_item.imageurl or "",
            })

        return inventory_data

    except Exception as e:
        return {"message": "Failed to fetch inventory", "error": str(e)}


def delete_inventory_item(db: Session, inventory_id: int, user_id: int):
    """
    Delete an inventory item for a specific user.
    
    Args:
        db: Database session
        inventory_id: Inventory item ID
        user_id: User ID
        
    Returns:
        dict: Success/failure message and status
    """
    try:
        # First check if the item belongs to the user
        inventory_item = db.query(models.Inventory).filter(
            models.Inventory.id == inventory_id,
            models.Inventory.u_id == user_id
        ).first()
        
        if not inventory_item:
            return {"message": "Item not found or not authorized", "status": False}
        
        # Delete the inventory item
        db.delete(inventory_item)
        db.commit()
        
        return {"message": "Item deleted successfully", "status": True}
        
    except Exception as e:
        return {"message": "Failed to delete item", "error": str(e), "status": False}


def check_barcode_in_database(db: Session, barcode: str):
    """
    Check if a barcode exists in the food_items database.
    
    Args:
        db: Database session
        barcode: Barcode to check
        
    Returns:
        dict: Food item data if found, None otherwise
    """
    try:
        f_id = int(barcode)
        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == f_id).first()
        
        if food_item:
            return {
                "code": str(food_item.f_id),
                "product_name_en": food_item.f_name,
                "brands": food_item.brands,
                "quantity": food_item.quantity,
                "energy_kcal_100g": food_item.energy,
                "category": food_item.category,
                "categorystatus": food_item.categorystatus,
                "imageurl": food_item.imageurl
            }
        return None
    except (ValueError, TypeError):
        return None


def add_food_item_to_database(db: Session, barcode: str, f_name: str, brands: str, 
                              quantity: str, energy: int, category: str):
    """
    Add a food item directly to the food_items table.
    
    Args:
        db: Database session
        barcode: Barcode (f_id)
        f_name: Food name
        brands: Brand name
        quantity: Quantity
        energy: Energy value (kcal per 100g)
        category: Category name
        
    Returns:
        dict: Success/failure message
    """
    try:
        f_id = int(barcode)
        
        # Check if item already exists
        existing_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == f_id).first()
        if existing_item:
            return {"message": "Food item already exists", "status": False}
        
        # Determine categorystatus based on category using find_categories
        category_data = find_categories([category], category, f_name)
        categorystatus = category_data.get("categorystatus", False) if category_data else False
        
        food_item = models.Food_Items(
            f_id=f_id,
            f_name=f_name,
            brands=brands,
            quantity=quantity,
            energy=energy or 0,
            category=category,
            categorystatus=categorystatus,
            imageurl=None  # Leave blank as requested
        )
        
        db.add(food_item)
        db.commit()
        db.refresh(food_item)
        
        return {"message": "Food item added successfully", "status": True}
        
    except Exception as e:
        return {"message": f"Failed to add food item: {str(e)}", "status": False}


def check_and_move_expired_items(db: Session, user_id: int = None):
    """
    Check for expired items and automatically move them to FoodStatusLog with 'expired' status.
    Items are considered expired when the expiry date is before today (not including today).
    If user_id is provided, only check that user's items. Otherwise, check all users.
    
    Args:
        db: Database session
        user_id: Optional user ID to check specific user's items
        
    Returns:
        dict: Message about moved items and count
    """
    try:
        today = datetime.now().date()  # Get today's date only (without time)
        today_start = datetime.combine(today, datetime.min.time())  # Today at 00:00:00
        
        # Query for expired items - only items that expired BEFORE today (not today)
        # This prevents items expiring today from being marked as expired
        query = db.query(models.Inventory).filter(
            models.Inventory.expiry_date < today_start
        )
        
        if user_id is not None:
            query = query.filter(models.Inventory.u_id == user_id)
        
        expired_items = query.all()
        
        moved_count = 0
        for item in expired_items:
            # Check if this item is already in FoodStatusLog
            existing_log = db.query(models.FoodStatusLog).filter(
                models.FoodStatusLog.inventory_id == item.id
            ).first()
            
            if not existing_log:
                # Move to FoodStatusLog with 'expired' status
                food_status_log = models.FoodStatusLog(
                    inventory_id=item.id,
                    status="expired",
                    notes="Automatically moved due to expiration",
                    timestamp=datetime.now()
                )
                db.add(food_status_log)
                moved_count += 1
        
        if moved_count > 0:
            db.commit()
            return {"message": f"Moved {moved_count} expired items to FoodStatusLog", "moved_count": moved_count}
        else:
            return {"message": "No expired items found", "moved_count": 0}
            
    except Exception as e:
        return {"message": "Failed to check expired items", "error": str(e)}
