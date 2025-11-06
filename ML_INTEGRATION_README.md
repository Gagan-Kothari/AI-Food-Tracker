# ML Integration for AI Food Tracker

This document describes the machine learning integration added to the AI Food Tracker project, including XGBoost-based grocery prediction and enhanced recipe suggestions.

## Overview

The ML integration provides:
1. **Smart Grocery Suggestions**: XGBoost models predict what items users will need based on consumption patterns
2. **Enhanced Recipe Suggestions**: Improved recipe recommendations using actual inventory data
3. **Model Training & Management**: Admin tools for training and retraining ML models

## New Features

### 1. Grocery Suggestions (`/groceries`)
- **Real-time predictions** based on user consumption history
- **Priority-based recommendations** (high/medium/low)
- **Confidence scores** for each suggestion
- **Category-based organization** of suggestions
- **Download functionality** for shopping lists

### 2. Enhanced Recipe Suggestions (`/recipes`)
- **Inventory-aware recommendations** using actual user inventory
- **Ingredient mapping** from product names to recipe ingredients
- **Fallback suggestions** when inventory is limited
- **Visual indicators** for available vs missing ingredients

### 3. ML Model Management
- **Admin dashboard** for model training
- **Individual user model retraining**
- **Training status monitoring**
- **Automatic model persistence**

## Technical Implementation

### Backend Changes

#### New Files:
- `app/ml_models.py` - Core ML functionality
- `test_ml_integration.py` - Integration testing script

#### Updated Files:
- `requirements.txt` - Added ML dependencies (pandas, xgboost, joblib)
- `app/schemas/schemas.py` - Added new data models
- `app/routes/routes.py` - Added ML endpoints

#### New Dependencies:
```
pandas==2.0.3
xgboost==2.0.3
joblib==1.3.2
```

### Frontend Changes

#### Updated Files:
- `frontend2/src/pages/Groceries.tsx` - Real data integration
- `frontend2/src/pages/Dashboard.tsx` - Admin tools
- `frontend2/src/services/api.ts` - New API endpoints

### API Endpoints

#### New Endpoints:
- `POST /user/grocery-suggestions` - Get AI-powered grocery suggestions
- `POST /admin/train-models` - Train models for all users
- `POST /user/retrain-model` - Retrain model for specific user

## ML Model Details

### XGBoost Configuration
- **Algorithm**: XGBClassifier
- **Evaluation Metric**: logloss
- **Features**: Previous week consumption pattern
- **Target**: Next week consumption prediction

### Training Process
1. **Data Collection**: User consumption history from `food_status_log`
2. **Feature Engineering**: Weekly consumption patterns, previous week indicators
3. **Model Training**: XGBoost classifier with consumption data
4. **Persistence**: Models saved as `.joblib` files in `aimodels/` directory

### Prediction Logic
1. **Model Loading**: Load user-specific trained model
2. **Feature Extraction**: Analyze recent consumption patterns
3. **Prediction**: Generate confidence scores for each inventory item
4. **Filtering**: Remove items already in current inventory
5. **Ranking**: Sort by confidence score and priority

## Usage Instructions

### For Users:
1. **Consume Items**: Mark items as consumed in your inventory
2. **View Suggestions**: Check the Groceries tab for AI recommendations
3. **Get Recipes**: Use the Recipes tab for inventory-based suggestions

### For Administrators:
1. **Train Models**: Use the Admin Tools section in Dashboard
2. **Monitor Training**: Check training status and results
3. **Retrain Individual Models**: Retrain specific user models

### For Developers:
1. **Install Dependencies**: `pip install -r requirements.txt`
2. **Test Integration**: Run `python test_ml_integration.py`
3. **Monitor Logs**: Check console for ML training progress

## Data Requirements

### For Effective Predictions:
- **Minimum Data**: At least 4 weeks of consumption history
- **Consumption Logging**: Regular marking of items as consumed
- **Inventory Updates**: Accurate inventory management

### Fallback Behavior:
- **No Model**: Uses frequency-based heuristics
- **Insufficient Data**: Provides basic recommendations
- **API Errors**: Graceful degradation with empty suggestions

## File Structure

```
app/
├── ml_models.py              # Core ML functionality
├── routes/routes.py          # API endpoints
├── schemas/schemas.py        # Data models
└── models/models.py          # Database models

frontend2/src/
├── pages/
│   ├── Groceries.tsx         # Grocery suggestions UI
│   ├── Recipes.tsx           # Recipe suggestions UI
│   └── Dashboard.tsx         # Admin tools
└── services/api.ts           # API service

aimodels/                     # Trained model storage
├── user_1.joblib
├── user_2.joblib
└── ...
```

## Performance Considerations

### Model Training:
- **Batch Processing**: Trains all user models in sequence
- **Error Handling**: Continues training even if individual models fail
- **Storage**: Models stored as compressed joblib files

### Prediction:
- **Caching**: Models loaded once per request
- **Fallback**: Graceful degradation when models unavailable
- **Filtering**: Efficient inventory filtering

## Troubleshooting

### Common Issues:
1. **No Suggestions**: Ensure consumption data exists
2. **Training Failures**: Check database connectivity
3. **API Errors**: Verify Spoonacular API key for recipes

### Debug Steps:
1. Run `test_ml_integration.py` to verify functionality
2. Check console logs for error messages
3. Verify database has consumption data
4. Ensure all dependencies are installed

## Future Enhancements

### Potential Improvements:
1. **Advanced Features**: Seasonal patterns, dietary preferences
2. **Real-time Updates**: Automatic model retraining
3. **A/B Testing**: Compare different ML approaches
4. **Analytics**: User behavior insights and recommendations

### Scalability:
1. **Model Optimization**: Reduce model size and training time
2. **Caching**: Implement model caching for better performance
3. **Batch Processing**: Async model training for large user bases

## Conclusion

The ML integration significantly enhances the AI Food Tracker by providing intelligent grocery suggestions and improved recipe recommendations. The system is designed to be robust, user-friendly, and easily maintainable while providing real value to users in managing their food inventory and reducing waste.
