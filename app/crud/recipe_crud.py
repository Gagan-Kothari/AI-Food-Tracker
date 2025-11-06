"""
Recipe suggestions using Spoonacular API based on user inventory
"""
import requests
from dotenv import load_dotenv
import os
from sqlalchemy.orm import Session
from app.models import models
from datetime import datetime, timedelta
from app.crud.inventory_crud import user_inventory

load_dotenv()

SPOONACULAR_API = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")


def get_recipes(ingredients):
    """
    Get recipe suggestions based on available ingredients using Spoonacular API.
    
    Args:
        ingredients: List of ingredient names
        
    Returns:
        dict: Recipe suggestions with success/error status
    """
    if not ingredients:
        return {"error": "No ingredients provided"}
    
    if not SPOONACULAR_API_KEY:
        return {"error": "Spoonacular API key not configured"}
    
    try:
        joined_ingredients = ",".join(ingredients)

        url = f"{SPOONACULAR_API}?ingredients={joined_ingredients}&number=10&ranking=1&ignorePantry=true&apiKey={SPOONACULAR_API_KEY}"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "ingredients_used": ingredients,
                "recipes": data,
                "total_recipes": len(data) if isinstance(data, list) else 0
            }
        else:
            return {
                "error": f"API request failed with status {response.status_code}",
                "details": response.text
            }
            
    except requests.exceptions.RequestException as e:
        return {"error": f"Network error: {str(e)}"}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}"}


def get_inventory_based_recipes(user_id: int, db: Session):
    """
    Get recipe suggestions based on user's inventory with proper prioritization.
    
    Prioritization order:
    1. Most ingredients in inventory + Expiry date close of items
    2. Expiry date close items
    3. Most ingredients
    
    Args:
        user_id: User ID to fetch inventory for
        db: Database session
        
    Returns:
        dict: Recipe suggestions with success/error status
    """
    try:
        # Get user's inventory using existing function
        inventory_data = user_inventory(user_id, db, models.FoodStatusLog, models.Inventory)
        
        # Check if inventory_data is an error dict instead of a list
        if isinstance(inventory_data, dict) and "error" in inventory_data:
            return {
                "success": False,
                "error": f"Error fetching inventory: {inventory_data.get('error', 'Unknown error')}",
                "recipes": [],
                "ingredients_used": []
            }
        
        # Ensure inventory_data is a list
        if not isinstance(inventory_data, list):
            return {
                "success": False,
                "error": "Invalid inventory data format",
                "recipes": [],
                "ingredients_used": []
            }
        
        if not inventory_data or len(inventory_data) == 0:
            return {
                "success": False,
                "error": "No ingredients found in inventory",
                "recipes": [],
                "ingredients_used": []
            }
        
        # Debug: Log inventory data
        print(f"DEBUG: Found {len(inventory_data)} items in inventory")
        print(f"DEBUG: Sample item: {inventory_data[0] if inventory_data else 'None'}")
        
        # Extract ingredient names for API call (use f_name from inventory)
        # Filter out empty strings and None values
        ingredients = []
        for item in inventory_data:
            f_name = item.get("f_name", "")
            if f_name and isinstance(f_name, str) and f_name.strip():
                ingredients.append(f_name.strip())
        
        print(f"DEBUG: Extracted {len(ingredients)} valid ingredients: {ingredients[:5]}")
        
        if not ingredients:
            return {
                "success": False,
                "error": "No valid ingredients found in inventory (items may have empty names)",
                "recipes": [],
                "ingredients_used": []
            }
        
        # Get recipes from Spoonacular API
        recipe_result = get_recipes(ingredients)
        
        if recipe_result.get("error"):
            return recipe_result
        
        recipes = recipe_result.get("recipes", [])
        if not recipes:
            return {
                "success": False,
                "error": "No recipes found for these ingredients",
                "recipes": [],
                "ingredients_used": ingredients
            }
        
        # Create a mapping of inventory items by name (case-insensitive)
        inventory_map = {}
        for item in inventory_data:
            item_name = (item.get("f_name") or "").lower()
            if item_name:
                if item_name not in inventory_map:
                    inventory_map[item_name] = []
                inventory_map[item_name].append(item)
        
        # Enhance recipes with inventory information and calculate priority
        enhanced_recipes = []
        today = datetime.now().date()
        
        for recipe in recipes:
            enhanced_recipe = recipe.copy()
            
            # Process used ingredients (available in inventory)
            used_ingredients_with_inventory = []
            total_days_until_expiry = 0
            items_expiring_soon = 0  # Items expiring in 7 days or less
            
            for used_ing in recipe.get("usedIngredients", []):
                ing_name = (used_ing.get("name") or "").lower()
                used_ing_enhanced = used_ing.copy()
                
                # Find matching inventory item
                inventory_match = None
                if ing_name in inventory_map:
                    # Use the first match, or find the one expiring soonest
                    inventory_items = inventory_map[ing_name]
                    # Sort by expiry date (soonest first)
                    inventory_items_sorted = sorted(
                        inventory_items,
                        key=lambda x: datetime.strptime(x.get("expiry_date") or "9999-12-31", "%Y-%m-%d").date()
                    )
                    inventory_match = inventory_items_sorted[0]
                
                if inventory_match:
                    expiry_date_str = inventory_match.get("expiry_date") or ""
                    if expiry_date_str:
                        expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                        days_until_expiry = (expiry_date - today).days
                    else:
                        days_until_expiry = None
                    
                    used_ing_enhanced.update({
                        "inventory_id": inventory_match.get("inventory_id"),
                        "expiry_date": inventory_match.get("expiry_date"),
                        "quantity": inventory_match.get("quantity", ""),
                        "category": inventory_match.get("category", ""),
                        "days_until_expiry": days_until_expiry,
                        "available": True
                    })
                    
                    # Track expiry information for prioritization
                    if days_until_expiry is not None:
                        if days_until_expiry <= 7:
                            items_expiring_soon += 1
                        if days_until_expiry >= 0:  # Not expired
                            total_days_until_expiry += days_until_expiry
                else:
                    used_ing_enhanced.update({
                        "available": True,  # Still available, just not in our inventory tracking
                        "days_until_expiry": None
                    })
                
                used_ingredients_with_inventory.append(used_ing_enhanced)
            
            # Process missed ingredients (not in inventory)
            missed_ingredients_enhanced = []
            for missed_ing in recipe.get("missedIngredients", []):
                missed_ing_enhanced = missed_ing.copy()
                missed_ing_enhanced.update({
                    "available": False
                })
                missed_ingredients_enhanced.append(missed_ing_enhanced)
            
            enhanced_recipe["usedIngredients"] = used_ingredients_with_inventory
            enhanced_recipe["missedIngredients"] = missed_ingredients_enhanced
            
            # Calculate priority score
            # Priority 1: Most ingredients in inventory + Expiry date close
            # Priority 2: Expiry date close items
            # Priority 3: Most ingredients
            
            used_count = len(used_ingredients_with_inventory)
            missed_count = len(missed_ingredients_enhanced)
            total_ingredients = used_count + missed_count
            
            # Score components:
            # 1. Ratio of used ingredients (higher is better)
            ingredient_ratio_score = (used_count / total_ingredients * 100) if total_ingredients > 0 else 0
            
            # 2. Items expiring soon (more items expiring soon = higher priority)
            expiring_soon_score = items_expiring_soon * 50  # 50 points per item expiring soon
            
            # 3. Average days until expiry (lower = higher priority, but only for items not expired)
            # Invert so lower days = higher score
            if used_count > 0 and total_days_until_expiry >= 0:
                avg_days = total_days_until_expiry / used_count
                # Items expiring in 0-3 days get highest score, 4-7 get medium, etc.
                if avg_days <= 3:
                    expiry_score = 100
                elif avg_days <= 7:
                    expiry_score = 70
                elif avg_days <= 14:
                    expiry_score = 40
                else:
                    expiry_score = 10
            else:
                expiry_score = 0
            
            # Combined priority score
            # Weight: ingredient ratio (40%), expiring soon count (40%), expiry proximity (20%)
            priority_score = (
                ingredient_ratio_score * 0.4 +
                expiring_soon_score * 0.4 +
                expiry_score * 0.2
            )
            
            enhanced_recipe["priority_score"] = round(priority_score, 2)
            enhanced_recipe["usedIngredientCount"] = used_count
            enhanced_recipe["missedIngredientCount"] = missed_count
            enhanced_recipe["items_expiring_soon"] = items_expiring_soon
            enhanced_recipe["avg_days_until_expiry"] = round(total_days_until_expiry / used_count, 1) if used_count > 0 else None
            
            enhanced_recipes.append(enhanced_recipe)
        
        # Sort recipes by priority score (highest first)
        # Secondary sort: by used ingredient count (more is better)
        # Tertiary sort: by items expiring soon (more is better)
        enhanced_recipes.sort(
            key=lambda x: (
                x.get("priority_score", 0),
                x.get("usedIngredientCount", 0),
                x.get("items_expiring_soon", 0)
            ),
            reverse=True
        )
        
        # Limit to top 10 recipes
        enhanced_recipes = enhanced_recipes[:10]
        
        return {
            "success": True,
            "ingredients_used": ingredients,
            "recipes": enhanced_recipes,
            "total_recipes": len(enhanced_recipes),
            "inventory_summary": {
                "total_items": len(inventory_data),
                "expiring_soon": len([item for item in inventory_data 
                                     if datetime.strptime(item.get("expiry_date") or "9999-12-31", "%Y-%m-%d").date() <= today + timedelta(days=7)])
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching inventory-based recipes: {str(e)}",
            "recipes": []
        }
