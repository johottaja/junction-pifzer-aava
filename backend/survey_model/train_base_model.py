"""
Train base RandomForest model on survey data with personalization.
Uses 'migraine' column as target and creates user features from survey responses.
"""
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report, confusion_matrix
import joblib
import os

# Configuration
DATA_PATH = "pretrain_data/survey_data.xlsx"
MODEL_PATH = "models/best_model.pkl"

def create_user_features(df, train_mask=None):
    """
    Create user-specific aggregated features for personalization.
    Uses survey response patterns (NOT Frequency) to avoid data leakage.
    If train_mask provided, calculate stats only from training data.
    """
    if train_mask is not None:
        train_df = df[train_mask].copy()
    else:
        train_df = df.copy()
    
    # Calculate user's typical survey response patterns (personalization)
    # These represent the user's baseline patterns, not derived from target
    survey_features = [
        'Stress', 'Sleep deprivation', 'Exercise', 'Physical fatigue',
        'Weather/temperature change', 'Noise', 'Excess caffeinated drinks',
        'Oversleeping', 'Extreme emotional changes'
    ]
    
    # Only use features that exist in the dataframe
    available_features = [f for f in survey_features if f in train_df.columns]
    
    if available_features:
        # Calculate mean and std for each survey feature per user
        agg_dict = {feat: ['mean', 'std'] for feat in available_features}
        user_stats = train_df.groupby('Unique ID').agg(agg_dict).reset_index()
        
        # Flatten column names: user_Stress_mean, user_Stress_std, etc.
        new_cols = ['Unique ID']
        for feat in available_features:
            new_cols.extend([f'user_{feat}_mean', f'user_{feat}_std'])
        user_stats.columns = new_cols
    else:
        # Fallback: create empty user stats
        user_stats = pd.DataFrame({'Unique ID': train_df['Unique ID'].unique()})
    
    # Merge back
    df = df.merge(user_stats, on='Unique ID', how='left')
    
    # Fill NaN for new users or users with single record
    user_feature_cols = [col for col in df.columns if col.startswith('user_')]
    for col in user_feature_cols:
        df[col] = df[col].fillna(0)
    
    return df

def load_and_prepare_data():
    """Load survey data and prepare features/target with personalization."""
    df = pd.read_excel(DATA_PATH)
    
    # Use Migraine column as target (binary: 0 or 1)
    if 'Migraine' not in df.columns:
        raise ValueError("'Migraine' column not found in data. Please add it to survey_data.xlsx")
    
    df['target'] = df['Migraine'].astype(int)
    
    # Check target distribution
    target_dist = df['target'].value_counts()
    print(f"Target distribution: {target_dist.to_dict()}")
    print(f"Migraine rate: {df['target'].mean():.3f}")
    
    # Encode Sex
    le_sex = LabelEncoder()
    df['Sex_encoded'] = le_sex.fit_transform(df['Sex'])
    
    # Store user IDs for proper train/test split
    user_ids = df['Unique ID'].copy()
    
    # Select base features: Age, Sex, and survey features (exclude ID, Date, Frequency, Migraine, target, Sex)
    exclude_cols = ['Unique ID', 'Date', 'Frequency', 'Migraine', 'target', 'Sex']
    feature_cols = [col for col in df.columns if col not in exclude_cols]
    
    # Remove user features for now - will add after split
    user_feature_cols = [col for col in feature_cols if col.startswith('user_')]
    feature_cols = [col for col in feature_cols if col not in user_feature_cols]
    
    X = df[feature_cols].copy()
    y = df['target'].copy()
    
    # Handle any missing values
    X = X.fillna(0)
    
    return X, y, feature_cols, user_ids, le_sex, df

def split_by_users(X, y, user_ids, df, test_size=0.2, random_state=42):
    """
    Proper train/test split by users to avoid data leakage.
    Some users in train, some in test.
    Calculate user features only from training data.
    """
    unique_users = user_ids.unique()
    train_users, test_users = train_test_split(
        unique_users, test_size=test_size, random_state=random_state
    )
    
    train_mask = user_ids.isin(train_users)
    test_mask = user_ids.isin(test_users)
    
    # Create user features only from training data to avoid leakage
    df_with_features = create_user_features(df.copy(), train_mask=train_mask)
    
    # Add user features to X (all columns starting with 'user_')
    user_feature_cols = [col for col in df_with_features.columns if col.startswith('user_')]
    for col in user_feature_cols:
        if col not in X.columns:
            X[col] = df_with_features[col].values
    
    X_train = X[train_mask].copy()
    X_test = X[test_mask].copy()
    y_train = y[train_mask].copy()
    y_test = y[test_mask].copy()
    
    print(f"\nTrain: {len(X_train)} samples from {len(train_users)} users")
    print(f"Test: {len(X_test)} samples from {len(test_users)} users")
    print(f"Train target distribution: {y_train.value_counts().to_dict()}")
    print(f"Test target distribution: {y_test.value_counts().to_dict()}")
    
    return X_train, X_test, y_train, y_test

def train_model(X, y, user_ids, df):
    """Train RandomForest model with proper user-based split."""
    # Split by users (proper way to avoid leakage)
    X_train, X_test, y_train, y_test = split_by_users(X, y, user_ids, df)
    
    # Train RandomForest
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=15,
        min_samples_split=5,
        min_samples_leaf=2,
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
    
    print("\n=== Confusion Matrix (Test) ===")
    cm = confusion_matrix(y_test, test_pred)
    print(f"True Negatives: {cm[0,0]}, False Positives: {cm[0,1]}")
    print(f"False Negatives: {cm[1,0]}, True Positives: {cm[1,1]}")
    
    return model, X_train

def save_model_and_features(model, X_train, le_sex):
    """Save model, feature names, and encoders."""
    os.makedirs("models", exist_ok=True)
    
    # Get feature names from training data
    feature_cols = list(X_train.columns)
    
    # Save model with feature names and encoders
    model_data = {
        'model': model,
        'feature_names': feature_cols,
        'label_encoder_sex': le_sex
    }
    joblib.dump(model_data, MODEL_PATH)
    print(f"\nModel saved to {MODEL_PATH}")
    
    # Display feature importance (not saved - only returned in inference)
    importance_df = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n=== Top 15 Features (Global Importance) ===")
    print(importance_df.head(15).to_string(index=False))

if __name__ == "__main__":
    print("=== Loading Data ===")
    X, y, feature_cols, user_ids, le_sex, df = load_and_prepare_data()
    
    print(f"\n=== Data Summary ===")
    print(f"Total samples: {len(X)}")
    print(f"Base features (before user features): {len(feature_cols)}")
    print(f"Number of users: {user_ids.nunique()}")
    
    print("\n=== Training Model ===")
    model, X_train = train_model(X, y, user_ids, df)
    
    print("\n=== Saving Model ===")
    save_model_and_features(model, X_train, le_sex)
    
    print("\n=== Training Complete! ===")
