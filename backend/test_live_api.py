import requests
import json

MATCH_ID = "401862897"

url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/summary?event={MATCH_ID}"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

print("Status:", response.status_code)
print("\n--- STATISTICS ---\n")

print(
    json.dumps(
        data.get("statistics", {}),
        indent=2
    )[:4000]
)
