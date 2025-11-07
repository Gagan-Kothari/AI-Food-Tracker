# Indian Recipes Integration Setup

This guide explains how to set up the Indian recipes feature using the Kaggle Indian Food Dataset.

## Overview

The system now supports three recipe types:
- **Indian Recipes**: ML-based matching using TF-IDF and cosine similarity
- **Foreign Recipes**: Spoonacular API (existing implementation)
- **Both**: Combines Indian and Foreign recipes, sorted by priority

## Dataset Setup

### Option 1: Use Kaggle Dataset (Recommended)

1. **Download the Dataset**:
   - Go to [Kaggle Indian Food Dataset](https://www.kaggle.com/datasets/nehaprabhavalkar/indian-food-101)
   - Download the CSV file (usually named `indian_food.csv`)

2. **Place the CSV File**:
   - Place `indian_food.csv` in the project root directory, OR
   - Place it in the `app/` directory, OR
   - Set the path via environment variable `INDIAN_RECIPES_CSV`

3. **Expected CSV Format**:
   The CSV should have at least these columns:
   - `name` or `recipe` or `dish_name`: Recipe name
   - `ingredients` or `ingredient_list`: Comma-separated list of ingredients
   - Optional: `prep_time`, `cook_time`, `image`, etc.

### Option 2: Use Sample Dataset

If no CSV file is found, the system will automatically use a sample dataset with 10 common Indian recipes (Dal Tadka, Chicken Curry, Aloo Gobi, etc.).

## Environment Variables

Add to your `.env` file or Railway environment variables:

```env
# Optional: Path to Indian recipes CSV file
INDIAN_RECIPES_CSV=indian_food.csv
```

## How It Works

### ML Model (Indian Recipes)

1. **TF-IDF Vectorization**: 
   - Converts recipe ingredients into numerical vectors
   - Uses unigrams and bigrams for better matching

2. **Cosine Similarity**:
   - Calculates similarity between user's inventory ingredients and recipe ingredients
   - Returns recipes with similarity > 0 (at least one matching ingredient)

3. **Prioritization**:
   - Recipes with expiry-alert ingredients are prioritized
   - Sorted by: expiry priority → matching ingredient count → similarity score

### Recipe Matching Logic

- **Exact Match**: Direct ingredient name match
- **Partial Match**: Handles cases like "flour" matching "wheat flour"
- **Word-based Match**: Matches individual words in multi-word ingredients
- **Synonym Support**: Uses the same synonym dictionary as foreign recipes

## API Usage

### Backend

```python
from app.crud.recipe_crud import get_inventory_based_recipes

# Get Indian recipes
recipes = get_inventory_based_recipes(user_id, db, recipe_type="indian")

# Get Foreign recipes (default)
recipes = get_inventory_based_recipes(user_id, db, recipe_type="foreign")

# Get Both
recipes = get_inventory_based_recipes(user_id, db, recipe_type="both")
```

### Frontend

```typescript
// Get Indian recipes
const response = await apiService.getInventoryBasedRecipes(userid, "indian");

// Get Foreign recipes
const response = await apiService.getInventoryBasedRecipes(userid, "foreign");

// Get Both
const response = await apiService.getInventoryBasedRecipes(userid, "both");
```

## Features

1. **Two Recipe Calls**:
   - First call: Recipes for yellow/red alert items (5 recipes, shown first)
   - Second call: Recipes for entire inventory (5 recipes, shown after)
   - Combined and limited to top 10 recipes

2. **Ingredient Matching**:
   - Ignores recipes with 0 matching ingredients
   - Matches ingredients using multiple strategies (exact, partial, word-based, synonym)

3. **Sorting**:
   - Expiry-alert recipes first
   - Then sorted by: used ingredient count → similarity score → expiry date

## Troubleshooting

### "No Indian recipes available"
- Check if the CSV file exists and is readable
- Verify the CSV has the required columns (`name`, `ingredients`)
- Check backend logs for loading errors

### "No recipes found for these ingredients"
- Ensure your inventory has items
- Check if ingredient names match (case-insensitive)
- Try the "Both" option to see if foreign recipes work

### Performance Issues
- The ML model loads on first use (may take 1-2 seconds)
- Large datasets (>1000 recipes) may be slower
- Consider limiting the dataset size if needed

## Dependencies

The following packages are required (already in `requirements.txt`):
- `pandas>=2.3.0`
- `numpy>=2.3.0`
- `scikit-learn>=1.3.0`

## Notes

- Indian recipes use high IDs (100000+) to avoid conflicts with Spoonacular recipe IDs
- The system automatically falls back to sample recipes if CSV is not found
- Recipe images may not be available for Indian recipes (uses placeholder if missing)

