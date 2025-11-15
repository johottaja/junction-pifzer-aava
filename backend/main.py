from sensorAiGet import train_user_model_from_db, check_migraine_risk

# Train model for user_id 1
result = train_user_model_from_db(user_id=1)
print(f"Accuracy: {result['accuracy']}")

# Check migraine risk
res = check_migraine_risk(1)
print(f"Probability: {res['probability']}")
print(f"Reason 1: {res['reason1']}")
print(f"Reason 2: {res['reason2']}")
