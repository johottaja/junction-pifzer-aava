"""
Retrain user-specific model from Flask request data.
Takes a list of dictionaries (all user's historical responses) and retrains model.
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder
from config import (
    USER_ID_COL, MIGRAINE_COL, AGE_COL, GENDER_COL, DATE_COL,
    SURVEY_FEATURES, EXCLUDE_COLS
)

MODELS_DIR = "models"
USER_MODELS_DIR = "models/user_models"
BASE_TRAINING_DATA_PATH = "pretrain_data/survey_data.xlsx"
MIN_USER_SAMPLES = 10

def load_base_model():
    """Load the base trained model structure."""
    model_path = f"{MODELS_DIR}/best_model.pkl"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Base model not found at {model_path}. Please run train_base_model.py first."
        )
    
    return joblib.load(model_path)

def create_user_features(df, train_mask=None):
    """Create user-specific aggregated features from survey responses."""
    if train_mask is not None:
        train_df = df[train_mask].copy()
    else:
        train_df = df.copy()
    
    available_features = [f for f in SURVEY_FEATURES if f in train_df.columns]
    
    if available_features:
        agg_dict = {feat: ['mean', 'std'] for feat in available_features}
        user_stats = train_df.groupby(USER_ID_COL).agg(agg_dict).reset_index()
        
        new_cols = [USER_ID_COL]
        for feat in available_features:
            new_cols.extend([f'user_{feat}_mean', f'user_{feat}_std'])
        user_stats.columns = new_cols
    else:
        user_stats = pd.DataFrame({USER_ID_COL: train_df[USER_ID_COL].unique()})
    
    df = df.merge(user_stats, on=USER_ID_COL, how='left')
    
    user_feature_cols = [col for col in df.columns if col.startswith('user_')]
    for col in user_feature_cols:
        df[col] = df[col].fillna(0)
    
    return df

def prepare_features_for_training(df, feature_names, le_gender):
    """Prepare features in the same way as training."""
    # Handle gender encoding if present (optional - may come from user profile)
    if GENDER_COL in df.columns and 'gender_encoded' not in df.columns and le_gender is not None:
        df['gender_encoded'] = le_gender.transform(df[GENDER_COL])
    
    # Exclude age/gender if they're in the data (they come from user profile, not survey)
    exclude_all = EXCLUDE_COLS.copy()
    if AGE_COL in df.columns:
        exclude_all.append(AGE_COL)
    if GENDER_COL in df.columns and 'gender_encoded' not in df.columns:
        exclude_all.append(GENDER_COL)
    
    base_features = [col for col in df.columns if col not in exclude_all]
    base_features = [col for col in base_features if not col.startswith('user_')]
    
    df = create_user_features(df)
    
    X = pd.DataFrame()
    for feat in feature_names:
        if feat in df.columns:
            X[feat] = df[feat]
        else:
            X[feat] = 0
    
    X = X[feature_names]
    X = X.fillna(0)
    
    return X

def retrain_user_model(user_id, user_data_list, base_training_data_path=None):
    """
    Retrain model for a user from Flask request data.
    
    Args:
        user_id: User identifier (string)
        user_data_list: List of dictionaries, each representing a survey response
        base_training_data_path: Optional path to base training data
    
    Returns:
        dict: {
            'success': bool,
            'message': str,
            'model_path': str (if successful),
            'n_user_samples': int
        }
    """
    try:
        user_df = pd.DataFrame(user_data_list)
        
        if MIGRAINE_COL not in user_df.columns:
            return {
                'success': False,
                'message': f"Missing '{MIGRAINE_COL}' column in user data",
                'n_user_samples': len(user_df)
            }
        
        if len(user_df) < MIN_USER_SAMPLES:
            return {
                'success': False,
                'message': f"Need at least {MIN_USER_SAMPLES} samples, got {len(user_df)}",
                'n_user_samples': len(user_df)
            }
        
        # Validate required columns
        if USER_ID_COL not in user_df.columns:
            user_df[USER_ID_COL] = user_id
        elif user_df[USER_ID_COL].iloc[0] != user_id:
            # Ensure consistency
            user_df[USER_ID_COL] = user_id
        
        print(f"Retraining model for user {user_id} with {len(user_df)} samples...")
        
        base_model_data = load_base_model()
        base_model = base_model_data['model']
        feature_names = base_model_data['feature_names']
        le_gender = base_model_data.get('label_encoder_gender', None)
        
        if base_training_data_path is None:
            base_training_data_path = BASE_TRAINING_DATA_PATH
        
        base_data = pd.read_excel(base_training_data_path)
        base_data['target'] = base_data[MIGRAINE_COL].astype(int)
        
        user_df['target'] = user_df[MIGRAINE_COL].astype(int)
        combined_data = pd.concat([base_data, user_df], ignore_index=True)
        
        X = prepare_features_for_training(combined_data, feature_names, le_gender)
        y = combined_data['target'].copy()
        
        print(f"  Combined dataset: {len(X)} samples ({len(base_data)} base + {len(user_df)} user)")
        
        adapted_model = LogisticRegression(
            class_weight='balanced',
            max_iter=1000,
            random_state=42,
            n_jobs=-1
        )
        
        adapted_model.fit(X, y)
        
        os.makedirs(USER_MODELS_DIR, exist_ok=True)
        user_model_data = {
            'model': adapted_model,
            'feature_names': feature_names,
            'label_encoder_gender': le_gender,
            'model_name': 'LogisticRegression',
            'user_id': user_id,
            'n_user_samples': len(user_df),
            'n_total_samples': len(X)
        }
        
        user_model_path = f"{USER_MODELS_DIR}/user_{user_id}_model.pkl"
        joblib.dump(user_model_data, user_model_path)
        
        print(f"  ✅ User model saved to {user_model_path}")
        
        return {
            'success': True,
            'message': f"Model retrained successfully with {len(user_df)} user samples",
            'model_path': user_model_path,
            'n_user_samples': len(user_df),
            'n_total_samples': len(X)
        }
        
    except Exception as e:
        return {
            'success': False,
            'message': f"Error during retraining: {str(e)}",
            'n_user_samples': len(user_df) if 'user_df' in locals() else 0
        }

def has_user_model(user_id):
    """Check if user has an adapted model."""
    user_model_path = f"{USER_MODELS_DIR}/user_{user_id}_model.pkl"
    return os.path.exists(user_model_path)

def load_user_model(user_id):
    """Load user-specific model if it exists."""
    user_model_path = f"{USER_MODELS_DIR}/user_{user_id}_model.pkl"
    if not os.path.exists(user_model_path):
        raise FileNotFoundError(f"User model not found for {user_id}")
    return joblib.load(user_model_path)
