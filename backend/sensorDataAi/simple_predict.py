"""
Simple Migraine Prediction System
- ONE model for all users
- No per-user files
- Just store data to training pool and make predictions
"""

from predict import predict_single
from data_utils import PersonalizedDataHandler

# Global data handler
_data_handler = None

def get_data_handler():
    """Get or create global data handler"""
    global _data_handler
    if _data_handler is None:
        _data_handler = PersonalizedDataHandler(data_dir='user_data')
    return _data_handler


def predict_migraine(user_id, data=None, days_data=None, explain=True):
    """
    Make migraine prediction for any user
    
    Can use either single day OR multiple days (1-7 days) for better accuracy.
    
    Parameters:
    -----------
    user_id : str
        User identifier (for tracking only)
    data : dict, optional
        Single day's sensor/health data (10 parameters, NO migraine field)
    days_data : list of dict, optional
        List of 1-7 days of data (most recent last)
        Better predictions with more days!
    explain : bool
        Show detailed explanation
    
    Returns:
    --------
    dict with 'probability', 'risk_level', 'recommendation', 'days_analyzed'
    
    Example (Single Day):
    ---------------------
    result = predict_migraine('patient123', data={
        'Screen_time_h': 8.0,
        'Average_heart_rate_bpm': 75,
        'Steps_and_activity': 6000,
        'Sleep_h': 6.5,
        'Stress_level_0_100': 65,
        'Respiration_rate_breaths_min': 16,
        'Saa_Temperature_average_C': 24.0,
        'Saa_Air_quality_0_5': 3,
        'Received_Condition_0_3': 1,
        'Received_Air_Pressure_hPa': 1010.0
    })
    
    Example (Multiple Days - BETTER):
    ----------------------------------
    result = predict_migraine('patient123', days_data=[
        {...day 7 ago...},
        {...day 6 ago...},
        {...day 5 ago...},
        {...yesterday...},
        {...today...}  # Most recent last
    ])
    
    print(f"Risk: {result['probability']}% (analyzed {result['days_analyzed']} days)")
    """
    if explain:
        print(f"\n{'='*70}")
        print(f"MIGRAINE PREDICTION FOR USER '{user_id}'")
        print(f"{'='*70}")
    
    # Determine how many days we're analyzing
    if days_data is not None:
        num_days = len(days_data)
        if num_days < 1 or num_days > 7:
            raise ValueError("days_data must contain 1-7 days of data")
        
        # Use the most recent day as "today"
        today_data = days_data[-1]
        history_data = days_data[:-1] if num_days > 1 else []
        
        if explain:
            print(f"\n📊 Analyzing {num_days} days of data")
            if history_data:
                print(f"   - Historical days: {len(history_data)}")
                print(f"   - Today (prediction day): 1")
    elif data is not None:
        num_days = 1
        today_data = data
        history_data = []
        
        if explain:
            print(f"\n📊 Analyzing 1 day of data (single-day prediction)")
    else:
        raise ValueError("Must provide either 'data' (single day) or 'days_data' (1-7 days)")
    
    # Make base prediction for today
    base_result = predict_single(today_data, explain=False)
    base_probability = base_result['probability']
    
    # Apply temporal adjustments if we have history
    if history_data:
        adjustment = _calculate_temporal_adjustment(history_data, today_data)
        adjusted_probability = min(100, max(0, base_probability + adjustment))
        
        if explain and adjustment != 0:
            print(f"\n📈 Temporal Analysis:")
            print(f"   Base prediction: {base_probability:.1f}%")
            print(f"   Temporal adjustment: {adjustment:+.1f}%")
            print(f"   Final prediction: {adjusted_probability:.1f}%")
    else:
        adjusted_probability = base_probability
        adjustment = 0
    
    # Determine risk level
    if adjusted_probability < 15:
        risk_level = "Very Low"
    elif adjusted_probability < 30:
        risk_level = "Low"
    elif adjusted_probability < 70:
        risk_level = "Moderate"
    elif adjusted_probability < 85:
        risk_level = "High"
    else:
        risk_level = "Very High"
    
    # Get recommendation
    recommendations = {
        "Very Low": "Low risk of migraine. Continue monitoring your health.",
        "Low": "Low risk. Maintain current healthy habits.",
        "Moderate": "Moderate risk. Avoid known triggers and ensure adequate rest.",
        "High": "High risk. Take preventive measures and prepare medication.",
        "Very High": "Very high risk. Consider consulting healthcare provider and take immediate preventive action."
    }
    recommendation = recommendations.get(risk_level, "Monitor your health.")
    
    result = {
        'probability': adjusted_probability,
        'base_probability': base_probability,
        'temporal_adjustment': adjustment,
        'risk_level': risk_level,
        'recommendation': recommendation,
        'days_analyzed': num_days
    }
    
    if explain:
        print(f"\n{'='*70}")
        print(f"PREDICTION RESULT")
        print(f"{'='*70}")
        print(f"\n🎯 Migraine Probability: {result['probability']:.1f}%")
        print(f"📊 Days Analyzed: {result['days_analyzed']}")
        if adjustment != 0:
            print(f"📈 Temporal Impact: {adjustment:+.1f}%")
        print(f"⚠️  Risk Level: {result['risk_level']}")
        print(f"💡 {result['recommendation']}\n")
    
    return result


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


def store_training_data(user_id, data, migraine_occurred):
    """
    Store data with migraine outcome to training pool
    
    Parameters:
    -----------
    user_id : str
        User identifier (for tracking)
    data : dict
        Sensor/health data (10 parameters)
    migraine_occurred : bool
        Did migraine actually occur? True/False
    
    Returns:
    --------
    dict with 'total_records'
    
    Example:
    --------
    store_training_data('patient123', {
        'Screen_time_h': 8.0,
        ... (10 parameters) ...
    }, migraine_occurred=True)
    """
    print(f"\n{'='*70}")
    print(f"STORING TRAINING DATA FOR USER '{user_id}'")
    print(f"{'='*70}")
    
    handler = get_data_handler()
    
    # Save to training pool
    total_records = handler.save_user_data(
        user_id=user_id,
        data=data,
        migraine_occurred=migraine_occurred
    )
    
    print(f"\n✓ Data stored successfully!")
    print(f"   - User ID: {user_id}")
    print(f"   - Migraine occurred: {'YES' if migraine_occurred else 'NO'}")
    print(f"   - Total records in pool: {total_records}")
    
    return {'total_records': total_records}


if __name__ == '__main__':
    print("\n" + "="*70)
    print("SIMPLE MIGRAINE PREDICTION SYSTEM")
    print("="*70)
    print("\nONE model for ALL users - Simple and effective!")
    
    # Example prediction
    test_data = {
        'Screen_time_h': 8.0,
        'Average_heart_rate_bpm': 75,
        'Steps_and_activity': 6000,
        'Sleep_h': 6.5,
        'Stress_level_0_100': 65,
        'Respiration_rate_breaths_min': 16,
        'Saa_Temperature_average_C': 24.0,
        'Saa_Air_quality_0_5': 3,
        'Received_Condition_0_3': 1,
        'Received_Air_Pressure_hPa': 1010.0
    }
    
    result = predict_migraine('demo_user', test_data)
    
    print("\n💡 Usage:")
    print("   PREDICT: predict_migraine(user_id, data)")
    print("   STORE:   store_training_data(user_id, data, migraine_occurred=True/False)")
    print()

