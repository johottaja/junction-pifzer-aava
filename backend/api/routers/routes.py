from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from supabase import create_client
import os
import sys
from dotenv import load_dotenv

from ..dependencies.auth import get_current_user

# Add parent directories to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../survey_model'))
sys.path.append(os.path.join(os.path.dirname(__file__), '../../sensorDataAi'))

# Import prediction functions
try:
    from survey_model.inference import predict_fastapi_format
except ImportError as e:
    print(f"Warning: Could not import survey_model.inference: {e}")
    predict_fastapi_format = None

try:
    from sensorDataAi.predict import MigrainePredictionSystem
except ImportError as e:
    print(f"Warning: Could not import sensorDataAi.predict: {e}")
    MigrainePredictionSystem = None

# Load environment variables
# Try multiple paths to find .env file
env_paths = [
    os.path.join(os.path.dirname(__file__), '../../.env'),  # backend/.env
    os.path.join(os.path.dirname(__file__), '../../../.env'),  # root/.env
    '.env',  # Current directory
    os.path.join(os.getcwd(), '.env'),  # Working directory
]

for env_path in env_paths:
    abs_path = os.path.abspath(env_path)
    if os.path.exists(abs_path):
        load_dotenv(abs_path)
        print(f"Loaded .env from: {abs_path}")
        break
else:
    # Try default load_dotenv behavior
    load_dotenv()
    print("Warning: Using default load_dotenv() - .env file may not be found")

# Initialize Supabase client
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("WARNING: SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY not set. Some endpoints may not work.")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Create router for all API endpoints
router = APIRouter(
    tags=["api"],   # For API documentation grouping
)

# ============================================================================
# Pydantic Models
# ============================================================================

class UserResponse(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    created_at: Optional[str] = None

class UserInfoResponse(BaseModel):
    success: bool
    user: UserResponse

# ============================================================================
# User Endpoints
# ============================================================================

@router.get("/users/{user_id}", response_model=UserInfoResponse)
async def get_user_info(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get user information by user_id.
    Route: GET /users/{user_id}
    Requires authentication via session cookie.
    """
    # Verify that the authenticated user can access this user_id
    if current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own user information.",
        )
    
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        
        user_data = response.data[0]
        
        return UserInfoResponse(
            success=True,
            user=UserResponse(
                user_id=user_data.get("id", user_id),
                email=user_data.get("email"),
                name=user_data.get("name"),
                created_at=user_data.get("created_at"),
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user data: {str(e)}",
        )

@router.get("/users/me", response_model=UserInfoResponse)
async def get_current_user_info(
    current_user: dict = Depends(get_current_user)
):
    """
    Get the currently authenticated user's information.
    Route: GET /users/me
    No user_id needed - uses the authenticated user from the session.
    """
    user_id = current_user.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in session.",
        )
    
    try:
        response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        
        user_data = response.data[0]
        
        return UserInfoResponse(
            success=True,
            user=UserResponse(
                user_id=user_data.get("id", user_id),
                email=user_data.get("email"),
                name=user_data.get("name"),
                created_at=user_data.get("created_at"),
            )
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user data: {str(e)}",
        )

# ============================================================================
# Migraine Data Endpoints
# ============================================================================

class MigraineDataResponse(BaseModel):
    success: bool
    user_id: str
    survey_prediction: Optional[Dict[str, Any]] = None
    sensor_prediction: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

class ReportSubmissionRequest(BaseModel):
    # Exact database schema fields
    had_migraine: Optional[bool] = None
    stress: Optional[bool] = False
    oversleep: Optional[bool] = False
    sleep_deprivation: Optional[bool] = False
    exercise: Optional[bool] = False
    fatigue: Optional[bool] = False
    menstrual: Optional[bool] = False
    emotional_distress: Optional[bool] = False
    excessive_noise: Optional[bool] = False
    excessive_smells: Optional[bool] = False
    excessive_alcohol: Optional[bool] = False
    irregular_meals: Optional[bool] = False
    overeating: Optional[bool] = False
    excessive_caffeine: Optional[bool] = False
    excessive_smoking: Optional[bool] = False
    travel: Optional[bool] = False
    
    # Legacy fields for backward compatibility (will be removed when frontend is updated)
    intensity: Optional[int] = None  # Will map to had_migraine if provided
    triggers: Optional[List[str]] = None  # Will be mapped to boolean fields
    symptoms: Optional[List[str]] = None  # Not stored in daily_form

class ReportSubmissionResponse(BaseModel):
    success: bool
    message: str
    log_id: Optional[int] = None

@router.get("/get-migraine-data/{user_id}", response_model=MigraineDataResponse)
async def get_migraine_data(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get migraine prediction data for a user.
    Combines predictions from survey_model and sensorDataAi.
    Route: GET /get-migraine-data/{user_id}
    Requires authentication via session cookie.
    """
    # Verify that the authenticated user can access this user_id
    if current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own migraine data.",
        )
    
    if not supabase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Supabase is not configured. Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env file.",
        )
    
    try:
        # Fetch user info from Supabase
        user_response = supabase.table("users").select("*").eq("id", user_id).execute()
        
        if not user_response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        
        user_data = user_response.data[0]
        age = user_data.get("age")
        sex = user_data.get("sex", user_data.get("gender", "male"))  # Try both field names
        
        if not age:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User age not found. Please update your profile.",
            )
        
        # Initialize response
        response_data = {
            "success": True,
            "user_id": user_id,
            "survey_prediction": None,
            "sensor_prediction": None,
            "error": None
        }
        
        # ========================================================================
        # 1. Survey Model Prediction (from survey_model/inference.py)
        # ========================================================================
        if predict_fastapi_format:
            try:
                # Fetch last 7 days of survey logs from Supabase
                # Adjust table name based on your Supabase schema
                survey_logs_response = supabase.table("survey_logs").select("*").eq("user_id", user_id).order("date", desc=True).limit(7).execute()
                
                if survey_logs_response.data and len(survey_logs_response.data) >= 7:
                    # Convert to list of dicts (last 7 days, oldest first)
                    logs_list = list(reversed(survey_logs_response.data))
                    
                    # Run survey model prediction
                    survey_result = predict_fastapi_format(
                        logs_list=logs_list,
                        user_id=user_id,
                        age=age,
                        sex=sex
                    )
                    response_data["survey_prediction"] = survey_result
                else:
                    response_data["error"] = "Insufficient survey data. Need at least 7 days of survey logs."
                    
            except Exception as e:
                print(f"Error in survey prediction: {e}")
                response_data["error"] = f"Survey prediction error: {str(e)}"
        else:
            response_data["error"] = "Survey model not available."
        
        # ========================================================================
        # 2. Sensor Data Prediction (from sensorDataAi/predict.py)
        # ========================================================================
        if MigrainePredictionSystem:
            try:
                # Initialize prediction system with correct model path
                # Adjust path based on your project structure
                model_path = os.path.join(os.path.dirname(__file__), '../../sensorDataAi/models')
                prediction_system = MigrainePredictionSystem(model_path=model_path)
                
                # Fetch today's sensor data from Supabase
                # Adjust table name and date field based on your schema
                from datetime import datetime
                today = datetime.now().date().isoformat()
                
                sensor_data_response = supabase.table("sensor_data").select("*").eq("user_id", user_id).eq("date", today).limit(1).execute()
                
                if sensor_data_response.data:
                    sensor_data = sensor_data_response.data[0]
                    
                    # Map Supabase fields to model expected fields
                    # Adjust field names based on your schema
                    sensor_dict = {
                        'Screen_time_h': sensor_data.get('screen_time', 0),
                        'Average_heart_rate_bpm': sensor_data.get('heart_rate', 0),
                        'Steps_and_activity': sensor_data.get('steps', 0),
                        'Sleep_h': sensor_data.get('sleep_hours', 0),
                        'Stress_level_0_100': sensor_data.get('stress_level', 0),
                        'Respiration_rate_breaths_min': sensor_data.get('respiration_rate', 0),
                        'Saa_Temperature_average_C': sensor_data.get('temperature', 0),
                        'Saa_Air_quality_0_5': sensor_data.get('air_quality', 0),
                        'Received_Condition_0_3': sensor_data.get('condition', 0),
                        'Received_Air_Pressure_hPa': sensor_data.get('air_pressure', 0),
                    }
                    
                    # Run sensor model prediction
                    sensor_result = prediction_system.predict_from_dict(sensor_dict)
                    response_data["sensor_prediction"] = sensor_result
                else:
                    if not response_data.get("error"):
                        response_data["error"] = "No sensor data available for today."
                    else:
                        response_data["error"] += " No sensor data available for today."
                        
            except Exception as e:
                print(f"Error in sensor prediction: {e}")
                if not response_data.get("error"):
                    response_data["error"] = f"Sensor prediction error: {str(e)}"
                else:
                    response_data["error"] += f" Sensor prediction error: {str(e)}"
        else:
            if not response_data.get("error"):
                response_data["error"] = "Sensor model not available."
            else:
                response_data["error"] += " Sensor model not available."
        
        return MigraineDataResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching migraine data: {str(e)}",
        )

# ============================================================================
# Report Submission Endpoints
# ============================================================================

@router.post("/submit-report", response_model=ReportSubmissionResponse)
async def submit_report(
    report_data: ReportSubmissionRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Submit a daily migraine report.
    Route: POST /submit-report
    Requires authentication via session cookie.
    
    Accepts data matching the database schema exactly:
    - All boolean fields from daily_form table
    - Legacy support: intensity/triggers will be mapped to boolean fields
    """
    user_id = current_user.get("id")
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in session.",
        )
    
    try:
        # Convert user_id to int (database expects bigint)
        try:
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format.",
            )
        
        # Build database payload with exact schema fields
        db_data = {
            'user_id': user_id_int,
        }
        
        # Handle had_migraine - check if explicitly provided or map from legacy intensity
        if report_data.had_migraine is not None:
            db_data['had_migraine'] = report_data.had_migraine
        elif report_data.intensity is not None:
            # Legacy: map intensity to had_migraine
            if report_data.intensity < 1 or report_data.intensity > 10:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Intensity must be between 1 and 10.",
                )
            db_data['had_migraine'] = report_data.intensity > 0
        else:
            # Default to False if neither provided
            db_data['had_migraine'] = False
        
        # Add all boolean fields from request (exact database schema)
        boolean_fields = [
            'stress', 'oversleep', 'sleep_deprivation', 'exercise', 'fatigue',
            'menstrual', 'emotional_distress', 'excessive_noise', 'excessive_smells',
            'excessive_alcohol', 'irregular_meals', 'overeating', 'excessive_caffeine',
            'excessive_smoking', 'travel'
        ]
        
        for field in boolean_fields:
            value = getattr(report_data, field, False)
            db_data[field] = value if value is not None else False
        
        # Legacy support: Map old trigger format to boolean fields
        if report_data.triggers:
            trigger_mapping = {
                'Stress': 'stress',
                'Sleep': 'sleep_deprivation',  # Default to sleep_deprivation
                'Hormones': 'menstrual',
                'Food': 'irregular_meals',
                'Noise': 'excessive_noise',
            }
            
            for trigger in report_data.triggers:
                if trigger in trigger_mapping:
                    db_field = trigger_mapping[trigger]
                    if db_field in db_data:
                        db_data[db_field] = True
        
        # Note: symptoms are accepted but not stored in daily_form table
        # If you need to store symptoms, consider a separate table or add to schema
        
        # Insert into Supabase daily_form table
        response = supabase.table("daily_form").insert(db_data).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to insert report into database.",
            )
        
        log_id = response.data[0].get('log_id')
        
        return ReportSubmissionResponse(
            success=True,
            message="Report submitted successfully.",
            log_id=log_id
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error submitting report: {str(e)}",
        )

