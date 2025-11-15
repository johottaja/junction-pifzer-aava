"""
Test script for inference.py with sample data (7 logs).
Tests various prediction functions with realistic sample data.
"""
import sys
import os
from datetime import datetime, timedelta
import json

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

from inference import (
    predict_migraine_probability,
    predict_from_dict,
    predict_from_json,
    predict_fastapi_format
)
from config import SURVEY_FEATURES, USER_ID_COL, DATE_COL

# Check if model exists - check both relative path (as inference.py uses) and absolute path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH_RELATIVE = "models/best_model.pkl"  # Relative path as used in inference.py
MODEL_PATH_ABSOLUTE = os.path.join(SCRIPT_DIR, "models", "best_model.pkl")

# Check if model exists in either location
MODEL_EXISTS = os.path.exists(MODEL_PATH_RELATIVE) or os.path.exists(MODEL_PATH_ABSOLUTE)

def check_model_exists():
    """Check if the model file exists and print helpful message if not"""
    # Check both relative and absolute paths
    relative_exists = os.path.exists(MODEL_PATH_RELATIVE)
    absolute_exists = os.path.exists(MODEL_PATH_ABSOLUTE)
    
    if not (relative_exists or absolute_exists):
        print("\n" + "=" * 70)
        print("WARNING: Model file not found!")
        print("=" * 70)
        print(f"Checked relative path: {MODEL_PATH_RELATIVE} - {'EXISTS' if relative_exists else 'NOT FOUND'}")
        print(f"Checked absolute path: {MODEL_PATH_ABSOLUTE} - {'EXISTS' if absolute_exists else 'NOT FOUND'}")
        print("\nTo train the model, run:")
        print("  python survey_model/train_base_model.py")
        print("\nOr from the survey_model directory:")
        print("  python train_base_model.py")
        print("\n" + "=" * 70)
        print("Tests will still run but will fail when trying to load the model.")
        print("=" * 70 + "\n")
        return False
    
    # Print which path was found
    if relative_exists:
        print(f"\n✓ Model found at relative path: {MODEL_PATH_RELATIVE}")
    if absolute_exists:
        print(f"✓ Model found at absolute path: {MODEL_PATH_ABSOLUTE}")
    
    return True

def create_sample_logs(user_id=1, days_ago_start=6):
    """
    Create 7 sample logs with realistic data.
    Each log represents a day's survey response.
    
    Args:
        user_id: User identifier
        days_ago_start: Number of days ago to start (default 6, so we get days -6 to 0 = 7 days)
    
    Returns:
        List of 7 dictionaries, each representing a day's survey response
    """
    base_date = datetime.now() - timedelta(days=days_ago_start)
    
    # Create 7 days of sample data with varying patterns
    sample_logs = []
    
    for day in range(7):
        log_date = base_date + timedelta(days=day)
        
        # Create realistic patterns - some days have more triggers
        # Day 0 (today) and Day 6 (7 days ago) have more triggers
        is_high_risk_day = (day == 0 or day == 6)
        
        log = {
            USER_ID_COL: user_id,
            DATE_COL: log_date.isoformat(),
            # High risk day: more triggers
            'stress': 1 if is_high_risk_day else (1 if day % 3 == 0 else 0),
            'oversleep': 1 if day == 2 else 0,
            'sleep_deprivation': 1 if is_high_risk_day or day == 1 else 0,
            'exercise': 1 if day % 2 == 0 else 0,
            'fatigue': 1 if is_high_risk_day or day == 3 else 0,
            'menstrual': 1 if day == 4 else 0,
            'emotional_distress': 1 if is_high_risk_day else 0,
            'excessive_noise': 1 if day == 5 else 0,
            'excessive_smells': 1 if is_high_risk_day else 0,
            'excessive_alcohol': 1 if day == 6 else 0,
            'irregular_meals': 1 if day % 2 == 1 else 0,
            'overeating': 1 if day == 3 else 0,
            'excessive_caffeine': 1 if is_high_risk_day or day == 2 else 0,
            'excessive_smoking': 0,  # No smoking
            'travel': 1 if day == 5 else 0,
        }
        
        sample_logs.append(log)
    
    return sample_logs

def test_predict_from_dict():
    """Test predict_from_dict function"""
    print("=" * 70)
    print("TEST 1: predict_from_dict")
    print("=" * 70)
    
    user_id = 1
    age = 35
    gender = "female"
    
    sample_logs = create_sample_logs(user_id=user_id)
    
    print(f"\nUser ID: {user_id}, Age: {age}, Gender: {gender}")
    print(f"Number of logs: {len(sample_logs)}")
    print("\nSample log (first day):")
    for key, value in sample_logs[0].items():
        if key in SURVEY_FEATURES:
            print(f"  {key}: {value}")
    
    try:
        # Test without interpretation
        print("\n--- Testing without interpretation ---")
        probability = predict_from_dict(
            logs_list=sample_logs,
            user_id=user_id,
            age=age,
            gender=gender,
            return_interpretation=False
        )
        print(f"Predicted Migraine Probability: {probability:.4f} ({probability*100:.2f}%)")
        
        # Test with interpretation
        print("\n--- Testing with interpretation ---")
        probability, top_features = predict_from_dict(
            logs_list=sample_logs,
            user_id=user_id,
            age=age,
            gender=gender,
            return_interpretation=True
        )
        print(f"Predicted Migraine Probability: {probability:.4f} ({probability*100:.2f}%)")
        print("\nTop 5 Contributing Features:")
        for i, (feat, score, val) in enumerate(top_features, 1):
            print(f"  {i}. {feat:25s} | Value: {val:6.3f} | Contribution: {score:.6f}")
        
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predict_fastapi_format():
    """Test predict_fastapi_format function"""
    print("\n" + "=" * 70)
    print("TEST 2: predict_fastapi_format")
    print("=" * 70)
    
    user_id = 1
    age = 35
    gender = "female"
    
    sample_logs = create_sample_logs(user_id=user_id)
    
    try:
        result = predict_fastapi_format(
            logs_list=sample_logs,
            user_id=user_id,
            age=age,
            gender=gender
        )
        
        print(f"\nResult:")
        print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
        print(f"  Number of top features: {len(result['top_features'])}")
        print("\nTop Features:")
        for i, feat in enumerate(result['top_features'], 1):
            print(f"  {i}. {feat['feature']:25s} | Value: {feat['value']:6.3f} | Contribution: {feat['contribution']:.6f}")
        
        # Test JSON serialization
        json_result = json.dumps(result, indent=2)
        print(f"\nJSON-serializable result (first 300 chars):")
        print(json_result[:300] + "...")
        
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predict_from_json():
    """Test predict_from_json function with JSON string"""
    print("\n" + "=" * 70)
    print("TEST 3: predict_from_json (JSON string)")
    print("=" * 70)
    
    user_id = 1
    age = 35
    gender = "female"
    
    sample_logs = create_sample_logs(user_id=user_id)
    
    # Convert to JSON format (as Supabase would return)
    json_logs = []
    for log in sample_logs:
        json_log = {}
        for key, value in log.items():
            if key in SURVEY_FEATURES:
                # Convert 1/0 to boolean for JSON
                json_log[key] = bool(value)
            else:
                json_log[key] = value
        json_logs.append(json_log)
    
    json_string = json.dumps(json_logs)
    
    print(f"\nJSON input length: {len(json_string)} characters")
    print(f"First 200 chars: {json_string[:200]}...")
    
    try:
        result = predict_from_json(
            json_data=json_string,
            user_id=user_id,
            age=age,
            gender=gender
        )
        
        print(f"\nResult:")
        print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
        print(f"  Top feature: {result['top_features'][0]['feature']}")
        print(f"  Top feature contribution: {result['top_features'][0]['contribution']:.6f}")
        
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_predict_from_json_dict():
    """Test predict_from_json function with dict/list"""
    print("\n" + "=" * 70)
    print("TEST 4: predict_from_json (dict/list)")
    print("=" * 70)
    
    user_id = 1
    age = 35
    gender = "female"
    
    sample_logs = create_sample_logs(user_id=user_id)
    
    # Convert to dict format (as Supabase API would return)
    json_logs = []
    for log in sample_logs:
        json_log = {}
        for key, value in log.items():
            if key in SURVEY_FEATURES:
                json_log[key] = bool(value)
            else:
                json_log[key] = value
        json_logs.append(json_log)
    
    try:
        # Test with list
        result = predict_from_json(
            json_data=json_logs,
            user_id=user_id,
            age=age,
            gender=gender
        )
        
        print(f"\nResult (from list):")
        print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
        
        # Test with wrapped dict
        wrapped_data = {'data': json_logs}
        result2 = predict_from_json(
            json_data=wrapped_data,
            user_id=user_id,
            age=age,
            gender=gender
        )
        
        print(f"\nResult (from wrapped dict):")
        print(f"  Probability: {result2['probability']:.4f} ({result2['probability']*100:.2f}%)")
        
        return True
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_supabase_data():
    """Test with real data from Supabase (optional)"""
    print("\n" + "=" * 70)
    print("TEST 6: Real Data from Supabase (Optional)")
    print("=" * 70)
    
    try:
        # Try to import surveyModelGet
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        from surveyModelGet import check_migraine_risk_from_survey
        
        user_id = 1
        print(f"\nFetching real data from Supabase for user_id: {user_id}")
        print("(This requires Supabase to be configured and data to exist)")
        
        result = check_migraine_risk_from_survey(user_id)
        
        if 'error' in result:
            print(f"\n⚠ Could not fetch from Supabase: {result.get('error')}")
            print("This is expected if Supabase is not configured or no data exists.")
            return None  # Not a failure, just no data available
        else:
            print(f"\n✓ Successfully fetched and predicted from Supabase data!")
            print(f"  Probability: {result.get('probability', 0):.2f}%")
            print(f"  Risk Level: {result.get('risk_level', 'unknown')}")
            print(f"  Data Points: {result.get('data_points', 0)}")
            print(f"  Model Type: {result.get('model_type', 'unknown')}")
            if result.get('top_features'):
                print(f"  Top Feature: {result['top_features'][0].get('feature', 'N/A')}")
            return True
    except ImportError:
        print("\n⚠ surveyModelGet not available (Supabase integration not found)")
        print("Skipping Supabase test.")
        return None
    except Exception as e:
        print(f"\n⚠ Error testing with Supabase: {e}")
        return None

def test_different_scenarios():
    """Test different risk scenarios"""
    print("\n" + "=" * 70)
    print("TEST 5: Different Risk Scenarios")
    print("=" * 70)
    
    user_id = 1
    age = 35
    gender = "female"
    
    scenarios = [
        ("Low Risk", {
            'stress': 0, 'sleep_deprivation': 0, 'fatigue': 0,
            'emotional_distress': 0, 'excessive_caffeine': 0
        }),
        ("High Risk", {
            'stress': 1, 'sleep_deprivation': 1, 'fatigue': 1,
            'emotional_distress': 1, 'excessive_caffeine': 1
        }),
        ("Mixed Risk", {
            'stress': 1, 'sleep_deprivation': 0, 'fatigue': 1,
            'emotional_distress': 0, 'excessive_caffeine': 1
        }),
    ]
    
    for scenario_name, trigger_pattern in scenarios:
        print(f"\n--- {scenario_name} Scenario ---")
        
        # Create logs with this pattern for all 7 days
        sample_logs = []
        base_date = datetime.now() - timedelta(days=6)
        
        for day in range(7):
            log_date = base_date + timedelta(days=day)
            log = {
                USER_ID_COL: user_id,
                DATE_COL: log_date.isoformat(),
            }
            
            # Apply trigger pattern
            for feature in SURVEY_FEATURES:
                if feature in trigger_pattern:
                    log[feature] = trigger_pattern[feature]
                else:
                    log[feature] = 0
            
            sample_logs.append(log)
        
        try:
            result = predict_fastapi_format(
                logs_list=sample_logs,
                user_id=user_id,
                age=age,
                gender=gender
            )
            
            risk_level = "Low" if result['probability'] < 0.4 else ("Medium" if result['probability'] < 0.6 else "High")
            print(f"  Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%) - {risk_level} Risk")
            print(f"  Top feature: {result['top_features'][0]['feature']}")
        except Exception as e:
            print(f"  ERROR: {e}")

def main():
    """Run all tests"""
    print("\n" + "=" * 70)
    print("TESTING INFERENCE.PY WITH SAMPLE DATA (7 LOGS)")
    print("=" * 70)
    
    # Change to the script's directory to ensure relative paths work
    # (inference.py uses relative path "models/best_model.pkl")
    original_cwd = os.getcwd()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    print(f"\nChanged working directory to: {script_dir}")
    
    # Check if model exists first
    model_available = check_model_exists()
    
    if not model_available:
        os.chdir(original_cwd)  # Restore original directory
        response = input("\nContinue with tests anyway? (y/n): ").strip().lower()
        if response != 'y':
            print("\nExiting. Please train the model first.")
            return 1
        os.chdir(script_dir)  # Change back if continuing
    
    results = []
    
    # Run all tests
    results.append(("predict_from_dict", test_predict_from_dict()))
    results.append(("predict_fastapi_format", test_predict_fastapi_format()))
    results.append(("predict_from_json (string)", test_predict_from_json()))
    results.append(("predict_from_json (dict/list)", test_predict_from_json_dict()))
    test_different_scenarios()
    
    # Optional: Test with real Supabase data
    supabase_result = test_with_supabase_data()
    if supabase_result is not None:
        results.append(("real_supabase_data", supabase_result))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"  {test_name:40s} {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    # Restore original working directory
    os.chdir(original_cwd)
    
    if passed == total:
        print("\n✓ All tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

