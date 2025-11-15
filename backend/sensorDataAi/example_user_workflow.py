"""
Example: Complete workflow for user-specific model training and prediction
"""

from simple_predict import (
    store_training_data, 
    train_user_model, 
    predict_migraine,
    get_user_info
)

print("\n" + "="*70)
print("USER-SPECIFIC MODEL EXAMPLE WORKFLOW")
print("="*70)

# ============================================================================
# STEP 1: Collect training data for a new user
# ============================================================================

user_id = 123  # Integer user ID (int8)

print(f"\n📊 STEP 1: Collecting training data for '{user_id}'...")
print("-" * 70)
print("NOTE: Training data = 10 sensor fields + Migraine_today_0_or_1 (11 total)")
print("      Prediction data = 10 sensor fields ONLY (no Migraine_today_0_or_1)\n")

# Simulate 15 days of data collection
# Each day has all 11 fields including Migraine_today_0_or_1
training_scenarios = [
    # Days with migraines (Migraine_today_0_or_1 = 1)
    {'Screen_time_h': 11.0, 'Average_heart_rate_bpm': 85, 'Steps_and_activity': 3000,
     'Sleep_h': 4.5, 'Stress_level_0_100': 90, 'Respiration_rate_breaths_min': 19,
     'Saa_Temperature_average_C': 27.0, 'Saa_Air_quality_0_5': 5,
     'Received_Condition_0_3': 3, 'Received_Air_Pressure_hPa': 1005.0,
     'Migraine_today_0_or_1': 1},
    
    
    {'Screen_time_h': 12.0, 'Average_heart_rate_bpm': 88, 'Steps_and_activity': 2500,
     'Sleep_h': 5.0, 'Stress_level_0_100': 85, 'Respiration_rate_breaths_min': 20,
     'Saa_Temperature_average_C': 28.0, 'Saa_Air_quality_0_5': 5,
     'Received_Condition_0_3': 3, 'Received_Air_Pressure_hPa': 1003.0,
     'Migraine_today_0_or_1': 1},
    
    {'Screen_time_h': 10.5, 'Average_heart_rate_bpm': 83, 'Steps_and_activity': 3200,
     'Sleep_h': 5.2, 'Stress_level_0_100': 88, 'Respiration_rate_breaths_min': 18,
     'Saa_Temperature_average_C': 26.5, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1006.0,
     'Migraine_today_0_or_1': 1},
    
    {'Screen_time_h': 11.5, 'Average_heart_rate_bpm': 86, 'Steps_and_activity': 2800,
     'Sleep_h': 4.8, 'Stress_level_0_100': 92, 'Respiration_rate_breaths_min': 19,
     'Saa_Temperature_average_C': 27.5, 'Saa_Air_quality_0_5': 5,
     'Received_Condition_0_3': 3, 'Received_Air_Pressure_hPa': 1004.0,
     'Migraine_today_0_or_1': 1},
    
    {'Screen_time_h': 13.0, 'Average_heart_rate_bpm': 90, 'Steps_and_activity': 2000,
     'Sleep_h': 4.0, 'Stress_level_0_100': 95, 'Respiration_rate_breaths_min': 21,
     'Saa_Temperature_average_C': 29.0, 'Saa_Air_quality_0_5': 5,
     'Received_Condition_0_3': 3, 'Received_Air_Pressure_hPa': 1002.0,
     'Migraine_today_0_or_1': 1},
    
    # Days without migraines (Migraine_today_0_or_1 = 0)
    {'Screen_time_h': 5.0, 'Average_heart_rate_bpm': 68, 'Steps_and_activity': 10000,
     'Sleep_h': 8.0, 'Stress_level_0_100': 30, 'Respiration_rate_breaths_min': 13,
     'Saa_Temperature_average_C': 21.0, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 5.5, 'Average_heart_rate_bpm': 67, 'Steps_and_activity': 10500,
     'Sleep_h': 7.8, 'Stress_level_0_100': 28, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 22.0, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 6.0, 'Average_heart_rate_bpm': 70, 'Steps_and_activity': 9800,
     'Sleep_h': 8.2, 'Stress_level_0_100': 25, 'Respiration_rate_breaths_min': 13,
     'Saa_Temperature_average_C': 21.5, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1014.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 5.2, 'Average_heart_rate_bpm': 69, 'Steps_and_activity': 10200,
     'Sleep_h': 7.5, 'Stress_level_0_100': 35, 'Respiration_rate_breaths_min': 14,
     'Saa_Temperature_average_C': 22.5, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 5.8, 'Average_heart_rate_bpm': 68, 'Steps_and_activity': 9500,
     'Sleep_h': 7.9, 'Stress_level_0_100': 33, 'Respiration_rate_breaths_min': 13,
     'Saa_Temperature_average_C': 22.0, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0,
     'Migraine_today_0_or_1': 0},
    
    # Mixed scenarios (no migraine)
    {'Screen_time_h': 7.5, 'Average_heart_rate_bpm': 74, 'Steps_and_activity': 7000,
     'Sleep_h': 6.8, 'Stress_level_0_100': 50, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 24.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1011.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 8.0, 'Average_heart_rate_bpm': 76, 'Steps_and_activity': 6500,
     'Sleep_h': 6.5, 'Stress_level_0_100': 55, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 24.5, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1010.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 9.0, 'Average_heart_rate_bpm': 78, 'Steps_and_activity': 5500,
     'Sleep_h': 6.2, 'Stress_level_0_100': 62, 'Respiration_rate_breaths_min': 16,
     'Saa_Temperature_average_C': 25.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1009.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 9.5, 'Average_heart_rate_bpm': 80, 'Steps_and_activity': 5000,
     'Sleep_h': 6.0, 'Stress_level_0_100': 68, 'Respiration_rate_breaths_min': 17,
     'Saa_Temperature_average_C': 25.5, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1008.0,
     'Migraine_today_0_or_1': 0},
    
    {'Screen_time_h': 10.0, 'Average_heart_rate_bpm': 82, 'Steps_and_activity': 4500,
     'Sleep_h': 5.8, 'Stress_level_0_100': 72, 'Respiration_rate_breaths_min': 17,
     'Saa_Temperature_average_C': 26.0, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1007.0,
     'Migraine_today_0_or_1': 0},
]

# Store all training data
for i, data in enumerate(training_scenarios, 1):
    status = "MIGRAINE" if data['Migraine_today_0_or_1'] == 1 else "No migraine"
    print(f"  Day {i}: {status}")
    count = store_training_data(user_id, data)

print(f"\n✓ Collected {count} training data points")

# ============================================================================
# STEP 2: Train user's personalized model
# ============================================================================

print(f"\n🤖 STEP 2: Training personalized model for '{user_id}'...")
print("-" * 70)

result = train_user_model(user_id)

print(f"\n✓ Model trained successfully!")
print(f"  Training accuracy: {result['accuracy']:.2f}%")
print(f"  Migraine days: {result['migraine_count']}")
print(f"  Healthy days: {result['no_migraine_count']}")

# ============================================================================
# STEP 3: Make predictions
# ============================================================================

print(f"\n🔮 STEP 3: Making predictions with personalized model...")
print("-" * 70)

# Test 1: Low risk scenario
print("\nTest 1: Low Risk Scenario (Healthy day)")
print("        (Note: NO 'Had_Migraine' field - only 10 sensor fields)")
low_risk_data = {
    'Screen_time_h': 5.5,
    'Average_heart_rate_bpm': 68,
    'Steps_and_activity': 10000,
    'Sleep_h': 8.0,
    'Stress_level_0_100': 30,
    'Respiration_rate_breaths_min': 13,
    'Saa_Temperature_average_C': 21.5,
    'Saa_Air_quality_0_5': 1,
    'Received_Condition_0_3': 0,
    'Received_Air_Pressure_hPa': 1015.0
}

result_low = predict_migraine(user_id, data=low_risk_data, explain=False)
print(f"  Prediction: {result_low['probability']:.1f}% ({result_low['risk_level']})")

# Test 2: High risk scenario
print("\nTest 2: High Risk Scenario (Poor health)")
print("        (Note: NO 'Had_Migraine' field - only 10 sensor fields)")
high_risk_data = {
    'Screen_time_h': 12.0,
    'Average_heart_rate_bpm': 88,
    'Steps_and_activity': 2500,
    'Sleep_h': 4.5,
    'Stress_level_0_100': 92,
    'Respiration_rate_breaths_min': 20,
    'Saa_Temperature_average_C': 28.0,
    'Saa_Air_quality_0_5': 5,
    'Received_Condition_0_3': 3,
    'Received_Air_Pressure_hPa': 1003.0
}

result_high = predict_migraine(user_id, data=high_risk_data, explain=False)
print(f"  Prediction: {result_high['probability']:.1f}% ({result_high['risk_level']})")

# Test 3: Moderate risk scenario
print("\nTest 3: Moderate Risk Scenario (Mixed - some risk factors)")
print("        (Note: NO 'Had_Migraine' field - only 10 sensor fields)")
moderate_risk_data = {
    'Screen_time_h': 10.0,  # Higher screen time
    'Average_heart_rate_bpm': 80,  # Elevated
    'Steps_and_activity': 4500,  # Lower activity
    'Sleep_h': 5.5,  # Poor sleep
    'Stress_level_0_100': 70,  # Elevated stress
    'Respiration_rate_breaths_min': 17,
    'Saa_Temperature_average_C': 26.0,  # Warmer
    'Saa_Air_quality_0_5': 4,  # Poor air quality
    'Received_Condition_0_3': 2,
    'Received_Air_Pressure_hPa': 1007.0  # Lower pressure
}

result_mod = predict_migraine(user_id, data=moderate_risk_data, explain=False)
print(f"  Prediction: {result_mod['probability']:.1f}% ({result_mod['risk_level']})")

# ============================================================================
# STEP 4: Check user info
# ============================================================================

print(f"\n📋 STEP 4: User information...")
print("-" * 70)

info = get_user_info(user_id)
print(f"\nUser ID: {info['user_id']}")
print(f"Data points: {info['data_points']}")
print(f"Has model: {info['has_model']}")
print(f"Status: {info['status']}")

# ============================================================================
# SUMMARY
# ============================================================================

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\n✅ User '{user_id}' has a fully trained personalized model")
print(f"✅ Model learned from {result['data_points']} data points")
print(f"✅ Training accuracy: {result['accuracy']:.2f}%")
print(f"\nPrediction Results:")
print(f"  Low Risk:      {result_low['probability']:.1f}% - {result_low['risk_level']}")
print(f"  Moderate Risk: {result_mod['probability']:.1f}% - {result_mod['risk_level']}")
print(f"  High Risk:     {result_high['probability']:.1f}% - {result_high['risk_level']}")
print("\n✅ User-specific model system working correctly!")
print("="*70 + "\n")

