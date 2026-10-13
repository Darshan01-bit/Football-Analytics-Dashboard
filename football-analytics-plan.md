# Football Player Performance Analytics Dashboard — Implementation Plan

## Top-Level Overview

**Goal:** Build a portfolio-quality, interactive football (soccer) player analytics dashboard using Python and Streamlit, backed by a reproducible synthetic dataset of 100+ players across multiple teams and positions.

**Scope:**
- Four deliverables: `app.py`, `football_players.csv`, `requirements.txt`, `README.md`
- An optional `generate_data.py` to regenerate the synthetic dataset
- Four dashboard pages: Overview, Player Analysis, Team Analysis, Position Analysis
- Sidebar filters: season, team, position, player
- Dark green football-inspired UI
- No external APIs; all data is synthetic and clearly labelled

**Non-Goals:**
- No live API integrations (e.g., transfermarkt, football-data.org)
- No user authentication
- No database backend

**Approach:** Build each file one at a time in dependency order: dataset → requirements → app core → pages → styling → documentation.

---

## Dataset Schema

File: `football_players.csv`

| Column | Type | Description |
|---|---|---|
| player_id | int | Unique player identifier (1–120) |
| player_name | str | Full synthetic name |
| team | str | One of 10 synthetic clubs |
| position | str | GK, DEF, MID, FWD |
| season | str | "2021-22", "2022-23", "2023-24" |
| age | int | 18–38 |
| nationality | str | One of ~20 countries |
| appearances | int | 1–38 (matches played) |
| goals | int | Position-realistic ranges (GK: 0–1, DEF: 0–5, MID: 0–15, FWD: 2–30) |
| assists | int | Position-realistic ranges |
| shots | int | Correlated with goals |
| shots_on_target | int | ≤ shots |
| pass_accuracy | float | 60–95% |
| minutes_played | int | appearances × ~75 |
| yellow_cards | int | 0–10 |
| red_cards | int | 0–3 |
| rating | float | 5.0–9.5 (1 decimal place) |
| clean_sheets | int | GK/DEF only meaningful; 0 for others |

**Synthetic label:** The CSV will include a header comment and the README will state clearly that all data is synthetic and does not represent real athletes.

**Seed:** `numpy.random.seed(42)` for full reproducibility.

---

## KPI Calculations

All KPIs are computed at runtime from the filtered dataframe — nothing is hardcoded.

| KPI Card | Calculation |
|---|---|
| Total Players | `df['player_id'].nunique()` |
| Total Goals | `df['goals'].sum()` |
| Total Assists | `df['assists'].sum()` |
| Total Minutes Played | `df['minutes_played'].sum()` |
| Average Player Rating | `df['rating'].mean().round(2)` |

---

## Chart Choices

| Chart | Library | Rationale |
|---|---|---|
| KPI cards | Streamlit `st.metric` | Clean delta-free summary |
| Goals vs Assists scatter | Plotly Express scatter | Shows player output relationship |
| Shots vs Goals scatter | Plotly Express scatter | Conversion efficiency |
| Top scorers bar | Plotly Express bar | Ranked leaderboard |
| Team goals/assists grouped bar | Plotly Express bar | Side-by-side team comparison |
| Team player count bar | Plotly Express bar | Squad depth |
| Position distribution pie | Plotly Express pie | Squad balance |
| Position KPI radar | Plotly Graph Objects Scatterpolar | Multi-metric position comparison |
| Player comparison radar | Plotly Graph Objects Scatterpolar | Head-to-head multi-stat view |
| Rating distribution histogram | Plotly Express histogram | Overall quality spread |

---

## Project File Structure

```
Super Analysis Dashboard/
├── app.py                    # Main Streamlit application
├── generate_data.py          # Synthetic dataset generator
├── football_players.csv      # Pre-generated synthetic dataset
├── requirements.txt          # Python dependencies
├── README.md                 # Setup, usage, and deployment guide
└── football-analytics-plan.md
```

---

## Sub-Tasks

---

### Sub-Task 1 — Generate Synthetic Dataset

**Status:** `[x] done`

**Intent:**
Create a reproducible CSV of 120 players (40 players × 3 seasons, or 120 unique player-season rows) across 10 teams and 4 positions. The dataset drives every KPI, chart, and filter in the app.

**Expected Outcomes:**
- `generate_data.py` runs without errors and writes `football_players.csv`
- CSV contains at least 100 rows with no nulls
- Goals, assists, shots are position-realistic (FWDs score more than GKs)
- All column types are correct (int, float, str as per schema)
- File opens cleanly in pandas with `pd.read_csv()`

**Todo List:**
1. Create `generate_data.py` with `numpy.random.seed(42)`
2. Define 10 team names, 4 positions, 3 seasons, ~20 nationalities, 120 player names
3. Generate per-position stat ranges using `numpy.random` with realistic distributions
4. Assemble into a pandas DataFrame and write to `football_players.csv`
5. Print row count and column summary as a sanity check

**Relevant Context:**
- Schema table above
- Positions: GK (10%), DEF (30%), MID (35%), FWD (25%) distribution

---

### Sub-Task 2 — Create requirements.txt

**Status:** `[x] done`

**Intent:**
Pin only the libraries that `app.py` directly imports so the project installs cleanly with `pip install -r requirements.txt`.

**Expected Outcomes:**
- `requirements.txt` lists streamlit, pandas, numpy, plotly
- No unnecessary packages
- Compatible with Python 3.9+

**Todo List:**
1. Create `requirements.txt` with pinned minimum versions:
   - `streamlit>=1.32.0`
   - `pandas>=2.0.0`
   - `numpy>=1.26.0`
   - `plotly>=5.20.0`

---

### Sub-Task 3 — Build app.py Core Structure

**Status:** `[x] done`

**Intent:**
Set up the Streamlit app skeleton: page config, CSS theming, data loading with caching, sidebar filters, and multi-page navigation. This is the foundation that all four pages build on.

**Expected Outcomes:**
- App runs with `streamlit run app.py` without errors on an empty page
- Page config sets dark theme, wide layout, football favicon emoji
- Custom CSS applies dark background (#0a1628), green accent (#00ff87), card styling
- `load_data()` is cached and reads `football_players.csv`
- Sidebar shows season, team, position, player filters that correctly subset `df`
- Navigation tabs or sidebar radio for Overview / Player Analysis / Team Analysis / Position Analysis
- Missing-value guard: if CSV missing, show `st.error` and `st.stop()`

**Todo List:**
1. Set `st.set_page_config(layout="wide", page_title="Football Analytics", page_icon="⚽")`
2. Inject custom CSS via `st.markdown` with `unsafe_allow_html=True`
3. Implement `load_data()` with `@st.cache_data` and try/except for missing file
4. Build sidebar filter widgets (multiselect for season, team, position; selectbox for player)
5. Apply filters to produce `filtered_df` used by all pages
6. Add navigation using `st.sidebar.radio` or `st.tabs`
7. Add synthetic data disclaimer banner

**Relevant Context:**
- CSS target: dark navy (#0a1628) background, green (#00ff87) accent, white text, card boxes with subtle border
- All pages receive `filtered_df` as input

---

### Sub-Task 4 — Overview Page

**Status:** `[x] done`

**Intent:**
Implement the landing page with five KPI metric cards and a rating distribution histogram, giving users an immediate summary of the filtered dataset.

**Expected Outcomes:**
- Five `st.metric` cards in one row: Total Players, Total Goals, Total Assists, Total Minutes Played, Average Rating
- Rating distribution histogram rendered with Plotly
- Top-10 scorers horizontal bar chart
- All values recalculate when sidebar filters change
- Empty state message if filters produce zero rows

**Todo List:**
1. Create `render_overview(df)` function
2. Compute all five KPIs from `df`
3. Render KPI cards using `st.columns(5)` + `st.metric`
4. Render rating histogram with `px.histogram`
5. Render top-10 scorers bar with `px.bar` (sorted descending by goals)
6. Add `if df.empty: st.warning(...)` guard

**Relevant Context:**
- KPI calculations table above
- Use `filtered_df` not raw `df`

---

### Sub-Task 5 — Player Analysis Page

**Status:** `[x] done`

**Intent:**
Implement player-level analysis: goals vs assists scatter, shots vs goals scatter, and a head-to-head radar comparison for any two selected players.

**Expected Outcomes:**
- Goals vs Assists scatter with team color, position shape, player name tooltip
- Shots vs Goals scatter showing conversion rate
- Player comparison section: two selectboxes → radar chart of 6 stats
- All charts have titles, axis labels, hover tooltips, and legend

**Todo List:**
1. Create `render_player_analysis(df)` function
2. Build goals vs assists scatter with `px.scatter`, color=team, symbol=position, hover_data=[player_name, rating]
3. Build shots vs goals scatter with trendline option (`trendline="ols"` via statsmodels — check dependency or use manual)
4. Build player comparison: two `st.selectbox` widgets from `df['player_name'].unique()`
5. Extract 6 stats per player (goals, assists, shots_on_target, pass_accuracy, rating, appearances)
6. Render radar using `go.Scatterpolar` with fill
7. Guard: if fewer than 2 players available, show info message

**Relevant Context:**
- Radar chart normalises each stat to 0–1 scale for fair comparison
- statsmodels adds weight to requirements.txt; use manual trendline or skip to keep deps light

---

### Sub-Task 6 — Team Analysis Page

**Status:** `[x] done`

**Intent:**
Implement team-level aggregations: grouped bar for goals+assists per team, player count bar, and a sorted team ranking table.

**Expected Outcomes:**
- Grouped bar chart: goals and assists per team side-by-side
- Bar chart: number of players per team
- Sortable summary table with team stats
- Charts update with season/position filters

**Todo List:**
1. Create `render_team_analysis(df)` function
2. Aggregate: `team_df = df.groupby('team').agg(goals=..., assists=..., players=..., avg_rating=...).reset_index()`
3. Build grouped bar with `px.bar(..., barmode='group')`
4. Build player count bar
5. Display `st.dataframe(team_df.sort_values('goals', ascending=False))`

---

### Sub-Task 7 — Position Analysis Page

**Status:** `[x] done`

**Intent:**
Implement position-level analysis: pie chart of position distribution, radar chart comparing average stats per position, and per-position KPI breakdown.

**Expected Outcomes:**
- Pie chart of player count by position
- Radar chart with average goals, assists, pass_accuracy, rating, shots per position
- Position KPI table: avg goals, avg assists, avg rating, player count
- Position-specific insight text (e.g. "Forwards average X goals per season")

**Todo List:**
1. Create `render_position_analysis(df)` function
2. Build position count pie with `px.pie`
3. Aggregate per position for radar axes
4. Build position radar with `go.Scatterpolar`
5. Build position summary table
6. Add dynamic insight strings using f-strings from aggregated data

---

### Sub-Task 8 — Searchable Stats Table and CSV Download

**Status:** `[x] done`

**Intent:**
Add a searchable player statistics table with column sorting and a one-click CSV download button so users can export filtered data.

**Expected Outcomes:**
- `st.dataframe` with all columns, sortable, full width
- Text input for player name search (filters the table further)
- `st.download_button` generates a CSV of the currently visible (filtered+searched) rows
- Download filename includes current filter context (e.g. `football_stats_filtered.csv`)

**Todo List:**
1. Add `render_stats_table(df)` function or inline section in Overview/Player page
2. Add `st.text_input("Search player...")` and apply `.str.contains()` filter
3. Convert filtered df to CSV with `df.to_csv(index=False)`
4. Wire `st.download_button` with `mime="text/csv"`

---

### Sub-Task 9 — UI Polish and Validation

**Status:** `[x] done`

**Intent:**
Apply the dark football-inspired CSS theme consistently, ensure all charts use the green-on-dark palette, add input validation, and add missing-value handling across the whole app.

**Expected Outcomes:**
- All Plotly charts use `template="plotly_dark"` or custom dark theme with green accents
- KPI cards styled with custom CSS box-shadow and green border
- Synthetic data disclaimer visible on every page
- `if df.empty` guards on every render function
- Tooltips configured on all charts
- Consistent font, spacing, and header styles

**Todo List:**
1. Define a shared `CHART_THEME` dict with `template`, `paper_bgcolor`, `plot_bgcolor`, `font_color`
2. Apply `CHART_THEME` to every `px.*` and `go.Figure` call via `.update_layout()`
3. Write CSS string covering: body background, sidebar, metric cards, section headers, dataframe
4. Add `st.sidebar.markdown("⚠️ Synthetic Data — not real football statistics")` disclaimer
5. Review all render functions for missing `if df.empty` checks

---

### Sub-Task 10 — README.md

**Status:** `[x] done`

**Intent:**
Write a clear README covering project overview, dataset description, local setup, deployment to Streamlit Community Cloud, and a feature list.

**Expected Outcomes:**
- README explains synthetic data clearly
- Step-by-step local run instructions (`pip install`, `streamlit run app.py`)
- Streamlit Community Cloud deployment steps
- Feature list matching the 10 requested features
- Screenshot placeholder section

**Todo List:**
1. Write project overview section
2. Write dataset schema section with synthetic data disclaimer
3. Write local setup section
4. Write Streamlit Cloud deployment section
5. Write feature list

---

## Implementation Order

```
Sub-Task 1 (Dataset)
    ↓
Sub-Task 2 (requirements.txt)
    ↓
Sub-Task 3 (app.py Core + Filters)
    ↓
Sub-Tasks 4–7 (Pages — can be done sequentially)
    ↓
Sub-Task 8 (Stats Table + CSV Download)
    ↓
Sub-Task 9 (UI Polish + Validation)
    ↓
Sub-Task 10 (README)
```
