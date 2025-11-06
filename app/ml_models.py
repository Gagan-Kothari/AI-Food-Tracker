import pandas as pd # type: ignore
import joblib # type: ignore
from xgboost import XGBClassifier # type: ignore
from sqlalchemy import text # type: ignore
from datetime import datetime, timedelta
from app.database import engine
import os
from typing import Dict, List, Tuple, Optional

def train_all_user_models():
    """
    Train XGBoost models for all users based on their consumption patterns.
    Returns training status for each user.
    """
    conn = engine.connect()
    user_ids = pd.read_sql("SELECT DISTINCT u_id FROM inventory", conn)['u_id'].tolist()
    os.makedirs("aimodels", exist_ok=True)

    training_status = {}

    for user_id in user_ids:
        query = f"""
        SELECT
            fsl.timestamp::date AS consumption_date,
            i.f_id,
            fi.f_name
        FROM food_status_log fsl
        JOIN inventory i ON fsl.inventory_id = i.id
        JOIN food_items fi ON i.f_id = fi.f_id
        WHERE i.u_id = {user_id} AND fsl.status = 'consumed'
        """
        df = pd.read_sql(query, conn)

        if df.empty:
            training_status[user_id] = "No consumption data"
            continue

        df['consumption_date'] = pd.to_datetime(df['consumption_date'], errors='coerce')
        df = df.dropna(subset=['consumption_date'])

        if df.empty:
            training_status[user_id] = "All dates invalid/missing"
            continue

        df['week'] = df['consumption_date'].dt.to_period('W').apply(lambda r: r.start_time)
        df['consumed'] = 1

        weekly = df.groupby(['week', 'f_id']).agg({'consumed': 'sum'}).reset_index()

        start_week = weekly['week'].min()
        end_week = datetime.now() + timedelta(weeks=1)
        all_weeks = pd.date_range(start=start_week, end=end_week, freq='W-MON')
        all_fids = df['f_id'].unique()
        grid = pd.MultiIndex.from_product([all_weeks, all_fids], names=['week', 'f_id']).to_frame(index=False)

        merged = pd.merge(grid, weekly, how='left').fillna(0)
        merged['consumed'] = (merged['consumed'] > 0).astype(int)

        merged = merged.sort_values(['f_id', 'week'])
        merged['prev_week'] = merged.groupby('f_id')['consumed'].shift(1).fillna(0)

        X = merged[['prev_week']]
        y = merged['consumed']

        if len(y.unique()) == 0:
            training_status[user_id] = "No valid labels to train"
            continue

        if len(y.unique()) == 1:
            dummy = pd.DataFrame({'prev_week': [1], 'consumed': [0 if y.iloc[0] == 1 else 1]})
            X = pd.concat([X, dummy[['prev_week']]], ignore_index=True)
            y = pd.concat([y, dummy['consumed']], ignore_index=True)
            msg = "Trained with dummy data"
        else:
            msg = "Trained"

        model = XGBClassifier(eval_metric='logloss')
        model.fit(X, y)

        model_path = f"aimodels/user_{user_id}.joblib"
        joblib.dump(model, model_path)

        training_status[user_id] = msg + f" → Saved at {model_path}"

    conn.close()
    return training_status

def predict_user_grocery_needs(user_id: int) -> List[Dict]:
    """
    Predict grocery needs for a specific user based on their consumption patterns.
    Returns list of recommended items with confidence scores.
    """
    conn = engine.connect()
    
    # Get user's inventory items
    inventory_query = f"""
    SELECT DISTINCT i.f_id, fi.f_name, fi.category
    FROM inventory i
    JOIN food_items fi ON i.f_id = fi.f_id
    WHERE i.u_id = {user_id}
    """
    inventory_df = pd.read_sql(inventory_query, conn)
    
    if inventory_df.empty:
        conn.close()
        return []
    
    # Get consumption history for prediction
    consumption_query = f"""
    SELECT
        fsl.timestamp::date AS consumption_date,
        i.f_id,
        fi.f_name
    FROM food_status_log fsl
    JOIN inventory i ON fsl.inventory_id = i.id
    JOIN food_items fi ON i.f_id = fi.f_id
    WHERE i.u_id = {user_id} AND fsl.status = 'consumed'
    ORDER BY fsl.timestamp DESC
    LIMIT 100
    """
    consumption_df = pd.read_sql(consumption_query, conn)
    conn.close()
    
    if consumption_df.empty:
        return []
    
    # Process consumption data
    consumption_df['consumption_date'] = pd.to_datetime(consumption_df['consumption_date'], errors='coerce')
    consumption_df = consumption_df.dropna(subset=['consumption_date'])
    
    if consumption_df.empty:
        return []
    
    # Get recent consumption (last 4 weeks)
    recent_date = datetime.now() - timedelta(weeks=4)
    recent_consumption = consumption_df[consumption_df['consumption_date'] >= recent_date]
    
    # Calculate consumption frequency for each item
    item_consumption = recent_consumption.groupby('f_id').size().reset_index(name='consumption_count')
    
    # Load user's model if it exists
    model_path = f"aimodels/user_{user_id}.joblib"
    if not os.path.exists(model_path):
        # If no model exists, use simple frequency-based prediction
        recommendations = []
        for _, item in inventory_df.iterrows():
            consumption_count = item_consumption[item_consumption['f_id'] == item['f_id']]['consumption_count'].iloc[0] if not item_consumption[item_consumption['f_id'] == item['f_id']].empty else 0
            
            # Simple heuristic: if consumed in last 4 weeks, likely to need again
            if consumption_count > 0:
                confidence = min(consumption_count / 4.0, 1.0)  # Normalize to 0-1
                recommendations.append({
                    'f_id': int(item['f_id']),
                    'name': str(item['f_name']),
                    'category': str(item['category']),
                    'confidence': float(confidence),
                    'reason': f"Consumed {int(consumption_count)} times in last 4 weeks"
                })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
    
    try:
        model = joblib.load(model_path)
        
        recommendations = []
        for _, item in inventory_df.iterrows():
            # Check if item was consumed last week
            last_week = datetime.now() - timedelta(weeks=1)
            was_consumed_last_week = not consumption_df[
                (consumption_df['f_id'] == item['f_id']) & 
                (consumption_df['consumption_date'] >= last_week)
            ].empty
            
            # Predict for next week
            X_pred = pd.DataFrame({'prev_week': [1 if was_consumed_last_week else 0]})
            prediction = model.predict(X_pred)[0]
            confidence = model.predict_proba(X_pred)[0][1]  # Probability of needing the item
            
            if prediction == 1 or confidence > 0.3:  # Threshold for recommendation
                recommendations.append({
                    'f_id': int(item['f_id']),
                    'name': str(item['f_name']),
                    'category': str(item['category']),
                    'confidence': float(confidence),
                    'reason': f"Based on consumption pattern (confidence: {float(confidence):.2f})"
                })
        
        return sorted(recommendations, key=lambda x: x['confidence'], reverse=True)
        
    except Exception as e:
        print(f"Error loading model for user {user_id}: {e}")
        return []

def get_grocery_suggestions(user_id: int) -> List[Dict]:
    """
    Get comprehensive grocery suggestions for a user.
    Combines ML predictions with inventory analysis.
    """
    try:
        # Get ML predictions
        ml_predictions = predict_user_grocery_needs(user_id)
        
        # Get current inventory to avoid suggesting items already in stock
        conn = engine.connect()
        current_inventory_query = f"""
        SELECT i.f_id, fi.f_name, fi.category, i.expiry_date
        FROM inventory i
        JOIN food_items fi ON i.f_id = fi.f_id
        WHERE i.u_id = {user_id} AND i.expiry_date > NOW()
        """
        current_inventory = pd.read_sql(current_inventory_query, conn)
        conn.close()
        
        current_item_ids = set(current_inventory['f_id'].tolist())
        
        # Filter out items already in inventory
        suggestions = []
        for pred in ml_predictions:
            if pred['f_id'] not in current_item_ids:
                # Determine priority based on confidence
                confidence = float(pred['confidence'])
                if confidence > 0.7:
                    priority = "high"
                elif confidence > 0.4:
                    priority = "medium"
                else:
                    priority = "low"
                
                suggestions.append({
                    'id': int(pred['f_id']),
                    'name': str(pred['name']),
                    'category': str(pred['category']),
                    'suggested': True,
                    'quantity': 1,
                    'unit': 'item',
                    'priority': str(priority),
                    'reason': str(pred['reason']),
                    'confidence': confidence
                })
        
        return suggestions
        
    except Exception as e:
        print(f"Error in get_grocery_suggestions for user {user_id}: {e}")
        return []

def retrain_user_model(user_id: int) -> Dict:
    """
    Retrain model for a specific user.
    """
    conn = engine.connect()
    
    # Check if user has consumption data
    consumption_check = f"""
    SELECT COUNT(*) as count
    FROM food_status_log fsl
    JOIN inventory i ON fsl.inventory_id = i.id
    WHERE i.u_id = {user_id} AND fsl.status = 'consumed'
    """
    result = pd.read_sql(consumption_check, conn)
    conn.close()
    
    if result['count'].iloc[0] == 0:
        return {"success": False, "message": "No consumption data available for training"}
    
    # Train model for this user
    training_status = train_all_user_models()
    
    if user_id in training_status:
        return {"success": True, "message": training_status[user_id]}
    else:
        return {"success": False, "message": "Failed to train model"}
