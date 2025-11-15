from sensorDataAi.simple_predict import predict_migraine

# format to get the data.
days_data = [
    # 6 days ago
    {'Screen_time_h': 6.0, 'Average_heart_rate_bpm': 70, 
     'Steps_and_activity': 8000, 'Sleep_h': 7.0, 
     'Stress_level_0_100': 45, 'Respiration_rate_breaths_min': 14,
     'Saa_Temperature_average_C': 22.0, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 0, 'Received_Air_Pressure_hPa': 1013.0},
    
    # 5 days ago
    {'Screen_time_h': 7.0, 'Average_heart_rate_bpm': 72, 
     'Steps_and_activity': 7500, 'Sleep_h': 6.8, 
     'Stress_level_0_100': 50, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 23.0, 'Saa_Air_quality_0_5': 2,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1012.0},
    
    # 4 days ago
    {'Screen_time_h': 8.0, 'Average_heart_rate_bpm': 74, 
     'Steps_and_activity': 7000, 'Sleep_h': 6.5, 
     'Stress_level_0_100': 55, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 24.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1011.0},
    
    # 3 days ago
    {'Screen_time_h': 7.5, 'Average_heart_rate_bpm': 73, 
     'Steps_and_activity': 7200, 'Sleep_h': 6.7, 
     'Stress_level_0_100': 52, 'Respiration_rate_breaths_min': 15,
     'Saa_Temperature_average_C': 23.5, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1011.5},
    
    # 2 days ago
    {'Screen_time_h': 9.0, 'Average_heart_rate_bpm': 76, 
     'Steps_and_activity': 6000, 'Sleep_h': 6.0, 
     'Stress_level_0_100': 60, 'Respiration_rate_breaths_min': 16,
     'Saa_Temperature_average_C': 25.0, 'Saa_Air_quality_0_5': 3,
     'Received_Condition_0_3': 1, 'Received_Air_Pressure_hPa': 1010.0},
    
    # Yesterday
    {'Screen_time_h': 10.0, 'Average_heart_rate_bpm': 78, 
     'Steps_and_activity': 5500, 'Sleep_h': 5.8, 
     'Stress_level_0_100': 65, 'Respiration_rate_breaths_min': 16,
     'Saa_Temperature_average_C': 25.5, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1009.0},
    
    # Today (most recent)
    {'Screen_time_h': 11.0, 'Average_heart_rate_bpm': 80, 
     'Steps_and_activity': 5000, 'Sleep_h': 5.5, 
     'Stress_level_0_100': 70, 'Respiration_rate_breaths_min': 17,
     'Saa_Temperature_average_C': 26.0, 'Saa_Air_quality_0_5': 4,
     'Received_Condition_0_3': 2, 'Received_Air_Pressure_hPa': 1008.0}
]

# Get prediction
result = predict_migraine('user123', days_data=days_data, explain=True)

print(f"Migraine Probability: {result['probability']:.1f}%")