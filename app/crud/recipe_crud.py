import requests
from dotenv import load_dotenv
import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime, timedelta

load_dotenv()

SPOONACULAR_API = "https://api.spoonacular.com/recipes/findByIngredients"
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./food_tracker.db")
engine = create_engine(DATABASE_URL)


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

        params = {
            "ingredients": joined_ingredients,
            "number": 10,  # Increased to 10 recipes
            "ranking": 1,
            "ignorePantry": True,
            "apikey": SPOONACULAR_API_KEY
        }
        
        url = f"{SPOONACULAR_API}?ingredients={joined_ingredients}&number={params.get('number')}&apiKey={SPOONACULAR_API_KEY}"
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


def get_inventory_based_recipes(user_id: int):
    """
    Get recipe suggestions based on user's inventory with prioritization by expiry date and category.
    
    Args:
        user_id: User ID to fetch inventory for
        
    Returns:
        dict: Recipe suggestions with success/error status
    """
    try:
        # Get user's inventory with expiry dates and categories
        conn = engine.connect()
        inventory_query = f"""
        SELECT 
            i.id as inventory_id,
            fi.f_name as name,
            fi.category,
            i.expiry_date,
            fi.quantity
        FROM inventory i
        JOIN food_items fi ON i.f_id = fi.f_id
        WHERE i.u_id = {user_id} 
        AND i.expiry_date > NOW()
        ORDER BY 
            i.expiry_date ASC,  -- Prioritize by expiry date (soonest first)
            fi.category ASC,    -- Then by category
            fi.f_name ASC       -- Finally by name
        """
        
        inventory_df = pd.read_sql(inventory_query, conn)
        conn.close()
        
        if inventory_df.empty:
            return {
                "success": False,
                "error": "No ingredients found in inventory",
                "recipes": [],
                "ingredients_used": []
            }
        
        # Extract ingredient names for API call
        ingredients = inventory_df['name'].tolist()
        
        # Get recipes from Spoonacular API
        recipe_result = get_recipes(ingredients)
        
        if recipe_result.get("error"):
            return recipe_result
        
        # Enhance recipes with inventory information
        enhanced_recipes = []
        for recipe in recipe_result.get("recipes", []):
            enhanced_recipe = recipe.copy()
            
            # Add inventory context for used ingredients
            used_ingredients_with_inventory = []
            for used_ing in recipe.get("usedIngredients", []):
                # Find matching inventory item
                inventory_match = inventory_df[
                    inventory_df['name'].str.lower() == used_ing.get('name', '').lower()
                ]
                
                if not inventory_match.empty:
                    inv_item = inventory_match.iloc[0]
                    used_ing_with_inventory = used_ing.copy()
                    used_ing_with_inventory.update({
                        'inventory_id': int(inv_item['inventory_id']),
                        'expiry_date': inv_item['expiry_date'].strftime('%Y-%m-%d') if pd.notna(inv_item['expiry_date']) else None,
                        'quantity': inv_item['quantity'] if pd.notna(inv_item['quantity']) else '1',
                        'unit': 'item',  # Default unit since it's not in the schema
                        'category': inv_item['category'],
                        'days_until_expiry': (inv_item['expiry_date'] - datetime.now()).days if pd.notna(inv_item['expiry_date']) else None
                    })
                    used_ingredients_with_inventory.append(used_ing_with_inventory)
                else:
                    used_ingredients_with_inventory.append(used_ing)
            
            enhanced_recipe['usedIngredients'] = used_ingredients_with_inventory
            
            # Calculate priority score based on expiry dates
            priority_score = 0
            for used_ing in used_ingredients_with_inventory:
                if 'days_until_expiry' in used_ing and used_ing['days_until_expiry'] is not None:
                    if used_ing['days_until_expiry'] <= 3:
                        priority_score += 10  # High priority for items expiring soon
                    elif used_ing['days_until_expiry'] <= 7:
                        priority_score += 5   # Medium priority
                    else:
                        priority_score += 1  # Low priority
            
            enhanced_recipe['priority_score'] = priority_score
            enhanced_recipes.append(enhanced_recipe)
        
        # Sort recipes by priority score (highest first)
        enhanced_recipes.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        return {
            "success": True,
            "ingredients_used": ingredients,
            "recipes": enhanced_recipes,
            "total_recipes": len(enhanced_recipes),
            "inventory_summary": {
                "total_items": len(inventory_df),
                "expiring_soon": len(inventory_df[inventory_df['expiry_date'] <= datetime.now() + timedelta(days=3)]),
                "categories": inventory_df['category'].unique().tolist()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": f"Error fetching inventory-based recipes: {str(e)}",
            "recipes": []
        }
