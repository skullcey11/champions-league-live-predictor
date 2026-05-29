import requests
import json

MATCH_ID = "401862897"

url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/summary?event={MATCH_ID}"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

print("\n--- KEYS ---\n")
print(data.keys())

print("\n--- LINEUPS ---\n")
print(
    json.dumps(
        data.get("lineups", {}),
        indent=2
    )[:5000]
)