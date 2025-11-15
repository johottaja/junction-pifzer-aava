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
    from sensorAiGet import check_migraine_risk, train_user_model_from_db
except ImportError as e:
    print(f"Warning: Could not import sensorAiGet: {e}")
    check_migraine_risk = None

try:
    from surveyModelGet import check_migraine_risk_from_survey
except ImportError as e:
    print(f"Warning: Could not import surveyModelGet: {e}")
    check_migraine_risk_from_survey = None

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
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        
        user_data = response.data[0]
        
        return UserInfoResponse(
            success=True,
            user=UserResponse(
                user_id=user_data.get("user_id", user_id),
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
        response = supabase.table("users").select("*").eq("user_id", user_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with id {user_id} not found.",
            )
        
        user_data = response.data[0]
        
        return UserInfoResponse(
            success=True,
            user=UserResponse(
                user_id=user_data.get("user_id", user_id),
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
    probability: Optional[float] = None  # Percentage value (0-100)
    reason1: Optional[str] = None  # Top contributing trigger/factor
    reason2: Optional[str] = None  # Second top contributing trigger/factor
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
    Get migraine prediction probability for a user.
    Combines predictions from both sensor model and survey model.
    Route: GET /get-migraine-data/{user_id}
    Requires authentication via session cookie.
    Returns the average migraine risk probability as a percentage (0-100).
    """
    # Verify that the authenticated user can access this user_id
    if current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own migraine data.",
        )
    
    # Check if at least one prediction system is available
    if not check_migraine_risk and not check_migraine_risk_from_survey:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Migraine prediction systems are not available.",
        )
    
    try:
        # Convert user_id to int (both functions expect int)
        try:
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format.",
            )
        
        probabilities = []
        errors = []
        reason1 = None  # From sensor model
        reason2 = None  # From survey model
        
        # Helper function to convert feature names to human-readable trigger names
        def feature_to_trigger_name(feature_name: str) -> str:
            """Convert ML feature names to human-readable trigger names"""
            feature_mapping = {
                # Survey model features
                'stress': 'Stress',
                'sleep_deprivation': 'Sleep deprivation',
                'fatigue': 'Fatigue',
                'emotional_distress': 'Emotional distress',
                'excessive_caffeine': 'Excessive caffeine',
                'menstrual': 'Hormonal changes',
                'irregular_meals': 'Irregular meals',
                'excessive_alcohol': 'Excessive alcohol',
                'excessive_noise': 'Excessive noise',
                'excessive_smells': 'Excessive smells',
                'travel': 'Travel',
                'oversleep': 'Oversleeping',
                'exercise': 'Lack of exercise',
                'overeating': 'Overeating',
                'excessive_smoking': 'Excessive smoking',
                # Sensor model features
                'Received_Air_Pressure_hPa': 'Air pressure changes',
                'Sleep_h': 'Sleep schedule',
                'Stress_level_0_100': 'Stress levels',
                'Screen_time_h': 'Screen time',
                'Average_heart_rate_bpm': 'Heart rate',
                'Steps_and_activity': 'Physical activity',
            }
            # Check for user-specific features (e.g., user_stress_mean)
            if feature_name.startswith('user_'):
                base_feature = feature_name.replace('user_', '').replace('_mean', '').replace('_std', '')
                return feature_mapping.get(base_feature, feature_name.replace('_', ' ').title())
            return feature_mapping.get(feature_name, feature_name.replace('_', ' ').title())
        
        # Call sensor model (check_migraine_risk)
        if check_migraine_risk:
            try:
                sensor_result = check_migraine_risk(user_id_int)
                print(f"[get_migraine_data] Result from check_migraine_risk: {sensor_result}")
                
                if 'error' not in sensor_result:
                    sensor_probability = sensor_result.get('probability')
                    if sensor_probability is not None:
                        probabilities.append(float(sensor_probability))
                        print(f"[get_migraine_data] Sensor model probability: {sensor_probability}")
                    else:
                        errors.append("Sensor model: Probability not found in result")
                    
                    # Extract reason1 from sensor model
                    sensor_reason1 = sensor_result.get('reason1')
                    if sensor_reason1:
                        reason1 = sensor_reason1
                        print(f"[get_migraine_data] Sensor model reason1: {reason1}")
                else:
                    errors.append(f"Sensor model: {sensor_result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"Sensor model: {str(e)}")
                print(f"[get_migraine_data] Error calling check_migraine_risk: {e}")
        else:
            print("[get_migraine_data] check_migraine_risk not available, skipping sensor model")
        
        # Call survey model (check_migraine_risk_from_survey)
        if check_migraine_risk_from_survey:
            try:
                survey_result = check_migraine_risk_from_survey(user_id_int)
                print(f"[get_migraine_data] Result from check_migraine_risk_from_survey: {survey_result}")
                
                if 'error' not in survey_result:
                    survey_probability = survey_result.get('probability')
                    if survey_probability is not None:
                        probabilities.append(float(survey_probability))
                        print(f"[get_migraine_data] Survey model probability: {survey_probability}")
                    
                    # Extract reason2 from survey model (from top_features or reason2 field)
                    survey_reason2 = survey_result.get('reason2')
                    if survey_reason2:
                        reason2 = survey_reason2
                        print(f"[get_migraine_data] Survey model reason2: {reason2}")
                    else:
                        # Fallback: extract from top_features if reason2 not available
                        survey_top_features = survey_result.get('top_features', [])
                        if survey_top_features and len(survey_top_features) >= 2:
                            # Get the second top feature
                            second_feat = survey_top_features[1]
                            feature_name = second_feat.get('feature', '') if isinstance(second_feat, dict) else str(second_feat)
                            if feature_name:
                                reason2 = feature_to_trigger_name(feature_name)
                                print(f"[get_migraine_data] Survey model reason2 (from top_features): {reason2}")
                        elif survey_top_features and len(survey_top_features) >= 1:
                            # If only one feature available, use it as reason2
                            first_feat = survey_top_features[0]
                            feature_name = first_feat.get('feature', '') if isinstance(first_feat, dict) else str(first_feat)
                            if feature_name:
                                reason2 = feature_to_trigger_name(feature_name)
                                print(f"[get_migraine_data] Survey model reason2 (from top_features, single): {reason2}")
                else:
                    errors.append(f"Survey model: {survey_result.get('error', 'Unknown error')}")
            except Exception as e:
                errors.append(f"Survey model: {str(e)}")
                print(f"[get_migraine_data] Error calling check_migraine_risk_from_survey: {e}")
        else:
            print("[get_migraine_data] check_migraine_risk_from_survey not available, skipping survey model")
        
        # Calculate average probability
        if len(probabilities) == 0:
            # No successful predictions
            error_message = "No predictions available. " + "; ".join(errors) if errors else "Both prediction systems failed."
            print(f"[get_migraine_data] No probabilities available: {error_message}")
            return MigraineDataResponse(
                success=False,
                probability=None,
                reason1=None,
                reason2=None,
                error=error_message
            )
        
        # Calculate average of available probabilities
        average_probability = sum(probabilities) / len(probabilities)
        print(f"[get_migraine_data] Calculated average probability: {average_probability} (from {len(probabilities)} model(s))")
        
        print(f"[get_migraine_data] Top triggers: reason1={reason1} (from sensor), reason2={reason2} (from survey)")
        
        # Return the average probability value with reasons
        return MigraineDataResponse(
            success=True,
            probability=float(average_probability),
            reason1=reason1,
            reason2=reason2,
            error=None
        )
        
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

