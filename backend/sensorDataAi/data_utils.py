"""
Data Utilities for Migraine Prediction System
Helper functions for data validation, preprocessing, and personalization
"""

import pandas as pd
import numpy as np
import json
import os
from typing import Dict, List, Tuple, Optional


class DataValidator:
    """
    Validates input data for migraine prediction
    """
    
    # Define expected ranges for each feature
    # NOTE: Migraine_today_0_or_1 is NOT included - we're predicting it!
    FEATURE_RANGES = {
        'Screen_time_h': (0, 24),
        'Average_heart_rate_bpm': (40, 200),
        'Steps_and_activity': (0, 50000),
        'Sleep_h': (0, 24),
        'Stress_level_0_100': (0, 100),
        'Respiration_rate_breaths_min': (8, 30),
        'Saa_Temperature_average_C': (-20, 50),
        'Saa_Air_quality_0_5': (0, 5),
        'Received_Condition_0_3': (0, 3),
        'Received_Air_Pressure_hPa': (950, 1050)
    }
    
    REQUIRED_FEATURES = list(FEATURE_RANGES.keys())
    
    @classmethod
    def validate_input(cls, data: Dict[str, float]) -> Tuple[bool, List[str]]:
        """
        Validate input data
        
        Returns:
        --------
        (is_valid, error_messages)
        """
        errors = []
        
        # Check for missing features
        missing = set(cls.REQUIRED_FEATURES) - set(data.keys())
        if missing:
            errors.append(f"Missing features: {', '.join(missing)}")
        
        # Check value ranges
        for feature, value in data.items():
            if feature in cls.FEATURE_RANGES:
                min_val, max_val = cls.FEATURE_RANGES[feature]
                if not (min_val <= value <= max_val):
                    errors.append(
                        f"{feature} = {value} is outside valid range [{min_val}, {max_val}]"
                    )
        
        return len(errors) == 0, errors
    
    @classmethod
    def print_feature_info(cls):
        """Print information about expected features"""
        print("\n" + "="*70)
        print("REQUIRED FEATURES AND VALID RANGES")
        print("="*70)
        
        for feature, (min_val, max_val) in cls.FEATURE_RANGES.items():
            print(f"{feature:40s} : [{min_val:>6}, {max_val:>6}]")
        
        print("="*70)


class PersonalizedDataHandler:
    """
    Handles personalized user data for improved predictions
    """
    
    def __init__(self, data_dir='user_data'):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def save_user_data(self, user_id: str, data: Dict[str, float], 
                       migraine_occurred: Optional[bool] = None):
        """
        Save user's data to centralized training pool
        
        Parameters:
        -----------
        user_id : str
            Unique user identifier (for tracking only)
        data : dict
            Daily sensor/health data
        migraine_occurred : bool, optional
            Whether migraine actually occurred (for feedback)
        """
        # Prepare record for training pool
        record = data.copy()
        record['UserID'] = user_id
        record['Timestamp'] = pd.Timestamp.now()
        
        if migraine_occurred is not None:
            # Store with standard column name used in training
            record['Migraine_today_0_or_1'] = int(migraine_occurred)
        
        # Add to centralized training data pool
        total_records = self._add_to_training_pool(record)
        
        return total_records
    
    def _add_to_training_pool(self, record: Dict):
        """
        Add user's data to centralized training pool
        ONE pool for ALL users - simple and clean!
        """
        training_pool_file = os.path.join(self.data_dir, 'training_pool.csv')
        
        # Only add if migraine outcome is known
        if 'Migraine_today_0_or_1' not in record:
            return 0
        
        # Remove timestamp for training data (not needed for model)
        training_record = {k: v for k, v in record.items() if k != 'Timestamp'}
        df_record = pd.DataFrame([training_record])
        
        if os.path.exists(training_pool_file):
            df_existing = pd.read_csv(training_pool_file)
            df_record = pd.concat([df_existing, df_record], ignore_index=True)
        
        df_record.to_csv(training_pool_file, index=False)
        
        total = len(df_record)
        print(f"   ✓ Added to training pool: {total} total records")
        
        return total
    
    def get_user_data(self, user_id: str) -> Optional[pd.DataFrame]:
        """
        Retrieve user's historical data
        
        Parameters:
        -----------
        user_id : str
            Unique user identifier
        
        Returns:
        --------
        DataFrame with user's historical data or None if no data exists
        """
        user_file = os.path.join(self.data_dir, f'user_{user_id}.csv')
        
        if os.path.exists(user_file):
            return pd.read_csv(user_file)
        return None
    
    def get_user_statistics(self, user_id: str) -> Optional[Dict]:
        """
        Get statistics about user's data
        
        Returns:
        --------
        Dictionary with user statistics or None if no data exists
        """
        df = self.get_user_data(user_id)
        
        if df is None or len(df) == 0:
            return None
        
        stats = {
            'total_records': len(df),
            'date_range': {
                'first': str(df['Timestamp'].min()) if 'Timestamp' in df.columns else None,
                'last': str(df['Timestamp'].max()) if 'Timestamp' in df.columns else None
            }
        }
        
        # Calculate migraine frequency if available
        if 'Migraine_occurred' in df.columns:
            stats['migraine_frequency'] = df['Migraine_occurred'].mean()
            stats['total_migraines'] = int(df['Migraine_occurred'].sum())
        
        # Feature averages
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        stats['averages'] = df[numeric_cols].mean().to_dict()
        
        return stats


class DataPreprocessor:
    """
    Preprocessing utilities for sensor data
    """
    
    @staticmethod
    def clean_data(df: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and preprocess raw sensor data
        
        Parameters:
        -----------
        df : DataFrame
            Raw data
        
        Returns:
        --------
        Cleaned DataFrame
        """
        df_clean = df.copy()
        
        # Remove duplicates
        df_clean = df_clean.drop_duplicates()
        
        # Handle outliers (using IQR method)
        numeric_cols = df_clean.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            if col in DataValidator.FEATURE_RANGES:
                min_val, max_val = DataValidator.FEATURE_RANGES[col]
                df_clean[col] = df_clean[col].clip(min_val, max_val)
        
        return df_clean
    
    @staticmethod
    def add_derived_features(df: pd.DataFrame) -> pd.DataFrame:
        """
        Add derived features that might be useful for prediction
        
        Parameters:
        -----------
        df : DataFrame
            Input data
        
        Returns:
        --------
        DataFrame with additional features
        """
        df_enhanced = df.copy()
        
        # Sleep quality indicator
        if 'Sleep_h' in df.columns:
            df_enhanced['Sleep_sufficient'] = (df['Sleep_h'] >= 7).astype(int)
            df_enhanced['Sleep_deficit'] = np.maximum(0, 7 - df['Sleep_h'])
        
        # Activity level
        if 'Steps_and_activity' in df.columns:
            df_enhanced['Activity_level'] = pd.cut(
                df['Steps_and_activity'],
                bins=[0, 3000, 7000, 10000, 50000],
                labels=[0, 1, 2, 3]
            ).astype(float)
        
        # Heart rate zones (simplified)
        if 'Average_heart_rate_bpm' in df.columns:
            df_enhanced['HR_elevated'] = (df['Average_heart_rate_bpm'] > 80).astype(int)
        
        # Combined stress indicator
        if 'Stress_level_0_100' in df.columns and 'Sleep_h' in df.columns:
            df_enhanced['Stress_sleep_interaction'] = (
                df['Stress_level_0_100'] * (1 / (df['Sleep_h'] + 1))
            )
        
        # Weather-related features
        if 'Received_Air_Pressure_hPa' in df.columns:
            # Pressure deviation from standard
            df_enhanced['Pressure_deviation'] = abs(df['Received_Air_Pressure_hPa'] - 1013.25)
        
        return df_enhanced
    
    @staticmethod
    def create_temporal_features(df: pd.DataFrame, group_by: str = 'UserID') -> pd.DataFrame:
        """
        Create temporal features (rolling averages, trends, etc.)
        Useful for time-series analysis
        
        Parameters:
        -----------
        df : DataFrame
            Input data with 'Day' column
        group_by : str
            Column to group by (e.g., 'UserID')
        
        Returns:
        --------
        DataFrame with temporal features
        """
        df_temporal = df.copy()
        
        if 'Day' not in df.columns or group_by not in df.columns:
            return df_temporal
        
        # Sort by user and day
        df_temporal = df_temporal.sort_values([group_by, 'Day'])
        
        # Features to create rolling statistics for
        rolling_features = [
            'Sleep_h', 'Stress_level_0_100', 'Steps_and_activity',
            'Average_heart_rate_bpm', 'Screen_time_h'
        ]
        
        for feature in rolling_features:
            if feature in df_temporal.columns:
                # 3-day rolling average
                df_temporal[f'{feature}_3day_avg'] = (
                    df_temporal.groupby(group_by)[feature]
                    .rolling(window=3, min_periods=1)
                    .mean()
                    .reset_index(0, drop=True)
                )
                
                # Day-over-day change
                df_temporal[f'{feature}_change'] = (
                    df_temporal.groupby(group_by)[feature].diff()
                )
        
        return df_temporal


def load_and_validate_input(filepath: str) -> Tuple[pd.DataFrame, List[str]]:
    """
    Load input file and validate data
    
    Parameters:
    -----------
    filepath : str
        Path to CSV or Excel file
    
    Returns:
    --------
    (DataFrame, list of warnings)
    """
    # Load file
    if filepath.endswith('.csv'):
        df = pd.read_csv(filepath)
    elif filepath.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(filepath)
    else:
        raise ValueError("File must be CSV or Excel format")
    
    warnings = []
    
    # Validate each row
    for idx, row in df.iterrows():
        is_valid, errors = DataValidator.validate_input(row.to_dict())
        if not is_valid:
            warnings.append(f"Row {idx}: {'; '.join(errors)}")
    
    return df, warnings


def create_example_input(output_file: str = 'example_input.csv', num_rows: int = 5):
    """
    Create an example input file for testing
    
    Parameters:
    -----------
    output_file : str
        Output file path
    num_rows : int
        Number of example rows to create
    """
    np.random.seed(42)
    
    examples = []
    for _ in range(num_rows):
        example = {
            'Screen_time_h': np.random.uniform(2, 12),
            'Average_heart_rate_bpm': np.random.uniform(60, 85),
            'Steps_and_activity': np.random.uniform(2000, 12000),
            'Sleep_h': np.random.uniform(4, 9),
            'Stress_level_0_100': np.random.uniform(20, 80),
            'Respiration_rate_breaths_min': np.random.uniform(12, 18),
            'Saa_Temperature_average_C': np.random.uniform(18, 26),
            'Saa_Air_quality_0_5': np.random.choice([1, 2, 3, 4]),
            'Received_Condition_0_3': np.random.choice([0, 1, 2]),
            'Received_Air_Pressure_hPa': np.random.uniform(1000, 1025)
        }
        examples.append(example)
    
    df = pd.DataFrame(examples)
    df.to_csv(output_file, index=False)
    
    print(f"✓ Example input file created: {output_file}")
    print(f"  Contains {num_rows} sample rows")
    
    return df


if __name__ == '__main__':
    # Demo the utilities
    print("Data Utilities Demo\n")
    
    # Show feature info
    DataValidator.print_feature_info()
    
    # Create example input
    print("\nCreating example input file...")
    df_example = create_example_input('example_input.csv')
    print("\nExample data:")
    print(df_example.head())

