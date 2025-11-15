"""
Quick Test - Copy this code to use in your own files
"""

from predict import predict_single

# Example: Get migraine prediction from sensor data
def get_migraine_chance(data):
    """
    Simple function: input data, get percentage (0-100)
    """
    result = predict_single(data, explain=False)
    return result['probability']


# Test it!
if __name__ == '__main__':
    # Your sensor data
    my_data = {
        'Screen_time_h': 7.5,
        'Average_heart_rate_bpm': 75,
        'Steps_and_activity': 8500,
        'Sleep_h': 6.5,
        'Migraine_today_0_or_1': 0,
        'Stress_level_0_100': 60,
        'Respiration_rate_breaths_min': 15,
        'Saa_Temperature_average_C': 22.0,
        'Saa_Air_quality_0_5': 3,
        'Received_Condition_0_3': 1,
        'Received_Air_Pressure_hPa': 1013.25
    }
    
    # Get prediction
    chance = get_migraine_chance(my_data)
    
    print(f"\n🧠 Migraine Probability: {chance}%")
    
    if chance > 70:
        print("🚨 HIGH RISK - Take preventive measures!")
    elif chance > 40:
        print("⚠️  MODERATE RISK - Be careful")
    else:
        print("✅ LOW RISK - You're good!")

