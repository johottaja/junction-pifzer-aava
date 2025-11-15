from simple_predict import predict_migraine

# Test moderate risk
moderate = {
    'Screen_time_h': 10.0,
    'Average_heart_rate_bpm': 80,
    'Steps_and_activity': 4500,
    'Sleep_h': 5.5,
    'Stress_level_0_100': 70,
    'Respiration_rate_breaths_min': 17,
    'Saa_Temperature_average_C': 26.0,
    'Saa_Air_quality_0_5': 4,
    'Received_Condition_0_3': 2,
    'Received_Air_Pressure_hPa': 1007.0
}

r = predict_migraine(123, data=moderate, explain=False)
print(f"Moderate Risk: {r['probability']:.1f}% - {r['risk_level']}")

