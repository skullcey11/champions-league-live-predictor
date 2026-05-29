import requests
import json

MATCH_ID = "401862897"

url = f"https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/summary?event={MATCH_ID}"

response = requests.get(
    url,
    headers={"User-Agent": "Mozilla/5.0"}
)

data = response.json()

print("\n--- ROSTERS ---\n")

print(
    json.dumps(
        data.get("rosters", {}),
        indent=2
    )[:5000]
)