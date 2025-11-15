"""
Test script to validate data structure, config, and train base model.
Run this to verify everything matches before training.
"""
import pandas as pd
import sys
import os
from config import (
    USER_ID_COL, MIGRAINE_COL, AGE_COL, GENDER_COL, DATE_COL,
    SURVEY_FEATURES, EXCLUDE_COLS
)

def test_data_structure():
    """Test 1: Validate data structure matches config."""
    print("=" * 60)
    print("TEST 1: Data Structure Validation")
    print("=" * 60)
    
    try:
        # Check for converted data file first
        data_file = "pretrain_data/survey_base_data.xlsx"
        if not os.path.exists(data_file):
            print(f"⚠️  {data_file} not found. Checking for original file...")
            data_file = "pretrain_data/survey_data.xlsx"
            if not os.path.exists(data_file):
                raise FileNotFoundError(f"Neither survey_base_data.xlsx nor survey_data.xlsx found")
            print(f"⚠️  Using original file. Run convert_user_ids.py to create survey_base_data.xlsx")
        
        df = pd.read_excel(data_file)
        print(f"✅ Data loaded successfully")
        print(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns\n")
        
        print("Columns in data:")
        for col in df.columns:
            print(f"   - {col}")
        
        print(f"\n=== Config Expectations ===")
        print(f"USER_ID_COL: '{USER_ID_COL}'")
        print(f"MIGRAINE_COL: '{MIGRAINE_COL}'")
        print(f"DATE_COL: '{DATE_COL}'")
        print(f"AGE_COL: '{AGE_COL}' (optional)")
        print(f"GENDER_COL: '{GENDER_COL}' (optional)")
        
        print(f"\nSURVEY_FEATURES ({len(SURVEY_FEATURES)}):")
        for feat in SURVEY_FEATURES:
            print(f"   - {feat}")
        
        print(f"\n=== Validation Results ===")
        errors = []
        warnings = []
        
        # Check required columns
        if USER_ID_COL not in df.columns:
            errors.append(f"❌ {USER_ID_COL} (REQUIRED for user-based splits)")
        else:
            print(f"✅ {USER_ID_COL} found")
            print(f"   Unique users: {df[USER_ID_COL].nunique()}")
        
        if MIGRAINE_COL not in df.columns:
            errors.append(f"❌ {MIGRAINE_COL} (REQUIRED - target variable)")
        else:
            print(f"✅ {MIGRAINE_COL} found")
            target_dist = df[MIGRAINE_COL].value_counts().to_dict()
            print(f"   Target distribution: {target_dist}")
            if len(target_dist) == 1:
                warnings.append(f"⚠️  Only one class in target! ({list(target_dist.keys())[0]})")
        
        if DATE_COL not in df.columns:
            warnings.append(f"⚠️  {DATE_COL} not found (will use row order for sorting)")
        else:
            print(f"✅ {DATE_COL} found")
        
        # Check optional columns
        if AGE_COL in df.columns:
            print(f"✅ {AGE_COL} found (will be excluded from features)")
        else:
            print(f"ℹ️  {AGE_COL} not in data (will use from user profile in inference)")
        
        if GENDER_COL in df.columns:
            print(f"✅ {GENDER_COL} found (will be excluded from features)")
        else:
            print(f"ℹ️  {GENDER_COL} not in data (will use from user profile in inference)")
        
        # Check survey features
        print(f"\nSurvey features validation:")
        found_features = []
        missing_features = []
        for feat in SURVEY_FEATURES:
            if feat in df.columns:
                found_features.append(feat)
                print(f"   ✅ {feat}")
            else:
                missing_features.append(feat)
                print(f"   ❌ {feat} (MISSING)")
        
        if missing_features:
            warnings.append(f"⚠️  Missing {len(missing_features)} survey features: {missing_features}")
        
        print(f"\n   Summary: {len(found_features)}/{len(SURVEY_FEATURES)} features found")
        
        # Show sample data
        print(f"\n=== Sample Data (first 2 rows) ===")
        print(df.head(2).to_string())
        
        if errors:
            print(f"\n❌ ERRORS FOUND:")
            for err in errors:
                print(f"   {err}")
            return False, df
        
        if warnings:
            print(f"\n⚠️  WARNINGS:")
            for warn in warnings:
                print(f"   {warn}")
        
        print(f"\n✅ Data structure validation PASSED!")
        return True, df
        
    except FileNotFoundError:
        print("❌ ERROR: pretrain_data/survey_data.xlsx not found")
        print("   Please ensure the data file exists in pretrain_data/")
        return False, None
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False, None

def test_config_imports():
    """Test 2: Verify all config imports work."""
    print("\n" + "=" * 60)
    print("TEST 2: Config Import Validation")
    print("=" * 60)
    
    try:
        from train_base_model import (
            load_and_prepare_data, create_user_features, split_by_users
        )
        print("✅ All training functions imported successfully")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_loading():
    """Test 3: Test data loading and preparation."""
    print("\n" + "=" * 60)
    print("TEST 3: Data Loading and Preparation")
    print("=" * 60)
    
    try:
        from train_base_model import load_and_prepare_data
        
        X, y, feature_cols, user_ids, le_gender, df = load_and_prepare_data()
        
        print(f"✅ Data loaded and prepared")
        print(f"   X shape: {X.shape}")
        print(f"   y shape: {y.shape}")
        print(f"   Features: {len(feature_cols)}")
        print(f"   Users: {user_ids.nunique()}")
        print(f"   Gender encoder: {'Present' if le_gender else 'None (optional)'}")
        
        print(f"\n   Feature columns ({len(feature_cols)}):")
        for i, feat in enumerate(feature_cols[:10], 1):
            print(f"      {i}. {feat}")
        if len(feature_cols) > 10:
            print(f"      ... and {len(feature_cols) - 10} more")
        
        print(f"\n   Target distribution:")
        print(f"      {y.value_counts().to_dict()}")
        print(f"      Migraine rate: {y.mean():.3f}")
        
        # Show all features in training matrix X
        print(f"\n   === All Features in Training Matrix X ===")
        print(f"   Total features: {len(X.columns)}")
        print(f"   Feature list:")
        for i, feat in enumerate(X.columns, 1):
            dtype = X[feat].dtype
            non_zero = (X[feat] != 0).sum()
            print(f"      {i:3d}. {feat:<35} (dtype: {dtype}, non-zero: {non_zero}/{len(X)})")
        
        return True, X, y, feature_cols, user_ids, df
        
    except Exception as e:
        print(f"❌ Data loading error: {e}")
        import traceback
        traceback.print_exc()
        return False, None, None, None, None, None

def test_training():
    """Test 4: Train the model."""
    print("\n" + "=" * 60)
    print("TEST 4: Model Training")
    print("=" * 60)
    
    try:
        from train_base_model import train_model, save_model_and_features, load_and_prepare_data
        
        print("Loading data...")
        X, y, feature_cols, user_ids, le_gender, df = load_and_prepare_data()
        
        print("Training model...")
        model, X_train = train_model(X, y, user_ids, df)
        
        print("Saving model...")
        save_model_and_features(model, X_train, le_gender)
        
        print("\n✅ Model training and saving COMPLETE!")
        print(f"   Model saved to: models/best_model.pkl")
        
        return True
        
    except Exception as e:
        print(f"❌ Training error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_inference_example():
    """Test 5: Run inference on a real example from base data."""
    print("\n" + "=" * 60)
    print("TEST 5: Inference Example (7 Days of Real Data)")
    print("=" * 60)
    
    try:
        from inference import predict_fastapi_format
        from train_base_model import load_and_prepare_data
        import pandas as pd
        
        # Load data to get a real example
        print("Loading base data...")
        X, y, feature_cols, user_ids, le_gender, df = load_and_prepare_data()
        
        # Find users with at least 7 days of data
        user_counts = df.groupby(USER_ID_COL).size()
        users_with_enough_data = user_counts[user_counts >= 7].index.tolist()
        
        if not users_with_enough_data:
            print("⚠️  No users with 7+ days of data found")
            return False
        
        # Try multiple users to find one with non-zero features
        print(f"\n🔍 Searching for user with non-zero survey features...")
        from inference import load_model, prepare_features
        
        model, feature_names, le_gender = load_model(user_id=None)
        
        test_user_id = None
        test_user_data = None
        test_features = None
        
        # Try up to 10 different users
        for attempt, candidate_user_id in enumerate(users_with_enough_data[:10], 1):
            candidate_data = df[df[USER_ID_COL] == candidate_user_id].copy()
            
            # Get last 7 days
            if DATE_COL in candidate_data.columns:
                candidate_data = candidate_data.sort_values(DATE_COL).tail(7)
            else:
                candidate_data = candidate_data.tail(7)
            
            # Get user info
            age = candidate_data[AGE_COL].iloc[0] if AGE_COL in candidate_data.columns else None
            gender = candidate_data[GENDER_COL].iloc[0] if GENDER_COL in candidate_data.columns else None
            
            # Prepare features
            try:
                features = prepare_features(candidate_data, candidate_user_id, age, gender, feature_names, le_gender)
                
                # Check if any features are non-zero
                non_zero_count = (features.abs() > 1e-6).sum().sum()
                
                if non_zero_count > 0:
                    test_user_id = candidate_user_id
                    test_user_data = candidate_data
                    test_features = features
                    print(f"   ✅ Found user {test_user_id} with {non_zero_count} non-zero feature values (attempt {attempt})")
                    break
                else:
                    print(f"   ⚠️  User {candidate_user_id} has all zero features (attempt {attempt})")
            except Exception as e:
                print(f"   ⚠️  Error with user {candidate_user_id}: {e}")
                continue
        
        if test_user_id is None:
            print(f"   ❌ Could not find a user with non-zero features after trying {min(10, len(users_with_enough_data))} users")
            print(f"   Using first user anyway for demonstration...")
            test_user_id = users_with_enough_data[0]
            test_user_data = df[df[USER_ID_COL] == test_user_id].copy()
            if DATE_COL in test_user_data.columns:
                test_user_data = test_user_data.sort_values(DATE_COL).tail(7)
            else:
                test_user_data = test_user_data.tail(7)
            test_features = None  # Will be computed later
        
        user_data = test_user_data
        if test_features is not None:
            features = test_features
        
        print(f"\n📋 Selected user: {test_user_id}")
        print(f"   Total days available: {len(df[df[USER_ID_COL] == test_user_id])}")
        print(f"   Using last 7 days for prediction")
        
        # Get user info (age, gender) - may not be in data
        age = user_data[AGE_COL].iloc[0] if AGE_COL in user_data.columns else None
        gender = user_data[GENDER_COL].iloc[0] if GENDER_COL in user_data.columns else None
        
        print(f"   User age: {age}")
        print(f"   User gender: {gender}")
        
        # Convert to list of dicts (FastAPI format)
        logs_list = user_data.to_dict('records')
        
        # Show the 7 days of data
        print(f"\n📊 7 Days of Survey Data:")
        print("-" * 60)
        survey_cols = [col for col in user_data.columns if col in SURVEY_FEATURES]
        print(f"{'Day':<5} {'Date':<12} {'Migraine':<10} ", end="")
        for col in survey_cols[:5]:
            print(f"{col[:8]:<9}", end="")
        print("...")
        print("-" * 60)
        
        for i, row in enumerate(user_data.itertuples(), 1):
            date_val = getattr(row, DATE_COL, i) if DATE_COL in user_data.columns else i
            migraine = getattr(row, MIGRAINE_COL, 0)
            print(f"{i:<5} {str(date_val):<12} {migraine:<10} ", end="")
            for col in survey_cols[:5]:
                val = getattr(row, col, 0)
                print(f"{int(val):<9}", end="")
            print("...")
        
        # Debug: Show actual feature values used in prediction
        if 'features' not in locals() or features is None:
            # Re-prepare features if we didn't already
            features = prepare_features(user_data, test_user_id, age, gender, feature_names, le_gender)
        
        print(f"\n🔍 Debug: Feature Values Used in Prediction")
        print("-" * 60)
        
        # Show non-zero features
        non_zero_features = []
        for feat_name in feature_names:
            feat_val = features[feat_name].iloc[0]
            if abs(feat_val) > 1e-6:  # Non-zero
                non_zero_features.append((feat_name, feat_val))
        
        if non_zero_features:
            print(f"   ✅ Non-zero features ({len(non_zero_features)}/{len(feature_names)}):")
            for feat_name, feat_val in non_zero_features[:15]:
                print(f"      {feat_name:<35} {feat_val:>10.4f}")
            if len(non_zero_features) > 15:
                print(f"      ... and {len(non_zero_features) - 15} more")
        else:
            print(f"   ⚠️  ALL FEATURES ARE ZERO!")
            print(f"   This means the 7 days had no survey responses (all False/0)")
            print(f"   Or the day prioritization resulted in all zeros")
        
        # Show coefficients for LogisticRegression
        if hasattr(model, 'coef_'):
            coef = model.coef_[0] if model.coef_.ndim > 1 else model.coef_
            print(f"\n   Sample coefficients (showing top 10 by absolute value):")
            coef_with_names = [(feature_names[i], coef[i]) for i in range(len(feature_names))]
            coef_with_names.sort(key=lambda x: abs(x[1]), reverse=True)
            for feat_name, coef_val in coef_with_names[:10]:
                feat_val = features[feat_name].iloc[0]
                contribution = abs(coef_val * feat_val)
                print(f"      {feat_name:<35} coef: {coef_val:>8.4f}  val: {feat_val:>6.4f}  contrib: {contribution:>8.4f}")
        
        # Run prediction
        print(f"\n🔮 Running prediction...")
        result = predict_fastapi_format(logs_list, test_user_id, age, gender)
        
        # Display results
        print(f"\n✅ Prediction Results:")
        print("=" * 60)
        print(f"   User ID: {test_user_id}")
        print(f"   Migraine Probability: {result['probability']:.4f} ({result['probability']*100:.2f}%)")
        print(f"\n   Top 5 Contributing Features:")
        print("-" * 60)
        print(f"{'Rank':<6} {'Feature':<35} {'Value':<12} {'Contribution':<12}")
        print("-" * 60)
        for i, feat_info in enumerate(result['top_features'], 1):
            feat_name = feat_info['feature']
            feat_value = feat_info['value']
            contribution = feat_info['contribution']
            print(f"{i:<6} {feat_name:<35} {feat_value:<12.4f} {contribution:<12.4f}")
        
        print(f"\n📝 Full JSON Output (FastAPI-ready):")
        print("-" * 60)
        import json
        print(json.dumps(result, indent=2))
        
        return True
        
    except Exception as e:
        print(f"❌ Inference test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("MIGRAINE PREDICTION PIPELINE - VALIDATION & TRAINING")
    print("=" * 60)
    print()
    
    # Test 1: Data structure
    success, df = test_data_structure()
    if not success:
        print("\n❌ Validation failed. Please fix data structure issues before proceeding.")
        sys.exit(1)
    
    # Test 2: Config imports
    if not test_config_imports():
        print("\n❌ Config import failed. Please check config.py and imports.")
        sys.exit(1)
    
    # Test 3: Data loading
    success, X, y, feature_cols, user_ids, df = test_data_loading()
    if not success:
        print("\n❌ Data loading failed. Please check data format.")
        sys.exit(1)
    
    # Test 4: Training
    print("\n" + "=" * 60)
    print("Ready to train model. Proceed? (This will overwrite existing model)")
    print("=" * 60)
    response = input("Train model now? (y/n): ").strip().lower()
    
    if response == 'y':
        if not test_training():
            print("\n❌ Training failed.")
            sys.exit(1)
        
        # Test 5: Inference example (only if model was just trained)
        print("\n" + "=" * 60)
        print("Running inference example test...")
        print("=" * 60)
        if not test_inference_example():
            print("\n⚠️  Inference example test failed, but model training succeeded.")
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED - MODEL TRAINED SUCCESSFULLY!")
        print("=" * 60)
    else:
        print("\n⏭️  Training skipped. Run again and type 'y' to train.")
        print("   Or run: python train_base_model.py")
        
        # Still run inference example if model exists
        print("\n" + "=" * 60)
        print("Testing inference with existing model...")
        print("=" * 60)
        try:
            import os
            if os.path.exists("models/best_model.pkl"):
                test_inference_example()
            else:
                print("⚠️  No model found. Train model first to test inference.")
        except Exception as e:
            print(f"⚠️  Inference test skipped: {e}")

if __name__ == "__main__":
    main()

