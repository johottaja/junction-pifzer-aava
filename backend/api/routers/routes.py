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
    Route: GET /get-migraine-data/{user_id}
    Requires authentication via session cookie.
    Returns the migraine risk probability as a percentage (0-100).
    """
    # Verify that the authenticated user can access this user_id
    if current_user.get("id") != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only access your own migraine data.",
        )
    
    if not check_migraine_risk:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Migraine prediction system is not available.",
        )
    
    try:
        # Convert user_id to int (check_migraine_risk expects int)
        try:
            user_id_int = int(user_id) if isinstance(user_id, str) else user_id
        except (ValueError, TypeError):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid user_id format.",
            )
        
        # Call check_migraine_risk to get predictio
        result = check_migraine_risk(user_id_int)
        
        print(f"[get_migraine_data] Result from check_migraine_risk: {result}")
        
        # Check if result has an error
        if 'error' in result:
            print(f"[get_migraine_data] Error in result: {result.get('error')}")
            return MigraineDataResponse(
                success=False,
                probability=None,
                error=result.get('error', 'Unknown error occurred')
            )
        
        # Extract probability from result
        probability = result.get('probability')
        
        if probability is None:
            print(f"[get_migraine_data] Probability not found in result: {result}")
            return MigraineDataResponse(
                success=False,
                probability=None,
                error="Probability not found in prediction result"
            )
        
        print(f"[get_migraine_data] Returning probability: {probability}")
        
        # Return the probability value
        return MigraineDataResponse(
            success=True,
            probability=float(probability),
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

