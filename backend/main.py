from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from elo import get_live_elo, elo_probability
import requests
import re

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

MATCH_ID = "401862897"


class MatchInput(BaseModel):
    minute: int

    psg_goals: int
    arsenal_goals: int

    psg_shots: int
    arsenal_shots: int

    psg_possession: int
    arsenal_possession: int

    psg_corners: int
    arsenal_corners: int


def fetch_match_data():
    url = (
        f"https://site.api.espn.com/apis/site/v2/"
        f"sports/soccer/uefa.champions/"
        f"summary?event={MATCH_ID}"
    )

    response = requests.get(
        url,
        headers={
            "User-Agent": "Mozilla/5.0"
        }
    )

    return response.json()


@app.post("/predict")
def predict(match: MatchInput):

    psg_elo, arsenal_elo = get_live_elo()

    psg_strength, arsenal_strength = elo_probability(
        psg_elo,
        arsenal_elo
    )

    score_diff = (
        match.psg_goals -
        match.arsenal_goals
    )

    psg_strength += score_diff * 18

    psg_strength += (
        match.psg_shots -
        match.arsenal_shots
    ) * 2

    psg_strength += (
        match.psg_possession -
        match.arsenal_possession
    ) * 0.5

    psg_strength += (
        match.psg_corners -
        match.arsenal_corners
    ) * 1.5

    if match.minute >= 75:
        psg_strength += score_diff * 8

    if match.minute >= 90:
        psg_strength += score_diff * 12

    if match.minute >= 105:
        psg_strength += score_diff * 16

    if match.minute >= 120:
        psg_strength += score_diff * 20

    psg_strength = max(
        1,
        min(99, psg_strength)
    )

    arsenal_strength = (
        100 - psg_strength
    )

    if score_diff == 0:
        draw = max(
            10,
            35 -
            (match.minute * 0.12)
        )
    else:
        draw = max(
            5,
            30 -
            abs(score_diff * 10) -
            (match.minute * 0.15)
        )

    if (
        match.minute >= 120
        and
        match.psg_goals ==
        match.arsenal_goals
    ):
        draw = 0

    total = (
        psg_strength +
        arsenal_strength +
        draw
    )

    return {
        "psg_win": round(
            (psg_strength / total) * 100
        ),
        "draw": round(
            (draw / total) * 100
        ),
        "arsenal_win": round(
            (arsenal_strength / total) * 100
        )
    }


@app.get("/live-match")
def live_match():
    try:
        data = fetch_match_data()

        competition = (
            data.get("header", {})
            .get("competitions", [{}])[0]
        )

        competitors = (
            competition.get(
                "competitors",
                []
            )
        )

        status = (
            competition
            .get("status", {})
            .get("type", {})
            .get(
                "detail",
                "Kickoff Soon"
            )
        )

        minute = 0
        added_time = 0

        match = re.search(
            r"(\d+)(?:\+(\d+))?'",
            status
        )

        if match:
            minute = int(
                match.group(1)
            )

            if match.group(2):
                added_time = int(
                    match.group(2)
                )

        psg_goals = 0
        arsenal_goals = 0

        for team in competitors:
            name = team.get(
                "team",
                {}
            ).get(
                "displayName",
                ""
            )

            score = int(
                team.get(
                    "score",
                    0
                )
            )

            if (
                "Paris Saint-Germain"
                in name
            ):
                psg_goals = score

            elif "Arsenal" in name:
                arsenal_goals = score

        psg_shots = 0
        arsenal_shots = 0

        psg_corners = 0
        arsenal_corners = 0

        psg_possession = 50
        arsenal_possession = 50

        stats = (
            data.get(
                "boxscore",
                {}
            ).get(
                "statistics",
                []
            )
        )

        for stat_group in stats:
            for stat in stat_group.get(
                "stats",
                []
            ):

                name = stat.get(
                    "name",
                    ""
                )

                values = stat.get(
                    "displayValue",
                    "0-0"
                )

                if "-" not in values:
                    continue

                split = values.split(
                    "-"
                )

                if len(split) != 2:
                    continue

                home = split[0]
                away = split[1]

                if name == "shotsTotal":
                    psg_shots = int(home)
                    arsenal_shots = int(away)

                elif name == "cornerKicks":
                    psg_corners = int(home)
                    arsenal_corners = int(away)

                elif name == "possessionPct":
                    psg_possession = int(home)
                    arsenal_possession = int(away)

        return {
            "minute": minute,
            "added_time": added_time,
            "status": status,

            "psg_goals": psg_goals,
            "arsenal_goals": arsenal_goals,

            "psg_shots": psg_shots,
            "arsenal_shots": arsenal_shots,

            "psg_corners": psg_corners,
            "arsenal_corners": arsenal_corners,

            "psg_possession": psg_possession,
            "arsenal_possession": arsenal_possession,
        }

    except Exception as e:
        print(
            "Live match fallback:",
            e
        )

        return {
            "minute": 0,
            "added_time": 0,
            "status": "Kickoff Soon",

            "psg_goals": 0,
            "arsenal_goals": 0,

            "psg_shots": 0,
            "arsenal_shots": 0,

            "psg_corners": 0,
            "arsenal_corners": 0,

            "psg_possession": 50,
            "arsenal_possession": 50,
        }


@app.get("/motm")
def get_motm():

    data = fetch_match_data()

    leaders_data = data.get(
        "leaders",
        []
    )

    player_scores = {}

    for team in leaders_data:
        for category in team.get(
            "leaders",
            []
        ):
            for leader in category.get(
                "leaders",
                []
            ):

                athlete = leader.get(
                    "athlete",
                    {}
                )

                name = athlete.get(
                    "displayName"
                )

                if not name:
                    continue

                if name not in player_scores:
                    player_scores[name] = 0

                for stat in leader.get(
                    "statistics",
                    []
                ):

                    stat_type = stat.get(
                        "name"
                    )

                    value = stat.get(
                        "value",
                        0
                    )

                    if stat_type == "totalGoals":
                        player_scores[name] += value * 10

                    elif stat_type == "assists":
                        player_scores[name] += value * 7

                    elif stat_type == "shotsTotal":
                        player_scores[name] += value * 2

    sorted_players = sorted(
        player_scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:5]

    total = sum(
        score for _, score
        in sorted_players
    )

    result = []

    for player, score in sorted_players:

        pct = round(
            (
                score / total
            ) * 100
        ) if total > 0 else 0

        result.append({
            "name": player,
            "score": pct
        })

    return result


@app.get("/recent-form")
def recent_form():

    data = fetch_match_data()

    form_data = (
        data.get("boxscore", {})
        .get("form", [])
    )

    psg = []
    arsenal = []

    if len(form_data) >= 2:

        psg = [
            event.get(
                "gameResult",
                "D"
            )
            for event in
            form_data[0].get(
                "events",
                []
            )[:5]
        ]

        arsenal = [
            event.get(
                "gameResult",
                "D"
            )
            for event in
            form_data[1].get(
                "events",
                []
            )[:5]
        ]

    return {
        "psg": psg,
        "arsenal": arsenal
    }