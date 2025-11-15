from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import router (similar to Django's urlpatterns)
from .routers import routes

# Initialize FastAPI app
app = FastAPI(
    title="Migraine Tracker API",
    version="1.0.0",
    description="API for Migraine Tracker application"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:8082", 
        "http://localhost:19006",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:8082",
        "http://127.0.0.1:19006",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],  # This includes Authorization header
)

# Include router (similar to Django's urlpatterns)
# All API endpoints are defined in routes.py
app.include_router(routes.router)

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Migraine Tracker API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
