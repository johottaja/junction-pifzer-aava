"""
Migraine Prediction Script
Easy-to-use interface for predicting migraine probability
"""

import pandas as pd
import numpy as np
import joblib
import json
import os
import sys
from typing import Dict, Union


class MigrainePredictionSystem:
    """
    System for predicting migraine probability and updating model with new data
    """
    
    def __init__(self, model_path='models', model_name='migraine_model'):
        self.model_path = model_path
        self.model_name = model_name
        self.model = None
        self.scaler = None
        self.feature_names = None
        self.feature_importance = None
        
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        try:
            model_file = os.path.join(self.model_path, f'{self.model_name}.pkl')
            scaler_file = os.path.join(self.model_path, f'{self.model_name}_scaler.pkl')
            
            self.model = joblib.load(model_file)
            self.scaler = joblib.load(scaler_file)
            
            # Default feature names (10 features)
            self.feature_names = [
                'Screen_time_h', 'Average_heart_rate_bpm', 'Steps_and_activity',
                'Sleep_h', 'Stress_level_0_100', 'Respiration_rate_breaths_min',
                'Saa_Temperature_average_C', 'Saa_Air_quality_0_5',
                'Received_Condition_0_3', 'Received_Air_Pressure_hPa'
            ]
            
            # Get feature importance from model if available
            if hasattr(self.model, 'feature_importances_'):
                self.feature_importance = dict(zip(self.feature_names, self.model.feature_importances_))
            else:
                self.feature_importance = None
            
            print(f"✓ Model loaded successfully!")
            print(f"  Features: {len(self.feature_names)}")
            
        except FileNotFoundError as e:
            print(f"Error: Model files not found in '{self.model_path}/'")
            print("Please run 'train_model.py' first to train the model.")
            sys.exit(1)
    
    def predict_from_dict(self, data: Dict[str, float]) -> Dict[str, Union[float, str]]:
        """
        Predict migraine probability from a dictionary of values
        
        Parameters:
        -----------
        data : dict
            Dictionary containing today's sensor and health data
            Required keys match feature names
        
        Returns:
        --------
        dict with 'probability', 'risk_level', and 'recommendation'
        """
        # Create DataFrame with the required features
        df = pd.DataFrame([data])
        
        # Ensure all required features are present
        missing_features = set(self.feature_names) - set(df.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Select and order features correctly
        X = df[self.feature_names].copy()
        
        # Handle missing values
        X = X.fillna(X.mean())
        
        # Scale features
        X_scaled = self.scaler.transform(X)
        
        # Predict probability
        probability = self.model.predict_proba(X_scaled)[0, 1]
        
        # Convert to percentage (0-100)
        percentage = probability * 100
        
        # Determine risk level
        if percentage < 20:
            risk_level = "Very Low"
            recommendation = "Low risk of migraine. Continue monitoring your health."
        elif percentage < 40:
            risk_level = "Low"
            recommendation = "Slight risk. Maintain good sleep and hydration."
        elif percentage < 60:
            risk_level = "Moderate"
            recommendation = "Moderate risk. Avoid known triggers and ensure adequate rest."
        elif percentage < 80:
            risk_level = "High"
            recommendation = "High risk! Consider preventive medication and avoid stressors."
        else:
            risk_level = "Very High"
            recommendation = "Very high risk! Take preventive measures and consult your doctor."
        
        return {
            'probability': round(percentage, 2),
            'risk_level': risk_level,
            'recommendation': recommendation,
            'raw_probability': round(probability, 4)
        }
    
    def predict_from_file(self, filepath: str) -> pd.DataFrame:
        """
        Predict migraine probability from a CSV or Excel file
        
        Parameters:
        -----------
        filepath : str
            Path to CSV or Excel file containing sensor data
            Each row will be processed separately
        
        Returns:
        --------
        DataFrame with original data plus prediction columns
        """
        # Load file
        if filepath.endswith('.csv'):
            df = pd.read_csv(filepath)
        elif filepath.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(filepath)
        else:
            raise ValueError("File must be CSV or Excel format")
        
        print(f"Loaded {len(df)} rows from {filepath}")
        
        # Check if required features exist
        missing_features = set(self.feature_names) - set(df.columns)
        if missing_features:
            raise ValueError(f"Missing required features: {missing_features}")
        
        # Prepare features
        X = df[self.feature_names].copy()
        X = X.fillna(X.mean())
        
        # Scale and predict
        X_scaled = self.scaler.transform(X)
        probabilities = self.model.predict_proba(X_scaled)[:, 1]
        
        # Add results to dataframe
        df['Migraine_Probability_%'] = (probabilities * 100).round(2)
        df['Risk_Level'] = pd.cut(
            df['Migraine_Probability_%'],
            bins=[0, 20, 40, 60, 80, 100],
            labels=['Very Low', 'Low', 'Moderate', 'High', 'Very High']
        )
        
        return df
    
    def explain_prediction(self, data: Dict[str, float], top_n: int = 5):
        """
        Explain which features are most important for the prediction
        
        Parameters:
        -----------
        data : dict
            Input data dictionary
        top_n : int
            Number of top features to display
        """
        result = self.predict_from_dict(data)
        
        print("\n" + "="*60)
        print("MIGRAINE PREDICTION EXPLANATION")
        print("="*60)
        
        print(f"\n📊 Migraine Probability: {result['probability']}%")
        print(f"⚠️  Risk Level: {result['risk_level']}")
        print(f"💡 Recommendation: {result['recommendation']}")
        
        print(f"\n🔍 Top {top_n} Most Important Features:")
        print("-" * 60)
        
        # Sort features by importance
        sorted_features = sorted(
            self.feature_importance.items(),
            key=lambda x: x[1],
            reverse=True
        )[:top_n]
        
        for i, (feature, importance) in enumerate(sorted_features, 1):
            value = data.get(feature, 'N/A')
            print(f"{i}. {feature:35s}: {value:>8} (Importance: {importance:.4f})")
        
        print("\n" + "="*60)
        
        return result
    
    def update_with_feedback(self, data: Dict[str, float], actual_migraine: bool):
        """
        Update the model with user feedback (for future personalization)
        This stores the data point for later retraining
        
        Parameters:
        -----------
        data : dict
            Input data that was used for prediction
        actual_migraine : bool
            Whether a migraine actually occurred (True/False)
        """
        feedback_file = os.path.join(self.model_path, 'user_feedback.csv')
        
        # Add actual outcome to data
        feedback_data = data.copy()
        feedback_data['Actual_Migraine'] = int(actual_migraine)
        feedback_data['Timestamp'] = pd.Timestamp.now()
        
        # Append to feedback file
        df_feedback = pd.DataFrame([feedback_data])
        
        if os.path.exists(feedback_file):
            df_existing = pd.read_csv(feedback_file)
            df_feedback = pd.concat([df_existing, df_feedback], ignore_index=True)
        
        df_feedback.to_csv(feedback_file, index=False)
        
        print(f"✓ Feedback saved! Total feedback records: {len(df_feedback)}")
        print("  This data can be used to retrain and personalize the model.")


def predict_single(data: Dict[str, float], explain: bool = True):
    """
    Quick function to predict migraine from a dictionary
    
    Parameters:
    -----------
    data : dict
        Dictionary with today's health/sensor data
    explain : bool
        Whether to show detailed explanation
    
    Returns:
    --------
    dict with prediction results
    """
    predictor = MigrainePredictionSystem()
    
    if explain:
        return predictor.explain_prediction(data)
    else:
        return predictor.predict_from_dict(data)


def predict_from_csv(filepath: str, output_file: str = None):
    """
    Quick function to predict from a CSV/Excel file
    
    Parameters:
    -----------
    filepath : str
        Path to input file
    output_file : str, optional
        Path to save results (if None, prints to console)
    
    Returns:
    --------
    DataFrame with predictions
    """
    predictor = MigrainePredictionSystem()
    results = predictor.predict_from_file(filepath)
    
    if output_file:
        if output_file.endswith('.csv'):
            results.to_csv(output_file, index=False)
        else:
            results.to_excel(output_file, index=False)
        print(f"\n✓ Results saved to: {output_file}")
    else:
        print("\nPrediction Results:")
        print(results.to_string())
    
    return results


def main():
    """
    Example usage and interactive mode
    """
    print("="*60)
    print("MIGRAINE PREDICTION SYSTEM")
    print("="*60)
    
    # Example: Predict from dictionary
    print("\n📋 Example 1: Predict from manual input")
    print("-" * 60)
    
    example_data = {
        'Screen_time_h': 6.5,
        'Average_heart_rate_bpm': 72,
        'Steps_and_activity': 8000,
        'Sleep_h': 6.0,
        'Migraine_today_0_or_1': 0,
        'Stress_level_0_100': 65,
        'Respiration_rate_breaths_min': 16,
        'Saa_Temperature_average_C': 22.5,
        'Saa_Air_quality_0_5': 3,
        'Received_Condition_0_3': 1,
        'Received_Air_Pressure_hPa': 1013.25
    }
    
    result = predict_single(example_data, explain=True)
    
    # Example: Predict from file
    print("\n\n📁 Example 2: Predict from file")
    print("-" * 60)
    print("To predict from a file, use:")
    print("  python predict.py --file your_data.csv")
    print("Or in code:")
    print("  predict_from_csv('your_data.csv', 'results.csv')")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Predict migraine probability')
    parser.add_argument('--file', type=str, help='CSV or Excel file with sensor data')
    parser.add_argument('--output', type=str, help='Output file for predictions')
    
    args = parser.parse_args()
    
    if args.file:
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found!")
            sys.exit(1)
        predict_from_csv(args.file, args.output)
    else:
        # Run example
        main()

