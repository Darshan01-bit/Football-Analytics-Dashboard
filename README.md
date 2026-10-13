# ⚽ Football Player Performance Analytics Dashboard

> **Synthetic Data Notice:** All player names, team names and statistics in this project are entirely AI-generated and fictional. They do not represent any real athletes, clubs, or competitions.

A portfolio-quality, interactive football (soccer) analytics dashboard built with **Python**, **Streamlit**, **Pandas**, and **Plotly**. Analyse synthetic player and team performance data across multiple seasons with a dark, football-inspired UI.

---

## Features

| # | Feature |
|---|---------|
| 1 | **Overview page** — KPI cards (Total Players, Goals, Assists, Minutes, Avg Rating), rating histogram, top-10 scorers bar, goals & assists by season |
| 2 | **Player Analysis page** — Goals vs Assists scatter, Shots vs Goals scatter with trendline, head-to-head radar comparison for any two players |
| 3 | **Team Analysis page** — Grouped goals + assists bar, squad-size bar, avg rating bar, team leaderboard table |
| 4 | **Position Analysis page** — Distribution donut, avg-stats radar across GK/DEF/MID/FWD, per-position KPI cards, position summary table |
| 5 | **Sidebar filters** — Season, Team, Position (multi-select), single Player highlight |
| 6 | **Searchable stats table** — Full-text player name search over the filtered dataset |
| 7 | **CSV download** — One-click export of the currently filtered and searched data |
| 8 | **Dark football UI** — Navy & green pitch theme, custom metric cards, consistent Plotly dark template |
| 9 | **Responsive layout** — Wide Streamlit layout, chart tooltips, axis labels on every chart |
| 10 | **Input validation** — Empty-state guards, missing-value handling, synthetic data disclaimers throughout |

---

## Dataset

| Column | Type | Description |
|--------|------|-------------|
| player_id | int | Unique player ID |
| player_name | str | Synthetic full name |
| team | str | One of 10 fictional clubs |
| position | str | GK / DEF / MID / FWD |
| season | str | 2021-22, 2022-23, 2023-24 |
| age | int | 18–38 |
| nationality | str | One of 20 nationalities |
| appearances | int | Matches played (1–38) |
| goals | int | Season goals (position-realistic) |
| assists | int | Season assists |
| shots | int | Total shots |
| shots_on_target | int | Shots on target |
| pass_accuracy | float | Pass accuracy % |
| minutes_played | int | Total minutes |
| yellow_cards | int | Yellow cards |
| red_cards | int | Red cards |
| rating | float | Season rating (5.0–9.5) |
| clean_sheets | int | GK/DEF meaningful; 0 for others |

**120 unique players × 3 seasons = 360 rows**  
Seed: `numpy.random.seed(42)` — fully reproducible.

---

## Project Structure

```
Super Analysis Dashboard/
├── app.py                     # Streamlit dashboard (all pages)
├── generate_data.py           # Synthetic dataset generator
├── football_players.csv       # Pre-generated dataset (360 rows)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## Local Setup

### Prerequisites
- Python 3.9 or higher
- pip

### Steps

```bash
# 1. Clone or download the project
cd "Super Analysis Dashboard"

# 2. (Optional) create a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS / Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) regenerate the synthetic dataset
py generate_data.py        # Windows
python generate_data.py    # macOS / Linux

# 5. Run the dashboard
streamlit run app.py
```

The app opens automatically at **http://localhost:8501**.

---

## Streamlit Community Cloud Deployment

1. Push the project folder to a **public GitHub repository**.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in.
3. Click **New app** → select your repository, branch, and set the main file to `app.py`.
4. Click **Deploy**. Streamlit Cloud installs `requirements.txt` automatically.

> **Note:** `football_players.csv` must be committed to the repository.  
> Alternatively, add a `@st.cache_data` call that runs `generate_data.build_dataset()` on cold start if the CSV is absent.

---

## Tech Stack

| Library | Version | Purpose |
|---------|---------|---------|
| [Streamlit](https://streamlit.io) | ≥ 1.32 | Web app framework |
| [Pandas](https://pandas.pydata.org) | ≥ 2.0 | Data manipulation |
| [NumPy](https://numpy.org) | ≥ 1.26 | Numerical operations |
| [Plotly](https://plotly.com/python/) | ≥ 5.20 | Interactive charts |

---

## Screenshots

_Add screenshots here after first run._

---

## License

This project is released for portfolio and educational purposes. The synthetic dataset may be freely reused. No real personal data is included.
