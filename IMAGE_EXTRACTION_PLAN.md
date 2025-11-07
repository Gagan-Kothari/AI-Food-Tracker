# Image URL Extraction Plan for Indian Recipes

## Overview
Extract image URLs from CSV file for Indian recipes that are matched by the ML model.

## Current Status
✅ **Local Testing**: Image extraction works perfectly (99.8% coverage)
✅ **CSV File**: Contains 4,236 recipes with valid image URLs
✅ **Recipe Name Matching**: ML model and CSV use identical recipe names (when normalized)

## Workflow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ 1. User Requests Indian Recipes                             │
│    Input: ingredients list                                   │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. ML Model Finds Matching Recipes                          │
│    - Uses TF-IDF + Cosine Similarity                        │
│    - Returns top N recipes with:                             │
│      * recipe name (title)                                   │
│      * ingredients                                           │
│      * similarity score                                       │
│      * NO image_url yet                                      │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Sort and Filter Recipes                                   │
│    - Sort by expiry priority, ingredient count, similarity   │
│    - Select top N recipes                                    │
│    - Recipes have empty image field                          │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Load CSV File (indian_food.csv)                           │
│    Search paths in order:                                    │
│    1. /app/../indian_food.csv (project root)                 │
│    2. /app/indian_food.csv                                   │
│    3. /app/crud/indian_food.csv                             │
│    4. Current working directory                             │
│    5. /indian_food.csv (absolute root)                      │
│                                                              │
│    If found: Load CSV and normalize column names            │
│    If not found: Log error, skip image extraction           │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Create Recipe Name → Image URL Mapping                   │
│    For each row in CSV:                                      │
│    - Extract recipe name: str(row['name']).strip().lower()  │
│    - Extract image URL: row['image_url']                     │
│    - Validate image URL:                                     │
│      * Not empty/null/nan                                    │
│      * Length > 10 characters                                │
│      * Starts with http:// or https://                      │
│    - Store in dictionary: {recipe_name: image_url}          │
│                                                              │
│    Result: Dictionary with ~4,226 valid mappings            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 6. Match Recipes with Images                                 │
│    For each matched recipe:                                  │
│    - Get recipe title: recipe['title']                      │
│    - Normalize: str(title).strip().lower()                   │
│    - Lookup in image mapping dictionary                     │
│    - If found: Set recipe['image'] = image_url              │
│    - If not found: Leave recipe['image'] = ""               │
│                                                              │
│    Note: Exact match required (case-insensitive)            │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│ 7. Return Recipes with Images                                │
│    - All recipes have 'image' field                          │
│    - Valid URLs for matched recipes                          │
│    - Empty string for unmatched recipes                     │
└─────────────────────────────────────────────────────────────┘
```

## Detailed Steps

### Step 1: Recipe Matching (ML Model)
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()`

**Input**: 
- `ingredients`: List of user's ingredients
- `number`: Number of recipes to return

**Process**:
1. Load pre-trained ML model (TF-IDF vectorizer + similarity matrix)
2. Vectorize user ingredients
3. Calculate cosine similarity with all recipes
4. Filter recipes with similarity > 0 (at least one matching ingredient)
5. Sort by similarity score
6. Return top N recipes

**Output**: List of recipe dictionaries with:
- `id`: Recipe ID
- `title`: Recipe name (e.g., "Thayir Semiya Recipe (Curd Semiya)")
- `image`: "" (empty, will be filled later)
- `usedIngredientCount`: Number of matching ingredients
- `similarity_score`: ML similarity score
- Other fields...

### Step 2: CSV File Location Resolution
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()` (after recipe matching)

**Process**:
```python
# Determine possible CSV locations
current_dir = os.path.dirname(__file__)  # app/crud/
app_dir = os.path.dirname(current_dir)  # app/
root_dir = os.path.dirname(app_dir)      # root/

csv_paths = [
    os.path.join(root_dir, "indian_food.csv"),      # Project root
    os.path.join(app_dir, "indian_food.csv"),       # app/indian_food.csv
    os.path.join(current_dir, "indian_food.csv"),   # app/crud/indian_food.csv
    "indian_food.csv",                               # Current working directory
    os.path.join("/app", "indian_food.csv"),         # Railway absolute
    os.path.join("/", "indian_food.csv"),            # Root absolute
    os.path.abspath(os.path.join("/app", "..", "indian_food.csv")),  # Railway project root
]

# Search for CSV file
for path in csv_paths:
    if os.path.exists(path):
        found_path = path
        break
```

**Railway Considerations**:
- Railway's working directory is typically `/app`
- CSV file is at project root (one level up from `/app`)
- Need to check multiple paths to handle different deployment scenarios

### Step 3: CSV Loading and Validation
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()`

**Process**:
```python
if found_path:
    csv_df = pd.read_csv(found_path)
    csv_df.columns = csv_df.columns.str.lower().str.strip()  # Normalize column names
    
    # Validate required columns
    if 'image_url' not in csv_df.columns:
        # Log error, skip image extraction
        return recipes_without_images
```

**Validation**:
- Check if CSV file exists
- Check if `image_url` column exists
- Handle missing or malformed data gracefully

### Step 4: Create Image Mapping Dictionary
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()`

**Process**:
```python
recipe_image_map = {}

for _, csv_row in csv_df.iterrows():
    # Extract and normalize recipe name
    recipe_name_csv = str(csv_row.get('name', '')).strip().lower()
    
    # Extract image URL
    image_url_csv = csv_row.get('image_url', '')
    
    # Handle pandas/numpy types
    if hasattr(image_url_csv, 'item'):
        image_url_csv = image_url_csv.item()
    
    img_str = str(image_url_csv).strip()
    
    # Validate image URL
    if (img_str and 
        len(img_str) > 10 and
        img_str.lower() not in ['nan', 'none', '', 'null'] and
        (img_str.startswith('http://') or img_str.startswith('https://'))):
        recipe_image_map[recipe_name_csv] = img_str
```

**Result**: Dictionary mapping normalized recipe names to image URLs
- Key: `"thayir semiya recipe (curd semiya)"`
- Value: `"https://www.archanaskitchen.com/images/..."`

### Step 5: Match Recipes with Images
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()`

**Process**:
```python
for recipe in top_recipes:
    recipe_title = str(recipe.get('title', '')).strip().lower()
    
    if recipe_title in recipe_image_map:
        recipe['image'] = recipe_image_map[recipe_title]
        # Log success
    else:
        recipe['image'] = ""  # Keep empty if not found
        # Log warning (optional)
```

**Matching Logic**:
- **Exact match** (case-insensitive): Recipe name from ML model must exactly match CSV recipe name
- Both are normalized: `.strip().lower()`
- No fuzzy matching (to ensure accuracy)

### Step 6: Return Final Recipes
**Location**: `app/crud/indian_recipes.py::get_indian_recipes()`

**Output**: List of recipe dictionaries with:
```python
{
    "id": 100001,
    "title": "Thayir Semiya Recipe (Curd Semiya)",
    "image": "https://www.archanaskitchen.com/images/...",  # ✅ Filled from CSV
    "usedIngredientCount": 3,
    "missedIngredientCount": 2,
    "similarity_score": 0.85,
    "prep_time": 10,
    "cook_time": 20,
    "source": "indian",
    "measurements": [...]
}
```

## Error Handling

### Scenario 1: CSV File Not Found
**Action**: 
- Log warning: "CSV not found, skipping image extraction"
- Return recipes with empty `image` fields
- Don't fail the entire request

### Scenario 2: CSV Missing `image_url` Column
**Action**:
- Log error: "CSV missing image_url column"
- Return recipes with empty `image` fields
- Don't fail the entire request

### Scenario 3: Recipe Name Mismatch
**Action**:
- Log debug info: "Recipe name not found in CSV mapping"
- Leave `image` field empty for that recipe
- Continue processing other recipes

### Scenario 4: Invalid Image URL
**Action**:
- Skip invalid URLs during mapping creation
- Only include valid HTTP/HTTPS URLs
- Log count of skipped invalid URLs

## Performance Considerations

1. **CSV Loading**: 
   - Load CSV once per request (not cached globally)
   - CSV is ~4,236 rows, loads quickly (~100ms)

2. **Dictionary Lookup**:
   - O(1) lookup time for each recipe
   - Very fast even for large number of recipes

3. **Memory**:
   - Image mapping dictionary: ~4,226 entries
   - Each entry: ~100 bytes (name + URL)
   - Total: ~400 KB (negligible)

## Debug Logging

The code includes comprehensive debug logging:

```python
# CSV file search
print(f"DEBUG: ===== SEARCHING FOR CSV FILE =====")
print(f"DEBUG: Current directory: {os.getcwd()}")
print(f"DEBUG: Checking {len(csv_paths)} possible paths:")

# CSV loading
print(f"DEBUG: ✓✓ FOUND CSV at: {found_path}")
print(f"DEBUG: Loaded CSV with {len(csv_df)} recipes")

# Image mapping
print(f"DEBUG: Created image map with {len(recipe_image_map)} recipes")

# Recipe matching
print(f"DEBUG: ✓✓ FOUND IMAGE for '{recipe_title}': {image_url}")
print(f"DEBUG: ✗✗ NO IMAGE FOUND for '{recipe_title}'")
```

## Testing

### Local Testing ✅
- Test script: `test_image_extraction.py`
- Results:
  - CSV found: ✅
  - Images extracted: 4,226/4,236 (99.8%)
  - Recipe name matching: ✅

### Railway Testing (Pending)
- Need to verify CSV file location on Railway
- Check deployment logs for path resolution
- Ensure CSV file is included in deployment

## Deployment Checklist

- [ ] Ensure `indian_food.csv` is in git repository (✅ Confirmed)
- [ ] Verify CSV file is included in Railway deployment
- [ ] Check Railway logs for CSV path resolution
- [ ] Verify image URLs are being extracted in production
- [ ] Test with actual recipe requests

## Future Improvements

1. **Caching**: Cache CSV data in memory to avoid reloading on every request
2. **Fuzzy Matching**: Add fuzzy matching for recipe names that don't match exactly
3. **Fallback Images**: Use placeholder images for recipes without images
4. **Image Validation**: Validate image URLs are accessible before returning

