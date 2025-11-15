"""
Migraine Prediction Model Training Script
Uses Random Forest to predict migraine occurrence based on sensor and health data
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score, roc_auc_score
import joblib
import os
import json
from datetime import datetime


class MigrainePredictor:
    """
    Migraine prediction model using Random Forest
    Predicts tomorrow's migraine based on today's data
    """
    
    def __init__(self, model_path='models'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.feature_importance = None
        
        # Create models directory if it doesn't exist
        os.makedirs(model_path, exist_ok=True)
    
    def prepare_data(self, filepath):
        """
        Load and prepare data for training
        Creates lagged features to predict tomorrow's migraine from today's data
        """
        print(f"Loading data from {filepath}...")
        
        # Load Excel file
        df = pd.read_excel(filepath)
        
        # Check if data is in a single column (CSV format within Excel)
        if len(df.columns) == 1:
            print("\nDetected CSV format within Excel. Parsing...")
            # Get the column name (which contains the header)
            col_name = df.columns[0]
            
            # Split the header to get column names
            header = col_name.split(',')
            
            # Split all data rows
            df = df[col_name].str.split(',', expand=True)
            
            # Set column names from the header
            df.columns = header
            
            print("Data successfully parsed!")
        
        # Clean column names (remove spaces)
        df.columns = df.columns.str.strip()
        
        # Display data info
        print(f"\nData shape: {df.shape}")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"\nFirst few rows:")
        print(df.head())
        
        # Convert numeric columns to proper types
        numeric_columns = [
            'Day', 'Screen_time_h', 'Average_heart_rate_bpm', 'Steps_and_activity',
            'Sleep_h', 'Migraine_today_0_or_1', 'Stress_level_0_100',
            'Respiration_rate_breaths_min', 'Saa_Temperature_average_C',
            'Saa_Air_quality_0_5', 'Received_Condition_0_3', 'Received_Air_Pressure_hPa'
        ]
        
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Check for missing values
        print(f"\nMissing values:")
        print(df.isnull().sum())
        
        # Sort by UserID and Day to ensure temporal order
        df = df.sort_values(['UserID', 'Day']).reset_index(drop=True)
        
        # Create target variable: Use TODAY's migraine as target
        # IMPORTANT: We predict if THESE health metrics indicate a migraine
        # Model learns: Poor sleep + high stress + elevated heart rate = MIGRAINE
        # The key insight: On migraine days, the health metrics are different!
        df['Migraine_target'] = df['Migraine_today_0_or_1']
        
        # Remove any rows with missing target
        df = df.dropna(subset=['Migraine_target'])
        
        # Define feature columns (today's data)
        # NOTE: We exclude 'Migraine_today_0_or_1' because that's what we're predicting!
        feature_columns = [
            'Screen_time_h',
            'Average_heart_rate_bpm',
            'Steps_and_activity',
            'Sleep_h',
            'Stress_level_0_100',
            'Respiration_rate_breaths_min',
            'Saa_Temperature_average_C',
            'Saa_Air_quality_0_5',
            'Received_Condition_0_3',
            'Received_Air_Pressure_hPa'
        ]
        
        # Check if all columns exist
        missing_cols = [col for col in feature_columns if col not in df.columns]
        if missing_cols:
            print(f"\nWarning: Missing columns: {missing_cols}")
            feature_columns = [col for col in feature_columns if col in df.columns]
        
        self.feature_names = feature_columns
        
        # Extract features and target
        X = df[feature_columns].copy()
        y = df['Migraine_target'].copy()
        
        # Handle any remaining missing values
        X = X.fillna(X.mean())
        
        print(f"\nFeatures used: {feature_columns}")
        print(f"\nTarget distribution:")
        print(y.value_counts())
        print(f"\nMigraine rate: {y.mean()*100:.2f}%")
        
        return X, y, df
    
    def train(self, X, y, test_size=0.2, random_state=42):
        """
        Train the Random Forest model
        """
        print("\n" + "="*50)
        print("TRAINING RANDOM FOREST MODEL")
        print("="*50)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state, stratify=y
        )
        
        print(f"\nTraining set size: {X_train.shape[0]}")
        print(f"Test set size: {X_test.shape[0]}")
        
        # Scale features
        print("\nScaling features...")
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        # Use TRULY BALANCED class weights - no multipliers
        # This prevents overconfident predictions (no 100% unless extremely clear)
        from sklearn.utils.class_weight import compute_class_weight
        
        classes = np.unique(y_train)
        class_weights = compute_class_weight('balanced', classes=classes, y=y_train)
        
        # Use only the computed balanced weights - NO ADDITIONAL MULTIPLIER
        class_weight_dict = {
            0: class_weights[0],      # No migraine weight
            1: class_weights[1]       # Migraine weight - balanced as computed
        }
        
        print(f"\nClass weights (TRULY BALANCED - realistic predictions):")
        print(f"  No Migraine (0): {class_weight_dict[0]:.2f}")
        print(f"  Migraine (1): {class_weight_dict[1]:.2f} (balanced - no multiplier)")
        
        # Train Random Forest with regularization to PREVENT OVERFITTING
        print("\nTraining Random Forest classifier...")
        print("Using STRONG regularization for realistic predictions:")
        print("  - n_estimators=100 (moderate ensemble size)")
        print("  - max_depth=8 (shallower trees)")
        print("  - min_samples_split=15 (strong regularization)")
        print("  - min_samples_leaf=5 (strong regularization)")
        print("  - max_features='sqrt' (random feature selection)")
        
        self.model = RandomForestClassifier(
            n_estimators=100,          # Fewer trees to prevent overconfidence
            max_depth=8,               # Shallower trees for more conservative predictions
            min_samples_split=15,      # More samples required (stronger regularization)
            min_samples_leaf=5,        # More samples in leaves (stronger regularization)
            max_features='sqrt',       # Random feature selection (reduces correlation)
            random_state=random_state,
            class_weight=class_weight_dict,  # Balanced weights
            n_jobs=-1,                 # Use all CPU cores
            criterion='gini',          # Gini impurity
            bootstrap=True,            # Bootstrap sampling (reduces overfitting)
            oob_score=True             # Out-of-bag score (validation during training)
        )
        
        self.model.fit(X_train_scaled, y_train)
        
        # Get feature importance
        self.feature_importance = dict(zip(
            self.feature_names,
            self.model.feature_importances_
        ))
        
        # Evaluate model
        print("\n" + "="*50)
        print("MODEL EVALUATION")
        print("="*50)
        
        # Training predictions (to check for overfitting)
        y_train_pred = self.model.predict(X_train_scaled)
        train_accuracy = accuracy_score(y_train, y_train_pred)
        
        # Test predictions
        y_pred = self.model.predict(X_test_scaled)
        y_pred_proba = self.model.predict_proba(X_test_scaled)[:, 1]
        test_accuracy = accuracy_score(y_test, y_pred)
        
        # Metrics
        print(f"\n📊 Training Accuracy: {train_accuracy*100:.2f}%")
        print(f"📊 Test Accuracy: {test_accuracy*100:.2f}%")
        print(f"📊 Difference: {(train_accuracy - test_accuracy)*100:.2f}%")
        
        if hasattr(self.model, 'oob_score_'):
            print(f"📊 Out-of-Bag Score: {self.model.oob_score_*100:.2f}%")
        
        # Check for overfitting
        overfit_threshold = 0.05  # 5% difference
        if (train_accuracy - test_accuracy) > overfit_threshold:
            print("\n⚠️  WARNING: Possible overfitting detected!")
            print(f"   Training accuracy is {(train_accuracy - test_accuracy)*100:.1f}% higher than test")
        else:
            print("\n✓ No significant overfitting detected")
            print(f"  Training and test accuracy are similar (diff: {(train_accuracy - test_accuracy)*100:.1f}%)")
        
        if len(np.unique(y_test)) > 1:
            print("ROC-AUC Score:", f"{roc_auc_score(y_test, y_pred_proba):.4f}")
        
        print("\nConfusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        print("\nConfusion Matrix Breakdown:")
        print(f"  True Negatives (correctly predicted no migraine): {cm[0][0]}")
        print(f"  False Positives (predicted migraine, but none): {cm[0][1]}")
        print(f"  False Negatives (missed migraines - BAD!): {cm[1][0]}")
        print(f"  True Positives (correctly caught migraines - GOOD!): {cm[1][1]}")
        
        # Calculate migraine detection rate
        if cm[1][0] + cm[1][1] > 0:
            migraine_recall = cm[1][1] / (cm[1][0] + cm[1][1])
            print(f"\n✓ Migraine Detection Rate: {migraine_recall*100:.2f}%")
            print(f"  (Caught {cm[1][1]} out of {cm[1][0] + cm[1][1]} actual migraines)")
        
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['No Migraine', 'Migraine']))
        
        # Show average probabilities for each class
        print("\nAverage Predicted Probabilities:")
        prob_no_migraine = y_pred_proba[y_test == 0].mean() if sum(y_test == 0) > 0 else 0
        prob_migraine = y_pred_proba[y_test == 1].mean() if sum(y_test == 1) > 0 else 0
        print(f"  When no migraine occurs: {prob_no_migraine*100:.2f}% (should be LOW)")
        print(f"  When migraine occurs: {prob_migraine*100:.2f}% (should be HIGH)")
        
        # Cross-validation
        print("\nPerforming 5-fold cross-validation...")
        cv_scores = cross_val_score(self.model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        print(f"CV Accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
        
        # Feature importance
        print("\n" + "="*50)
        print("FEATURE IMPORTANCE")
        print("="*50)
        sorted_features = sorted(self.feature_importance.items(), key=lambda x: x[1], reverse=True)
        for feature, importance in sorted_features:
            print(f"{feature:40s}: {importance:.4f}")
        
        return {
            'accuracy': accuracy_score(y_test, y_pred),
            'cv_scores': cv_scores,
            'feature_importance': self.feature_importance
        }
    
    def save_model(self, name='migraine_model'):
        """
        Save trained model, scaler, and metadata
        """
        if self.model is None:
            raise ValueError("Model has not been trained yet!")
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # Save model
        model_file = os.path.join(self.model_path, f'{name}.pkl')
        joblib.dump(self.model, model_file)
        print(f"\nModel saved to: {model_file}")
        
        # Save scaler
        scaler_file = os.path.join(self.model_path, f'{name}_scaler.pkl')
        joblib.dump(self.scaler, scaler_file)
        print(f"Scaler saved to: {scaler_file}")
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'feature_importance': self.feature_importance,
            'training_date': timestamp,
            'model_type': 'RandomForestClassifier'
        }
        
        metadata_file = os.path.join(self.model_path, f'{name}_metadata.json')
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to: {metadata_file}")
        
        print("\nModel training complete!")
    
    def load_model(self, name='migraine_model'):
        """
        Load a trained model
        """
        model_file = os.path.join(self.model_path, f'{name}.pkl')
        scaler_file = os.path.join(self.model_path, f'{name}_scaler.pkl')
        metadata_file = os.path.join(self.model_path, f'{name}_metadata.json')
        
        self.model = joblib.load(model_file)
        self.scaler = joblib.load(scaler_file)
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.feature_names = metadata['feature_names']
        self.feature_importance = metadata['feature_importance']
        
        print(f"Model loaded from: {model_file}")
        return metadata


def main():
    """
    Main training function
    """
    # Path to data file
    data_file = '../junc2025sensordata.xlsx'
    
    if not os.path.exists(data_file):
        print(f"Error: Data file not found at {data_file}")
        print("Please ensure the Excel file is in the correct location.")
        return
    
    # Initialize predictor
    predictor = MigrainePredictor()
    
    # Load and prepare data
    X, y, df = predictor.prepare_data(data_file)
    
    # Train model
    results = predictor.train(X, y)
    
    # Save model
    predictor.save_model('migraine_model')
    
    print("\n" + "="*50)
    print("TRAINING SUMMARY")
    print("="*50)
    print(f"Total samples: {len(X)}")
    print(f"Features used: {len(predictor.feature_names)}")
    print(f"Model accuracy: {results['accuracy']*100:.2f}%")
    print(f"Cross-validation accuracy: {results['cv_scores'].mean()*100:.2f}%")
    print("\nYou can now use predict.py to make predictions!")


if __name__ == '__main__':
    main()

