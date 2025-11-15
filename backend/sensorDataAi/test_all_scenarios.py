"""
Test all risk scenarios to verify model predictions
"""

from simple_predict import predict_migraine

print("\n" + "="*70)
print("TESTING ALL RISK SCENARIOS")
print("="*70)

# ============================================
# LOW RISK - Excellent health
# ============================================
print("\n📊 LOW RISK SCENARIO:")
print("   Sleep: 8.5h, Stress: 15, Steps: 12500, Screen: 3h, HR: 62")

low_risk = {
    'Screen_time_h': 3.0,
    'Average_heart_rate_bpm': 62,
    'Steps_and_activity': 12500,
    'Sleep_h': 8.5,
    'Stress_level_0_100': 15,
    'Respiration_rate_breaths_min': 11,
    'Saa_Temperature_average_C': 21.0,
    'Saa_Air_quality_0_5': 1,
    'Received_Condition_0_3': 0,
    'Received_Air_Pressure_hPa': 1016.0
}

r1 = predict_migraine('test_low', data=low_risk, explain=False)
print(f"   RESULT: {r1['probability']:.1f}% ({r1['risk_level']})")

# ============================================
# MODERATE RISK - Mixed health
# ============================================
print("\n📊 MODERATE RISK SCENARIO:")
print("   Sleep: 6.0h, Stress: 65, Steps: 5000, Screen: 8.5h, HR: 77")

moderate_risk = {
    'Screen_time_h': 8.5,
    'Average_heart_rate_bpm': 77,
    'Steps_and_activity': 5000,
    'Sleep_h': 6.0,
    'Stress_level_0_100': 65,
    'Respiration_rate_breaths_min': 16,
    'Saa_Temperature_average_C': 25.0,
    'Saa_Air_quality_0_5': 3,
    'Received_Condition_0_3': 1,
    'Received_Air_Pressure_hPa': 1010.0
}

r2 = predict_migraine('test_mod', data=moderate_risk, explain=False)
print(f"   RESULT: {r2['probability']:.1f}% ({r2['risk_level']})")

# ============================================
# HIGH RISK - Poor health
# ============================================
print("\n📊 HIGH RISK SCENARIO:")
print("   Sleep: 5.0h, Stress: 85, Steps: 3000, Screen: 11h, HR: 85")

high_risk = {
    'Screen_time_h': 11.0,
    'Average_heart_rate_bpm': 85,
    'Steps_and_activity': 3000,
    'Sleep_h': 5.0,
    'Stress_level_0_100': 85,
    'Respiration_rate_breaths_min': 18,
    'Saa_Temperature_average_C': 27.0,
    'Saa_Air_quality_0_5': 4,
    'Received_Condition_0_3': 2,
    'Received_Air_Pressure_hPa': 1006.0
}

r3 = predict_migraine('test_high', data=high_risk, explain=False)
print(f"   RESULT: {r3['probability']:.1f}% ({r3['risk_level']})")

# ============================================
# SUMMARY
# ============================================
print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print(f"\nLow Risk (excellent health):     {r1['probability']:.1f}%")
print(f"Moderate Risk (mixed health):    {r2['probability']:.1f}%")
print(f"High Risk (poor health):         {r3['probability']:.1f}%")

# Check if progression makes sense
print("\n" + "="*70)
if r1['probability'] < 20 and r2['probability'] > 30 and r2['probability'] < 70 and r3['probability'] > 70:
    print("✅ PASS: Model predictions follow expected pattern!")
    print(f"   Low < 20%: {r1['probability']:.1f}% ✓")
    print(f"   Moderate 30-70%: {r2['probability']:.1f}% ✓")
    print(f"   High > 70%: {r3['probability']:.1f}% ✓")
elif r1['probability'] == r2['probability'] == r3['probability']:
    print("❌ FAIL: Model gives same prediction for all scenarios!")
    print("   The model is not analyzing the data correctly.")
else:
    print("⚠️  WARNING: Predictions don't follow expected pattern")
    print(f"   Expected: Low<20%, Moderate 30-70%, High>70%")
    print(f"   Got: Low={r1['probability']:.1f}%, Mod={r2['probability']:.1f}%, High={r3['probability']:.1f}%")

print("="*70 + "\n")

