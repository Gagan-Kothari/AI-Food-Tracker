from app.schemas.schemas import *
from app.crud import *
from app.crud.recipe_crud import get_inventory_based_recipes
from app.ml_models import get_grocery_suggestions, train_all_user_models, retrain_user_model
from fastapi import APIRouter, Depends, Query, Header, HTTPException, status # type: ignore
from datetime import date, datetime
from app.database import get_db
from sqlalchemy.orm import Session # type: ignore
from app.models import models

router = APIRouter()

ADMIN_EMAIL = "adminghh@gmail.com"

def verify_admin_by_userid(userid: int, db: Session):
    """Verify if a user is admin by checking their email"""
    user = db.query(models.Users).filter(models.Users.id == userid).first()
    if not user or user.email.lower() != ADMIN_EMAIL.lower():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return True

@router.post("/item/scan")
async def scan_item(senddata : UserData, db: Session = Depends(get_db)):
    """
    Scan item with new flow:
    1. Check database first
    2. If not found, check OpenFoodFacts API
    3. If not found there, return response asking if user wants to add manually
    """
    barcode_data = senddata.barcode

    if not barcode_data:
        return {"message": "No barcode detected.", "status": False, "requires_manual": False}

    # Step 1: Check database first
    item_data = check_barcode_in_database(db, barcode_data)
    
    if item_data:
        # Found in database, add to inventory
        try:
            exp_dt = datetime.strptime(senddata.expiry_date, '%Y-%m-%d').date()
            expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
            status = add_to_database(db, item_data, expiry_datetime, int(senddata.userid))
            return {**status, "source": "database"}
        except Exception as e:
            return {"message": str(e), "status": False, "requires_manual": False}
    
    # Step 2: Check OpenFoodFacts API
    item_data = fetch_items_offAPI(barcode_data)
    
    if item_data and item_data.get("Message") != "failed: fetch_items_offAPI":
        # Found in API, add to database and inventory
        try:
            exp_dt = datetime.strptime(senddata.expiry_date, '%Y-%m-%d').date()
            expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
            status = add_to_database(db, item_data, expiry_datetime, int(senddata.userid))
            return {**status, "source": "api"}
        except Exception as e:
            return {"message": str(e), "status": False, "requires_manual": False}
    
    # Step 3: Not found in database or API, ask user if they want to add manually
    return {
        "message": "Item not found in database or OpenFoodFacts API",
        "status": False,
        "requires_manual": True,
        "barcode": barcode_data
    }

# @router.post("/item/scan")
# async def scan_item(senddata : UserData, db: Session = Depends(get_db)):
#     item_data = fetch_items_offAPI(senddata.barcode)
#     status = add_to_database(db, item_data, senddata.expiry_date, int(senddata.userid))
#     return status

@router.post("/user/add")
async def add_new_user(signupinfo : SignupInfo, db : Session = Depends(get_db)):
    name = signupinfo.name
    email = signupinfo.email
    password = signupinfo.password
    
    status = add_user_to_database(db, name, email, password)

    return status


@router.post("/user/verify")
async def verify_user(logininfo : LoginInfo, db : Session = Depends(get_db)):
    email = logininfo.email
    password = logininfo.password

    return verify_user_from_db(email, password, db)

@router.post("/admin/verifyitem")
async def verify_item(item:AdminVerifyItem):
    return fetch_items_offAPI(item.barcode)

# @router.post("/user/inventory")
# async def show_inventory(userid, db : Session = Depends(get_db)):
#     return user_inventory(userid, db)


@router.post("/user/inventory")
async def show_inventory(request: UserIdRequest, db: Session = Depends(get_db)):
    return user_inventory(request.userid, db,models.FoodStatusLog,models.Inventory)

# @router.get("/user/recipe/input")
# async def recipes(ingredients: list[str] = Query(...)):
#     return get_recipes(ingredients)

@router.post("/user/recipe/suggestions")
async def get_recipe_suggestions(ingredients: Ingredients):
    return get_recipes(ingredients.ingredients)

@router.post("/user/recipe/inventory-based")
async def get_inventory_based_recipe_suggestions(request: UserIdRequest, db: Session = Depends(get_db)):
    return get_inventory_based_recipes(request.userid, db)
 

@router.post("/user/expiry_alerts")
async def expiry_alerts(userid: int, db: Session = Depends(get_db)):
    """Get expiry alerts for a user (for display purposes)"""
    items = get_expiring_items(db, userid)
    if not items:
        return {"message": "No items expiring soon."}
    
    return [
        {
            "name": item.f_name,
            "expiry": item.expiry_date.strftime("%Y-%m-%d"),
            "quantity": item.quantity,
            "brand": item.brands
        } 
        for item in items
    ]


@router.post("/admin/send-expiry-alerts")
async def send_expiry_alerts_route(request: UserIdRequest, db: Session = Depends(get_db)):
    """Send WhatsApp expiry alerts to users (admin endpoint)"""
    from app.whatsapp_alerts import send_expiry_alerts
    verify_admin_by_userid(request.userid, db)
    result = send_expiry_alerts(db, None)  # Send to all users
    return result


@router.post("/user/send-expiry-alerts")
async def send_user_expiry_alerts_route(request: UserIdRequest, db: Session = Depends(get_db)):
    """Send WhatsApp expiry alerts to a specific user"""
    from app.whatsapp_alerts import send_expiry_alerts
    result = send_expiry_alerts(db, request.userid)
    return result

# @router.post("/admin/verifyitem")
# async def verify_item(barcode:str):
#     return fetch_items_offAPI(barcode)

@router.post("/user/foodstatus")
async def food_status(foodstatus:FoodStatus,db:Session = Depends(get_db)):
    return update_food_status(db,foodstatus)

@router.delete("/user/inventory/{inventory_id}")
async def delete_inventory_item_route(inventory_id: int, userid: int, db: Session = Depends(get_db)):
    return delete_inventory_item(db, inventory_id, userid)

@router.post("/user/check-expired")
async def check_expired_items_route(userid: int = None, db: Session = Depends(get_db)):
    return check_and_move_expired_items(db, userid)

@router.post("/user/donate")
async def donate_items_route(request: dict, db: Session = Depends(get_db)):
    inventory_ids = request.get("inventory_ids", [])
    userid = request.get("userid")
    
    if not inventory_ids or not userid:
        return {"message": "Missing inventory_ids or userid", "status": False}
    
    return donate_items(db, inventory_ids, int(userid))

@router.get("/user/points/{user_id}")
async def get_user_points_route(user_id: int, db: Session = Depends(get_db)):
    return get_user_points(db, user_id)

@router.post("/user/grocery-suggestions")
async def get_grocery_suggestions_route(request: UserIdRequest):
    """Get AI-powered grocery suggestions for a user based on consumption patterns"""
    suggestions = get_grocery_suggestions(request.userid)
    return {"suggestions": suggestions, "count": len(suggestions)}

@router.post("/admin/train-models")
async def train_models_route(request: UserIdRequest, db: Session = Depends(get_db)):
    """Train ML models for all users (admin endpoint)"""
    verify_admin_by_userid(request.userid, db)
    training_status = train_all_user_models()
    return {"training_status": training_status}

@router.post("/user/retrain-model")
async def retrain_user_model_route(request: UserIdRequest):
    """Retrain ML model for a specific user"""
    result = retrain_user_model(request.userid)
    return result


@router.post("/admin/users")
async def admin_list_users(request: UserIdRequest, db: Session = Depends(get_db)):
    """List all users (admin endpoint)"""
    verify_admin_by_userid(request.userid, db)
    users = db.query(models.Users).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "points": u.points}
        for u in users
    ]


@router.post("/admin/inventory/add")
async def admin_add_inventory(payload: AdminAddInventoryRequest, db: Session = Depends(get_db)):
    """Add item to user inventory (admin endpoint)"""
    verify_admin_by_userid(payload.admin_userid, db)
    item_data = fetch_items_offAPI(payload.barcode)
    try:
        exp_dt = datetime.strptime(payload.expiry_date, '%Y-%m-%d').date()
        expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
        status_resp = add_to_database(db, item_data, expiry_datetime, int(payload.userid))
        return status_resp
    except Exception as e:
        return {"message": str(e), "status": False}


@router.post("/admin/user/retrain")
async def admin_retrain_user_model(request: AdminRetrainRequest, db: Session = Depends(get_db)):
    """Retrain a user's model (admin endpoint)"""
    verify_admin_by_userid(request.admin_userid, db)
    result = retrain_user_model(request.target_userid)
    return result


@router.post("/admin/food-item/add")
async def admin_add_food_item(payload: AdminAddFoodItemRequest, db: Session = Depends(get_db)):
    """Add food item directly to food_items table (admin endpoint)"""
    verify_admin_by_userid(payload.admin_userid, db)
    result = add_food_item_to_database(
        db, 
        payload.barcode, 
        payload.f_name, 
        payload.brands, 
        payload.quantity, 
        payload.energy or 0, 
        payload.category
    )
    return result


@router.post("/item/manual-add")
async def manual_add_item(payload: ManualFoodItemRequest, db: Session = Depends(get_db)):
    """Manually add food item when barcode not found in database or API"""
    # First add to food_items table
    result = add_food_item_to_database(
        db,
        payload.barcode,
        payload.f_name,
        payload.brands,
        payload.quantity,
        payload.energy or 0,
        payload.category
    )
    
    if not result.get("status"):
        return result
    
    # Then add to user's inventory
    try:
        exp_dt = datetime.strptime(payload.expiry_date, '%Y-%m-%d').date()
        expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
        
        # Get the food item we just created
        f_id = int(payload.barcode)
        food_item = db.query(models.Food_Items).filter(models.Food_Items.f_id == f_id).first()
        
        if not food_item:
            return {"message": "Failed to create food item", "status": False}
        
        # Create inventory item
        inventory_item = models.Inventory(
            f_id=food_item.f_id,
            u_id=int(payload.userid),
            expiry_date=expiry_datetime
        )
        db.add(inventory_item)
        db.commit()
        
        return {"message": "Item added successfully", "status": True, "source": "manual"}
    except Exception as e:
        return {"message": f"Failed to add to inventory: {str(e)}", "status": False}


@router.get("/categories")
async def get_categories():
    """Get list of available food categories"""
    from app.crud.barcode_crud import FOOD_CATEGORIES
    # Return unique categories, sorted
    unique_categories = sorted(list(set(FOOD_CATEGORIES)))
    return {"categories": unique_categories}

