# Migraine Tracker

A full-stack mobile application for tracking and predicting migraine occurrences using machine learning. Built for the Junction Hackathon (Pfizer & Aava challenge).

## Overview

Migraine Tracker helps users monitor their health data and receive personalized migraine risk predictions. The application combines sensor data (heart rate, sleep, stress levels, etc.) and daily survey responses to provide accurate, user-specific predictions using machine learning models.

## Architecture

The application follows a three-tier architecture:

```
┌─────────────────┐
│  Mobile Client  │  React Native/Expo (iOS/Android)
│   (Frontend)    │
└────────┬────────┘
         │
         │ HTTP/REST API
         │
┌────────▼────────┐
│  FastAPI Server │  Python Backend
│   (Backend)     │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼───┐ ┌──▼────────┐
│Supabase│ │ ML Models │
│  (DB)  │ │ (scikit)  │
└────────┘ └───────────┘
```

### Components

- **Frontend**: React Native mobile application built with Expo, providing cross-platform support for iOS and Android
- **Backend API**: FastAPI REST API handling authentication, data persistence, and ML model inference
- **Database**: Supabase (PostgreSQL) for user data, daily logs, and health records
- **ML Pipeline**: Two prediction models:
  - **Sensor Model**: Predicts based on health sensor data (heart rate, sleep, stress, etc.)
  - **Survey Model**: Predicts based on daily survey responses (triggers, symptoms, etc.)
- **Personalization**: User-specific models that adapt to individual patterns over time

## Tech Stack

### Frontend
- **React Native** 0.81.5
- **Expo** ~54.0.23
- **TypeScript** 5.9.2
- **Expo Router** for navigation
- **React Navigation** for tab-based navigation

### Backend
- **FastAPI** 0.115.0
- **Python** 3.11
- **Uvicorn** for ASGI server
- **Pydantic** for data validation

### Database & Services
- **Supabase** for PostgreSQL database and authentication
- **Supabase Python Client** for database operations

### Machine Learning
- **scikit-learn** for Random Forest models
- **pandas** for data processing
- **numpy** for numerical operations
- **joblib** for model serialization

## Project Structure

```
junction-pifzer-aava/
├── frontend/                 # React Native/Expo application
│   ├── app/                  # Expo Router pages
│   │   ├── (tabs)/           # Tab navigation screens
│   │   │   ├── today.tsx     # Daily prediction view
│   │   │   ├── prediction.tsx # AI assistant
│   │   │   ├── report.tsx    # Report submission
│   │   │   └── ...
│   │   └── _layout.tsx       # Root layout
│   ├── components/           # Reusable components
│   └── constants/            # Theme and configuration
│
├── backend/                  # Python backend
│   ├── api/                  # FastAPI application
│   │   ├── main.py           # FastAPI app entry point
│   │   ├── routers/          # API route handlers
│   │   │   └── routes.py     # All API endpoints
│   │   ├── dependencies/     # Shared dependencies
│   │   │   └── auth.py       # Authentication logic
│   │   └── requirements.txt  # Python dependencies
│   │
│   ├── sensorDataAi/         # Sensor-based ML model
│   │   ├── predict.py        # Prediction system
│   │   ├── train_model.py    # Model training
│   │   └── models/           # Saved user models
│   │
│   └── survey_model/         # Survey-based ML model
│       ├── inference.py      # Prediction inference
│       ├── train_base_model.py # Base model training
│       ├── retrain_user_model.py # User model retraining
│       └── models/           # Saved models
│
└── README.md                 # This file
```

## How to Use

### Prerequisites

- **Node.js** 18+ and npm
- **Python** 3.11+
- **Expo CLI** (`npm install -g expo-cli`)
- **Supabase account** and project credentials

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r api/requirements.txt
```

4. Create a `.env` file in the `backend` directory:
```bash
cp ENV_TEMPLATE.txt .env
```

5. Add your Supabase credentials to `.env`:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

6. Start the FastAPI server:
```bash
cd api
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`. Interactive API documentation is available at `http://localhost:8000/docs`.

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Configure the API endpoint in `app/(tabs)/today.tsx` (or use environment variables):
```typescript
const API_BASE_URL = 'http://localhost:8000'; // Or your backend IP
```

4. Start the Expo development server:
```bash
npm start
```

5. Run on your preferred platform:
   - Press `i` for iOS simulator
   - Press `a` for Android emulator
   - Scan QR code with Expo Go app on physical device

### Database Setup

Ensure your Supabase database has the following tables:
- `users`: User profiles
- `daily_form`: Daily survey responses and health logs
- `daily_sensor`: Sensor data records

Refer to the backend API code for the exact schema requirements.

### ML Model Training

#### Sensor Model
Train user-specific models after collecting at least 10 data points:
```python
from sensorAiGet import train_user_model_from_db

result = train_user_model_from_db(user_id=1)
print(f"Accuracy: {result['accuracy']}")
```

#### Survey Model
Train the base model first:
```bash
cd backend/survey_model
python train_base_model.py
```

Then retrain for individual users:
```python
from survey_model.retrain_user_model import retrain_user_model

result = retrain_user_model(user_id="user_123", user_data_list=user_data)
```

## API Endpoints

Key endpoints (see `/docs` for full documentation):

- `GET /users/{user_id}` - Get user information
- `GET /get-migraine-data/{user_id}` - Get migraine risk prediction
- `POST /submit-report` - Submit daily health report
- `GET /migraine-history/{user_id}` - Get migraine history
- `GET /health` - Health check

All endpoints require authentication via session cookie or Authorization header.

## Development

### Running Tests

Backend API tests can be run using the interactive documentation at `/docs` or via curl:
```bash
curl -X GET "http://localhost:8000/health"
```

### Environment Variables

- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Your Supabase service role key
- `AGENT_AUTH`: AI assistant authentication (frontend)
- `AI_ENDPOINT`: AI assistant endpoint (frontend)

## License

Built for Junction Hackathon 2025 - Pfizer & Aava Challenge
