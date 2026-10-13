"""
generate_data.py
----------------
Generates a reproducible SYNTHETIC football player dataset.
All names, teams, statistics and results are entirely fictional.
This data does NOT represent any real athletes or competitions.

Run:  python generate_data.py
Output: football_players.csv
"""

import numpy as np
import pandas as pd

# ── Reproducibility ───────────────────────────────────────────────────────────
np.random.seed(42)

# ── Reference data ────────────────────────────────────────────────────────────
TEAMS = [
    "Northgate United", "Riverside City", "Eastfield FC",
    "Westbrook Athletic", "Southport Rovers", "Ironbridge Town",
    "Lakewood Dynamo", "Cresthill Rangers", "Stonewall FC", "Portview Stars",
]

POSITIONS = {
    "GK":  0.10,   # 10 % of squad
    "DEF": 0.30,
    "MID": 0.35,
    "FWD": 0.25,
}

SEASONS = ["2021-22", "2022-23", "2023-24"]

NATIONALITIES = [
    "English", "Spanish", "French", "German", "Brazilian",
    "Argentine", "Portuguese", "Italian", "Dutch", "Belgian",
    "Croatian", "Senegalese", "Ghanaian", "Moroccan", "Japanese",
    "Korean", "Mexican", "Colombian", "Norwegian", "Swedish",
]

FIRST_NAMES = [
    "James", "Carlos", "Luca", "Marco", "Pedro", "Lucas", "Theo", "Kai",
    "Emil", "Diego", "Andre", "Niko", "Sven", "Omar", "Yusuf", "Kenji",
    "Paulo", "Rafa", "Tom", "Alex", "Ben", "Chris", "Dan", "Eli",
    "Felix", "Gabe", "Hugo", "Ivan", "Jake", "Kurt", "Leo", "Max",
    "Noel", "Oscar", "Phil", "Quinn", "Ryan", "Sam", "Tyler", "Victor",
]

LAST_NAMES = [
    "Silva", "Costa", "Müller", "Dupont", "Rossi", "García", "Jones",
    "Bakker", "Petrov", "Nkosi", "Diallo", "Tanaka", "Park", "Martínez",
    "Ferreira", "Berg", "Hansen", "Andersen", "Mensah", "Boateng",
    "Alves", "Gomez", "Richter", "Laurent", "Moreira", "Santos",
    "Fischer", "Wagner", "Weber", "Becker", "Hoffmann", "Schulz",
    "Maier", "Koch", "Wolf", "Schäfer", "Meyer", "Neumann", "Schwarz",
    "Zimmermann",
]


def make_name(used: set) -> str:
    while True:
        name = f"{np.random.choice(FIRST_NAMES)} {np.random.choice(LAST_NAMES)}"
        if name not in used:
            used.add(name)
            return name


# ── Per-position stat generators ──────────────────────────────────────────────
def position_stats(pos: str, appearances: int) -> dict:
    """Return position-realistic per-season stats."""

    if pos == "GK":
        goals         = int(np.random.choice([0, 1], p=[0.97, 0.03]))
        assists        = int(np.random.choice([0, 1], p=[0.90, 0.10]))
        shots          = goals + int(np.random.randint(0, 3))
        shots_on_tgt   = min(shots, goals + int(np.random.randint(0, 2)))
        pass_acc       = round(float(np.random.uniform(58, 78)), 1)
        clean_sheets   = int(np.random.randint(0, min(appearances, 20) + 1))
        rating         = round(float(np.random.uniform(6.0, 8.5)), 1)

    elif pos == "DEF":
        goals         = int(np.random.randint(0, 6))
        assists        = int(np.random.randint(0, 8))
        shots          = goals + int(np.random.randint(0, 15))
        shots_on_tgt   = min(shots, goals + int(np.random.randint(0, 8)))
        pass_acc       = round(float(np.random.uniform(68, 90)), 1)
        clean_sheets   = int(np.random.randint(0, min(appearances, 15) + 1))
        rating         = round(float(np.random.uniform(5.5, 8.8)), 1)

    elif pos == "MID":
        goals         = int(np.random.randint(0, 16))
        assists        = int(np.random.randint(0, 18))
        shots          = goals + int(np.random.randint(2, 30))
        shots_on_tgt   = min(shots, goals + int(np.random.randint(1, 15)))
        pass_acc       = round(float(np.random.uniform(72, 95)), 1)
        clean_sheets   = 0
        rating         = round(float(np.random.uniform(5.5, 9.0)), 1)

    else:  # FWD
        goals         = int(np.random.randint(2, 31))
        assists        = int(np.random.randint(0, 15))
        shots          = goals + int(np.random.randint(5, 40))
        shots_on_tgt   = min(shots, goals + int(np.random.randint(3, 20)))
        pass_acc       = round(float(np.random.uniform(62, 88)), 1)
        clean_sheets   = 0
        rating         = round(float(np.random.uniform(5.8, 9.5)), 1)

    return dict(
        goals=goals,
        assists=assists,
        shots=shots,
        shots_on_target=shots_on_tgt,
        pass_accuracy=pass_acc,
        clean_sheets=clean_sheets,
        rating=rating,
    )


# ── Build dataset ─────────────────────────────────────────────────────────────
PLAYERS_PER_TEAM = 12   # 10 teams × 12 = 120 unique players

def build_dataset() -> pd.DataFrame:
    rows = []
    player_id = 1
    used_names: set = set()
    positions_list = list(POSITIONS.keys())
    pos_weights    = list(POSITIONS.values())

    for team in TEAMS:
        team_positions = np.random.choice(
            positions_list, size=PLAYERS_PER_TEAM, p=pos_weights
        )
        # Ensure at least 1 GK per team
        if "GK" not in team_positions:
            team_positions[0] = "GK"

        for pos in team_positions:
            name        = make_name(used_names)
            nationality = np.random.choice(NATIONALITIES)
            age_base    = int(np.random.randint(18, 35))

            for season_idx, season in enumerate(SEASONS):
                appearances = int(np.random.randint(5, 38))
                minutes     = int(appearances * np.random.randint(50, 95))
                yellow      = int(np.random.randint(0, 10))
                red         = int(np.random.randint(0, 3))
                stats       = position_stats(pos, appearances)

                rows.append({
                    "player_id":      player_id,
                    "player_name":    name,
                    "team":           team,
                    "position":       pos,
                    "season":         season,
                    "age":            age_base + season_idx,
                    "nationality":    nationality,
                    "appearances":    appearances,
                    "minutes_played": minutes,
                    "goals":          stats["goals"],
                    "assists":        stats["assists"],
                    "shots":          stats["shots"],
                    "shots_on_target": stats["shots_on_target"],
                    "pass_accuracy":  stats["pass_accuracy"],
                    "clean_sheets":   stats["clean_sheets"],
                    "yellow_cards":   yellow,
                    "red_cards":      red,
                    "rating":         stats["rating"],
                })

            player_id += 1

    df = pd.DataFrame(rows)

    # Enforce dtypes
    int_cols = [
        "player_id", "age", "appearances", "minutes_played",
        "goals", "assists", "shots", "shots_on_target",
        "clean_sheets", "yellow_cards", "red_cards",
    ]
    for c in int_cols:
        df[c] = df[c].astype(int)

    df["pass_accuracy"] = df["pass_accuracy"].astype(float)
    df["rating"]        = df["rating"].astype(float)

    return df


if __name__ == "__main__":
    df = build_dataset()
    df.to_csv("football_players.csv", index=False)
    print(f"[OK] football_players.csv written -- {len(df)} rows, {df.shape[1]} columns")
    print(f"    Unique players  : {df['player_id'].nunique()}")
    print(f"    Seasons         : {sorted(df['season'].unique())}")
    print(f"    Teams           : {df['team'].nunique()}")
    print(f"    Positions       : {df['position'].value_counts().to_dict()}")
    print(f"    Null values     : {df.isnull().sum().sum()}")
