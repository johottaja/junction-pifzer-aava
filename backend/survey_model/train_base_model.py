"""
Train base LogisticRegression model on survey data with personalization.
Uses config.py for column names matching Supabase schema.
"""
import pandas as pd
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
import joblib
import os
from config import (
    USER_ID_COL, MIGRAINE_COL, AGE_COL, GENDER_COL, DATE_COL,
    SURVEY_FEATURES, EXCLUDE_COLS
)

# Configuration
DATA_PATH = "pretrain_data/survey_base_data.xlsx"  # Use converted data with numeric user_ids
MODEL_PATH = "models/best_model.pkl"

def create_user_features(df, train_mask=None):
    """
    Create user-specific aggregated features for personalization.
    Uses survey response patterns (NOT target) to avoid data leakage.
    """
    if train_mask is not None:
        train_df = df[train_mask].copy()
    else:
        train_df = df.copy()
    
    # Use user_id column (should be numeric from survey_base_data.xlsx)
    user_id_col = USER_ID_COL
    
    if user_id_col not in train_df.columns:
        raise ValueError(f"'{user_id_col}' column not found. Update config.py to match your data.")
    
    # Use survey features from config (only those that exist)
    available_features = [f for f in SURVEY_FEATURES if f in train_df.columns]
    
    if available_features:
        agg_dict = {feat: ['mean', 'std'] for feat in available_features}
        user_stats = train_df.groupby(user_id_col).agg(agg_dict).reset_index()
        
        new_cols = [user_id_col]
        for feat in available_features:
            new_cols.extend([f'user_{feat}_mean', f'user_{feat}_std'])
        user_stats.columns = new_cols
    else:
        user_stats = pd.DataFrame({user_id_col: train_df[user_id_col].unique()})
    
    df = df.merge(user_stats, on=user_id_col, how='left')
    
    user_feature_cols = [col for col in df.columns if col.startswith('user_')]
    for col in user_feature_cols:
        df[col] = df[col].fillna(0)
    
    return df

def load_and_prepare_data():
    """Load survey data and prepare features/target with personalization."""
    df = pd.read_excel(DATA_PATH)
    
    # Use config column name (no autodetection - format must match)
    if MIGRAINE_COL not in df.columns:
        raise ValueError(f"'{MIGRAINE_COL}' column not found. Update config.py to match your data.")
    
    df['target'] = df[MIGRAINE_COL].astype(int)
    
    print(f"Target distribution: {df['target'].value_counts().to_dict()}")
    print(f"Migraine rate: {df['target'].mean():.3f}")
    
    # Encode Gender (optional - may come from user profile, not survey table)
    le_gender = None
    if GENDER_COL in df.columns:
        le_gender = LabelEncoder()
        df['gender_encoded'] = le_gender.fit_transform(df[GENDER_COL])
    else:
        # Gender not in data - will be handled in inference from user profile
        print(f"Note: '{GENDER_COL}' not in data. Will use from user profile in inference.")
    
    # Store user IDs (should already be numeric from survey_base_data.xlsx)
    if USER_ID_COL not in df.columns:
        raise ValueError(f"'{USER_ID_COL}' column not found. Update config.py to match your data.")
    
    # Verify user_id is numeric
    if df[USER_ID_COL].dtype == 'object':
        raise ValueError(
            f"'{USER_ID_COL}' column contains non-numeric values. "
            f"Please run convert_user_ids.py first to convert user_ids to numeric."
        )
    
    user_ids = df[USER_ID_COL].copy()
    print(f"Using {user_ids.nunique()} unique users (user_ids should be numeric)")
    
    # Select base features (exclude non-feature columns)
    # Also exclude age/gender if present (they come from user profile, not survey)
    exclude_all = EXCLUDE_COLS.copy()
    exclude_all.append(USER_ID_COL)  # Always exclude user_id column (used for splits only)
    if AGE_COL in df.columns:
        exclude_all.append(AGE_COL)
    # Always exclude original gender column (we use gender_encoded if it exists)
    if GENDER_COL in df.columns:
        exclude_all.append(GENDER_COL)
    
    feature_cols = [col for col in df.columns if col not in exclude_all]
    feature_cols = [col for col in feature_cols if not col.startswith('user_')]
    
    # Ensure only numeric columns are included (exclude any remaining string columns)
    X = df[feature_cols].copy()
    
    # Convert any remaining non-numeric columns to numeric or drop them
    for col in X.columns:
        if X[col].dtype == 'object':
            # Try to convert to numeric, if fails, drop the column
            try:
                X[col] = pd.to_numeric(X[col], errors='coerce')
            except:
                print(f"Warning: Dropping non-numeric column '{col}'")
                X = X.drop(columns=[col])
                if col in feature_cols:
                    feature_cols.remove(col)
    
    y = df['target'].copy()
    X = X.fillna(0)
    
    # Update feature_cols to match what's actually in X
    feature_cols = list(X.columns)
    
    return X, y, feature_cols, user_ids, le_gender, df

def split_by_users(X, y, user_ids, df, test_size=0.2, random_state=42):
    """Proper train/test split by users to avoid data leakage."""
    unique_users = user_ids.unique()
    train_users, test_users = train_test_split(
        unique_users, test_size=test_size, random_state=random_state
    )
    
    train_mask = user_ids.isin(train_users)
    test_mask = user_ids.isin(test_users)
    
    # Create user features only from training data
    df_with_features = create_user_features(df.copy(), train_mask=train_mask)
    
    # Add user features to X
    user_feature_cols = [col for col in df_with_features.columns if col.startswith('user_')]
    for col in user_feature_cols:
        if col not in X.columns:
            X[col] = df_with_features[col].values
    
    X_train = X[train_mask].copy()
    X_test = X[test_mask].copy()
    y_train = y[train_mask].copy()
    y_test = y[test_mask].copy()
    
    # Verify no user overlap between train and test
    train_user_set = set(train_users)
    test_user_set = set(test_users)
    overlap = train_user_set & test_user_set
    
    if overlap:
        raise ValueError(f"❌ Data leakage detected! Users in both train and test: {overlap}")
    
    print(f"\nTrain: {len(X_train)} samples from {len(train_users)} users")
    print(f"Test: {len(X_test)} samples from {len(test_users)} users")
    print(f"✅ Train/Test separation verified: {len(overlap)} overlapping users (should be 0)")
    print(f"Train target: {y_train.value_counts().to_dict()}")
    print(f"Test target: {y_test.value_counts().to_dict()}")
    
    return X_train, X_test, y_train, y_test

def train_model(X, y, user_ids, df):
    """Train LogisticRegression model with proper user-based split."""
    X_train, X_test, y_train, y_test = split_by_users(X, y, user_ids, df)
    
    # Train LogisticRegression
    model = LogisticRegression(
        class_weight='balanced',
        max_iter=1000,
        random_state=42,
        n_jobs=-1
    )
    
    model.fit(X_train, y_train)
    
    # Evaluate
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)
    train_proba = model.predict_proba(X_train)[:, 1]
    test_proba = model.predict_proba(X_test)[:, 1]
    
    print(f"\n=== Model Performance ===")
    print(f"Train Accuracy: {accuracy_score(y_train, train_pred):.3f}")
    print(f"Test Accuracy: {accuracy_score(y_test, test_pred):.3f}")
    print(f"Train AUC: {roc_auc_score(y_train, train_proba):.3f}")
    print(f"Test AUC: {roc_auc_score(y_test, test_proba):.3f}")
    
    print("\n=== Test Set Classification Report ===")
    print(classification_report(y_test, test_pred))
    
    cm = confusion_matrix(y_test, test_pred)
    print(f"\n=== Confusion Matrix (Test) ===")
    print(f"TN: {cm[0,0]}, FP: {cm[0,1]}")
    print(f"FN: {cm[1,0]}, TP: {cm[1,1]}")
    
    return model, X_train

def save_model_and_features(model, X_train, le_gender):
    """Save model, feature names, and encoders."""
    os.makedirs("models", exist_ok=True)
    
    feature_cols = list(X_train.columns)
    
    model_data = {
        'model': model,
        'feature_names': feature_cols,
        'label_encoder_gender': le_gender,
        'model_name': 'LogisticRegression'
    }
    joblib.dump(model_data, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    
    # Display feature importance
    if hasattr(model, 'coef_'):
        coef_abs = np.abs(model.coef_[0])
        importance_df = pd.DataFrame({
            'feature': feature_cols,
            'importance': coef_abs
        }).sort_values('importance', ascending=False)
        
        print("\n=== Top 15 Features (Coefficient Magnitude) ===")
        print(importance_df.head(15).to_string(index=False))

if __name__ == "__main__":
    print("=== Loading Data ===")
    X, y, feature_cols, user_ids, le_gender, df = load_and_prepare_data()
    
    print(f"\n=== Data Summary ===")
    print(f"Total samples: {len(X)}")
    print(f"Base features: {len(feature_cols)}")
    print(f"Number of users: {user_ids.nunique()}")
    
    print("\n=== Training Model ===")
    model, X_train = train_model(X, y, user_ids, df)
    
    print("\n=== Saving Model ===")
    save_model_and_features(model, X_train, le_gender)
    
    print("\n=== Training Complete! ===")
