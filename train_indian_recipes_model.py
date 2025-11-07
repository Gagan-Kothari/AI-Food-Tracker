"""
Train Indian Recipes ML Model Locally
This script trains the TF-IDF vectorizer and saves it for deployment.
Run this locally, then upload the model files to Railway.
"""
import os
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import re
from typing import List

# Path to Indian recipes dataset (CSV file)
INDIAN_RECIPES_CSV = "indian_food.csv"
MODEL_DIR = "app/models/indian_recipes"
VECTORIZER_FILE = os.path.join(MODEL_DIR, "indian_recipes_vectorizer.joblib")
TFIDF_MATRIX_FILE = os.path.join(MODEL_DIR, "indian_recipes_tfidf.joblib")
RECIPES_DATA_FILE = os.path.join(MODEL_DIR, "indian_recipes_data.parquet")


def clean_ingredients(ingredients_str: str) -> str:
    """Clean and normalize ingredient string."""
    if pd.isna(ingredients_str) or not ingredients_str:
        return ""
    
    ingredients_str = str(ingredients_str)
    ingredients_str = re.sub(r'[^\w\s,]+', ' ', ingredients_str)
    ingredients_str = ' '.join(ingredients_str.split())
    ingredients_str = ingredients_str.lower()
    
    return ingredients_str


def create_sample_indian_recipes():
    """Create a sample dataset of Indian recipes if CSV is not available."""
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


def load_indian_recipes():
    """Load Indian recipes dataset from CSV file."""
    csv_paths = [
        INDIAN_RECIPES_CSV,
        os.path.join("app", INDIAN_RECIPES_CSV),
        os.path.join("..", INDIAN_RECIPES_CSV),
    ]
    
    df = None
    for path in csv_paths:
        if os.path.exists(path):
            print(f"Loading Indian recipes from {path}")
            df = pd.read_csv(path)
            break
    
    if df is None:
        print(f"CSV not found. Using sample dataset.")
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
    
    return df


def train_model():
    """Train the TF-IDF model and save it."""
    print("=" * 50)
    print("Training Indian Recipes ML Model")
    print("=" * 50)
    
    # Load recipes
    df = load_indian_recipes()
    print(f"Loaded {len(df)} recipes")
    
    # Clean and preprocess ingredients
    df['ingredients_clean'] = df['ingredients'].apply(clean_ingredients)
    
    # Create TF-IDF vectorizer
    print("Creating TF-IDF vectorizer...")
    vectorizer = TfidfVectorizer(
        lowercase=True,
        token_pattern=r'\b\w+\b',
        max_features=5000,
        ngram_range=(1, 2)
    )
    
    # Fit vectorizer on all recipe ingredients
    print("Fitting vectorizer on recipe ingredients...")
    ingredient_texts = df['ingredients_clean'].fillna('').tolist()
    tfidf_matrix = vectorizer.fit_transform(ingredient_texts)
    
    print(f"Vectorizer vocabulary size: {len(vectorizer.vocabulary_)}")
    print(f"TF-IDF matrix shape: {tfidf_matrix.shape}")
    
    # Create model directory
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    # Save vectorizer
    print(f"Saving vectorizer to {VECTORIZER_FILE}...")
    joblib.dump(vectorizer, VECTORIZER_FILE)
    
    # Save TF-IDF matrix
    print(f"Saving TF-IDF matrix to {TFIDF_MATRIX_FILE}...")
    joblib.dump(tfidf_matrix, TFIDF_MATRIX_FILE)
    
    # Save recipes data
    print(f"Saving recipes data to {RECIPES_DATA_FILE}...")
    df.to_parquet(RECIPES_DATA_FILE, index=False)
    
    print("=" * 50)
    print("Model training complete!")
    print(f"Model files saved to: {MODEL_DIR}")
    print("=" * 50)
    print("\nFiles created:")
    print(f"  - {VECTORIZER_FILE}")
    print(f"  - {TFIDF_MATRIX_FILE}")
    print(f"  - {RECIPES_DATA_FILE}")
    print("\nUpload these files to Railway for deployment.")


if __name__ == "__main__":
    train_model()

