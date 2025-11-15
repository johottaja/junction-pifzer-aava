"""
User-Specific Model Manager
Handles individual models for each user
"""

import os
import joblib
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.utils.class_weight import compute_class_weight

class UserModelManager:
    """Manages individual models for each user"""
    
    def __init__(self, models_dir='models', user_data_dir='user_data'):
        self.models_dir = models_dir
        self.user_data_dir = user_data_dir
        
        # Create directories if they don't exist
        os.makedirs(self.models_dir, exist_ok=True)
        os.makedirs(self.user_data_dir, exist_ok=True)
        
        self.feature_names = [
            'Screen_time_h', 'Average_heart_rate_bpm', 'Steps_and_activity',
            'Sleep_h', 'Stress_level_0_100', 'Respiration_rate_breaths_min',
            'Saa_Temperature_average_C', 'Saa_Air_quality_0_5',
            'Received_Condition_0_3', 'Received_Air_Pressure_hPa'
        ]
    
    def get_user_model_path(self, user_id):
        """Get file path for user's model"""
        user_id = int(user_id)  # Ensure int8 format
        return os.path.join(self.models_dir, f'user_{user_id}_model.pkl')
    
    def get_user_scaler_path(self, user_id):
        """Get file path for user's scaler"""
        user_id = int(user_id)  # Ensure int8 format
        return os.path.join(self.models_dir, f'user_{user_id}_scaler.pkl')
    
    def get_user_data_path(self, user_id):
        """Get file path for user's training data"""
        user_id = int(user_id)  # Ensure int8 format
        return os.path.join(self.user_data_dir, f'user_{user_id}_data.csv')
    
    def user_has_model(self, user_id):
        """Check if user has a trained model"""
        model_path = self.get_user_model_path(user_id)
        scaler_path = self.get_user_scaler_path(user_id)
        return os.path.exists(model_path) and os.path.exists(scaler_path)
    
    def user_has_data(self, user_id):
        """Check if user has training data"""
        data_path = self.get_user_data_path(user_id)
        return os.path.exists(data_path)
    
    def get_user_data_count(self, user_id):
        """Get number of data points for user"""
        if not self.user_has_data(user_id):
            return 0
        data_path = self.get_user_data_path(user_id)
        df = pd.read_csv(data_path)
        return len(df)
    
    def load_user_model(self, user_id):
        """Load user's trained model and scaler"""
        if not self.user_has_model(user_id):
            raise FileNotFoundError(f"No trained model found for user '{user_id}'")
        
        model_path = self.get_user_model_path(user_id)
        scaler_path = self.get_user_scaler_path(user_id)
        
        model = joblib.load(model_path)
        scaler = joblib.load(scaler_path)
        
        return model, scaler
    
    def save_user_data(self, user_id, data_dict):
        """
        Save user's training data point
        
        Args:
            user_id: Integer user ID
            data_dict: Dictionary with 11 fields (10 sensors + Migraine_today_0_or_1)
        """
        user_id = int(user_id)  # Ensure int8 format
        data_path = self.get_user_data_path(user_id)
        
        # Ensure Migraine_today_0_or_1 is present
        if 'Migraine_today_0_or_1' not in data_dict:
            raise ValueError("Training data must include 'Migraine_today_0_or_1' field")
        
        # Prepare record
        record = data_dict.copy()
        record['UserID'] = user_id  # Store as integer
        record['Timestamp'] = pd.Timestamp.now()
        
        # Ensure all required features are present
        for feature in self.feature_names:
            if feature not in record:
                raise ValueError(f"Missing required feature: {feature}")
        
        # Save to CSV
        df_record = pd.DataFrame([record])
        
        if os.path.exists(data_path):
            df_existing = pd.read_csv(data_path)
            df_record = pd.concat([df_existing, df_record], ignore_index=True)
        
        df_record.to_csv(data_path, index=False)
        
        print(f"✓ Saved data for user '{user_id}' (total: {len(df_record)} records)")
        return len(df_record)
    
    def train_user_model(self, user_id, min_data_points=10):
        """Train a personalized model for a specific user"""
        user_id = int(user_id)  # Ensure int8 format
        data_path = self.get_user_data_path(user_id)
        
        if not os.path.exists(data_path):
            raise FileNotFoundError(f"No training data found for user '{user_id}'")
        
        # Load user's data
        df = pd.read_csv(data_path)
        
        # Check minimum data points
        if len(df) < min_data_points:
            raise ValueError(
                f"User '{user_id}' has only {len(df)} data points. "
                f"Need at least {min_data_points} to train a model."
            )
        
        print(f"\n{'='*70}")
        print(f"Training personalized model for user: {user_id}")
        print(f"{'='*70}")
        print(f"Training data points: {len(df)}")
        
        # Prepare features and target
        X = df[self.feature_names].values
        y = df['Migraine_today_0_or_1'].values
        
        # Check class distribution
        migraine_count = np.sum(y == 1)
        no_migraine_count = np.sum(y == 0)
        
        print(f"Migraine occurrences: {migraine_count}")
        print(f"No migraine: {no_migraine_count}")
        
        if migraine_count == 0 or no_migraine_count == 0:
            raise ValueError(
                f"User '{user_id}' needs data points with BOTH migraine and no-migraine outcomes. "
                f"Current: {migraine_count} migraine, {no_migraine_count} no-migraine"
            )
        
        # Scale features
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        
        # Calculate balanced class weights
        classes = np.unique(y)
        class_weights = compute_class_weight('balanced', classes=classes, y=y)
        class_weight_dict = {
            0: class_weights[0],
            1: class_weights[1]
        }
        
        print(f"\nClass weights:")
        print(f"  No Migraine (0): {class_weight_dict[0]:.2f}")
        print(f"  Migraine (1): {class_weight_dict[1]:.2f}")
        
        # Train model with STRONG regularization to prevent overfitting
        print("\nTraining Random Forest classifier...")
        
        # For small datasets, use very conservative parameters
        if len(df) < 30:
            n_est = 50  # Fewer trees
            max_dep = 3  # Very shallow trees
            min_split = max(5, len(df) // 3)  # Require many samples to split
            min_leaf = max(2, len(df) // 6)   # Require many samples in leaves
        else:
            n_est = 100
            max_dep = 5
            min_split = 10
            min_leaf = 4
        
        print(f"  Using conservative params for dataset size {len(df)}:")
        print(f"  n_estimators={n_est}, max_depth={max_dep}")
        
        model = RandomForestClassifier(
            n_estimators=n_est,
            max_depth=max_dep,
            min_samples_split=min_split,
            min_samples_leaf=min_leaf,
            max_features='sqrt',
            random_state=42,
            class_weight=class_weight_dict,
            n_jobs=-1,
            bootstrap=True,
            min_impurity_decrease=0.01  # Require improvement to split
        )
        
        model.fit(X_scaled, y)
        
        # Calculate training accuracy
        train_pred = model.predict(X_scaled)
        train_accuracy = np.mean(train_pred == y) * 100
        
        print(f"\nTraining accuracy: {train_accuracy:.2f}%")
        
        # Feature importance
        feature_importance = dict(zip(self.feature_names, model.feature_importances_))
        print("\nTop 5 most important features for this user:")
        sorted_features = sorted(feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features[:5]:
            print(f"  {feature}: {importance:.4f}")
        
        # Save model and scaler
        model_path = self.get_user_model_path(user_id)
        scaler_path = self.get_user_scaler_path(user_id)
        
        joblib.dump(model, model_path)
        joblib.dump(scaler, scaler_path)
        
        print(f"\n✓ Model saved successfully!")
        print(f"  Model: {model_path}")
        print(f"  Scaler: {scaler_path}")
        print(f"{'='*70}\n")
        
        return {
            'user_id': user_id,
            'data_points': len(df),
            'accuracy': train_accuracy,
            'migraine_count': migraine_count,
            'no_migraine_count': no_migraine_count,
            'feature_importance': feature_importance
        }
    
    def predict(self, user_id, data_dict):
        """Make prediction using user's model with probability smoothing"""
        user_id = int(user_id)  # Ensure int8 format
        if not self.user_has_model(user_id):
            raise FileNotFoundError(
                f"No trained model found for user '{user_id}'. "
                f"Please train a model first using train_user_model()"
            )
        
        # Load model and scaler
        model, scaler = self.load_user_model(user_id)
        
        # Prepare features
        features = [data_dict[feature] for feature in self.feature_names]
        features_array = np.array(features).reshape(1, -1)
        
        # Scale and predict
        features_scaled = scaler.transform(features_array)
        raw_proba = model.predict_proba(features_scaled)[0][1]
        
        # Apply probability smoothing to avoid extreme 0% or 100%
        # This prevents overconfidence, especially with small datasets
        smoothing_factor = 0.05  # Add 5% uncertainty
        smoothed_proba = (raw_proba * (1 - 2 * smoothing_factor)) + smoothing_factor
        
        # Convert to percentage
        probability = smoothed_proba * 100
        
        # Ensure bounds
        probability = max(0.0, min(100.0, probability))
        
        return probability
    
    def get_top_risk_factors(self, user_id, data_dict, top_n=2):
        """Get top N risk factors contributing to migraine prediction"""
        user_id = int(user_id)
        if not self.user_has_model(user_id):
            raise FileNotFoundError(f"No trained model found for user '{user_id}'.")
        
        model, scaler = self.load_user_model(user_id)
        
        feature_importance = model.feature_importances_
        importance_dict = dict(zip(self.feature_names, feature_importance))
        
        thresholds = {
            'Screen_time_h': 8.0,
            'Average_heart_rate_bpm': 80.0,
            'Steps_and_activity': 5000.0,
            'Sleep_h': 6.5,
            'Stress_level_0_100': 70.0,
            'Respiration_rate_breaths_min': 18.0,
            'Saa_Temperature_average_C': 27.0,
            'Saa_Air_quality_0_5': 3.0,
            'Received_Condition_0_3': 2.0,
            'Received_Air_Pressure_hPa': 1010.0
        }
        
        risk_scores = []
        for feature, importance in importance_dict.items():
            value = data_dict.get(feature, 0)
            threshold = thresholds.get(feature, 0)
            
            if feature == 'Sleep_h':
                deviation = max(0, threshold - value)
            elif feature == 'Steps_and_activity':
                deviation = max(0, threshold - value) / 1000.0
            else:
                deviation = max(0, value - threshold)
            
            risk_score = importance * (1 + deviation)
            risk_scores.append((feature, risk_score, value))
        
        risk_scores.sort(key=lambda x: x[1], reverse=True)
        
        readable_names = {
            'Screen_time_h': 'High screen time',
            'Average_heart_rate_bpm': 'Elevated heart rate',
            'Steps_and_activity': 'Low physical activity',
            'Sleep_h': 'Insufficient sleep',
            'Stress_level_0_100': 'High stress level',
            'Respiration_rate_breaths_min': 'Elevated respiration rate',
            'Saa_Temperature_average_C': 'High temperature',
            'Saa_Air_quality_0_5': 'Poor air quality',
            'Received_Condition_0_3': 'Weather conditions',
            'Received_Air_Pressure_hPa': 'Air pressure changes'
        }
        
        top_factors = []
        for feature, score, value in risk_scores[:top_n]:
            readable = readable_names.get(feature, feature)
            top_factors.append(readable)
        
        return top_factors
    
    def list_all_users(self):
        """List all users with models or data"""
        users_with_data = set()
        users_with_models = set()
        
        # Check data directory
        if os.path.exists(self.user_data_dir):
            for file in os.listdir(self.user_data_dir):
                if file.startswith('user_') and file.endswith('_data.csv'):
                    user_id = file[5:-9]  # Extract user_id from filename
                    users_with_data.add(user_id)
        
        # Check models directory
        if os.path.exists(self.models_dir):
            for file in os.listdir(self.models_dir):
                if file.startswith('user_') and file.endswith('_model.pkl'):
                    user_id = file[5:-10]  # Extract user_id from filename
                    users_with_models.add(user_id)
        
        all_users = users_with_data.union(users_with_models)
        
        return {
            'all_users': sorted(list(all_users)),
            'users_with_data': sorted(list(users_with_data)),
            'users_with_models': sorted(list(users_with_models))
        }

