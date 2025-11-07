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
from app.whatsapp_alerts import send_whatsapp_message
import re

load_dotenv()

# Synonym mapping for better recipe matching
# Maps specific terms to their broader categories
SYNONYMS = {
    "wheat flour": ["flour", "wheat", "all-purpose flour"],
    "flour": ["wheat flour", "all-purpose flour"],
    "rice": ["white rice", "brown rice", "basmati rice"],
    "oil": ["cooking oil", "vegetable oil", "sunflower oil", "olive oil"],
    "milk": ["whole milk", "skim milk", "dairy milk"],
    "cheese": ["cheddar cheese", "mozzarella", "gouda"],
    "bread": ["white bread", "whole wheat bread", "sliced bread"],
    "chicken": ["chicken breast", "chicken thigh", "whole chicken"],
    "tomato": ["tomatoes", "cherry tomato", "roma tomato"],
    "onion": ["onions", "yellow onion", "red onion"],
    "garlic": ["garlic cloves", "minced garlic"],
    "sugar": ["white sugar", "granulated sugar"],
    "salt": ["table salt", "sea salt"],
    "butter": ["unsalted butter", "salted butter"],
    "egg": ["eggs", "chicken egg"],
    "potato": ["potatoes", "russet potato", "red potato"],
    "carrot": ["carrots", "baby carrot"],
    "pepper": ["bell pepper", "black pepper", "red pepper"],
}

SPOONACULAR_API = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")


def get_recipes(ingredients, number=10):
    """
    Get recipe suggestions based on available ingredients using Spoonacular API.
    
    Args:
        ingredients: List of ingredient names
        number: Number of recipes to return (default: 10)
        
    Returns:
        dict: Recipe suggestions with success/error status
    """
    if not ingredients:
        return {"error": "No ingredients provided"}
    
    if not SPOONACULAR_API_KEY:
        return {"error": "Spoonacular API key not configured"}
    
    try:
        joined_ingredients = ",".join(ingredients)

        url = f"{SPOONACULAR_API}?ingredients={joined_ingredients}&number={number}&ranking=1&ignorePantry=true&apiKey={SPOONACULAR_API_KEY}"
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
        
        # Extract ingredient names for API call
        # Use category if categorystatus is true, otherwise use f_name
        # Add synonyms for better recipe matching
        # Filter out empty strings and None values
        ingredients = []
        ingredients_set = set()  # Use set to avoid duplicates
        
        for item in inventory_data:
            categorystatus = item.get("categorystatus", False)
            base_ingredient = None
            
            if categorystatus:
                # Use category if categorystatus is true
                category = item.get("category", "")
                if category and isinstance(category, str) and category.strip():
                    base_ingredient = category.strip().lower()
            else:
                # Use f_name if categorystatus is false
                f_name = item.get("f_name", "")
                if f_name and isinstance(f_name, str) and f_name.strip():
                    base_ingredient = f_name.strip().lower()
            
            if base_ingredient:
                # Add the base ingredient
                ingredients_set.add(base_ingredient)
                
                # Add synonyms if available
                for key, synonyms in SYNONYMS.items():
                    if key.lower() in base_ingredient or base_ingredient in key.lower():
                        for synonym in synonyms:
                            ingredients_set.add(synonym.lower())
        
        ingredients = list(ingredients_set)
        print(f"DEBUG: Extracted {len(ingredients)} valid ingredients (with synonyms): {ingredients[:10]}")
        
        if not ingredients:
            return {
                "success": False,
                "error": "No valid ingredients found in inventory (items may have empty names)",
                "recipes": [],
                "ingredients_used": []
            }
        
        # Identify yellow (7 days) and red (3 days) alert items
        today = datetime.now().date()
        yellow_threshold = today + timedelta(days=7)  # 7 days from now
        red_threshold = today + timedelta(days=3)    # 3 days from now
        
        expiry_alert_items = []
        for item in inventory_data:
            expiry_date_str = item.get("expiry_date")
            if expiry_date_str:
                try:
                    expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                    # Include items expiring in 7 days or less (yellow and red alerts)
                    if expiry_date <= yellow_threshold and expiry_date >= today:
                        expiry_alert_items.append(item)
                except (ValueError, TypeError):
                    continue
        
        # Extract ingredients for expiry alert items only
        expiry_ingredients_set = set()
        for item in expiry_alert_items:
            categorystatus = item.get("categorystatus", False)
            base_ingredient = None
            
            if categorystatus:
                category = item.get("category", "")
                if category and isinstance(category, str) and category.strip():
                    base_ingredient = category.strip().lower()
            else:
                f_name = item.get("f_name", "")
                if f_name and isinstance(f_name, str) and f_name.strip():
                    base_ingredient = f_name.strip().lower()
            
            if base_ingredient:
                expiry_ingredients_set.add(base_ingredient)
                # Add synonyms
                for key, synonyms in SYNONYMS.items():
                    if key.lower() in base_ingredient or base_ingredient in key.lower():
                        for synonym in synonyms:
                            expiry_ingredients_set.add(synonym.lower())
        
        expiry_ingredients = list(expiry_ingredients_set)
        print(f"DEBUG: Found {len(expiry_alert_items)} items with expiry alerts (yellow/red)")
        print(f"DEBUG: Extracted {len(expiry_ingredients)} ingredients from expiry alert items")
        
        # Make two separate API calls
        # 1. Get recipes for expiry alert items (5 recipes, shown first)
        expiry_recipes = []
        if expiry_ingredients:
            expiry_recipe_result = get_recipes(expiry_ingredients, number=5)
            if not expiry_recipe_result.get("error"):
                expiry_recipes = expiry_recipe_result.get("recipes", [])
                print(f"DEBUG: Got {len(expiry_recipes)} recipes for expiry alert items")
        
        # 2. Get recipes for entire inventory (5 recipes, shown after)
        all_recipe_result = get_recipes(ingredients, number=5)
        
        if all_recipe_result.get("error"):
            # If main call fails but expiry call succeeded, still return expiry recipes
            if expiry_recipes:
                recipes = expiry_recipes
            else:
                return all_recipe_result
        else:
            all_recipes = all_recipe_result.get("recipes", [])
            # Combine: expiry recipes first, then all recipes
            # Remove duplicates by recipe ID
            seen_recipe_ids = set()
            combined_recipes = []
            
            # Add expiry recipes first
            for recipe in expiry_recipes:
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in seen_recipe_ids:
                    seen_recipe_ids.add(recipe_id)
                    combined_recipes.append(recipe)
            
            # Add all recipes (excluding duplicates)
            for recipe in all_recipes:
                recipe_id = recipe.get("id")
                if recipe_id and recipe_id not in seen_recipe_ids:
                    seen_recipe_ids.add(recipe_id)
                    combined_recipes.append(recipe)
            
            recipes = combined_recipes
            print(f"DEBUG: Combined {len(expiry_recipes)} expiry recipes + {len(all_recipes)} all recipes = {len(recipes)} total")
        
        if not recipes:
            return {
                "success": False,
                "error": "No recipes found for these ingredients",
                "recipes": [],
                "ingredients_used": ingredients
            }
        
        # Create a mapping of inventory items by name/category (case-insensitive)
        # Map both f_name and category (if categorystatus is true) to the same items
        inventory_map = {}
        for item in inventory_data:
            categorystatus = item.get("categorystatus", False)
            
            # Map by category if categorystatus is true
            if categorystatus:
                category = (item.get("category") or "").lower()
                if category:
                    if category not in inventory_map:
                        inventory_map[category] = []
                    inventory_map[category].append(item)
            
            # Always also map by f_name for matching
            f_name = (item.get("f_name") or "").lower()
            if f_name:
                if f_name not in inventory_map:
                    inventory_map[f_name] = []
                inventory_map[f_name].append(item)
        
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
                ing_name = (used_ing.get("name") or "").lower().strip()
                used_ing_enhanced = used_ing.copy()
                
                # Find matching inventory item
                # Try multiple matching strategies to handle cases like:
                # - "raspberry jam" should match "jam" in inventory
                # - "strawberry jam" should match "jam" in inventory
                inventory_match = None
                inventory_items = []
                
                # 1. Try exact match
                if ing_name in inventory_map:
                    inventory_items = inventory_map[ing_name]
                else:
                    # 2. Try partial match - check if any inventory item name is contained in ingredient name
                    # This handles cases like:
                    # - "raspberry jam" matching "jam"
                    # - "wheat flour" matching "flour"
                    # - "sunflower oil" matching "oil"
                    # - "cheddar cheese" matching "cheese"
                    # - "whole milk" matching "milk"
                    for map_key, items in inventory_map.items():
                        # Check if inventory name is contained in ingredient name (e.g., "jam" in "raspberry jam")
                        # Use word boundaries to avoid false matches like "rice" in "price"
                        if len(map_key) > 2:  # Only match words longer than 2 characters
                            if map_key in ing_name:
                                # Make sure it's a whole word match or at word boundary
                                # Check if it's at the start, end, or has space/separator around it
                                if (ing_name.startswith(map_key + " ") or 
                                    ing_name.endswith(" " + map_key) or 
                                    " " + map_key + " " in ing_name or
                                    ing_name == map_key):
                                    inventory_items.extend(items)
                        # Also check if ingredient name is contained in inventory name (e.g., "flour" in "wheat flour")
                        if len(ing_name) > 2:
                            if ing_name in map_key:
                                if (map_key.startswith(ing_name + " ") or 
                                    map_key.endswith(" " + ing_name) or 
                                    " " + ing_name + " " in map_key or
                                    map_key == ing_name):
                                    inventory_items.extend(items)
                    
                    # 3. Try word-based matching (split by spaces and check individual words)
                    if not inventory_items:
                        ing_words = set(ing_name.split())
                        for map_key, items in inventory_map.items():
                            map_words = set(map_key.split())
                            # If any significant word matches (words longer than 3 chars to avoid "a", "an", "the")
                            common_words = [w for w in ing_words if len(w) > 3 and w in map_words]
                            if common_words:
                                inventory_items.extend(items)
                    
                    # 4. Try synonym match
                    if not inventory_items:
                        for key, synonyms in SYNONYMS.items():
                            # Check if ingredient matches the key or any synonym
                            if key.lower() in ing_name or ing_name in key.lower():
                                # Check if any synonym matches our inventory
                                for synonym in synonyms:
                                    if synonym.lower() in inventory_map:
                                        inventory_items.extend(inventory_map[synonym.lower()])
                                # Also check if the key itself is in inventory
                                if key.lower() in inventory_map:
                                    inventory_items.extend(inventory_map[key.lower()])
                            # Also check if any synonym is in the ingredient name
                            for synonym in synonyms:
                                if synonym.lower() in ing_name or ing_name in synonym.lower():
                                    if key.lower() in inventory_map:
                                        inventory_items.extend(inventory_map[key.lower()])
                                    if synonym.lower() in inventory_map:
                                        inventory_items.extend(inventory_map[synonym.lower()])
                
                if inventory_items:
                    # Remove duplicates while preserving order
                    seen = set()
                    unique_items = []
                    for item in inventory_items:
                        item_id = item.get("inventory_id")
                        if item_id not in seen:
                            seen.add(item_id)
                            unique_items.append(item)
                    
                    # Sort by expiry date (soonest first)
                    inventory_items_sorted = sorted(
                        unique_items,
                        key=lambda x: datetime.strptime(x.get("expiry_date") or "9999-12-31", "%Y-%m-%d").date()
                    )
                    inventory_match = inventory_items_sorted[0]
                
                if inventory_match:
                    expiry_date_str = inventory_match.get("expiry_date")
                    expiry_date_value = None
                    days_until_expiry = None
                    
                    if expiry_date_str:
                        try:
                            expiry_date_value = expiry_date_str  # Keep as string for frontend
                            expiry_date = datetime.strptime(expiry_date_str, "%Y-%m-%d").date()
                            days_until_expiry = (expiry_date - today).days
                        except (ValueError, TypeError) as e:
                            print(f"DEBUG: Error parsing expiry_date '{expiry_date_str}': {e}")
                            expiry_date_value = None
                            days_until_expiry = None
                    
                    used_ing_enhanced.update({
                        "inventory_id": inventory_match.get("inventory_id"),
                        "expiry_date": expiry_date_value,  # Always set, even if None
                        "quantity": inventory_match.get("quantity", ""),
                        "unit": inventory_match.get("quantity", ""),  # Add unit field
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
                        "expiry_date": None,  # Explicitly set to None
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
        
        # Filter out recipes with 0 ingredients (usedIngredientCount = 0)
        enhanced_recipes = [recipe for recipe in enhanced_recipes if recipe.get("usedIngredientCount", 0) > 0]
        
        # Separate recipes into two groups:
        # 1. Recipes using yellow/red alert items (expiring in 7 days or less) - shown first
        # 2. Recipes using general inventory items - shown after
        
        # Get inventory IDs of expiry alert items
        expiry_alert_inventory_ids = {item.get("inventory_id") for item in expiry_alert_items}
        
        expiry_alert_recipes = []
        general_recipes = []
        
        for recipe in enhanced_recipes:
            # Check if recipe uses any expiry alert items
            uses_expiry_items = False
            for used_ing in recipe.get("usedIngredients", []):
                if used_ing.get("inventory_id") in expiry_alert_inventory_ids:
                    uses_expiry_items = True
                    break
            
            if uses_expiry_items:
                expiry_alert_recipes.append(recipe)
            else:
                general_recipes.append(recipe)
        
        # Sort each group by priority score (maintaining same sorting order)
        expiry_alert_recipes.sort(
            key=lambda x: (
                x.get("priority_score", 0),
                x.get("usedIngredientCount", 0),
                x.get("items_expiring_soon", 0)
            ),
            reverse=True
        )
        
        general_recipes.sort(
            key=lambda x: (
                x.get("priority_score", 0),
                x.get("usedIngredientCount", 0),
                x.get("items_expiring_soon", 0)
            ),
            reverse=True
        )
        
        # Limit each group to 5 recipes
        expiry_alert_recipes = expiry_alert_recipes[:5]
        general_recipes = general_recipes[:5]
        
        # Combine: expiry alert recipes first, then general recipes
        enhanced_recipes = expiry_alert_recipes + general_recipes
        
        print(f"DEBUG: Final recipe count - {len(expiry_alert_recipes)} expiry alert recipes (shown first) + {len(general_recipes)} general recipes = {len(enhanced_recipes)} total")
        
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


def mark_recipe_as_cooked(db: Session, user_id: int, recipe_id: int, recipe_title: str, used_ingredients: list):
    """
    Mark a recipe as cooked and send WhatsApp notification with items saved from expiring.
    
    Args:
        db: Database session
        user_id: User ID
        recipe_id: Recipe ID from Spoonacular
        recipe_title: Recipe title
        used_ingredients: List of used ingredients with inventory information
        
    Returns:
        dict: Success/failure message
    """
    try:
        user = db.query(models.Users).filter(models.Users.id == user_id).first()
        if not user:
            return {"status": False, "message": "User not found"}
        
        # Find items that were saved from expiring (items with expiry dates)
        saved_items = []
        for ing in used_ingredients:
            if ing.get("inventory_id") and ing.get("expiry_date") and ing.get("days_until_expiry") is not None:
                days_until_expiry = ing.get("days_until_expiry")
                # Items expiring in 7 days or less are considered "saved"
                if days_until_expiry <= 7 and days_until_expiry >= 0:
                    item_name = ing.get("name", "Unknown")
                    saved_items.append({
                        "name": item_name,
                        "days_until_expiry": days_until_expiry
                    })
        
        # Mark used ingredients as consumed
        consumed_count = 0
        for ing in used_ingredients:
            inventory_id = ing.get("inventory_id")
            if inventory_id:
                # Check if already logged
                existing_log = db.query(models.FoodStatusLog).filter(
                    models.FoodStatusLog.inventory_id == inventory_id
                ).first()
                
                if not existing_log:
                    food_status_log = models.FoodStatusLog(
                        inventory_id=inventory_id,
                        status="consumed",
                        notes=f"Used in recipe: {recipe_title}",
                        timestamp=datetime.now()
                    )
                    db.add(food_status_log)
                    consumed_count += 1
        
        # Track recipe as tried (only once per recipe per user)
        existing_recipe = db.query(models.RecipesTried).filter(
            models.RecipesTried.user_id == user_id,
            models.RecipesTried.recipe_id == recipe_id
        ).first()
        
        recipe_added = False
        if not existing_recipe:
            recipe_tried = models.RecipesTried(
                user_id=user_id,
                recipe_id=recipe_id,
                recipe_title=recipe_title,
                timestamp=datetime.now()
            )
            db.add(recipe_tried)
            recipe_added = True
        
        if consumed_count > 0 or recipe_added:
            db.commit()
        
        # Send WhatsApp notification
        if user.phone_number:
            print(f"DEBUG: User found with phone number: {user.phone_number}")
            cooked_message = f"🍳 Wonderful! You've cooked '{recipe_title}'!\n\n"
            
            if saved_items:
                cooked_message += f"🌟 You saved {len(saved_items)} item{'s' if len(saved_items) > 1 else ''} from expiring:\n"
                for item in saved_items[:5]:  # Limit to first 5 items
                    days = item["days_until_expiry"]
                    if days == 0:
                        cooked_message += f"• {item['name']} (expiring today!)\n"
                    elif days == 1:
                        cooked_message += f"• {item['name']} (expiring tomorrow)\n"
                    else:
                        cooked_message += f"• {item['name']} ({days} days left)\n"
                if len(saved_items) > 5:
                    cooked_message += f"• ... and {len(saved_items) - 5} more\n"
                cooked_message += "\n"
            
            cooked_message += f"Your smart cooking helps reduce food waste and keeps your kitchen fresh! 🎉\n\n"
            cooked_message += f"Keep up the great work! Every meal counts in the fight against food waste. 💚"
            
            result = send_whatsapp_message(user.phone_number, cooked_message, template_name="recipe_cooked")
            print(f"DEBUG: Recipe cooked notification result: {result}")
        else:
            print(f"DEBUG: User has no phone number. User ID: {user_id}, Phone: {user.phone_number if user else 'No user'}")
        
        return {
            "status": True,
            "message": f"Recipe '{recipe_title}' marked as cooked",
            "consumed_count": consumed_count,
            "saved_items_count": len(saved_items)
        }
        
    except Exception as e:
        return {
            "status": False,
            "message": f"Failed to mark recipe as cooked: {str(e)}"
        }
