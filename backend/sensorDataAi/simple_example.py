"""
Simple Example: High-Risk 7-Day Migraine Prediction
Shows a person with declining health over 7 days.
"""

from simple_predict import predict_migraine

# Last 7 days of data - declining health pattern
days_data = [
    # Day 7 ago - Good
    {'Screen_time_h': 5.5, 'Average_heart_rate_bpm': 68, 'Steps_and_activity': 9500,
     'Sleep_h': 7.8, 'Stress_level_0_100': 35, 'Respiration_rate_breaths_min': 14,
     'Saa_Temperature_average_C': 21.0, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0},
    
    # Day 6 ago - Good
    {'Screen_time_h': 6.0, 'Average_heart_rate_bpm': 70, 'Steps_and_activity': 10200,
     'Sleep_h': 8.0, 'Stress_level_0_100': 30, 'Respiration_rate_breaths_min': 13,
     'Saa_Temperature_average_C': 22.0, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0},
    
    # Day 5 ago - Declining
    {'Screen_time_h': 4, 'Average_heart_rate_bpm': 73, 'Steps_and_activity': 7000,
     'Sleep_h': 4, 'Stress_level_0_100': 55, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 23.0, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1013.0},
    
    # Day 4 ago - Worse
    {'Screen_time_h': 5, 'Average_heart_rate_bpm': 76, 'Steps_and_activity': 5500,
     'Sleep_h': 6.2, 'Stress_level_0_100': 45, 'Respiration_rate_breaths_min': 16,
     'Saa_Temperature_average_C': 24.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1011.0},
    
    # Day 3 ago - Poor
    {'Screen_time_h': 5.5, 'Average_heart_rate_bpm': 79, 'Steps_and_activity': 4800,
     'Sleep_h': 5.8, 'Stress_level_0_100': 45, 'Respiration_rate_breaths_min': 16,
     'Saa_Temperature_average_C': 25.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1010.0},
    
    # Yesterday - Poor
    {'Screen_time_h': 10.0, 'Average_heart_rate_bpm': 81, 'Steps_and_activity': 4200,
     'Sleep_h': 5.5, 'Stress_level_0_100': 78, 'Respiration_rate_breaths_min': 17,
     'Saa_Temperature_average_C': 25.5, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1009.0},
    
    # Today - Poor continues
    {'Screen_time_h': 10.5, 'Average_heart_rate_bpm': 83, 'Steps_and_activity': 3800,
     'Sleep_h': 5.2, 'Stress_level_0_100': 82, 'Respiration_rate_breaths_min': 17,
     'Saa_Temperature_average_C': 26.0, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1008.0}
]

# Make prediction
result = predict_migraine('patient123', days_data=days_data, explain=False)

# Print only the percentage
print(f"{result['probability']:.1f}%")
