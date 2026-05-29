import requests

MATCH_ID = "401862897"


def calculate_team_elo(team_data):
    elo = 1500

    events = team_data.get("events", [])[:5]

    for match in events:
        result = match.get("gameResult", "D")

        home_score = int(
            match.get(
                "homeTeamScore",
                0
            )
        )

        away_score = int(
            match.get(
                "awayTeamScore",
                0
            )
        )

        goal_diff = abs(
            home_score - away_score
        )

        if result == "W":
            elo += 25

        elif result == "D":
            elo += 10

        elif result == "L":
            elo -= 15

        elo += goal_diff * 4

    return elo


def get_live_elo():
    url = (
        f"https://site.api.espn.com/apis/site/v2/sports/soccer/uefa.champions/summary?event={MATCH_ID}"
    )

    response = requests.get(
        url,
        headers={
            "User-Agent":
            "Mozilla/5.0"
        }
    )

    data = response.json()

    form_data = (
        data.get("boxscore", {})
        .get("form", [])
    )

    if len(form_data) < 2:
        return 1500, 1500

    psg_elo = calculate_team_elo(
        form_data[0]
    )

    arsenal_elo = (
        calculate_team_elo(
            form_data[1]
        )
    )

    return psg_elo, arsenal_elo


def elo_probability(
    psg_elo,
    arsenal_elo
):
    total = (
        psg_elo +
        arsenal_elo
    )

    psg_pct = (
        psg_elo / total
    ) * 100

    arsenal_pct = (
        arsenal_elo / total
    ) * 100

    return psg_pct, arsenal_pct