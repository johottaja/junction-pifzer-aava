"""
Train personalized models for specific users
"""

import sys
from simple_predict import train_user_model, get_user_info, list_all_users


def main():
    """Main training function"""
    
    if len(sys.argv) < 2:
        print("\n" + "="*70)
        print("TRAIN USER-SPECIFIC MODEL")
        print("="*70)
        print("\nUsage:")
        print("  python train_user.py <user_id>        - Train model for specific user")
        print("  python train_user.py --list           - List all users")
        print("  python train_user.py --info <user_id> - Get info about a user")
        print("\nExamples:")
        print("  python train_user.py user123")
        print("  python train_user.py patient_001")
        print("  python train_user.py --list")
        print("  python train_user.py --info user123")
        print("="*70 + "\n")
        sys.exit(1)
    
    command = sys.argv[1]
    
    # List all users
    if command == "--list":
        users_info = list_all_users()
        print("\n" + "="*70)
        print("ALL USERS IN SYSTEM")
        print("="*70)
        
        if not users_info['all_users']:
            print("\nNo users found in the system.")
            print("Start by storing data with store_training_data()")
        else:
            print(f"\nTotal users: {len(users_info['all_users'])}")
            print(f"\nUsers with data: {len(users_info['users_with_data'])}")
            for user_id in users_info['users_with_data']:
                info = get_user_info(user_id)
                print(f"  - {user_id}: {info['data_points']} data points")
            
            print(f"\nUsers with trained models: {len(users_info['users_with_models'])}")
            for user_id in users_info['users_with_models']:
                print(f"  - {user_id}: ✓ Model trained")
        
        print("="*70 + "\n")
        return
    
    # Get user info
    if command == "--info":
        if len(sys.argv) < 3:
            print("Error: Please specify user_id")
            print("Usage: python train_user.py --info <user_id>")
            sys.exit(1)
        
        user_id = sys.argv[2]
        info = get_user_info(user_id)
        
        print("\n" + "="*70)
        print(f"USER INFO: {user_id}")
        print("="*70)
        print(f"Has data: {'Yes' if info['has_data'] else 'No'}")
        print(f"Data points: {info['data_points']}")
        print(f"Has trained model: {'Yes' if info['has_model'] else 'No'}")
        print(f"Can train model: {'Yes' if info['can_train'] else 'No'}")
        print(f"\nStatus: {info['status']}")
        print("="*70 + "\n")
        return
    
    # Train model for user
    user_id = command
    
    print(f"\nChecking user '{user_id}'...")
    info = get_user_info(user_id)
    
    if not info['has_data']:
        print(f"\n❌ ERROR: User '{user_id}' has no data.")
        print("   Please collect data first using store_training_data()")
        sys.exit(1)
    
    if info['data_points'] < 10:
        print(f"\n❌ ERROR: User '{user_id}' has only {info['data_points']} data points.")
        print(f"   Need at least 10 data points to train a model.")
        print(f"   Collect {10 - info['data_points']} more data points.")
        sys.exit(1)
    
    # Train the model
    try:
        result = train_user_model(user_id)
        
        print("\n" + "="*70)
        print("TRAINING COMPLETE!")
        print("="*70)
        print(f"User ID: {user_id}")
        print(f"Data points used: {result['data_points']}")
        print(f"Training accuracy: {result['accuracy']:.2f}%")
        print(f"Migraine occurrences: {result['migraine_count']}")
        print(f"No migraine: {result['no_migraine_count']}")
        print("\nTop 3 triggers for this user:")
        sorted_features = sorted(result['feature_importance'].items(), 
                                key=lambda x: x[1], reverse=True)
        for i, (feature, importance) in enumerate(sorted_features[:3], 1):
            print(f"  {i}. {feature}: {importance:.4f}")
        print("="*70 + "\n")
        
    except Exception as e:
        print(f"\n❌ TRAINING FAILED: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

