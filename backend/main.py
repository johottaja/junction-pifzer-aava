from sensorAiGet import check_migraine_risk

res = check_migraine_risk(1)
print(f"Probability: {res['probability']}")
print(f"Reason 1: {res['reason1']}")
print(f"Reason 2: {res['reason2']}")

