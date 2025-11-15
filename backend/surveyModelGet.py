import os
import sys
from datetime import datetime, timedelta
from supabase import create_client
from dotenv import load_dotenv

# Add survey_model to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'survey_model'))
from survey_model.inference import predict_fastapi_format

# Load environment variables
# Try multiple paths to find .env file
env_paths = [
    os.path.join(os.path.dirname(__file__), '.env'),  # backend/.env
    os.path.join(os.path.dirname(__file__), '../.env'),  # root/.env
    '.env',  # Current directory
    os.path.join(os.getcwd(), '.env'),  # Working directory
]

for env_path in env_paths:
    abs_path = os.path.abspath(env_path)
    if os.path.exists(abs_path):
        load_dotenv(abs_path)
        print(f"[surveyModelGet] Loaded .env from: {abs_path}")
        break
else:
    # Try default load_dotenv behavior
    load_dotenv()
    print("[surveyModelGet] Warning: Using default load_dotenv() - .env file may not be found")

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("[surveyModelGet] WARNING: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY not set. Some functions may not work.")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_last_7_days_survey_data(user_id):
    """
    Fetch last 7 days of survey data from daily_form table.
    Returns list of dictionaries, sorted by created_at (oldest first).
    """
    if not supabase:
        raise ValueError("Supabase client not initialized. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.")
    
    seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
    
    response = supabase.table('daily_form') \
        .select('*') \
        .eq('user_id', user_id) \
        .gte('created_at', seven_days_ago) \
        .order('created_at', desc=False) \
        .execute()
    
    return response.data

def get_user_profile(user_id):
    """
    Fetch user profile (age, gender) from users table.
    Returns dict with age and gender, or None if not found.
    """
    if not supabase:
        return None
    
    try:
        response = supabase.table('users') \
            .select('age, gender') \
            .eq('user_id', user_id) \
            .execute()
        
        if response.data and len(response.data) > 0:
            user_data = response.data[0]
            return {
                'age': user_data.get('age'),
                'gender': user_data.get('gender')
            }
        return None
    except Exception as e:
        print(f"Error fetching user profile: {e}")
        return None

def format_survey_data(row):
    """
    Format a single row from daily_form table.
    Converts boolean fields to 1/0 format expected by the model.
    """
    formatted = {}
    
    # Include all survey feature columns (boolean fields)
    survey_features = [
        'stress', 'oversleep', 'sleep_deprivation', 'exercise', 'fatigue',
        'menstrual', 'emotional_distress', 'excessive_noise', 'excessive_smells',
        'excessive_alcohol', 'irregular_meals', 'overeating', 'excessive_caffeine',
        'excessive_smoking', 'travel'
    ]
    
    for feature in survey_features:
        value = row.get(feature)
        # Convert boolean to 1/0, None to 0
        if isinstance(value, bool):
            formatted[feature] = 1 if value else 0
        elif value is None:
            formatted[feature] = 0
        else:
            formatted[feature] = int(value) if value else 0
    
    # Include created_at for sorting
    if 'created_at' in row:
        formatted['created_at'] = row['created_at']
    
    # Include user_id
    if 'user_id' in row:
        formatted['user_id'] = row['user_id']
    
    return formatted

def check_migraine_risk_from_survey(user_id):
    """
    Check migraine risk using survey data from daily_form table.
    Fetches last 7 days of data and runs prediction.
    
    Returns:
        dict with 'probability' (0-1), 'top_features', 'user_id', 'model_type'
        OR dict with 'error' if something went wrong
    """
    try:
        # Fetch last 7 days of survey data
        rows = get_last_7_days_survey_data(user_id)
        
        if not rows:
            return {
                'error': 'No survey data found for the last 7 days',
                'user_id': user_id
            }
        
        # Check if we have at least 7 days of data
        if len(rows) < 7:
            return {
                'error': f'Insufficient data: found {len(rows)} days, need 7 days',
                'user_id': user_id,
                'data_points': len(rows)
            }
        
        # Format the data
        formatted_data = [format_survey_data(row) for row in rows]
        
        # Get user profile (age, gender) for better prediction
        user_profile = get_user_profile(user_id)
        age = user_profile.get('age') if user_profile else None
        gender = user_profile.get('gender') if user_profile else None
        
        # Fix the MODEL_PATH in inference.py to use absolute path
        # inference.py uses relative path "models/best_model.pkl" which doesn't work
        # when called from different directories
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        survey_model_dir = os.path.join(backend_dir, 'survey_model')
        model_path_absolute = os.path.join(survey_model_dir, 'models', 'best_model.pkl')
        
        # Temporarily patch inference.MODEL_PATH to use absolute path
        import survey_model.inference as inference_module
        original_model_path = inference_module.MODEL_PATH
        inference_module.MODEL_PATH = model_path_absolute
        
        try:
            # Run prediction with patched MODEL_PATH
            result = predict_fastapi_format(
                logs_list=formatted_data,
                user_id=user_id,
                age=age,
                gender=gender
            )
            
            # Convert probability from 0-1 to 0-100 percentage for consistency
            probability_percentage = result['probability'] * 100
            
            return {
                'user_id': user_id,
                'probability': probability_percentage,  # Percentage (0-100)
                'risk_level': 'low' if probability_percentage < 40 else ('medium' if probability_percentage < 60 else 'high'),
                'top_features': result.get('top_features', []),
                'model_type': 'survey_model',
                'data_points': len(rows)
            }
        except FileNotFoundError as e:
            return {
                'error': 'Model not found or not trained',
                'message': str(e),
                'user_id': user_id
            }
        finally:
            # Always restore original MODEL_PATH
            inference_module.MODEL_PATH = original_model_path
    except Exception as e:
        return {
            'error': 'Prediction failed',
            'message': str(e),
            'user_id': user_id
        }

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python surveyModelGet.py <user_id>  - Check migraine risk from survey data")
        print("\nExample:")
        print("  python surveyModelGet.py 1\n")
        sys.exit(1)
    
    user_id = int(sys.argv[1])
    
    result = check_migraine_risk_from_survey(user_id)
    print("\nSurvey-Based Migraine Risk Assessment:")
    for key, value in result.items():
        print(f"  {key}: {value}")
    print()

