"""
Authentication dependencies for FastAPI.
Similar to Django's authentication decorators/middleware.
"""
from fastapi import HTTPException, Cookie, Header, status
from typing import Optional
from supabase import create_client
import os
from dotenv import load_dotenv

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
        break
else:
    # Try default load_dotenv behavior
    load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

# Don't raise error on import - only fail when actually using Supabase
supabase = None
if SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

# Hardcoded development token (for testing only)
# In production, remove this and use proper Supabase authentication
DEV_TOKEN = "dev-token-12345"
DEV_USER_ID = "1"  # Default test user ID

async def get_current_user(
    session_token: Optional[str] = Cookie(None),
    authorization: Optional[str] = Header(None)
) -> dict:
    """
    Dependency function that checks authentication.
    Accepts token from either Cookie or Authorization header.
    Similar to Django's @login_required decorator.
    
    Usage in endpoint:
    @router.get("/some-endpoint")
    async def some_endpoint(current_user: dict = Depends(get_current_user)):
        ...
    """
    # Try to get token from header first (for React Native), then cookie
    token = None
    if authorization:
        # Support "Bearer <token>" or just "<token>"
        if authorization.startswith("Bearer "):
            token = authorization[7:]
        else:
            token = authorization
    elif session_token:
        token = session_token
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please provide a token.",
        )
    
    # Development mode: Check for hardcoded dev token first
    if token == DEV_TOKEN:
        return {
            "id": DEV_USER_ID,
            "email": "dev@test.com",
        }
    
    # Check if Supabase is configured
    if not supabase:
        # If Supabase not configured, allow dev token only
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Supabase not configured. Use dev token: {DEV_TOKEN}",
        )
    
    # Verify session token with Supabase
    try:
        # Verify the session token with Supabase Auth
        # Note: You may need to adjust this based on your Supabase Auth setup
        user_data = supabase.auth.get_user(token)
        
        if not user_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired session token.",
            )
        
        # Return user data in a consistent format
        user = user_data.user
        return {
            "id": user.id if hasattr(user, 'id') else str(user),
            "email": getattr(user, 'email', None),
            # Add other user attributes as needed
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
        )

