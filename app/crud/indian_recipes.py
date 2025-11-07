"""
Indian Recipe Matching using ML model (TF-IDF + Cosine Similarity)
Loads pre-trained model or trains on-the-fly if model not found
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import re
from typing import List, Dict, Any
from dotenv import load_dotenv

load_dotenv()

# Path to Indian recipes dataset (CSV file)
INDIAN_RECIPES_CSV = os.getenv("INDIAN_RECIPES_CSV", "indian_food.csv")

# Pre-trained model paths
MODEL_DIR = os.path.join(os.path.dirname(__file__), "..", "models", "indian_recipes")
VECTORIZER_FILE = os.path.join(MODEL_DIR, "indian_recipes_vectorizer.joblib")
TFIDF_MATRIX_FILE = os.path.join(MODEL_DIR, "indian_recipes_tfidf.joblib")
RECIPES_DATA_FILE = os.path.join(MODEL_DIR, "indian_recipes_data.parquet")

INDIAN_RECIPES_DATA = None
INDIAN_RECIPES_VECTORIZER = None
INDIAN_RECIPES_TFIDF = None


def load_indian_recipes():
    """
    Load Indian recipes - first tries to load pre-trained model, 
    otherwise trains on-the-fly from CSV or sample data.
    """
    global INDIAN_RECIPES_DATA, INDIAN_RECIPES_VECTORIZER, INDIAN_RECIPES_TFIDF
    
    if INDIAN_RECIPES_DATA is not None:
        return INDIAN_RECIPES_DATA
    
    try:
        # Try to load pre-trained model first
        if (os.path.exists(VECTORIZER_FILE) and 
            os.path.exists(TFIDF_MATRIX_FILE) and 
            os.path.exists(RECIPES_DATA_FILE)):
            
            print(f"DEBUG: Loading pre-trained Indian recipes model from {MODEL_DIR}")
            
            INDIAN_RECIPES_VECTORIZER = joblib.load(VECTORIZER_FILE)
            INDIAN_RECIPES_TFIDF = joblib.load(TFIDF_MATRIX_FILE)
            INDIAN_RECIPES_DATA = pd.read_parquet(RECIPES_DATA_FILE)
            
            print(f"DEBUG: Loaded {len(INDIAN_RECIPES_DATA)} Indian recipes from pre-trained model")
            print(f"DEBUG: Vectorizer vocabulary size: {len(INDIAN_RECIPES_VECTORIZER.vocabulary_)}")
            print(f"DEBUG: TF-IDF matrix shape: {INDIAN_RECIPES_TFIDF.shape}")
            
            return INDIAN_RECIPES_DATA
        
        # Fallback: Train model on-the-fly (for backward compatibility)
        print(f"DEBUG: Pre-trained model not found. Training on-the-fly...")
        
        # Try to load from CSV
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
            df = create_sample_indian_recipes()
        
        # Normalize column names
        df.columns = df.columns.str.lower().str.strip()
        
        # Ensure required columns exist
        required_cols = ['name', 'ingredients']
        for col in required_cols:
            if col not in df.columns:
                if col == 'name':
                    alternatives = ['recipe', 'dish', 'dish_name', 'recipe_name', 'title']
                elif col == 'ingredients':
                    alternatives = ['ingredient', 'ingredient_list', 'ingredients_list']
                
                for alt in alternatives:
                    if alt in df.columns:
                        df[col] = df[alt]
                        break
                else:
                    df[col] = ""
        
        # Clean and preprocess ingredients
        df['ingredients_clean'] = df['ingredients'].apply(clean_ingredients)
        
        # Create and train TF-IDF vectorizer
        INDIAN_RECIPES_VECTORIZER = TfidfVectorizer(
            lowercase=True,
            token_pattern=r'\b\w+\b',
            max_features=5000,
            ngram_range=(1, 2)
        )
        
        ingredient_texts = df['ingredients_clean'].fillna('').tolist()
        INDIAN_RECIPES_TFIDF = INDIAN_RECIPES_VECTORIZER.fit_transform(ingredient_texts)
        
        INDIAN_RECIPES_DATA = df
        print(f"DEBUG: Trained model on {len(df)} Indian recipes")
        print(f"DEBUG: Vectorizer vocabulary size: {len(INDIAN_RECIPES_VECTORIZER.vocabulary_)}")
        print(f"DEBUG: TF-IDF matrix shape: {INDIAN_RECIPES_TFIDF.shape}")
        
        return df
        
    except Exception as e:
        print(f"ERROR: Failed to load Indian recipes: {str(e)}")
        import traceback
        traceback.print_exc()
        # Return sample dataset on error
        try:
            df = create_sample_indian_recipes()
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


def safe_int_parse(value, default=0):
    """
    Safely parse a value to integer, handling strings, None, and invalid formats.
    
    Args:
        value: Value to parse (can be int, str, None, or other types)
        default: Default value to return if parsing fails
        
    Returns:
        int: Parsed integer value or default
    """
    if value is None:
        return default
    
    # If already an integer
    if isinstance(value, int):
        return value
    
    # If it's a float, convert to int
    if isinstance(value, float):
        return int(value)
    
    # If it's a string, try to extract number
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        
        # Try direct conversion first
        try:
            return int(float(value))
        except (ValueError, TypeError):
            pass
        
        # Try to extract number from string (e.g., "Total in 55 M" -> 55)
        numbers = re.findall(r'\d+', value)
        if numbers:
            try:
                return int(numbers[0])
            except (ValueError, TypeError):
                pass
    
    return default


def extract_ingredient_name(ingredient_text: str) -> tuple:
    """
    Extract ingredient name and measurement from recipe ingredient text.
    Example: "1 cup wheat flour" -> ("wheat flour", "1 cup")
    
    Args:
        ingredient_text: Full ingredient text from recipe
        
    Returns:
        tuple: (ingredient_name, measurement)
    """
    if not ingredient_text or pd.isna(ingredient_text):
        return ("", "")
    
    ingredient_text = str(ingredient_text).strip()
    
    # Pattern to match measurements at the start (e.g., "1 cup", "2 tbsp", "500g", "1/2 teaspoon")
    measurement_pattern = r'^(\d+(?:[\.,]\d+)?(?:\s*/\s*\d+)?\s*(?:cup|cups|tbsp|tablespoon|tablespoons|tsp|teaspoon|teaspoons|gram|grams|g|kg|kilogram|kilograms|ml|l|litre|litres|oz|ounce|ounces|piece|pieces|pcs|pc|whole|halves|halved|sliced|chopped|diced|minced|grated|crushed|powdered|pinch|pinches|dash|dashes|bunch|bunches|clove|cloves|leaf|leaves|sprig|sprigs|inch|inches|cm|mm|lb|pound|pounds)\s*,?\s*)'
    
    # Try to extract measurement
    measurement_match = re.match(measurement_pattern, ingredient_text.lower())
    measurement = ""
    ingredient_name = ingredient_text
    
    if measurement_match:
        measurement = measurement_match.group(0).strip()
        ingredient_name = ingredient_text[len(measurement):].strip()
    
    # Clean ingredient name - remove extra punctuation, normalize
    ingredient_name = re.sub(r'[^\w\s]+', ' ', ingredient_name)
    ingredient_name = ' '.join(ingredient_name.split())
    ingredient_name = ingredient_name.lower().strip()
    
    return (ingredient_name, measurement)


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


def match_ingredient_strict(recipe_ing: str, user_ing: str, is_indian: bool = True) -> bool:
    """
    Strict matching for Indian recipes - requires exact or very close matches.
    For foreign recipes, allows more flexible matching.
    
    Args:
        recipe_ing: Recipe ingredient name (cleaned)
        user_ing: User inventory ingredient name (cleaned)
        is_indian: Whether this is for Indian recipes (stricter matching)
        
    Returns:
        bool: True if ingredients match
    """
    recipe_ing = recipe_ing.lower().strip()
    user_ing = user_ing.lower().strip()
    
    # Exact match
    if recipe_ing == user_ing:
        return True
    
    if is_indian:
        # For Indian recipes, be stricter
        # Don't match different flour types
        flour_types = {
            'wheat flour': ['wheat flour', 'whole wheat flour'],
            'refined wheat flour': ['refined wheat flour', 'maida', 'all purpose flour', 'all-purpose flour'],
            'atta': ['atta', 'whole wheat flour'],
            'semolina': ['semolina', 'sooji', 'rava'],
            'rice flour': ['rice flour'],
            'besan': ['besan', 'gram flour', 'chickpea flour'],
            'corn flour': ['corn flour', 'cornflour', 'cornstarch'],
            'ragi flour': ['ragi flour', 'finger millet flour']
        }
        
        # Check if either is a flour type
        recipe_flour_type = None
        user_flour_type = None
        
        for flour_name, variants in flour_types.items():
            for variant in variants:
                if variant in recipe_ing:
                    recipe_flour_type = flour_name
                    break
                if variant in user_ing:
                    user_flour_type = flour_name
                    break
            if recipe_flour_type and user_flour_type:
                break
        
        # If both are flours, they must be the same type
        if recipe_flour_type and user_flour_type:
            return recipe_flour_type == user_flour_type
        
        # If only one is a flour, don't match (e.g., "wheat flour" shouldn't match "flour")
        if recipe_flour_type or user_flour_type:
            return False
        
        # For non-flour items, allow partial match but be more careful
        # Only match if one is contained in the other and they're similar length
        if user_ing in recipe_ing:
            # User ingredient is in recipe (e.g., "jam" in "raspberry jam")
            # Check if it's a reasonable match (not too different in length)
            if len(recipe_ing) - len(user_ing) <= 15:  # Allow some prefix/suffix
                return True
        elif recipe_ing in user_ing:
            # Recipe ingredient is in user ingredient (e.g., "onion" in "red onion")
            if len(user_ing) - len(recipe_ing) <= 15:
                return True
        
        return False
    else:
        # For foreign recipes, more flexible matching
        # Allow "wheat flour" to match "refined wheat flour" for foreign recipes
        if user_ing in recipe_ing or recipe_ing in user_ing:
            return True
        return False


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
            
            # Extract image URL directly from dataframe (before converting to dict)
            # The CSV has 'image_url' column which becomes 'image_url' after normalization
            recipe_image = ""
            try:
                # Access directly from dataframe to ensure we get the right column
                row = df.iloc[idx]
                # Check for image_url column (normalized to lowercase)
                if 'image_url' in df.columns:
                    img_val = row['image_url']  # Use bracket notation for pandas Series
                    if pd.notna(img_val) and img_val:
                        img_str = str(img_val).strip()
                        if img_str and img_str.lower() != 'nan' and img_str.lower() != 'none' and (img_str.startswith('http://') or img_str.startswith('https://')):
                            recipe_image = img_str
                            print(f"DEBUG: Found image for {recipe_name}: {recipe_image[:50]}...")
            except (KeyError, IndexError, Exception) as e:
                print(f"DEBUG: Error extracting image for recipe {recipe_name}: {str(e)}")
                # Try alternative column names
                for col in df.columns:
                    if 'image' in str(col).lower():
                        try:
                            img_val = row[col]
                            if pd.notna(img_val) and img_val:
                                img_str = str(img_val).strip()
                                if img_str and img_str.lower() != 'nan' and (img_str.startswith('http://') or img_str.startswith('https://')):
                                    recipe_image = img_str
                                    break
                        except:
                            continue
            
            # Extract ingredients list
            recipe_ingredients_str = recipe.get('ingredients', '')
            recipe_ingredients = [ing.strip() for ing in recipe_ingredients_str.split(',') if ing.strip()]
            
            # Count matching ingredients
            matching_count = 0
            used_ingredients = []
            missed_ingredients = []
            recipe_measurements = []  # Store measurements for recipe display
            
            user_ingredients_lower = [ing.lower().strip() for ing in ingredients]
            
            for recipe_ing_full in recipe_ingredients:
                # Extract ingredient name and measurement
                ingredient_name, measurement = extract_ingredient_name(recipe_ing_full)
                
                if not ingredient_name:
                    continue
                
                is_matched = False
                matched_user_ing = None
                
                # Check if recipe ingredient matches any user ingredient using strict matching
                for user_ing in user_ingredients_lower:
                    if match_ingredient_strict(ingredient_name, user_ing, is_indian=True):
                        is_matched = True
                        matched_user_ing = user_ing
                        break
                
                if is_matched:
                    matching_count += 1
                    used_ingredients.append({
                        "id": int(len(used_ingredients) + 1),
                        "name": ingredient_name,  # Just the ingredient name, no measurement
                        "image": "",  # Indian recipes may not have images
                        "available": True
                    })
                    if measurement:
                        recipe_measurements.append(f"{ingredient_name}: {measurement}")
                else:
                    missed_ingredients.append({
                        "id": int(len(missed_ingredients) + 1),
                        "name": ingredient_name,  # Just the ingredient name, no measurement
                        "image": "",
                        "available": False
                    })
                    if measurement:
                        recipe_measurements.append(f"{ingredient_name}: {measurement}")
            
            # Only include recipes with at least one matching ingredient
            if matching_count > 0:
                # Convert numpy types to native Python types for JSON serialization
                recipe_id = int(idx) + 100000  # Use high IDs to avoid conflicts with Spoonacular
                prep_time = safe_int_parse(recipe.get('prep_time'), default=0)
                cook_time = safe_int_parse(recipe.get('cook_time'), default=0)
                
                # recipe_image was already extracted above from the dataframe
                # If it's still empty, try one more time from the dict
                if not recipe_image:
                    for img_col in ['image_url', 'imageurl', 'image', 'image_urls', 'photo', 'photo_url']:
                        img_val = recipe.get(img_col, '')
                        if img_val and pd.notna(img_val):
                            img_str = str(img_val).strip()
                            if img_str and img_str.lower() != 'nan' and (img_str.startswith('http://') or img_str.startswith('https://')):
                                recipe_image = img_str
                                break
                
                recipe_data = {
                    "id": recipe_id,
                    "title": str(recipe_name),
                    "image": recipe_image,
                    "usedIngredientCount": int(matching_count),
                    "missedIngredientCount": int(len(missed_ingredients)),
                    "usedIngredients": used_ingredients,
                    "missedIngredients": missed_ingredients,
                    "similarity_score": float(similarities[idx]),
                    "prep_time": prep_time,
                    "cook_time": cook_time,
                    "source": "indian",
                    "measurements": recipe_measurements  # Add measurements for recipe display
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

