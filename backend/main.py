from sensorAiGet import train_user_model_from_db,check_migraine_risk


# Train model for user_id 1
result = train_user_model_from_db(user_id=1)


 
print(result['accuracy'])
   
res =check_migraine_risk(1)
print(res['probability'])