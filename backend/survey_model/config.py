"""
Configuration for column names matching Supabase schema.
"""
# Core columns - Supabase schema
USER_ID_COL = 'user_id'  # Used for training splits and user-specific models, NOT for prediction
MIGRAINE_COL = 'had_migraine'  # Target variable
AGE_COL = 'age'  # Note: Not in Supabase schema - may need to be added or removed
GENDER_COL = 'gender'  # Note: Not in Supabase schema - may come from user profile
DATE_COL = 'created_at'  # Used for sorting 7 days, NOT for prediction

# Survey feature columns - All boolean features from Supabase schema
SURVEY_FEATURES = [
    'stress',
    'oversleep',
    'sleep_deprivation',
    'exercise',
    'fatigue',
    'menstrual',
    'emotional_distress',
    'excessive_noise',
    'excessive_smells',
    'excessive_alcohol',
    'irregular_meals',
    'overeating',
    'excessive_caffeine',
    'excessive_smoking',
    'travel'
]

# Columns to exclude from features
EXCLUDE_COLS = [
    'log_id',  # Identity column, not used
    USER_ID_COL,  # Used for splits, not prediction
    DATE_COL,  # Used for sorting, not prediction
    MIGRAINE_COL,  # Target variable
    'target'  # Internal target column
]
