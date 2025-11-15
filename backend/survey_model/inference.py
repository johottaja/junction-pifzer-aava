"""
Inference script: takes 7 days of survey logs and returns migraine probability.
Uses config.py for column names. Prioritizes current day and previous day.
Supports JSON input from Supabase API.
"""
import pandas as pd
import numpy as np
import joblib
import os
import json
from datetime import datetime
from config import (
    USER_ID_COL, MIGRAINE_COL, AGE_COL, GENDER_COL, DATE_COL,
    SURVEY_FEATURES, EXCLUDE_COLS
)

MODEL_PATH = "models/best_model.pkl"

def load_model(user_id=None):
    """Load model - user-specific if available, otherwise base model."""
    if user_id:
        from retrain_user_model import has_user_model, load_user_model
        if has_user_model(user_id):
            user_model_data = load_user_model(user_id)
            print(f"Using user-specific model for {user_id}")
            return (
                user_model_data['model'],
                user_model_data.get('feature_names', None),
                user_model_data.get('label_encoder_gender', None)
            )
    
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)
        if isinstance(model_data, dict):
            return (
                model_data['model'],
                model_data.get('feature_names', None),
                model_data.get('label_encoder_gender', None)
            )
        else:
            return model_data, None, None
    
    raise FileNotFoundError(
        f"Model not found at {MODEL_PATH}. Please run train_base_model.py first."
    )

def create_user_features(logs_df, user_id, exclude_last=True):
    """Create user-specific aggregated features from historical logs."""
    if USER_ID_COL not in logs_df.columns:
        raise ValueError(f"'{USER_ID_COL}' column not found. Update config.py to match your data.")
    user_data = logs_df[logs_df[USER_ID_COL] == user_id]
    
    if exclude_last and len(user_data) > 1:
        historical_data = user_data.iloc[:-1]
    else:
        historical_data = user_data
    
    # Use survey features from config
    available_features = [f for f in SURVEY_FEATURES if f in historical_data.columns]
    
    user_features = {}
    for feat in available_features:
        if len(historical_data) > 0:
            user_features[f'user_{feat}_mean'] = historical_data[feat].mean()
            user_features[f'user_{feat}_std'] = historical_data[feat].std() if len(historical_data) > 1 else 0
        else:
            user_features[f'user_{feat}_mean'] = 0
            user_features[f'user_{feat}_std'] = 0
    
    return user_features

def prepare_features(logs_df, user_id, age, gender, feature_names, le_gender):
    """
    Prepare features from 7 days of survey logs with personalization.
    Prioritizes current day (60%) and previous day (40%).
    """
    if len(logs_df) == 0:
        raise ValueError("logs_df is empty")
    
    # Sort by created_at if available (for proper day prioritization)
    if DATE_COL in logs_df.columns:
        logs_df = logs_df.sort_values(DATE_COL).reset_index(drop=True)
    
    # Ensure exactly 7 days (most recent last)
    logs_df = logs_df.tail(7).reset_index(drop=True)
    
    # Get current day (day 7) and previous day (day 6)
    current_day = logs_df.iloc[-1:].copy()
    previous_day = logs_df.iloc[-2:-1].copy() if len(logs_df) > 1 else current_day
    
    # Create user-specific features (from days 1-6, excluding current day)
    user_features = create_user_features(logs_df, user_id)
    
    features_dict = {}
    
    # Add Age (if model expects it - may not be in Supabase survey table)
    if AGE_COL in feature_names:
        features_dict[AGE_COL] = age if age is not None else 0
    
    # Add Gender (encoded) - if model expects it
    if 'gender_encoded' in feature_names:
        if le_gender is not None:
            try:
                features_dict['gender_encoded'] = le_gender.transform([gender])[0] if gender else 0
            except:
                features_dict['gender_encoded'] = 0
        else:
            features_dict['gender_encoded'] = 0 if (gender and gender.lower() == 'male') else 1
    
    # Add user-specific features
    features_dict.update(user_features)
    
    # Add survey features with day prioritization
    # Current day gets 60% weight, previous day gets 40% weight
    exclude_cols = EXCLUDE_COLS + [col for col in logs_df.columns if col.startswith('user_')]
    # Only include survey features from config (Supabase boolean columns)
    survey_cols = [col for col in SURVEY_FEATURES if col in logs_df.columns]
    
    for col in survey_cols:
        current_val = current_day[col].iloc[0] if col in current_day.columns else 0
        prev_val = previous_day[col].iloc[0] if col in previous_day.columns and len(previous_day) > 0 else 0
        
        # Weighted: 60% current day, 40% previous day
        features_dict[col] = 0.6 * current_val + 0.4 * prev_val
    
    # Create DataFrame
    features_df = pd.DataFrame([features_dict])
    
    # Ensure all required features exist
    if feature_names:
        missing = set(feature_names) - set(features_df.columns)
        if missing:
            for feat in missing:
                features_df[feat] = 0
        features_df = features_df[feature_names]
    
    features_df = features_df.fillna(0)
    
    return features_df

def get_top_features_contribution(model, features_df, feature_names, top_k=5):
    """Calculate top K features contributing to this prediction."""
    feature_values = features_df.iloc[0].values
    
    # Get global importance based on model type
    if hasattr(model, 'feature_importances_'):
        # RandomForest: use feature importances
        global_importance = model.feature_importances_
        contributions = []
        for i, feat_name in enumerate(feature_names):
            global_imp = global_importance[i]
            local_val = feature_values[i]
            contribution_score = global_imp * abs(local_val)
            contributions.append((feat_name, contribution_score, local_val))
    elif hasattr(model, 'coef_'):
        # LogisticRegression: use actual coefficient * feature_value (contribution to log-odds)
        coef = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
        contributions = []
        for i, feat_name in enumerate(feature_names):
            coefficient = coef[i]
            local_val = feature_values[i]
            # Actual contribution to log-odds: coefficient * feature_value
            contribution_score = abs(coefficient * local_val)
            contributions.append((feat_name, contribution_score, local_val))
    else:
        # Fallback: use feature values as importance
        contributions = []
        for i, feat_name in enumerate(feature_names):
            local_val = feature_values[i]
            contribution_score = abs(local_val)
            contributions.append((feat_name, contribution_score, local_val))
    
    contributions.sort(key=lambda x: x[1], reverse=True)
    return contributions[:top_k]

def predict_migraine_probability(logs_df, user_id, age=None, gender=None, return_interpretation=False):
    """
    Predict migraine probability for today based on 7 days of logs.
    
    Args:
        logs_df: DataFrame with 7 days of survey data (must have DATE_COL for sorting)
        user_id: User identifier (string or int) - used for user-specific models
        age: User's age (int, optional - may come from user profile)
        gender: User's gender (string, optional - may come from user profile)
        return_interpretation: If True, also return top contributing features
    
    Returns:
        float: Probability of migraine (0-1)
        OR tuple: (probability, top_features) if return_interpretation=True
    """
    model, feature_names, le_gender = load_model(user_id=user_id)
    
    features = prepare_features(logs_df, user_id, age, gender, feature_names, le_gender)
    
    probability = model.predict_proba(features)[0, 1]
    
    if return_interpretation:
        top_features = get_top_features_contribution(model, features, feature_names, top_k=5)
        return float(probability), top_features
    else:
        return float(probability)

def predict_from_dict(logs_list, user_id, age=None, gender=None, return_interpretation=False):
    """
    Convenience function: predict from list of daily log dictionaries.
    FastAPI/Flask ready - accepts list of dicts directly.
    
    Args:
        logs_list: List of dicts, each representing a day's survey response
        user_id: User identifier (string or int)
        age: User's age (int, optional)
        gender: User's gender (string, optional)
        return_interpretation: If True, return top features
    
    Note: logs_list should be sorted by created_at (most recent last) for proper day weighting.
    """
    logs_df = pd.DataFrame(logs_list)
    
    # Ensure user_id column exists
    if USER_ID_COL not in logs_df.columns:
        logs_df[USER_ID_COL] = user_id
    
    # Sort by created_at if available (for day prioritization)
    if DATE_COL in logs_df.columns:
        logs_df = logs_df.sort_values(DATE_COL).reset_index(drop=True)
    
    return predict_migraine_probability(logs_df, user_id, age, gender, return_interpretation)

def predict_from_json(json_data, user_id=None, age=None, gender=None):
    """
    Predict from JSON input (Supabase API format).
    Accepts JSON string or dict/list and handles type conversions.
    
    Args:
        json_data: JSON string, dict, or list of dicts from Supabase API
        user_id: User identifier (int, optional - extracted from json_data if not provided)
        age: User's age (int, optional - from user profile or json_data)
        gender: User's gender (string, optional - from user profile or json_data)
    
    Returns:
        dict: FastAPI-ready JSON response with probability and top features
    """
    # Parse JSON if string
    if isinstance(json_data, str):
        data = json.loads(json_data)
    else:
        data = json_data
    
    # Handle different JSON structures
    if isinstance(data, dict):
        # Single record or wrapped structure
        if 'logs' in data or 'data' in data:
            logs_list = data.get('logs', data.get('data', []))
        elif isinstance(data.get('items'), list):
            logs_list = data['items']
        else:
            # Single record - wrap in list
            logs_list = [data]
    elif isinstance(data, list):
        logs_list = data
    else:
        raise ValueError(f"Invalid JSON format. Expected dict or list, got {type(data)}")
    
    if not logs_list or len(logs_list) == 0:
        raise ValueError("Empty logs list. Need at least 1 day of data.")
    
    # Extract user_id, age, gender from first record if not provided
    first_record = logs_list[0]
    if user_id is None:
        user_id = first_record.get(USER_ID_COL) or first_record.get('user_id')
        if user_id is None:
            raise ValueError(f"user_id not found in JSON data and not provided as parameter")
    
    if age is None:
        age = first_record.get(AGE_COL) or first_record.get('age')
    
    if gender is None:
        gender = first_record.get(GENDER_COL) or first_record.get('gender')
    
    # Convert JSON data to proper format
    converted_logs = []
    for record in logs_list:
        converted = {}
        
        # Convert boolean fields (Supabase returns true/false, we need 1/0)
        for key, value in record.items():
            if isinstance(value, bool):
                converted[key] = 1 if value else 0
            elif value is None:
                converted[key] = 0
            elif key == DATE_COL or key == 'created_at':
                # Handle date conversion if needed
                if isinstance(value, str):
                    # Try to parse date string, but keep as string if it fails
                    try:
                        # Try common formats
                        datetime.fromisoformat(value.replace('Z', '+00:00'))
                        converted[key] = value
                    except:
                        converted[key] = value
                else:
                    converted[key] = value
            else:
                converted[key] = value
        
        converted_logs.append(converted)
    
    # Ensure we have exactly 7 days (take last 7 if more)
    if len(converted_logs) > 7:
        converted_logs = converted_logs[-7:]
    
    # Use existing predict_from_dict function
    return predict_fastapi_format(converted_logs, user_id, age, gender)

def predict_fastapi_format(logs_list, user_id, age=None, gender=None):
    """
    FastAPI-ready prediction function.
    Accepts list of dicts and returns JSON-serializable response.
    
    Args:
        logs_list: List of dicts with survey responses (sorted by created_at, most recent last)
        user_id: User identifier (string or int)
        age: User's age (int, optional - from user profile)
        gender: User's gender (string, optional - from user profile)
    """
    probability, top_features = predict_from_dict(
        logs_list, user_id, age, gender, return_interpretation=True
    )
    
    return {
        'probability': float(probability),
        'top_features': [
            {
                'feature': str(feat),
                'value': float(val) if isinstance(val, (int, float, np.number)) else 0.0,
                'contribution': float(score)
            }
            for feat, score, val in top_features
        ]
    }

if __name__ == "__main__":
    print("=== Example: Predicting from sample data ===\n")
    
    try:
        print("Loading data...")
        data_path = "pretrain_data/survey_base_data.xlsx"
        df = pd.read_excel(data_path)
        
        print("Preparing user data...")
        user_id = df[USER_ID_COL].iloc[0]
        user_data = df[df[USER_ID_COL] == user_id].tail(7)
        age = user_data[AGE_COL].iloc[0] if AGE_COL in user_data.columns else None
        gender = user_data[GENDER_COL].iloc[0] if GENDER_COL in user_data.columns else None
        
        print(f"User: {user_id} (Age: {age}, Gender: {gender})\n")
        
        print("Predicting (simple)...")
        probability = predict_migraine_probability(
            user_data, user_id, age, gender, return_interpretation=False
        )
        print(f"Probability: {probability:.3f}\n")
        
        print("Predicting (with interpretation)...")
        probability, top_features = predict_migraine_probability(
            user_data, user_id, age, gender, return_interpretation=True
        )
        
        print(f"Predicted Migraine Probability: {probability:.3f}\n")
        print("Top 5 Contributing Features:")
        for i, (feat, score, val) in enumerate(top_features, 1):
            print(f"  {i}. {feat}: {val} (contribution: {score:.4f})")
        
        print("\n" + "=" * 60)
        print("Example: Predicting from JSON (Supabase format)")
        print("=" * 60)
        
        # Convert to JSON format (simulating Supabase API response)
        logs_json = user_data.to_dict('records')
        # Convert booleans to true/false for JSON
        for record in logs_json:
            for key, value in record.items():
                if isinstance(value, (int, float)) and key in SURVEY_FEATURES:
                    record[key] = bool(value)
        
        json_string = json.dumps(logs_json)
        print(f"\nJSON input (first 200 chars): {json_string[:200]}...")
        
        result = predict_from_json(json_string, user_id=user_id, age=age, gender=gender)
        print(f"\nResult from JSON:")
        print(f"  Probability: {result['probability']:.4f}")
        print(f"  Top feature: {result['top_features'][0]['feature']} (contribution: {result['top_features'][0]['contribution']:.4f})")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
