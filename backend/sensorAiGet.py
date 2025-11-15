import os
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv
from sensorDataAi.simple_predict import predict_migraine, train_user_model, store_training_data, get_user_info

load_dotenv()

supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

FEATURE_COLUMNS = [
    'Screen_time_h', 'Average_heart_rate_bpm', 'Steps_and_activity',
    'Sleep_h', 'Stress_level_0_100', 'Respiration_rate_breaths_min',
    'Saa_Temperature_average_C', 'Saa_Air_quality_0_5',
    'Received_Condition_0_3', 'Received_Air_Pressure_hPa'
]

def get_last_7_days_data(user_id):
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    response = supabase.table('daily_sensor') \
        .select('*') \
        .eq('user_id', user_id) \
        .gte('created_at', seven_days_ago) \
        .order('created_at', desc=False) \
        .execute()
    
    return response.data

def format_sensor_data(row):
    return {feature: row[feature] for feature in FEATURE_COLUMNS if row.get(feature) is not None}

def check_migraine_risk(user_id):
    rows = get_last_7_days_data(user_id)
    
    if not rows:
        return {'error': 'No data found for the last 7 days', 'user_id': user_id}
    
    days_data = [format_sensor_data(row) for row in rows]
    
    if not all(len(day) == len(FEATURE_COLUMNS) for day in days_data):
        return {'error': 'Incomplete sensor data found', 'user_id': user_id}
    
    try:
        result = predict_migraine(user_id, days_data=days_data, explain=False)
        return result
    except FileNotFoundError as e:
        return {
            'error': 'Model not trained',
            'message': str(e),
            'user_id': user_id,
            'data_points': len(rows)
        }

def train_user_model_from_db(user_id):
    response = supabase.table('daily_sensor') \
        .select('*') \
        .eq('user_id', user_id) \
        .not_.is_('Migraine_today_0_or_1', 'null') \
        .execute()
    
    if not response.data:
        return {'error': 'No training data with migraine outcomes found', 'user_id': user_id}
    
    stored_count = 0
    for row in response.data:
        sensor_data = format_sensor_data(row)
        sensor_data['Migraine_today_0_or_1'] = row['Migraine_today_0_or_1']
        
        if len(sensor_data) == len(FEATURE_COLUMNS) + 1:
            store_training_data(user_id, sensor_data)
            stored_count += 1
    
    if stored_count < 10:
        return {
            'error': 'Insufficient training data',
            'message': f'Only {stored_count} valid records found. Need at least 10.',
            'user_id': user_id
        }
    
    try:
        result = train_user_model(user_id)
        return {
            'success': True,
            'user_id': user_id,
            'data_points': result['data_points'],
            'accuracy': result['accuracy'],
            'message': 'Model trained successfully'
        }
    except Exception as e:
        return {'error': 'Training failed', 'message': str(e), 'user_id': user_id}

def get_user_model_status(user_id):
    info = get_user_info(user_id)
    return {
        'user_id': user_id,
        'has_model': info['has_model'],
        'data_points': info['data_points'],
        'can_train': info['can_train'],
        'status': info['status']
    }

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 3:
        print("\nUsage:")
        print("  python sensorAiGet.py predict <user_id>  - Check migraine risk")
        print("  python sensorAiGet.py train <user_id>    - Train/update user model")
        print("  python sensorAiGet.py status <user_id>   - Check model status")
        print("\nExamples:")
        print("  python sensorAiGet.py predict 123")
        print("  python sensorAiGet.py train 123")
        print("  python sensorAiGet.py status 123\n")
        sys.exit(1)
    
    action = sys.argv[1]
    user_id = int(sys.argv[2])
    
    if action == 'predict':
        result = check_migraine_risk(user_id)
        print("\nMigraine Risk Assessment:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()
    elif action == 'train':
        result = train_user_model_from_db(user_id)
        print("\nModel Training Result:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()
    elif action == 'status':
        result = get_user_model_status(user_id)
        print("\nUser Model Status:")
        for key, value in result.items():
            print(f"  {key}: {value}")
        print()
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)

