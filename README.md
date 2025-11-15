# HeadSync

A full-stack mobile application for tracking and predicting migraine occurrences using machine learning. Built for the Junction Hackathon (Pfizer & Aava challenge).

## Overview

HeadSync helps users monitor their health data and receive personalized migraine risk predictions. The application combines sensor data (heart rate, sleep, stress levels, etc.) and daily survey responses to provide accurate, user-specific predictions using machine learning models.

## Architecture

The application follows a three-tier architecture:

```
┌─────────────────┐
│  Mobile Client  │  React Native/Expo (iOS/Android)
│   (Frontend)    │
└────┬──────┬─────┘
     │      │
     │      │ AI Queries
     │      │
     │  ┌───▼──────────┐
     │  │  n8n AI      │
     │  │  Assistant   │
     │  └───┬──────────┘
     │      │
     │ HTTP/REST API
     │
┌────▼────────────┐
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
- **ML Pipeline**: Advanced dual-model ensemble system with real-time personalization
  - **Sensor Model**: Random Forest ensemble analyzing physiological and environmental data
  - **Survey Model**: Logistic Regression processing behavioral and trigger patterns
  - **Ensemble Fusion**: Weighted averaging of predictions for robust risk assessment
- **Personalization**: Adaptive user-specific models with transfer learning and continuous retraining
- **AI Assistant**: Agentic AI system built with n8n that provides personalized health insights and answers questions about user reports and migraine patterns

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
- **n8n** for agentic AI workflow automation and intelligent health assistant

### Machine Learning
- **scikit-learn** for ensemble models and classification
- **pandas** for data processing and feature engineering
- **numpy** for numerical operations
- **joblib** for model serialization and persistence

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

## Machine Learning Architecture

HeadSync employs a sophisticated dual-model ensemble system that combines physiological sensor data with behavioral survey responses to deliver highly accurate, personalized migraine risk predictions. The architecture leverages state-of-the-art machine learning techniques including ensemble methods, transfer learning, and advanced feature engineering.

### Dual-Model Ensemble System

The prediction pipeline integrates two complementary machine learning models that analyze different aspects of user health data:

#### 1. Sensor-Based Model (Random Forest Ensemble)

The sensor model utilizes a **Random Forest Classifier** with 100 decision trees to analyze real-time physiological and environmental data. This model processes 10 key features:

**Input Features:**
- Physiological metrics: Heart rate (bpm), respiration rate, sleep duration
- Activity data: Steps, screen time, physical activity levels
- Environmental factors: Air pressure, temperature, air quality, weather conditions
- Stress indicators: Self-reported stress levels (0-100 scale)

**Model Architecture:**
- **Algorithm**: Random Forest Classifier (scikit-learn)
- **Ensemble Size**: 100 estimators for robust predictions
- **Regularization**: Strong regularization to prevent overfitting
  - `max_depth=8`: Shallow trees for conservative predictions
  - `min_samples_split=15`: High threshold for node splitting
  - `min_samples_leaf=5`: Minimum samples in leaf nodes
  - `max_features='sqrt'`: Random feature selection per tree
- **Class Balancing**: Automatic class weight computation for imbalanced datasets
- **Validation**: Out-of-bag (OOB) scoring for unbiased performance estimation
- **Cross-Validation**: 5-fold cross-validation for robust accuracy metrics

**Feature Engineering:**
- Standard scaling (Z-score normalization) for all numerical features
- Temporal feature extraction from historical patterns
- Missing value imputation using feature means
- Feature importance analysis for explainability

**Performance Characteristics:**
- Handles non-linear relationships between features
- Robust to outliers and missing data
- Provides feature importance rankings for interpretability
- Real-time inference with sub-second latency

#### 2. Survey-Based Model (Logistic Regression)

The survey model employs **Logistic Regression** with L2 regularization to analyze behavioral patterns and self-reported triggers. This model processes 15+ binary and categorical features:

**Input Features:**
- Behavioral triggers: Stress, sleep deprivation, fatigue, emotional distress
- Dietary factors: Caffeine, alcohol, irregular meals, overeating
- Environmental triggers: Noise, smells, travel
- Lifestyle factors: Exercise, smoking, oversleeping
- Hormonal factors: Menstrual cycle indicators
- User demographics: Age, gender (encoded)

**Model Architecture:**
- **Algorithm**: Logistic Regression with L2 regularization
- **Class Balancing**: Balanced class weights for imbalanced data
- **Optimization**: Maximum 1000 iterations with convergence tolerance
- **Feature Engineering**: User-specific aggregated features (mean, std) from historical data
- **Temporal Weighting**: 60% weight on current day, 40% on previous day for recency

**Advanced Personalization:**
- **User-Specific Features**: Aggregated statistics (mean, standard deviation) computed from each user's historical survey responses
- **Transfer Learning**: Base model trained on population data, fine-tuned per user
- **Temporal Context**: 7-day rolling window with day prioritization
- **Data Leakage Prevention**: Strict user-based train/test splitting

**Feature Engineering Pipeline:**
1. **Base Features**: Direct survey responses (binary triggers, symptoms)
2. **User Aggregations**: Historical mean and standard deviation per feature
3. **Temporal Features**: Weighted combination of current and previous day
4. **Demographic Encoding**: Label encoding for categorical variables

### Ensemble Fusion Strategy

The final prediction combines both models using a **weighted averaging ensemble**:

```python
final_probability = (sensor_probability + survey_probability) / 2
```

This approach:
- **Reduces Variance**: Ensemble averaging decreases prediction variance
- **Improves Robustness**: Single model failures don't compromise predictions
- **Enhances Accuracy**: Complementary models capture different signal patterns
- **Provides Explainability**: Separate feature importance from each model

### Personalization & Adaptation

HeadSync implements a sophisticated personalization system that adapts to individual user patterns:

#### User-Specific Model Training

**Sensor Model Personalization:**
- Individual Random Forest models trained per user after 10+ data points
- Models stored as `user_{id}_model.pkl` with associated scalers
- Automatic retraining when sufficient new data accumulates
- Feature importance tracking for personalized trigger identification

**Survey Model Personalization:**
- Base model trained on population data (transfer learning approach)
- User-specific fine-tuning with minimum 10 historical samples
- Incremental learning: Models retrain as new data arrives
- User feature statistics computed from historical patterns only (prevents data leakage)

#### Continuous Learning Pipeline

1. **Data Collection**: Daily sensor readings and survey responses stored in Supabase
2. **Model Triggering**: Automatic retraining when threshold reached (10+ new samples)
3. **Validation**: Cross-validation ensures model quality before deployment
4. **A/B Testing**: Base model fallback if user model performance degrades
5. **Feature Evolution**: Dynamic feature importance tracking adapts to user patterns

### Model Performance & Validation

**Training Methodology:**
- **Stratified Splitting**: Maintains class distribution in train/test splits
- **User-Based Splitting**: Prevents data leakage by splitting on user ID
- **Cross-Validation**: 5-fold CV for robust performance estimation
- **Out-of-Bag Scoring**: Unbiased validation during Random Forest training

**Performance Metrics:**
- **Accuracy**: Classification accuracy on held-out test sets
- **ROC-AUC**: Area under receiver operating characteristic curve
- **Recall**: Migraine detection rate (critical for health applications)
- **Precision**: Positive predictive value
- **Confusion Matrix**: Detailed breakdown of prediction errors

**Model Monitoring:**
- Overfitting detection via train/test accuracy comparison
- Feature importance tracking for model interpretability
- Prediction confidence intervals
- Error analysis and false positive/negative tracking

### Explainability & Interpretability

Both models provide explainable predictions:

- **Feature Importance**: Ranked list of most influential factors
- **Top Contributing Features**: Per-prediction feature contribution analysis
- **Human-Readable Triggers**: ML feature names mapped to understandable triggers
- **Risk Reasoning**: Two primary reasons provided for each prediction

### Real-Time Inference

The system is optimized for production use:

- **Sub-second Latency**: Models load from disk and predict in <100ms
- **Scalable Architecture**: Models cached in memory for fast access
- **Graceful Degradation**: Falls back to base models if user models unavailable
- **Batch Processing**: Supports both single predictions and batch inference

### ML Model Training

#### Sensor Model Training

Train user-specific models after collecting at least 10 data points:

```python
from sensorAiGet import train_user_model_from_db

result = train_user_model_from_db(user_id=1)
print(f"Accuracy: {result['accuracy']:.2%}")
print(f"Feature Importance: {result['feature_importance']}")
```

The training process:
1. Loads user's historical sensor data from Supabase
2. Prepares features with scaling and normalization
3. Trains Random Forest with regularization
4. Validates using cross-validation
5. Saves model, scaler, and metadata to disk

#### Survey Model Training

**Base Model Training:**
```bash
cd backend/survey_model
python train_base_model.py
```

This trains the population-level model on aggregated survey data with proper user-based splitting.

**User-Specific Fine-Tuning:**
```python
from survey_model.retrain_user_model import retrain_user_model

result = retrain_user_model(
    user_id="user_123", 
    user_data_list=user_data  # List of historical survey responses
)

if result['success']:
    print(f"Model retrained: {result['model_path']}")
    print(f"Accuracy improvement: {result['accuracy']:.2%}")
```

The retraining process:
1. Loads base model architecture and feature names
2. Combines user data with base training data
3. Creates user-specific aggregated features
4. Retrains Logistic Regression with balanced weights
5. Validates performance and saves user-specific model

## AI Assistant (Agentic AI)

HeadSync includes an intelligent AI assistant powered by **n8n** workflows that provides personalized health guidance and insights. The assistant has direct access to user reports, health data, and migraine patterns, enabling contextual conversations about individual health journeys.

### Architecture

The AI assistant is built using **n8n**, an open-source workflow automation platform that orchestrates intelligent agentic workflows. The system connects to the mobile app via secure webhook endpoints and processes user queries with full context of their health data.

**Key Components:**
- **n8n Workflow Engine**: Orchestrates AI agent workflows and data retrieval
- **Webhook Integration**: Secure REST API endpoints for mobile app communication
- **Data Access Layer**: Direct integration with Supabase to retrieve user reports and health records
- **Contextual Understanding**: AI agent processes user queries with full access to historical data

### Capabilities

The AI assistant can:

- **Analyze Health Patterns**: Review user's daily reports, migraine history, and trigger patterns
- **Identify Triggers**: Analyze historical data to identify personalized migraine triggers
- **Provide Prevention Tips**: Offer personalized recommendations based on individual patterns
- **Answer Questions**: Respond to queries about health data, predictions, and trends
- **Explain Predictions**: Clarify ML model predictions and feature contributions
- **Pattern Recognition**: Identify correlations and trends in user's health data over time

### User Interaction

Users interact with the AI assistant through a conversational interface in the mobile app:

- **Natural Language Queries**: Ask questions in plain language about health data
- **Quick Actions**: Pre-configured queries for common questions:
  - "What are my triggers?"
  - "How can I prevent migraines?"
  - "Show my patterns"
  - "Analyze my data"
- **Contextual Responses**: Answers are personalized based on the user's complete health history
- **Real-Time Insights**: Get instant analysis of recent reports and patterns

### Data Privacy & Security

- **User-Specific Context**: Each conversation is scoped to the authenticated user's data only
- **Secure Authentication**: API requests include authentication tokens
- **Data Isolation**: User reports and health data are accessed securely through Supabase
- **Session Management**: Conversations maintain context within user sessions

### Integration

The AI assistant integrates seamlessly with the HeadSync ecosystem:

```typescript
// Frontend integration
const response = await fetch(AI_ENDPOINT, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'auth': AGENT_AUTH
  },
  body: JSON.stringify({
    message: userQuery,
    sessionId: userId
  })
});
```

The n8n workflow:
1. Receives user query with session context
2. Retrieves user's health reports from Supabase
3. Analyzes patterns and historical data
4. Generates contextual response using AI models
5. Returns personalized insights to the mobile app

### Configuration

Configure the AI assistant endpoint in `frontend/app.config.js`:

```javascript
extra: {
  AGENT_AUTH: process.env.AGENT_AUTH,
  AI_ENDPOINT: process.env.AI_ENDPOINT || 'https://your-n8n-webhook-url'
}
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
