from pydantic import BaseModel # type: ignore
from datetime import date

class UserCreate(BaseModel):
    name : str
    email : str
    password : str

class UserOut(BaseModel):
    id : int
    name : str
    email : str

class FoodItemInput(BaseModel):
    barcode : str

class LoginInfo(BaseModel):
    email : str
    password : str

class SignupInfo(BaseModel):
    name : str
    email : str
    password : str

class UserData(BaseModel):
    barcode : str
    expiry_date : str
    userid : str

class Ingredients(BaseModel):
    ingredients : list[str]

class UserIdRequest(BaseModel):
    userid: int

class FoodStatus(BaseModel):
    inventory_id : int
    status : str
    notes : str

class AdminVerifyItem(BaseModel):
    barcode : str

class GrocerySuggestion(BaseModel):
    id: int
    name: str
    category: str
    suggested: bool
    quantity: int
    unit: str
    priority: str
    reason: str
    confidence: float

class ModelTrainingResponse(BaseModel):
    success: bool
    message: str


class AdminLogin(BaseModel):
    username: str
    password: str


class AdminAddInventoryRequest(BaseModel):
    admin_userid: int  # Admin's user ID for verification
    userid: int  # Target user's ID to add item to
    barcode: str
    expiry_date: str

class AdminRetrainRequest(BaseModel):
    admin_userid: int  # Admin's user ID for verification
    target_userid: int  # Target user's ID to retrain model for

class ManualFoodItemRequest(BaseModel):
    barcode: str
    f_name: str
    brands: str
    quantity: str
    energy: int | None = None  # Optional
    category: str
    expiry_date: str
    userid: str

class AdminAddFoodItemRequest(BaseModel):
    admin_userid: int  # Admin's user ID for verification
    barcode: str
    f_name: str
    brands: str
    quantity: str
    energy: int | None = None  # Optional
    category: str