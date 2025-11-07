# Train Indian Recipes ML Model Locally

This guide explains how to train the Indian recipes ML model locally and deploy it to Railway.

## Why Train Locally?

- **Faster**: Training happens once locally, not on every Railway deployment
- **Efficient**: No need to train the model on Railway (saves time and resources)
- **Reliable**: Pre-trained model ensures consistent results

## Prerequisites

1. Python 3.8+ installed locally
2. Required packages: `pandas`, `numpy`, `scikit-learn`, `joblib`, `pyarrow`
3. (Optional) Kaggle Indian Food Dataset CSV file

## Steps

### 1. Install Dependencies

```bash
pip install pandas numpy scikit-learn joblib pyarrow
```

### 2. Prepare Dataset (Optional)

If you have the Kaggle Indian Food Dataset:
- Place `indian_food.csv` in the project root directory
- The script will use it automatically

If you don't have the dataset:
- The script will use a sample dataset with 10 common Indian recipes

### 3. Train the Model

Run the training script from the project root:

```bash
python train_indian_recipes_model.py
```

This will:
- Load recipes from CSV (or use sample data)
- Train the TF-IDF vectorizer
- Save the model files to `app/models/indian_recipes/`

### 4. Model Files Created

After training, you'll have these files in `app/models/indian_recipes/`:

- `indian_recipes_vectorizer.joblib` - The trained TF-IDF vectorizer
- `indian_recipes_tfidf.joblib` - The TF-IDF matrix for all recipes
- `indian_recipes_data.parquet` - The recipes dataset

### 5. Deploy to Railway

1. **Commit the model files** to your repository:
   ```bash
   git add app/models/indian_recipes/
   git commit -m "Add pre-trained Indian recipes model"
   git push
   ```

2. **Railway will automatically deploy** the model files with your code

3. The application will automatically load the pre-trained model on startup

## How It Works

### On Railway (Production)

1. Application starts
2. `load_indian_recipes()` is called
3. Checks for pre-trained model files in `app/models/indian_recipes/`
4. If found: Loads the model (fast, ~1 second)
5. If not found: Falls back to training on-the-fly (slower, ~5-10 seconds)

### Local Development

- If model files exist: Uses pre-trained model
- If not: Trains on-the-fly from CSV or sample data

## File Structure

```
project/
├── train_indian_recipes_model.py  # Training script
├── indian_food.csv                 # (Optional) Kaggle dataset
└── app/
    ├── models/
    │   └── indian_recipes/
    │       ├── indian_recipes_vectorizer.joblib
    │       ├── indian_recipes_tfidf.joblib
    │       └── indian_recipes_data.parquet
    └── crud/
        └── indian_recipes.py       # Model loading code
```

## Updating the Model

If you want to retrain with new recipes:

1. Update the CSV file or modify `create_sample_indian_recipes()` in the training script
2. Run `python train_indian_recipes_model.py` again
3. Commit and push the new model files
4. Railway will deploy the updated model

## Troubleshooting

### "Module not found" errors
- Make sure all dependencies are installed: `pip install -r app/requirements.txt`

### Model files not found on Railway
- Check that files are committed to git
- Verify the path: `app/models/indian_recipes/`
- Check Railway logs for loading errors

### Model loads but recipes not matching
- Verify the model was trained with the same recipe dataset
- Check that ingredient names match between training and inference

## Notes

- Model files are typically 1-5 MB in size
- Training takes 1-5 seconds depending on dataset size
- Loading pre-trained model takes <1 second
- The model uses TF-IDF vectorization with cosine similarity for matching

