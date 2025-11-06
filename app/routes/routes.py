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

ADMIN_USERNAME = "admin_ghh"
ADMIN_PASSWORD = "ghh123"
ADMIN_TOKEN = "admin-token-ghh"

def verify_admin(x_admin_token: str | None = Header(default=None)):
    if x_admin_token != ADMIN_TOKEN:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin token missing or invalid")

@router.post("/admin/login")
async def admin_login(creds: AdminLogin):
    if creds.username == ADMIN_USERNAME and creds.password == ADMIN_PASSWORD:
        return {"token": ADMIN_TOKEN, "role": "admin"}
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid admin credentials")

@router.post("/item/scan")
async def scan_item(senddata : UserData, db: Session = Depends(get_db)):
    # barcode_data = scan_barcode_live()
    barcode_data = senddata.barcode

    if barcode_data:
        barcode = barcode_data
        item_data = fetch_items_offAPI(barcode)

        try:
            exp_dt = datetime.strptime(senddata.expiry_date, '%Y-%m-%d').date()
            expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
            status = add_to_database(db, item_data, expiry_datetime, int(senddata.userid))
            return status
        
        except Exception as e:
            return {"message" : e}
        
    else:
        return {"message": "No barcode detected."}

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
async def get_inventory_based_recipe_suggestions(request: UserIdRequest):
    return get_inventory_based_recipes(request.userid)
 

@router.post("/user/expiry_alerts")
async def expiry_alerts(userid: int, db: Session = Depends(get_db)):
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
async def train_models_route(x_admin_token: str | None = Header(default=None)):
    """Train ML models for all users (admin endpoint)"""
    verify_admin(x_admin_token)
    training_status = train_all_user_models()
    return {"training_status": training_status}

@router.post("/user/retrain-model")
async def retrain_user_model_route(request: UserIdRequest):
    """Retrain ML model for a specific user"""
    result = retrain_user_model(request.userid)
    return result


@router.get("/admin/users")
async def admin_list_users(db: Session = Depends(get_db), x_admin_token: str | None = Header(default=None)):
    verify_admin(x_admin_token)
    users = db.query(models.Users).all()
    return [
        {"id": u.id, "name": u.name, "email": u.email, "points": u.points}
        for u in users
    ]


@router.post("/admin/inventory/add")
async def admin_add_inventory(payload: AdminAddInventoryRequest, db: Session = Depends(get_db), x_admin_token: str | None = Header(default=None)):
    verify_admin(x_admin_token)
    item_data = fetch_items_offAPI(payload.barcode)
    try:
        exp_dt = datetime.strptime(payload.expiry_date, '%Y-%m-%d').date()
        expiry_datetime = datetime.combine(exp_dt, datetime.min.time())
        status_resp = add_to_database(db, item_data, expiry_datetime, int(payload.userid))
        return status_resp
    except Exception as e:
        return {"message": str(e), "status": False}


@router.post("/admin/user/retrain")
async def admin_retrain_user_model(request: UserIdRequest, x_admin_token: str | None = Header(default=None)):
    verify_admin(x_admin_token)
    result = retrain_user_model(request.userid)
    return result

