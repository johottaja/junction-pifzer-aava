# Migraine Prediction Pipeline

Minimal ML pipeline for predicting migraine probability (0-1) based on daily survey data with personalization.

## Structure

- `train_base_model.py`: Initial model training on base dataset
- `retrain_user_model.py`: Retrain model for individual users (Flask integration)
- `inference.py`: Predict migraine probability from 7 days of logs
- `compare_models.py`: Model comparison tool (optional)
- `models/`: Saved models and feature importance
- `pretrain_data/`: Base training data

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Train base model
```bash
python train_base_model.py
```

### 3. Run inference
```python
from inference import predict_migraine_probability
import pandas as pd

logs_df = pd.read_excel("path/to/logs.xlsx")
probability = predict_migraine_probability(logs_df, user_id="CM-001", age=46, gender="female")
print(f"Migraine probability: {probability:.3f}")
```

## Flask Integration

### Retrain User Model (Daily Adaptation)

When Flask receives new user data from Supabase, call:

```python
from retrain_user_model import retrain_user_model

# user_data_list: List of dicts from Supabase (all user's historical responses)
user_data_list = [
    {
        'Unique ID': 'CM-001',
        'Age': 46,
        'gender': 'female',
        'Date': 20240101,
        'Stress': 1,
        'Sleep deprivation': 0,
        'Migraine': 1,
        # ... all survey fields
    },
    # ... more entries
]

result = retrain_user_model(user_id="CM-001", user_data_list=user_data_list)

if result['success']:
    print(f"Model retrained: {result['model_path']}")
else:
    print(f"Error: {result['message']}")
```

**Requirements:**
- Minimum 10 user samples
- Each dict must include 'Migraine' column
- All survey fields should match training data format

### Inference (7 Days of Data)

Flask provides last 7 days for inference:

```python
from inference import predict_migraine_probability

# logs_df: DataFrame with 7 days of survey data
probability, top_features = predict_migraine_probability(
    logs_df, 
    user_id="CM-001", 
    age=46, 
    gender="female",
    return_interpretation=True
)
```

The inference automatically uses user-specific model if available, otherwise falls back to base model.

## Model Details

- **Algorithm**: RandomForest (100 trees, max_depth=15)
- **Target**: Binary classification (Migraine: 0 or 1)
- **Features**: 20+ features including:
  - Demographics: Age, Gender (from user profile, not survey table)
  - Daily survey responses: Stress, Sleep, Exercise, etc.
  - User-specific patterns: Historical averages and std dev
- **Class balancing**: `class_weight='balanced'` to reduce false negatives
- **Train/Test Split**: User-based to avoid data leakage

## User Adaptation

**Strategy**: Retrain from scratch on base_data + user_data

- When user has 10+ samples, retrain model combining base training data + user data
- Model learns user's specific migraine patterns
- Saved to `models/user_models/user_{user_id}_model.pkl`
- Inference automatically uses user model when available

## Files

### Core Files
- `train_base_model.py` - Initial training
- `retrain_user_model.py` - User adaptation (Flask integration)
- `inference.py` - Prediction with interpretability
- `compare_models.py` - Model comparison (optional)

### Data
- `pretrain_data/survey_data.xlsx` - Base training data
- `models/` - Saved models
  - `best_model.pkl` - Base model (from compare_models.py or train_base_model.py)
  - `user_models/` - User-specific models

