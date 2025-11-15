"""
Retrain Model with User-Collected Data

This script retrains the migraine prediction model by combining:
1. Original training data
2. User-collected data from the training pool

Run this script periodically (e.g., weekly) after collecting sufficient user data.
"""

import pandas as pd
import os
import sys
from datetime import datetime
import shutil
from train_model import MigrainePredictionSystem

def retrain_model():
    print("\n" + "="*70)
    print("RETRAINING MODEL WITH USER DATA")
    print("="*70)
    
    # ============================================
    # 1. Load Original Training Data
    # ============================================
    print("\n📂 Step 1: Loading original training data...")
    
    try:
        df_original = pd.read_excel('../junc2025sensordata.xlsx')
        
        # Parse if CSV-in-Excel format
        if len(df_original.columns) == 1:
            print("   Parsing CSV-formatted Excel file...")
            col_name = df_original.columns[0]
            header = col_name.split(',')
            df_original = df_original[col_name].str.split(',', expand=True)
            df_original.columns = header
            
            # Convert to numeric
            for col in df_original.columns:
                if col not in ['UserID']:
                    df_original[col] = pd.to_numeric(df_original[col], errors='coerce')
        
        print(f"   ✓ Original data: {len(df_original)} records")
        print(f"   ✓ Users: {df_original['UserID'].nunique()}")
        
        # Show migraine distribution
        migraine_dist = df_original['Migraine_today_0_or_1'].value_counts()
        print(f"   ✓ Migraines: {migraine_dist.get(1, 0)} ({migraine_dist.get(1, 0)/len(df_original)*100:.1f}%)")
        print(f"   ✓ No migraines: {migraine_dist.get(0, 0)} ({migraine_dist.get(0, 0)/len(df_original)*100:.1f}%)")
        
    except Exception as e:
        print(f"   ⚠️  Could not load original data: {e}")
        print(f"   → Will train on user data only")
        df_original = None
    
    # ============================================
    # 2. Load User Training Pool
    # ============================================
    print("\n📚 Step 2: Loading user training pool...")
    
    training_pool_file = 'user_data/training_pool.csv'
    
    if not os.path.exists(training_pool_file):
        print(f"   ❌ Training pool not found at {training_pool_file}")
        print(f"\n   💡 No user data collected yet!")
        print(f"   → Use store_temporal_data() to collect user data")
        print(f"   → Each time a user confirms a migraine outcome, data is added")
        print(f"   → Come back when you have at least 30-50 user records\n")
        return False
    
    try:
        df_pool = pd.read_csv(training_pool_file)
        
        print(f"   ✓ Training pool: {len(df_pool)} records")
        print(f"   ✓ Unique users: {df_pool['UserID'].nunique()}")
        
        # Show migraine distribution
        migraine_counts = df_pool['Migraine_today_0_or_1'].value_counts()
        print(f"   ✓ Migraines: {migraine_counts.get(1, 0)} ({migraine_counts.get(1, 0)/len(df_pool)*100:.1f}%)")
        print(f"   ✓ No migraines: {migraine_counts.get(0, 0)} ({migraine_counts.get(0, 0)/len(df_pool)*100:.1f}%)")
        
        # Check if enough data
        if len(df_pool) < 30:
            print(f"\n   ⚠️  Warning: Only {len(df_pool)} records in training pool")
            print(f"   → Recommended minimum: 30-50 records")
            response = input(f"   → Continue anyway? (y/n): ")
            if response.lower() != 'y':
                print("\n   → Retraining cancelled. Collect more data and try again.\n")
                return False
        
    except Exception as e:
        print(f"   ❌ Error loading training pool: {e}")
        return False
    
    # ============================================
    # 3. Combine Datasets
    # ============================================
    print("\n🔗 Step 3: Combining datasets...")
    
    if df_original is not None:
        # Get common columns
        common_cols = list(set(df_original.columns) & set(df_pool.columns))
        print(f"   ✓ Common columns: {len(common_cols)}")
        
        # Ensure both have same columns in same order
        df_original_aligned = df_original[common_cols]
        df_pool_aligned = df_pool[common_cols]
        
        # Combine
        df_combined = pd.concat([df_original_aligned, df_pool_aligned], ignore_index=True)
        
        print(f"\n   📊 Combined Dataset:")
        print(f"   ✓ Total records: {len(df_combined)}")
        print(f"   ✓ Original data: {len(df_original)} ({len(df_original)/len(df_combined)*100:.1f}%)")
        print(f"   ✓ User data: {len(df_pool)} ({len(df_pool)/len(df_combined)*100:.1f}%)")
        
    else:
        df_combined = df_pool
        print(f"   ✓ Using only user data: {len(df_combined)} records")
    
    # Show final distribution
    print(f"\n   📊 Final Dataset:")
    print(f"   ✓ Total records: {len(df_combined)}")
    print(f"   ✓ Unique users: {df_combined['UserID'].nunique()}")
    
    migraine_final = df_combined['Migraine_today_0_or_1'].value_counts()
    print(f"   ✓ Migraines: {migraine_final.get(1, 0)} ({migraine_final.get(1, 0)/len(df_combined)*100:.1f}%)")
    print(f"   ✓ No migraines: {migraine_final.get(0, 0)} ({migraine_final.get(0, 0)/len(df_combined)*100:.1f}%)")
    
    # ============================================
    # 4. Backup Old Model
    # ============================================
    print("\n💾 Step 4: Backing up current model...")
    
    model_file = 'models/migraine_model.pkl'
    scaler_file = 'models/scaler.pkl'
    
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    if os.path.exists(model_file):
        backup_model = f'models/backups/migraine_model_backup_{timestamp}.pkl'
        backup_scaler = f'models/backups/scaler_backup_{timestamp}.pkl'
        
        # Create backup directory
        os.makedirs('models/backups', exist_ok=True)
        
        shutil.copy(model_file, backup_model)
        shutil.copy(scaler_file, backup_scaler)
        
        print(f"   ✓ Model backed up: {backup_model}")
        print(f"   ✓ Scaler backed up: {backup_scaler}")
        print(f"   💡 You can restore from backup if needed")
    else:
        print(f"   → No existing model to backup")
    
    # ============================================
    # 5. Train New Model
    # ============================================
    print("\n🎓 Step 5: Training new model...")
    print(f"   This may take a minute...\n")
    
    # Save combined data temporarily
    temp_file = 'temp_training_data.csv'
    df_combined.to_csv(temp_file, index=False)
    
    try:
        # Initialize predictor
        predictor = MigrainePredictionSystem()
        
        # Prepare data
        print("   Preparing data...")
        X, y, df_processed = predictor.prepare_data(temp_file)
        
        # Train
        print("   Training model...")
        predictor.train(X, y, df_processed)
        
        # Save
        print("   Saving new model...")
        predictor.save_model(model_file, scaler_file)
        
        print(f"\n{'='*70}")
        print("✅ MODEL RETRAINED SUCCESSFULLY")
        print(f"{'='*70}")
        
        print(f"\n📊 Training Summary:")
        print(f"   ✓ Model saved to: {model_file}")
        print(f"   ✓ Scaler saved to: {scaler_file}")
        print(f"   ✓ Trained on {len(df_combined)} records")
        print(f"   ✓ Includes {df_combined['UserID'].nunique()} users")
        if df_original is not None:
            print(f"   ✓ User contribution: {len(df_pool)} records ({len(df_pool)/len(df_combined)*100:.1f}%)")
        
        print(f"\n💡 Next Steps:")
        print(f"   1. Test the updated model with test data")
        print(f"   2. Make predictions using predict_temporal()")
        print(f"   3. Continue collecting user data")
        print(f"   4. Retrain again when you have more data")
        
        print(f"\n🎉 The model will now use the updated version for all predictions!\n")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Training failed: {e}")
        print(f"\n💡 The old model is still intact and can be used.")
        
        import traceback
        print("\nError details:")
        traceback.print_exc()
        
        return False
        
    finally:
        # Clean up temp file
        if os.path.exists(temp_file):
            os.remove(temp_file)


def show_training_pool_status():
    """Show current status of training pool"""
    print("\n" + "="*70)
    print("TRAINING POOL STATUS")
    print("="*70)
    
    training_pool_file = 'user_data/training_pool.csv'
    
    if not os.path.exists(training_pool_file):
        print("\n❌ No training pool found")
        print("   → Start collecting user data with store_temporal_data()\n")
        return
    
    df = pd.read_csv(training_pool_file)
    
    print(f"\n📊 Overall Statistics:")
    print(f"   Total records: {len(df)}")
    print(f"   Unique users: {df['UserID'].nunique()}")
    
    print(f"\n📈 Migraine Distribution:")
    migraine_counts = df['Migraine_today_0_or_1'].value_counts()
    print(f"   Migraines (1): {migraine_counts.get(1, 0)} ({migraine_counts.get(1, 0)/len(df)*100:.1f}%)")
    print(f"   No migraines (0): {migraine_counts.get(0, 0)} ({migraine_counts.get(0, 0)/len(df)*100:.1f}%)")
    
    print(f"\n👥 Data per User:")
    user_counts = df['UserID'].value_counts()
    for user, count in user_counts.head(10).items():
        print(f"   {user}: {count} records")
    
    if len(user_counts) > 10:
        print(f"   ... and {len(user_counts) - 10} more users")
    
    print(f"\n💡 Recommendations:")
    if len(df) < 30:
        print(f"   ⚠️  Only {len(df)} records - collect at least 30 before retraining")
    elif len(df) < 100:
        print(f"   ✓ {len(df)} records - ready for retraining!")
        print(f"   → More data will improve model accuracy")
    else:
        print(f"   ✅ {len(df)} records - excellent dataset!")
        print(f"   → Ready for retraining")
    
    print()


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'status':
        # Show status only
        show_training_pool_status()
    else:
        # Run retraining
        print("\n🚀 Starting model retraining process...")
        print("="*70)
        
        # Show current pool status first
        show_training_pool_status()
        
        # Confirm before proceeding
        print("\n" + "="*70)
        response = input("Proceed with retraining? (y/n): ")
        
        if response.lower() == 'y':
            success = retrain_model()
            
            if success:
                print("\n✅ Retraining complete!")
            else:
                print("\n❌ Retraining failed or cancelled")
        else:
            print("\n→ Retraining cancelled\n")

