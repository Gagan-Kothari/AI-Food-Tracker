"""
Indian Recipe Matching using ML model (TF-IDF + Cosine Similarity)
Loads recipes from Kaggle Indian Food Dataset and matches based on ingredients
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Path to Indian recipes dataset (CSV file)
INDIAN_RECIPES_CSV = os.getenv("INDIAN_RECIPES_CSV", "indian_food.csv")
INDIAN_RECIPES_DATA = None
INDIAN_RECIPES_VECTORIZER = None
INDIAN_RECIPES_TFIDF = None


def load_indian_recipes():
    """
    Load Indian recipes dataset from CSV file.
    Expected CSV columns: name, ingredients, instructions, prep_time, cook_time, etc.
    """
    global INDIAN_RECIPES_DATA, INDIAN_RECIPES_VECTORIZER, INDIAN_RECIPES_TFIDF
    
    if INDIAN_RECIPES_DATA is not None:
        return INDIAN_RECIPES_DATA
    
    try:
        # Try to load from app directory first
        csv_paths = [
            os.path.join(os.path.dirname(__file__), "..", "..", INDIAN_RECIPES_CSV),
            os.path.join(os.path.dirname(__file__), "..", INDIAN_RECIPES_CSV),
            INDIAN_RECIPES_CSV,
        ]
        
        df = None
        for path in csv_paths:
            if os.path.exists(path):
                print(f"DEBUG: Loading Indian recipes from {path}")
                df = pd.read_csv(path)
                break
        
        if df is None:
            print(f"WARNING: Indian recipes CSV not found. Creating sample dataset.")
            # Create a sample dataset if CSV is not found
            df = create_sample_indian_recipes()
        
        # Normalize column names (handle different possible column names)
        df.columns = df.columns.str.lower().str.strip()
        
        # Ensure required columns exist
        required_cols = ['name', 'ingredients']
        for col in required_cols:
            if col not in df.columns:
                # Try alternative column names
                if col == 'name':
                    alternatives = ['recipe', 'dish', 'dish_name', 'recipe_name', 'title']
                elif col == 'ingredients':
                    alternatives = ['ingredient', 'ingredient_list', 'ingredients_list']
                
                for alt in alternatives:
                    if alt in df.columns:
                        df[col] = df[alt]
                        break
                else:
                    # If still not found, create a placeholder
                    df[col] = ""
        
        # Clean and preprocess ingredients
        df['ingredients_clean'] = df['ingredients'].apply(clean_ingredients)
        
        # Create TF-IDF vectorizer for ingredient matching
        global INDIAN_RECIPES_VECTORIZER, INDIAN_RECIPES_TFIDF
        INDIAN_RECIPES_VECTORIZER = TfidfVectorizer(
            lowercase=True,
            token_pattern=r'\b\w+\b',
            max_features=5000,
            ngram_range=(1, 2)  # Include unigrams and bigrams
        )
        
        # Fit vectorizer on all recipe ingredients
        ingredient_texts = df['ingredients_clean'].fillna('').tolist()
        INDIAN_RECIPES_TFIDF = INDIAN_RECIPES_VECTORIZER.fit_transform(ingredient_texts)
        
        INDIAN_RECIPES_DATA = df
        print(f"DEBUG: Loaded {len(df)} Indian recipes")
        print(f"DEBUG: Vectorizer initialized: {INDIAN_RECIPES_VECTORIZER is not None}")
        print(f"DEBUG: TF-IDF matrix shape: {INDIAN_RECIPES_TFIDF.shape if INDIAN_RECIPES_TFIDF is not None else 'None'}")
        
        return df
        
    except Exception as e:
        print(f"ERROR: Failed to load Indian recipes: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return sample dataset on error and try to initialize it
        try:
            df = create_sample_indian_recipes()
            # Initialize vectorizer for sample data
            global INDIAN_RECIPES_VECTORIZER, INDIAN_RECIPES_TFIDF
            df['ingredients_clean'] = df['ingredients'].apply(clean_ingredients)
            INDIAN_RECIPES_VECTORIZER = TfidfVectorizer(
                lowercase=True,
                token_pattern=r'\b\w+\b',
                max_features=5000,
                ngram_range=(1, 2)
            )
            ingredient_texts = df['ingredients_clean'].fillna('').tolist()
            INDIAN_RECIPES_TFIDF = INDIAN_RECIPES_VECTORIZER.fit_transform(ingredient_texts)
            INDIAN_RECIPES_DATA = df
            print(f"DEBUG: Loaded {len(df)} sample Indian recipes after error")
            return df
        except Exception as e2:
            print(f"ERROR: Failed to load sample recipes: {str(e2)}")
            return None


def clean_ingredients(ingredients_str: str) -> str:
    """
    Clean and normalize ingredient string.
    """
    if pd.isna(ingredients_str) or not ingredients_str:
        return ""
    
    # Convert to string
    ingredients_str = str(ingredients_str)
    
    # Remove special characters but keep spaces and commas
    ingredients_str = re.sub(r'[^\w\s,]+', ' ', ingredients_str)
    
    # Normalize whitespace
    ingredients_str = ' '.join(ingredients_str.split())
    
    # Convert to lowercase
    ingredients_str = ingredients_str.lower()
    
    return ingredients_str


def create_sample_indian_recipes():
    """
    Create a sample dataset of Indian recipes if CSV is not available.
    """
    sample_recipes = [
        {
            'name': 'Dal Tadka',
            'ingredients': 'toor dal, onion, tomato, garlic, ginger, turmeric, red chili powder, cumin seeds, mustard seeds, curry leaves, oil, salt',
            'prep_time': 10,
            'cook_time': 30
        },
        {
            'name': 'Chicken Curry',
            'ingredients': 'chicken, onion, tomato, garlic, ginger, turmeric, red chili powder, garam masala, coriander powder, oil, salt',
            'prep_time': 15,
            'cook_time': 45
        },
        {
            'name': 'Aloo Gobi',
            'ingredients': 'potato, cauliflower, onion, tomato, garlic, ginger, turmeric, red chili powder, cumin seeds, coriander powder, oil, salt',
            'prep_time': 10,
            'cook_time': 25
        },
        {
            'name': 'Paneer Butter Masala',
            'ingredients': 'paneer, onion, tomato, garlic, ginger, cashews, cream, butter, garam masala, turmeric, red chili powder, oil, salt',
            'prep_time': 15,
            'cook_time': 30
        },
        {
            'name': 'Biryani',
            'ingredients': 'rice, chicken, onion, tomato, yogurt, garlic, ginger, biryani masala, turmeric, red chili powder, mint leaves, coriander leaves, oil, salt',
            'prep_time': 20,
            'cook_time': 60
        },
        {
            'name': 'Palak Paneer',
            'ingredients': 'paneer, spinach, onion, tomato, garlic, ginger, garam masala, turmeric, red chili powder, cream, oil, salt',
            'prep_time': 15,
            'cook_time': 30
        },
        {
            'name': 'Rajma',
            'ingredients': 'kidney beans, onion, tomato, garlic, ginger, turmeric, red chili powder, cumin seeds, coriander powder, oil, salt',
            'prep_time': 10,
            'cook_time': 40
        },
        {
            'name': 'Chole',
            'ingredients': 'chickpeas, onion, tomato, garlic, ginger, chole masala, turmeric, red chili powder, amchur, oil, salt',
            'prep_time': 10,
            'cook_time': 35
        },
        {
            'name': 'Matar Paneer',
            'ingredients': 'paneer, green peas, onion, tomato, garlic, ginger, garam masala, turmeric, red chili powder, oil, salt',
            'prep_time': 15,
            'cook_time': 30
        },
        {
            'name': 'Baingan Bharta',
            'ingredients': 'eggplant, onion, tomato, garlic, ginger, green chili, turmeric, red chili powder, cumin seeds, coriander leaves, oil, salt',
            'prep_time': 10,
            'cook_time': 35
        },
    ]
    
    return pd.DataFrame(sample_recipes)


def get_indian_recipes(ingredients: List[str], number: int = 10, expiry_ingredients: List[str] = None) -> Dict[str, Any]:
    """
    Get Indian recipe suggestions based on available ingredients using ML matching.
    
    Args:
        ingredients: List of ingredient names from inventory
        number: Maximum number of recipes to return
        expiry_ingredients: List of ingredients from items expiring soon (for prioritization)
        
    Returns:
        dict: Recipe suggestions with success/error status
    """
    try:
        # Load recipes if not already loaded
        df = load_indian_recipes()
        
        if df is None or len(df) == 0:
            return {
                "error": "No Indian recipes available",
                "recipes": []
            }
        
        # Prepare user ingredients text
        user_ingredients_text = ' '.join([clean_ingredients(ing) for ing in ingredients])
        
        if not user_ingredients_text.strip():
            return {
                "error": "No valid ingredients provided",
                "recipes": []
            }
        
        # Check if vectorizer is initialized
        if INDIAN_RECIPES_VECTORIZER is None or INDIAN_RECIPES_TFIDF is None:
            print("ERROR: Indian recipes vectorizer not initialized. Reloading...")
            # Force reload
            global INDIAN_RECIPES_DATA
            INDIAN_RECIPES_DATA = None
            df = load_indian_recipes()
            if INDIAN_RECIPES_VECTORIZER is None or INDIAN_RECIPES_TFIDF is None:
                return {
                    "error": "Failed to initialize Indian recipes ML model",
                    "recipes": []
                }
        
        # Vectorize user ingredients
        try:
            user_vector = INDIAN_RECIPES_VECTORIZER.transform([user_ingredients_text])
            
            # Calculate cosine similarity
            similarities = cosine_similarity(user_vector, INDIAN_RECIPES_TFIDF).flatten()
        except Exception as e:
            print(f"ERROR: Failed to vectorize ingredients: {str(e)}")
            return {
                "error": f"Failed to process ingredients: {str(e)}",
                "recipes": []
            }
        
        # Get top matching recipes
        top_indices = np.argsort(similarities)[::-1]  # Sort descending
        
        # Filter recipes with at least one matching ingredient (similarity > 0)
        matching_recipes = []
        seen_names = set()
        
        for idx in top_indices:
            if similarities[idx] <= 0:
                continue  # Skip recipes with no matching ingredients
            
            recipe = df.iloc[idx].to_dict()
            recipe_name = recipe.get('name', '')
            
            # Avoid duplicates
            if recipe_name in seen_names:
                continue
            seen_names.add(recipe_name)
            
            # Extract ingredients list
            recipe_ingredients_str = recipe.get('ingredients', '')
            recipe_ingredients = [ing.strip() for ing in recipe_ingredients_str.split(',') if ing.strip()]
            
            # Count matching ingredients
            matching_count = 0
            used_ingredients = []
            missed_ingredients = []
            
            user_ingredients_lower = [ing.lower().strip() for ing in ingredients]
            
            for recipe_ing in recipe_ingredients:
                recipe_ing_lower = recipe_ing.lower().strip()
                is_matched = False
                
                # Check if recipe ingredient matches any user ingredient
                for user_ing in user_ingredients_lower:
                    # Exact match
                    if user_ing == recipe_ing_lower:
                        is_matched = True
                        break
                    # Partial match (e.g., "flour" in "wheat flour")
                    if user_ing in recipe_ing_lower or recipe_ing_lower in user_ing:
                        is_matched = True
                        break
                
                if is_matched:
                    matching_count += 1
                    used_ingredients.append({
                        "id": len(used_ingredients) + 1,
                        "name": recipe_ing,
                        "image": "",  # Indian recipes may not have images
                        "available": True
                    })
                else:
                    missed_ingredients.append({
                        "id": len(missed_ingredients) + 1,
                        "name": recipe_ing,
                        "image": "",
                        "available": False
                    })
            
            # Only include recipes with at least one matching ingredient
            if matching_count > 0:
                recipe_data = {
                    "id": idx + 100000,  # Use high IDs to avoid conflicts with Spoonacular
                    "title": recipe_name,
                    "image": recipe.get('image', '') or "",
                    "usedIngredientCount": matching_count,
                    "missedIngredientCount": len(missed_ingredients),
                    "usedIngredients": used_ingredients,
                    "missedIngredients": missed_ingredients,
                    "similarity_score": float(similarities[idx]),
                    "prep_time": recipe.get('prep_time', 0),
                    "cook_time": recipe.get('cook_time', 0),
                    "source": "indian"
                }
                
                # Prioritize recipes with expiry ingredients
                if expiry_ingredients:
                    expiry_matches = sum(1 for ing in expiry_ingredients 
                                       if any(ing.lower() in used_ing['name'].lower() 
                                            for used_ing in used_ingredients))
                    recipe_data["expiry_priority"] = expiry_matches > 0
                else:
                    recipe_data["expiry_priority"] = False
                
                matching_recipes.append(recipe_data)
                
                if len(matching_recipes) >= number * 2:  # Get more to filter later
                    break
        
        # Sort by: expiry priority first, then by matching count, then by similarity
        matching_recipes.sort(
            key=lambda x: (
                not x.get("expiry_priority", False),  # False first (expiry priority recipes first)
                -x.get("usedIngredientCount", 0),  # More ingredients first
                -x.get("similarity_score", 0)  # Higher similarity first
            )
        )
        
        # Return top N recipes
        top_recipes = matching_recipes[:number]
        
        return {
            "success": True,
            "ingredients_used": ingredients,
            "recipes": top_recipes,
            "total_recipes": len(top_recipes)
        }
        
    except Exception as e:
        print(f"ERROR: Failed to get Indian recipes: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "error": f"Failed to get Indian recipes: {str(e)}",
            "recipes": []
        }

