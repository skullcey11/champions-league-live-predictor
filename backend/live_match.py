import requests
import json

url = "https://www.fotmob.com/api/matches"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, headers=headers)

print("Status:", response.status_code)

data = response.json()

print(json.dumps(data, indent=2)[:1000])