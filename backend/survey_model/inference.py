"""
Inference script: takes 7 days of survey logs with user info and returns migraine probability.
Includes interpretability - shows top 5 features contributing to each prediction.
"""
import pandas as pd
import numpy as np
import joblib
import os

MODEL_PATH = "models/best_model.pkl"

def load_model(user_id=None):
    """
    Load model - user-specific if available, otherwise base model.
    
    Args:
        user_id: User identifier. If provided, checks for user-specific model.
    
    Returns:
        Tuple: (model, feature_names, label_encoder_sex)
    """
    # Try to load user-specific model first
    if user_id:
        from retrain_user_model import has_user_model, load_user_model
        if has_user_model(user_id):
            user_model_data = load_user_model(user_id)
            print(f"Using user-specific model for {user_id}")
            return (
                user_model_data['model'],
                user_model_data.get('feature_names', None),
                user_model_data.get('label_encoder_sex', None)
            )
    
    # Fall back to base model
    if os.path.exists(MODEL_PATH):
        model_data = joblib.load(MODEL_PATH)
        if isinstance(model_data, dict):
            return (
                model_data['model'], 
                model_data.get('feature_names', None),
                model_data.get('label_encoder_sex', None)
            )
        else:
            return model_data, None, None
    
    raise FileNotFoundError(
        f"Model not found at {MODEL_PATH}. Please run compare_models.py or train_base_model.py first."
    )

def create_user_features(logs_df, user_id, exclude_last=True):
    """
    Create user-specific aggregated features from historical logs.
    Uses survey response patterns, not Frequency.
    Excludes the last day to avoid data leakage.
    """
    user_data = logs_df[logs_df['Unique ID'] == user_id] if 'Unique ID' in logs_df.columns else logs_df
    
    # Exclude last day for user stats (to avoid leakage)
    if exclude_last and len(user_data) > 1:
        historical_data = user_data.iloc[:-1]
    else:
        historical_data = user_data
    
    # Calculate user's typical survey response patterns
    survey_features = [
        'Stress', 'Sleep deprivation', 'Exercise', 'Physical fatigue',
        'Weather/temperature change', 'Noise', 'Excess caffeinated drinks',
        'Oversleeping', 'Extreme emotional changes'
    ]
    
    available_features = [f for f in survey_features if f in historical_data.columns]
    
    user_features = {}
    for feat in available_features:
        if len(historical_data) > 0:
            user_features[f'user_{feat}_mean'] = historical_data[feat].mean()
            user_features[f'user_{feat}_std'] = historical_data[feat].std() if len(historical_data) > 1 else 0
        else:
            user_features[f'user_{feat}_mean'] = 0
            user_features[f'user_{feat}_std'] = 0
    
    return user_features

def prepare_features(logs_df, user_id, age, sex, feature_names, le_sex):
    """
    Prepare features from 7 days of survey logs with personalization.
    
    Args:
        logs_df: DataFrame with survey data for 7 days
        user_id: User identifier
        age: User's age
        sex: User's sex (string: 'male' or 'female')
        feature_names: List of feature names in the order expected by the model
        le_sex: LabelEncoder for Sex
    
    Returns:
        DataFrame with features ready for prediction
    """
    # Use the most recent day's data (last row)
    if len(logs_df) == 0:
        raise ValueError("logs_df is empty")
    
    # Get most recent day
    latest_day = logs_df.iloc[-1:].copy()
    
    # Create user-specific features
    user_features = create_user_features(logs_df, user_id)
    
    # Prepare feature dictionary
    features_dict = {}
    
    # Add Age
    features_dict['Age'] = age
    
    # Add Sex (encoded)
    if le_sex is not None:
        try:
            features_dict['Sex_encoded'] = le_sex.transform([sex])[0]
        except:
            # Fallback: use most common encoding
            features_dict['Sex_encoded'] = 0
    else:
        features_dict['Sex_encoded'] = 0 if sex.lower() == 'male' else 1
    
    # Add user-specific features
    features_dict.update(user_features)
    
    # Add survey features from latest day
    exclude_cols = ['Unique ID', 'Date', 'Frequency', 'Migraine', 'target', 'Sex', 'Age']
    # Also exclude user_* columns that might be in latest_day
    exclude_cols.extend([col for col in latest_day.columns if col.startswith('user_')])
    
    for col in latest_day.columns:
        if col not in exclude_cols:
            features_dict[col] = latest_day[col].iloc[0] if col in latest_day.columns else 0
    
    # Create DataFrame
    features_df = pd.DataFrame([features_dict])
    
    # Ensure all required features exist
    if feature_names:
        missing = set(feature_names) - set(features_df.columns)
        if missing:
            # Fill missing features with 0
            for feat in missing:
                features_df[feat] = 0
        
        # Reorder to match training
        features_df = features_df[feature_names]
    
    # Handle missing values
    features_df = features_df.fillna(0)
    
    return features_df

def get_top_features_contribution(model, features_df, feature_names, top_k=5):
    """
    Calculate top K features contributing to this prediction.
    Handles both RandomForest (feature_importances_) and LogisticRegression (coefficients).
    
    Args:
        model: Trained model (RandomForest or LogisticRegression)
        features_df: Single row DataFrame with features
        feature_names: List of feature names
        top_k: Number of top features to return
    
    Returns:
        List of tuples: (feature_name, contribution_score, feature_value)
    """
    # Get feature values for this prediction
    feature_values = features_df.iloc[0].values
    
    # Get global importance based on model type
    if hasattr(model, 'feature_importances_'):
        # RandomForest: use feature importances
        global_importance = model.feature_importances_
    elif hasattr(model, 'coef_'):
        # LogisticRegression: use absolute coefficients as importance
        # For binary classification, coef_ is shape (1, n_features)
        coef = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
        # Normalize coefficients to 0-1 range for consistency
        coef_abs = np.abs(coef)
        global_importance = coef_abs / (coef_abs.max() + 1e-10) if coef_abs.max() > 0 else coef_abs
    else:
        # Fallback: equal importance
        global_importance = np.ones(len(feature_names))
    
    # Calculate local contribution score
    # Score = global_importance * abs(feature_value)
    # This highlights features that are both important globally and have non-zero values
    contributions = []
    for i, feat_name in enumerate(feature_names):
        global_imp = global_importance[i]
        local_val = feature_values[i]
        
        # Contribution score: importance weighted by absolute value
        # For binary features (0/1), this works well
        # For continuous, we use absolute value
        contribution_score = global_imp * abs(local_val)
        
        contributions.append((feat_name, contribution_score, local_val))
    
    # Sort by contribution score
    contributions.sort(key=lambda x: x[1], reverse=True)
    
    return contributions[:top_k]

def predict_migraine_probability(logs_df, user_id, age, sex, return_interpretation=False):
    """
    Predict migraine probability for today based on 7 days of logs with personalization.
    Uses user-specific model if available, otherwise uses base model.
    
    Args:
        logs_df: DataFrame with 7 days of survey data
        user_id: User identifier (string)
        age: User's age (int)
        sex: User's sex (string: 'male' or 'female')
        return_interpretation: If True, also return top contributing features
    
    Returns:
        float: Probability of migraine (0-1)
        OR tuple: (probability, top_features) if return_interpretation=True
    """
    model, feature_names, le_sex = load_model(user_id=user_id)
    
    # Prepare features with personalization
    features = prepare_features(logs_df, user_id, age, sex, feature_names, le_sex)
    
    # Predict probability
    probability = model.predict_proba(features)[0, 1]
    
    if return_interpretation:
        top_features = get_top_features_contribution(model, features, feature_names, top_k=5)
        return float(probability), top_features
    else:
        return float(probability)

def predict_from_dict(logs_list, user_id, age, sex, return_interpretation=False):
    """
    Convenience function: predict from list of daily log dictionaries.
    FastAPI/Flask ready - accepts list of dicts directly.
    
    Args:
        logs_list: List of 7 dictionaries, each representing one day's survey data
        user_id: User identifier
        age: User's age
        sex: User's sex
        return_interpretation: If True, also return top contributing features
    
    Returns:
        float: Probability of migraine (0-1)
        OR tuple: (probability, top_features) if return_interpretation=True
    """
    logs_df = pd.DataFrame(logs_list)
    # Ensure user_id is in the dataframe
    if 'Unique ID' not in logs_df.columns:
        logs_df['Unique ID'] = user_id
    return predict_migraine_probability(logs_df, user_id, age, sex, return_interpretation)

def predict_fastapi_format(logs_list, user_id, age, sex):
    """
    FastAPI-ready prediction function.
    Accepts list of dicts and returns JSON-serializable response.
    
    Args:
        logs_list: List of 7 dictionaries (previous days' survey responses)
        user_id: User identifier (string)
        age: User's age (int)
        sex: User's sex (string: 'male' or 'female')
    
    Returns:
        dict: {
            'probability': float (0-1),
            'top_features': [
                {
                    'feature': str,
                    'value': float,
                    'contribution': float
                },
                ...
            ]
        }
    """
    probability, top_features = predict_from_dict(
        logs_list, user_id, age, sex, return_interpretation=True
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

def format_interpretation(probability, top_features):
    """
    Format interpretation results for display.
    
    Args:
        probability: Predicted probability
        top_features: List of (feature_name, contribution_score, feature_value) tuples
    
    Returns:
        Formatted string
    """
    result = f"Predicted Migraine Probability: {probability:.3f}\n\n"
    result += "Top 5 Contributing Features:\n"
    result += "-" * 60 + "\n"
    
    for i, (feat_name, contrib_score, feat_value) in enumerate(top_features, 1):
        # Format feature value
        if isinstance(feat_value, (int, float)):
            if feat_value == int(feat_value):
                value_str = str(int(feat_value))
            else:
                value_str = f"{feat_value:.2f}"
        else:
            value_str = str(feat_value)
        
        result += f"{i}. {feat_name:35s} | Value: {value_str:8s} | Contribution: {contrib_score:.4f}\n"
    
    return result

if __name__ == "__main__":
    # Example usage
    print("=== Example: Predicting from sample data ===\n")
    
    # Load some sample data for testing
    try:
        print("Loading data...")
        data_path = "pretrain_data/survey_data.xlsx"
        df = pd.read_excel(data_path)
        
        print("Preparing user data...")
        # Get last 7 days for a user
        user_id = df['Unique ID'].iloc[0]
        user_data = df[df['Unique ID'] == user_id].tail(7)
        age = user_data['Age'].iloc[0]
        sex = user_data['Sex'].iloc[0]
        
        print(f"User: {user_id} (Age: {age}, Sex: {sex})\n")
        
        print("Predicting (simple)...")
        # First test without interpretation
        probability = predict_migraine_probability(
            user_data, user_id, age, sex, return_interpretation=False
        )
        print(f"Probability: {probability:.3f}\n")
        
        print("Predicting (with interpretation)...")
        # Then test with interpretation
        probability, top_features = predict_migraine_probability(
            user_data, user_id, age, sex, return_interpretation=True
        )
        
        # Display results
        print(format_interpretation(probability, top_features))
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        print("\nMake sure to:")
        print("1. Run train_base_model.py first")
        print("2. Provide logs_df with matching feature columns")
        print("3. Provide user_id, age, and sex for personalization")
