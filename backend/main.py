from supabase import create_client
import requests
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# Debug: Print what we got
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')


supabase = create_client(url, key)

# Hae kaikki rivit taulusta "users"
data = supabase.table("users").select("*").execute()
rows = data.data  # lista dict-muotoisia rivejä
print("Rows fetched from Supabase:", rows)

# Lähetä rivit POST-pyynnöllä FastAPIin
for row in rows:
    response = requests.post("http://127.0.0.1:8000/users/", json=row)
    print(response.json())