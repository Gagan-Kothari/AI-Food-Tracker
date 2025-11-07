from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, BigInteger, Boolean  # type: ignore
from sqlalchemy.orm import relationship  # type: ignore
from app.database import Base

class Users(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    password = Column(String)
    phone_number=Column(String,unique=True,index=True)
    points = Column(Integer, default=0)  # Points earned from donations

    inventory_items = relationship("Inventory", back_populates="user")


class Food_Items(Base):
    __tablename__ = "food_items"

    f_id = Column(BigInteger, index=True, unique=True, primary_key=True)
    f_name = Column(String)
    brands = Column(String)
    quantity = Column(String)
    energy = Column(Integer)
    category = Column(String)
    categorystatus = Column(Boolean, default=False)
    imageurl = Column(String)

    inventory_items = relationship("Inventory", back_populates="food_item")


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(BigInteger, index=True, autoincrement=True, primary_key=True)
    f_id = Column(BigInteger, ForeignKey("food_items.f_id"))
    u_id = Column(Integer, ForeignKey("users.id"))
    expiry_date = Column(DateTime)

    food_item = relationship("Food_Items", back_populates="inventory_items")
    user = relationship("Users", back_populates="inventory_items")

class FoodStatusLog(Base):
    __tablename__ = "food_status_log"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inventory_id = Column(BigInteger, ForeignKey("inventory.id"))
    status = Column(String)  # 'consumed', 'donated', 'expired'
    timestamp = Column(DateTime)
    # quantity = Column(String)
    notes = Column(String)

    inventory = relationship("Inventory")


class RecipesTried(Base):
    __tablename__ = "recipes_tried"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    recipe_id = Column(Integer)  # Spoonacular recipe ID
    recipe_title = Column(String)
    timestamp = Column(DateTime)

    user = relationship("Users")
