"""
Simple Example 1: Low-Risk 7-Day Migraine Prediction
Shows a person with excellent health over 7 days.
"""

from simple_predict import predict_migraine

# Last 7 days - excellent health (very low risk)
days_data = [
    # Day 7 ago - Excellent
    {'Screen_time_h': 3.5, 'Average_heart_rate_bpm': 63, 'Steps_and_activity': 12000,
     'Sleep_h': 8.5, 'Stress_level_0_100': 18, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.0, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0},
    
    # Day 6 ago - Excellent
    {'Screen_time_h': 4.0, 'Average_heart_rate_bpm': 64, 'Steps_and_activity': 11500,
     'Sleep_h': 8.3, 'Stress_level_0_100': 20, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.5, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0},
    
    # Day 5 ago - Excellent
    {'Screen_time_h': 3.8, 'Average_heart_rate_bpm': 62, 'Steps_and_activity': 12500,
     'Sleep_h': 8.6, 'Stress_level_0_100': 15, 'Respiration_rate_breaths_min': 11,
     'Saa_Temperature_average_C': 21.2, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1017.0},
    
    # Day 4 ago - Excellent
    {'Screen_time_h': 4.2, 'Average_heart_rate_bpm': 65, 'Steps_and_activity': 11800,
     'Sleep_h': 8.4, 'Stress_level_0_100': 22, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.8, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0},
    
    # Day 3 ago - Excellent
    {'Screen_time_h': 3.9, 'Average_heart_rate_bpm': 63, 'Steps_and_activity': 12200,
     'Sleep_h': 8.5, 'Stress_level_0_100': 19, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.5, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0},
    
    # Yesterday - Excellent
    {'Screen_time_h': 4.1, 'Average_heart_rate_bpm': 64, 'Steps_and_activity': 11900,
     'Sleep_h': 8.3, 'Stress_level_0_100': 21, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.3, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1015.0},
    
    # Today - Excellent
    {'Screen_time_h': 3.7, 'Average_heart_rate_bpm': 63, 'Steps_and_activity': 12100,
     'Sleep_h': 8.4, 'Stress_level_0_100': 20, 'Respiration_rate_breaths_min': 12,
     'Saa_Temperature_average_C': 21.4, 'Saa_Air_quality_0_5': 1,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1016.0}
]

# Make prediction
result = predict_migraine('healthy_patient', days_data=days_data, explain=False)

# Print only the percentage
print(f"{result['probability']:.1f}%")
