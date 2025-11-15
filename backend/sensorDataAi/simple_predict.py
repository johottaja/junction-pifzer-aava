"""
User-Specific Migraine Prediction System
- PERSONALIZED model for EACH user
- Each user has their own trained model based on their data
- Temporal analysis (7-day predictions) with user-specific patterns
"""

import os
import sys

# Handle both package import and direct script execution
try:
    from .user_model_manager import UserModelManager
except ImportError:
    from user_model_manager import UserModelManager

# Global model manager
_model_manager = None

def get_model_manager():
    """Get or create global model manager"""
    global _model_manager
    if _model_manager is None:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        _model_manager = UserModelManager(
            models_dir=os.path.join(script_dir, 'models'),
            user_data_dir=os.path.join(script_dir, 'user_data')
        )
    return _model_manager


def predict_migraine(user_id, data=None, days_data=None, explain=True):
    """
    Predict migraine probability for a specific user using THEIR personalized model
    
    Args:
        user_id (int): User identifier (e.g., 123, 456) - must be integer (int8)
        data (dict, optional): Single day of sensor data
        days_data (list, optional): List of 1-7 days of sensor data (oldest first)
        explain (bool): Whether to print explanation
    
    Returns:
        dict: {
            'user_id': str,
            'probability': float (0-100),
            'risk_level': str,
            'model_type': str ('personalized' or 'fallback')
        }
    
    Note: User must have a trained model first. Use store_training_data() to collect data,
          then train_user_model() to create their personalized model.
    """
    user_id = int(user_id)  # Ensure int8 format
    manager = get_model_manager()
    
    # Determine which data format was provided
    if days_data is not None:
        # Multi-day prediction
        if not isinstance(days_data, list) or len(days_data) == 0:
            raise ValueError("days_data must be a non-empty list")
        today_data = days_data[-1]  # Most recent day
        history_data = days_data[:-1] if len(days_data) > 1 else []
    elif data is not None:
        # Single day prediction
        today_data = data
        history_data = []
    else:
        raise ValueError("Must provide either 'data' or 'days_data'")
    
    # Check if user has a trained model
    if not manager.user_has_model(user_id):
        data_count = manager.get_user_data_count(user_id)
        raise FileNotFoundError(
            f"❌ No trained model found for user '{user_id}'.\n"
            f"   User has {data_count} data points.\n"
            f"   Please collect at least 10 data points with store_training_data(),\n"
            f"   then train the model with train_user_model('{user_id}')"
        )
    
    # Get base prediction from user's personalized model
    base_probability = manager.predict(user_id, today_data)
    
    # Apply temporal adjustment if we have history
    if len(history_data) > 0:
        adjustment = _calculate_temporal_adjustment(history_data, today_data)
        final_probability = min(100.0, max(0.0, base_probability + adjustment))
        
        if explain:
            print(f"\n{'='*70}")
            print(f"PERSONALIZED PREDICTION FOR USER: {user_id}")
            print(f"{'='*70}")
            print(f"Analysis period: {len(days_data)} days")
            print(f"Base prediction (user's model): {base_probability:.1f}%")
            print(f"Temporal adjustment: {adjustment:+.1f}%")
            print(f"Final prediction: {final_probability:.1f}%")
            print(f"{'='*70}\n")
    else:
        final_probability = base_probability
        
        if explain:
            print(f"\n{'='*70}")
            print(f"PERSONALIZED PREDICTION FOR USER: {user_id}")
            print(f"{'='*70}")
            print(f"Single-day prediction: {final_probability:.1f}%")
            print(f"Using user's personalized model")
            print(f"{'='*70}\n")
    
    # Determine risk level
    if final_probability < 20:
        risk_level = "Very Low"
    elif final_probability < 40:
        risk_level = "Low"
    elif final_probability < 60:
        risk_level = "Moderate"
    elif final_probability < 80:
        risk_level = "High"
    else:
        risk_level = "Very High"
    
    return {
        'user_id': user_id,
        'probability': final_probability,
        'risk_level': risk_level,
        'model_type': 'personalized'
    }


def _calculate_temporal_adjustment(history_data, today_data):
    """
    Calculate temporal adjustment based on historical patterns
    Returns adjustment to add to base probability (can be + or -)
    
    Balanced weighting - not too aggressive
    """
    import numpy as np
    
    adjustment = 0.0
    
    # Sleep debt analysis - MODERATE weight
    sleep_hours = [day['Sleep_h'] for day in history_data] + [today_data['Sleep_h']]
    avg_sleep = np.mean(sleep_hours)
    sleep_debt = max(0, (7.0 * len(sleep_hours)) - sum(sleep_hours))
    
    if sleep_debt > 7:  # More conservative threshold
        adjustment += min(10, sleep_debt * 1.0)  # Moderate weight
    
    # Stress accumulation - MODERATE weight
    stress_levels = [day['Stress_level_0_100'] for day in history_data] + [today_data['Stress_level_0_100']]
    high_stress_days = sum(1 for s in stress_levels if s > 70)
    
    if high_stress_days >= 3:  # Conservative threshold
        adjustment += min(8, high_stress_days * 2)  # Moderate weight
    
    # Consecutive poor days - MODERATE weight
    consecutive_poor = 0
    max_consecutive = 0
    for day in history_data + [today_data]:
        poor_indicators = 0
        if day['Sleep_h'] < 6.5:
            poor_indicators += 1
        if day['Stress_level_0_100'] > 70:
            poor_indicators += 1
        if day['Steps_and_activity'] < 5000:
            poor_indicators += 1
        if day['Screen_time_h'] > 8:
            poor_indicators += 1
        
        if poor_indicators >= 2:
            consecutive_poor += 1
            max_consecutive = max(max_consecutive, consecutive_poor)
        else:
            consecutive_poor = 0
    
    if max_consecutive >= 3:  # More conservative
        adjustment += min(15, max_consecutive * 4)  # Moderate weight
    
    # Activity decline trend - LIGHT weight
    activities = [day['Steps_and_activity'] for day in history_data] + [today_data['Steps_and_activity']]
    if len(activities) >= 3:
        if activities[-1] < activities[0] * 0.6:  # Significant decline only
            adjustment += 3  # Small boost
    
    # Screen time pattern - LIGHT weight
    screen_times = [day['Screen_time_h'] for day in history_data] + [today_data['Screen_time_h']]
    high_screen_days = sum(1 for st in screen_times if st > 9)  # Higher threshold
    
    if high_screen_days >= 4:  # More conservative
        adjustment += min(5, high_screen_days * 1)  # Light weight
    
    # Heart rate elevation - LIGHT weight
    heart_rates = [day['Average_heart_rate_bpm'] for day in history_data] + [today_data['Average_heart_rate_bpm']]
    elevated_hr_days = sum(1 for hr in heart_rates if hr > 78)  # Higher threshold
    
    if elevated_hr_days >= 4:  # More conservative
        adjustment += min(5, elevated_hr_days * 1)  # Light weight
    
    # Very poor sleep pattern - MODERATE weight
    very_poor_sleep_days = sum(1 for s in sleep_hours if s < 5.5)  # Very low threshold
    if very_poor_sleep_days >= 4:  # More conservative
        adjustment += min(8, very_poor_sleep_days * 2)
    
    # Extreme stress - MODERATE weight
    extreme_stress_days = sum(1 for s in stress_levels if s > 85)
    if extreme_stress_days >= 3:  # More conservative
        adjustment += min(10, extreme_stress_days * 3)
    
    return adjustment


def store_training_data(user_id, data):
    """
    Store user's sensor data with migraine outcome for training
    
    Args:
        user_id (int): User identifier (e.g., 123, 456) - must be integer (int8)
        data (dict): Training data with 11 fields:
                    - 10 sensor features
                    - Migraine_today_0_or_1 (0 or 1)
    
    Returns:
        int: Total number of data points stored for this user
    
    Example:
        data = {
            'Screen_time_h': 11.0,
            'Average_heart_rate_bpm': 85,
            'Steps_and_activity': 3000,
            'Sleep_h': 5.0,
            'Stress_level_0_100': 85,
            'Respiration_rate_breaths_min': 18,
            'Saa_Temperature_average_C': 27.0,
            'Saa_Air_quality_0_5': 4,
            'Received_Condition_0_3': 2,
            'Received_Air_Pressure_hPa': 1006.0,
            'Migraine_today_0_or_1': 1  # 1 = had migraine, 0 = no migraine
        }
        
        count = store_training_data(123, data)
        print(f"User now has {count} training data points")
    """
    user_id = int(user_id)  # Ensure int8 format
    manager = get_model_manager()
    
    if 'Migraine_today_0_or_1' not in data:
        raise ValueError("Training data must include 'Migraine_today_0_or_1' field (0 or 1)")
    
    total_count = manager.save_user_data(user_id, data)
    
    print(f"\n✓ Data stored for user '{user_id}'")
    print(f"  Total data points: {total_count}")
    
    if total_count >= 10:
        if not manager.user_has_model(user_id):
            print(f"\n💡 TIP: User has {total_count} data points. You can now train a personalized model!")
            print(f"     Run: train_user_model({user_id})")
        else:
            print(f"\n💡 TIP: User's model can be retrained with updated data!")
            print(f"     Run: train_user_model({user_id})")
    else:
        print(f"\n📊 Need {10 - total_count} more data points before training a model")
    
    return total_count


def train_user_model(user_id, min_data_points=10):
    """
    Train a personalized model for a specific user
    
    Args:
        user_id (int): User identifier (e.g., 123, 456) - must be integer (int8)
        min_data_points (int): Minimum data points required (default: 10)
    
    Returns:
        dict: Training results including accuracy and feature importance
    
    Example:
        # After collecting at least 10 data points
        result = train_user_model(123)
        print(f"Model trained with {result['data_points']} data points")
        print(f"Training accuracy: {result['accuracy']:.2f}%")
    """
    user_id = int(user_id)  # Ensure int8 format
    manager = get_model_manager()
    
    try:
        result = manager.train_user_model(user_id, min_data_points)
        print(f"\n✅ SUCCESS: Personalized model ready for user '{user_id}'")
        print(f"   You can now make predictions with predict_migraine({user_id}, ...)\n")
        return result
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}\n")
        raise


def get_user_info(user_id):
    """
    Get information about a user's data and model status
    
    Args:
        user_id (int): User identifier (e.g., 123, 456) - must be integer (int8)
    
    Returns:
        dict: User info including data count and model status
    """
    user_id = int(user_id)  # Ensure int8 format
    manager = get_model_manager()
    
    has_data = manager.user_has_data(user_id)
    has_model = manager.user_has_model(user_id)
    data_count = manager.get_user_data_count(user_id)
    
    info = {
        'user_id': user_id,
        'has_data': has_data,
        'has_model': has_model,
        'data_points': data_count,
        'can_train': data_count >= 10,
        'status': 'Unknown'
    }
    
    if not has_data:
        info['status'] = 'No data - start collecting with store_training_data()'
    elif data_count < 10:
        info['status'] = f'Need {10 - data_count} more data points before training'
    elif not has_model:
        info['status'] = 'Ready to train - call train_user_model()'
    else:
        info['status'] = 'Model trained - ready for predictions'
    
    return info


def list_all_users():
    """
    List all users in the system
    
    Returns:
        dict: Lists of users with data and/or models
    """
    manager = get_model_manager()
    return manager.list_all_users()

