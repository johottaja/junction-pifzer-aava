"""
Retrain user-specific model from Flask request data.
Takes a list of dictionaries (all user's historical responses) and retrains model.
Designed for daily adaptation as new data comes in.
"""
import pandas as pd
import numpy as np
import joblib
import os
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder

MODELS_DIR = "models"
USER_MODELS_DIR = "models/user_models"
BASE_TRAINING_DATA_PATH = "pretrain_data/survey_data.xlsx"
MIN_USER_SAMPLES = 10  # Lower threshold for daily adaptation

def load_base_model():
    """Load the base trained model structure."""
    model_path = f"{MODELS_DIR}/best_model.pkl"
    
    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Base model not found at {model_path}. Please run compare_models.py or train_base_model.py first."
        )
    
    return joblib.load(model_path)

def create_user_features(df, train_mask=None):
    """Create user-specific aggregated features from survey responses."""
    if train_mask is not None:
        train_df = df[train_mask].copy()
    else:
        train_df = df.copy()
    
    survey_features = [
        'Stress', 'Sleep deprivation', 'Exercise', 'Physical fatigue',
        'Weather/temperature change', 'Noise', 'Excess caffeinated drinks',
        'Oversleeping', 'Extreme emotional changes'
    ]
    
    available_features = [f for f in survey_features if f in train_df.columns]
    
    if available_features:
        agg_dict = {feat: ['mean', 'std'] for feat in available_features}
        user_stats = train_df.groupby('Unique ID').agg(agg_dict).reset_index()
        
        new_cols = ['Unique ID']
        for feat in available_features:
            new_cols.extend([f'user_{feat}_mean', f'user_{feat}_std'])
        user_stats.columns = new_cols
    else:
        user_stats = pd.DataFrame({'Unique ID': train_df['Unique ID'].unique()})
    
    df = df.merge(user_stats, on='Unique ID', how='left')
    
    user_feature_cols = [col for col in df.columns if col.startswith('user_')]
    for col in user_feature_cols:
        df[col] = df[col].fillna(0)
    
    return df

def prepare_features_for_training(df, feature_names, le_sex):
    """Prepare features in the same way as training."""
    if 'Sex_encoded' not in df.columns and 'Sex' in df.columns:
        df['Sex_encoded'] = le_sex.transform(df['Sex'])
    
    exclude_cols = ['Unique ID', 'Date', 'Frequency', 'Migraine', 'target', 'Sex']
    base_features = [col for col in df.columns if col not in exclude_cols]
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
            Each dict should have keys matching survey columns including 'Migraine'
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
        # Convert list of dicts to DataFrame
        user_df = pd.DataFrame(user_data_list)
        
        # Validate required columns
        if 'Migraine' not in user_df.columns:
            return {
                'success': False,
                'message': "Missing 'Migraine' column in user data",
                'n_user_samples': len(user_df)
            }
        
        # Check minimum samples
        if len(user_df) < MIN_USER_SAMPLES:
            return {
                'success': False,
                'message': f"Need at least {MIN_USER_SAMPLES} samples, got {len(user_df)}",
                'n_user_samples': len(user_df)
            }
        
        # Ensure user_id is set
        if 'Unique ID' not in user_df.columns:
            user_df['Unique ID'] = user_id
        
        print(f"Retraining model for user {user_id} with {len(user_df)} samples...")
        
        # Load base model structure
        base_model_data = load_base_model()
        base_model = base_model_data['model']
        feature_names = base_model_data['feature_names']
        le_sex = base_model_data.get('label_encoder_sex', None)
        model_name = base_model_data.get('model_name', 'RandomForest')
        
        # Load base training data
        if base_training_data_path is None:
            base_training_data_path = BASE_TRAINING_DATA_PATH
        
        base_data = pd.read_excel(base_training_data_path)
        base_data['target'] = base_data['Migraine'].astype(int)
        
        # Combine base data + user data
        user_df['target'] = user_df['Migraine'].astype(int)
        combined_data = pd.concat([base_data, user_df], ignore_index=True)
        
        # Prepare features
        X = prepare_features_for_training(combined_data, feature_names, le_sex)
        y = combined_data['target'].copy()
        
        print(f"  Combined dataset: {len(X)} samples ({len(base_data)} base + {len(user_df)} user)")
        
        # Create model with same structure
        if model_name == 'LogisticRegression' or isinstance(base_model, LogisticRegression):
            adapted_model = LogisticRegression(
                class_weight='balanced',
                max_iter=1000,
                random_state=42,
                n_jobs=-1
            )
        else:
            adapted_model = RandomForestClassifier(
                n_estimators=100,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced',
                random_state=42,
                n_jobs=-1
            )
        
        # Train on combined data
        adapted_model.fit(X, y)
        
        # Save user-specific model
        os.makedirs(USER_MODELS_DIR, exist_ok=True)
        user_model_data = {
            'model': adapted_model,
            'feature_names': feature_names,
            'label_encoder_sex': le_sex,
            'model_name': model_name,
            'user_id': user_id,
            'n_user_samples': len(user_df),
            'n_total_samples': len(X)
        }
        
        user_model_path = f"{USER_MODELS_DIR}/user_{user_id}_model.pkl"
        joblib.dump(user_model_data, user_model_path)
        
        print(f"  ✅ Model saved to {user_model_path}")
        
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

if __name__ == "__main__":
    # Example usage - proof of concept
    print("=== Retrain User Model - Proof of Concept ===\n")
    
    # Simulate Flask request data (list of dictionaries)
    example_user_data = [
        {
            'Unique ID': 'CM-001',
            'Age': 46,
            'Sex': 'female',
            'Date': 20240101,
            'Stress': 1,
            'Sleep deprivation': 0,
            'Exercise': 0,
            'Physical fatigue': 1,
            'Migraine': 1,
            # ... other survey fields
        },
        {
            'Unique ID': 'CM-001',
            'Age': 46,
            'Sex': 'female',
            'Date': 20240102,
            'Stress': 0,
            'Sleep deprivation': 1,
            'Exercise': 1,
            'Physical fatigue': 0,
            'Migraine': 0,
            # ... other survey fields
        },
        # ... more entries
    ]
    
    # Load real data for example
    try:
        df = pd.read_excel(BASE_TRAINING_DATA_PATH)
        user_id = df['Unique ID'].iloc[0]
        user_data = df[df['Unique ID'] == user_id].head(30).to_dict('records')
        
        print(f"Testing with user: {user_id}")
        print(f"User data: {len(user_data)} samples\n")
        
        result = retrain_user_model(user_id, user_data)
        
        print(f"\nResult:")
        print(f"  Success: {result['success']}")
        print(f"  Message: {result['message']}")
        if result['success']:
            print(f"  Model path: {result['model_path']}")
            print(f"  User samples: {result['n_user_samples']}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

