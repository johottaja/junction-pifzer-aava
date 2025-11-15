# FastAPI Backend for Migraine Tracker

## Project Structure

FastAPI doesn't use a `urls.py` file like Django. Instead, routes are organized using **APIRouter** and included in the main app.

```
backend/api/
├── main.py              # Main FastAPI app (like Django's urls.py - includes all routers)
├── routers/             # Route modules (like Django's views)
│   ├── __init__.py
│   └── users.py         # User-related endpoints
├── dependencies/        # Shared dependencies (like Django's decorators/middleware)
│   ├── __init__.py
│   └── auth.py          # Authentication dependency
└── requirements.txt
```

## How Routing Works

### Django vs FastAPI

**Django:**
```python
# urls.py
urlpatterns = [
    path('users/<int:user_id>/', views.get_user, name='get_user'),
]

# views.py
@login_required
def get_user(request, user_id):
    ...
```

**FastAPI:**
```python
# routers/users.py (like Django's views.py)
router = APIRouter(prefix="/users")

@router.get("/{user_id}")  # Creates route: GET /users/{user_id}
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    ...

# main.py (like Django's urls.py)
app.include_router(users.router)  # Includes all routes from users.py
```

### Key Differences:

1. **No separate urls.py**: Routes are defined in router files and included in `main.py`
2. **APIRouter**: Similar to Django's URL patterns, groups related routes
3. **Dependency Injection**: `Depends(get_current_user)` replaces `@login_required`
4. **Automatic Documentation**: FastAPI auto-generates OpenAPI docs at `/docs`

## Setup

1. Install dependencies:
```bash
cd backend
pip install -r api/requirements.txt
```

2. Create a `.env` file in the `backend` directory with:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

3. Run the server:
```bash
# From backend directory
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Or:
```bash
python -m api.main
```

## Adding New Routes

To add a new endpoint:

1. **Create or edit a router file** in `routers/`:
```python
# routers/reports.py
from fastapi import APIRouter
router = APIRouter(prefix="/reports", tags=["reports"])

@router.post("/")
async def create_report(...):
    ...
```

2. **Include the router in main.py**:
```python
# main.py
from .routers import users, reports

app.include_router(users.router)
app.include_router(reports.router)  # Add this
```

That's it! The route is now available at `/reports/`

## Authentication

FastAPI uses **dependency injection** instead of decorators like Django. The `get_current_user` dependency function works similarly to Django's `@login_required` decorator.

### How it works:

**Django style:**
```python
@login_required
def get_user(request, user_id):
    ...
```

**FastAPI style:**
```python
@router.get("/{user_id}")
async def get_user(user_id: str, current_user: dict = Depends(get_current_user)):
    ...
```

The `Depends(get_current_user)` automatically:
- Checks for the `session_token` cookie
- Verifies the session with Supabase
- Returns the authenticated user data
- Raises 401 if not authenticated

## API Endpoints

### GET `/users/{user_id}`
Get user information by user_id. Requires authentication.

**Route defined in:** `routers/users.py`

**Headers:**
- Cookie: `session_token=<token>`

**Response:**
```json
{
  "success": true,
  "user": {
    "user_id": "123",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2024-01-01T00:00:00"
  }
}
```

### GET `/users/me`
Get the currently authenticated user's information. No user_id needed.

**Route defined in:** `routers/users.py`

**Headers:**
- Cookie: `session_token=<token>`

**Response:**
Same as above.

## Viewing All Routes

FastAPI automatically generates interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

These show all available endpoints, their parameters, and allow you to test them directly!

## Testing

Test with curl:
```bash
# Get user info (requires session cookie)
curl -X GET "http://localhost:8000/users/123" \
  -H "Cookie: session_token=your_token_here"

# Get current user info
curl -X GET "http://localhost:8000/users/me" \
  -H "Cookie: session_token=your_token_here"
```

## Notes

- The authentication currently uses Supabase Auth. You may need to adjust the session verification logic based on your authentication setup.
- CORS is configured for Expo development ports. Adjust `allow_origins` in `main.py` for production.
- All routes are automatically documented at `/docs` - no need to maintain separate API docs!

