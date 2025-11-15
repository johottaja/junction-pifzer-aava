"""
Migraine Prediction System

A Random Forest-based machine learning system for predicting migraine occurrence
based on health and sensor data.

Quick Start:
-----------
    from predict import predict_single
    
    result = predict_single(data)
    print(f"Migraine probability: {result['probability']}%")

For more information, see README.md
"""

__version__ = '1.0.0'
__author__ = 'Junction Pifzer Aava'

# Import main functions for easy access
from .predict import (
    predict_single,
    predict_from_csv,
    MigrainePredictionSystem
)

from .data_utils import (
    DataValidator,
    PersonalizedDataHandler,
    create_example_input
)

__all__ = [
    'predict_single',
    'predict_from_csv',
    'MigrainePredictionSystem',
    'DataValidator',
    'PersonalizedDataHandler',
    'create_example_input'
]

