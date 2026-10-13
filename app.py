"""
app.py  —  Football Player Performance Analytics Dashboard
===========================================================
NOTICE: All player names, teams and statistics are SYNTHETIC (AI-generated).
They do NOT represent real athletes, clubs or competitions.

Run locally:
    pip install -r requirements.txt
    streamlit run app.py
"""

import os
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Football Analytics Dashboard",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
/* ── Base ── */
html, body, [data-testid="stAppViewContainer"] {
    background-color: #0a1628;
    color: #e8eaf0;
}
[data-testid="stSidebar"] {
    background-color: #0d1f3c;
    border-right: 1px solid #1e3a5f;
}
[data-testid="stSidebar"] * { color: #c8d6e8 !important; }

/* ── Headings ── */
h1, h2, h3 { color: #00ff87 !important; letter-spacing: 0.03em; }
h4, h5, h6 { color: #c8d6e8 !important; }

/* ── Metric cards ── */
[data-testid="metric-container"] {
    background: linear-gradient(135deg, #0d1f3c 0%, #112240 100%);
    border: 1px solid #00ff87;
    border-radius: 10px;
    padding: 16px 20px;
    box-shadow: 0 4px 16px rgba(0,255,135,0.08);
}
[data-testid="metric-container"] [data-testid="stMetricValue"] {
    color: #00ff87 !important;
    font-size: 1.8rem !important;
    font-weight: 700 !important;
}
[data-testid="metric-container"] [data-testid="stMetricLabel"] {
    color: #8aa4c0 !important;
    font-size: 0.78rem !important;
    text-transform: uppercase;
    letter-spacing: 0.08em;
}

/* ── Tabs ── */
[data-testid="stTabs"] button {
    color: #8aa4c0 !important;
    font-weight: 600;
    border-bottom: 2px solid transparent;
}
[data-testid="stTabs"] button[aria-selected="true"] {
    color: #00ff87 !important;
    border-bottom: 2px solid #00ff87 !important;
}

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1e3a5f; border-radius: 8px; }

/* ── Inputs ── */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] div,
[data-testid="stMultiSelect"] div {
    background-color: #112240 !important;
    color: #e8eaf0 !important;
    border-color: #1e3a5f !important;
}

/* ── Disclaimer banner ── */
.disclaimer {
    background: #0d2740;
    border-left: 4px solid #f0a500;
    border-radius: 6px;
    padding: 8px 14px;
    font-size: 0.78rem;
    color: #f0c060;
    margin-bottom: 14px;
}

/* ── Section divider ── */
.section-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #00ff87;
    border-bottom: 1px solid #1e3a5f;
    padding-bottom: 4px;
    margin: 24px 0 10px;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background-color: #00a86b !important;
    color: #0a1628 !important;
    font-weight: 700 !important;
    border: none !important;
    border-radius: 6px !important;
}
[data-testid="stDownloadButton"] button:hover {
    background-color: #00ff87 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Plotly shared theme ────────────────────────────────────────────────────────
CHART_LAYOUT = dict(
    template="plotly_dark",
    paper_bgcolor="#0a1628",
    plot_bgcolor="#0d1f3c",
    font=dict(color="#c8d6e8", family="Segoe UI, sans-serif", size=12),
    margin=dict(l=40, r=20, t=50, b=40),
    hoverlabel=dict(bgcolor="#112240", font_color="#e8eaf0", bordercolor="#00ff87"),
    legend=dict(bgcolor="rgba(0,0,0,0)", bordercolor="#1e3a5f", borderwidth=1),
)

GREEN_PALETTE = px.colors.sequential.Greens[::-1]
TEAM_COLORS   = px.colors.qualitative.Bold


# ── Data loading ──────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="Loading player data…")
def load_data() -> pd.DataFrame:
    csv_path = os.path.join(os.path.dirname(__file__), "football_players.csv")
    if not os.path.exists(csv_path):
        return pd.DataFrame()
    df = pd.read_csv(csv_path)
    # Fill any unexpected nulls
    numeric_cols = df.select_dtypes(include="number").columns
    df[numeric_cols] = df[numeric_cols].fillna(0)
    str_cols = df.select_dtypes(include="object").columns
    df[str_cols] = df[str_cols].fillna("Unknown")
    return df


# ── Disclaimer helper ─────────────────────────────────────────────────────────
def show_disclaimer():
    st.markdown(
        '<div class="disclaimer">'
        "⚠️  <strong>Synthetic Data Notice:</strong> All player names, teams and statistics "
        "are AI-generated and entirely fictional. They do not represent real athletes or competitions."
        "</div>",
        unsafe_allow_html=True,
    )


# ── KPI helpers ───────────────────────────────────────────────────────────────
def fmt_number(n: int | float) -> str:
    if n >= 1_000_000:
        return f"{n/1_000_000:.1f}M"
    if n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n)) if isinstance(n, (int, np.integer)) else f"{n:.2f}"


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — OVERVIEW
# ═══════════════════════════════════════════════════════════════════════════════
def render_overview(df: pd.DataFrame):
    show_disclaimer()

    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar selections.")
        return

    # ── KPI cards ──────────────────────────────────────────────────────────────
    total_players  = df["player_id"].nunique()
    total_goals    = int(df["goals"].sum())
    total_assists  = int(df["assists"].sum())
    total_minutes  = int(df["minutes_played"].sum())
    avg_rating     = round(float(df["rating"].mean()), 2)

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Players",       fmt_number(total_players))
    c2.metric("Total Goals",         fmt_number(total_goals))
    c3.metric("Total Assists",       fmt_number(total_assists))
    c4.metric("Total Minutes Played",fmt_number(total_minutes))
    c5.metric("Avg Player Rating",   f"{avg_rating:.2f}")

    st.markdown("---")

    col_a, col_b = st.columns(2)

    # ── Rating distribution ───────────────────────────────────────────────────
    with col_a:
        st.markdown('<div class="section-title">Player Rating Distribution</div>', unsafe_allow_html=True)
        fig_hist = px.histogram(
            df, x="rating", nbins=25,
            labels={"rating": "Rating", "count": "Players"},
            color_discrete_sequence=["#00ff87"],
        )
        fig_hist.update_layout(**CHART_LAYOUT, title="")
        fig_hist.update_traces(marker_line_color="#0a1628", marker_line_width=0.5)
        st.plotly_chart(fig_hist, use_container_width=True)

    # ── Top 10 scorers ────────────────────────────────────────────────────────
    with col_b:
        st.markdown('<div class="section-title">Top 10 Goal Scorers</div>', unsafe_allow_html=True)
        top_scorers = (
            df.groupby(["player_name", "team"], as_index=False)["goals"]
            .sum()
            .sort_values("goals", ascending=False)
            .head(10)
        )
        top_scorers["label"] = top_scorers["player_name"] + " (" + top_scorers["team"] + ")"
        fig_top = px.bar(
            top_scorers,
            x="goals", y="label",
            orientation="h",
            labels={"goals": "Goals", "label": ""},
            color="goals",
            color_continuous_scale=GREEN_PALETTE,
        )
        fig_top.update_layout(**CHART_LAYOUT, title="", yaxis=dict(autorange="reversed"), coloraxis_showscale=False)
        st.plotly_chart(fig_top, use_container_width=True)

    # ── Goals + Assists by Season ─────────────────────────────────────────────
    st.markdown('<div class="section-title">Goals & Assists by Season</div>', unsafe_allow_html=True)
    season_agg = df.groupby("season", as_index=False).agg(
        Goals=("goals", "sum"), Assists=("assists", "sum")
    )
    fig_season = px.bar(
        season_agg.melt(id_vars="season", value_vars=["Goals", "Assists"],
                        var_name="Metric", value_name="Count"),
        x="season", y="Count", color="Metric", barmode="group",
        labels={"season": "Season", "Count": "Total"},
        color_discrete_map={"Goals": "#00ff87", "Assists": "#3b82f6"},
    )
    fig_season.update_layout(**CHART_LAYOUT, title="")
    st.plotly_chart(fig_season, use_container_width=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — PLAYER ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def render_player_analysis(df: pd.DataFrame):
    show_disclaimer()

    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar selections.")
        return

    # ── Goals vs Assists scatter ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Goals vs Assists</div>', unsafe_allow_html=True)
    fig_ga = px.scatter(
        df,
        x="goals", y="assists",
        color="team",
        symbol="position",
        hover_name="player_name",
        hover_data={"season": True, "rating": True, "team": True, "position": True},
        labels={"goals": "Goals", "assists": "Assists", "team": "Team", "position": "Position"},
        color_discrete_sequence=TEAM_COLORS,
        size_max=12,
    )
    fig_ga.update_traces(marker=dict(size=8, opacity=0.82, line=dict(width=0.5, color="#0a1628")))
    fig_ga.update_layout(**CHART_LAYOUT, title="")
    st.plotly_chart(fig_ga, use_container_width=True)

    # ── Shots vs Goals scatter ────────────────────────────────────────────────
    st.markdown('<div class="section-title">Shots vs Goals (Conversion Efficiency)</div>', unsafe_allow_html=True)
    fig_sg = px.scatter(
        df,
        x="shots", y="goals",
        color="position",
        hover_name="player_name",
        hover_data={"team": True, "season": True, "shots_on_target": True},
        labels={"shots": "Total Shots", "goals": "Goals", "position": "Position"},
        color_discrete_sequence=px.colors.qualitative.Safe,
        size="shots_on_target",
        size_max=18,
    )
    # Manual trendline via numpy polyfit
    valid = df[["shots", "goals"]].dropna()
    if len(valid) > 2:
        z = np.polyfit(valid["shots"], valid["goals"], 1)
        x_range = np.linspace(valid["shots"].min(), valid["shots"].max(), 100)
        y_trend = np.poly1d(z)(x_range)
        fig_sg.add_trace(go.Scatter(
            x=x_range, y=y_trend,
            mode="lines",
            name="Trend",
            line=dict(color="#f0a500", width=2, dash="dash"),
        ))
    fig_sg.update_layout(**CHART_LAYOUT, title="")
    st.plotly_chart(fig_sg, use_container_width=True)

    # ── Player Comparison Radar ───────────────────────────────────────────────
    st.markdown('<div class="section-title">Head-to-Head Player Comparison</div>', unsafe_allow_html=True)

    all_players = sorted(df["player_name"].unique())
    if len(all_players) < 2:
        st.info("Select at least 2 players using the sidebar filters for comparison.")
        return

    col_p1, col_p2 = st.columns(2)
    player_a = col_p1.selectbox("Player A", all_players, index=0, key="radar_a")
    player_b = col_p2.selectbox("Player B", all_players,
                                index=min(1, len(all_players) - 1), key="radar_b")

    if player_a == player_b:
        st.info("Please select two different players.")
        return

    RADAR_STATS = ["goals", "assists", "shots_on_target", "pass_accuracy", "rating", "appearances"]
    RADAR_LABELS = ["Goals", "Assists", "Shots on Target", "Pass Accuracy", "Rating", "Appearances"]

    def player_radar_values(name: str) -> list[float]:
        row = df[df["player_name"] == name][RADAR_STATS].mean()
        return row.tolist()

    vals_a = player_radar_values(player_a)
    vals_b = player_radar_values(player_b)

    # Normalise 0→1 against column max in filtered df
    col_maxes = [df[c].max() for c in RADAR_STATS]
    norm_a = [v / m if m > 0 else 0 for v, m in zip(vals_a, col_maxes)]
    norm_b = [v / m if m > 0 else 0 for v, m in zip(vals_b, col_maxes)]

    PLAYER_COLORS = [
        ("#00ff87", "rgba(0,255,135,0.15)"),
        ("#3b82f6", "rgba(59,130,246,0.15)"),
    ]

    fig_radar = go.Figure()
    for (norm_vals, raw_vals, pname), (line_color, fill_color) in zip(
        [(norm_a, vals_a, player_a), (norm_b, vals_b, player_b)],
        PLAYER_COLORS,
    ):
        hover_text = "<br>".join(
            f"{lbl}: {raw:.1f}" for lbl, raw in zip(RADAR_LABELS, raw_vals)
        )
        fig_radar.add_trace(go.Scatterpolar(
            r=norm_vals + [norm_vals[0]],
            theta=RADAR_LABELS + [RADAR_LABELS[0]],
            fill="toself",
            name=pname,
            line=dict(color=line_color, width=2),
            fillcolor=fill_color,
            hovertemplate=f"<b>{pname}</b><br>{hover_text}<extra></extra>",
        ))

    fig_radar.update_layout(
        **CHART_LAYOUT,
        polar=dict(
            bgcolor="#0d1f3c",
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(color="#8aa4c0"), gridcolor="#1e3a5f"),
            angularaxis=dict(tickfont=dict(color="#c8d6e8"), gridcolor="#1e3a5f"),
        ),
        showlegend=True,
        height=480,
    )

    st.plotly_chart(fig_radar, use_container_width=True)

    # Raw values table
    compare_df = pd.DataFrame({
        "Stat": RADAR_LABELS,
        player_a: [f"{v:.1f}" for v in vals_a],
        player_b: [f"{v:.1f}" for v in vals_b],
    })
    st.dataframe(compare_df, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — TEAM ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def render_team_analysis(df: pd.DataFrame):
    show_disclaimer()

    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar selections.")
        return

    team_agg = (
        df.groupby("team", as_index=False)
        .agg(
            Goals      =("goals",        "sum"),
            Assists    =("assists",       "sum"),
            Players    =("player_id",    "nunique"),
            Avg_Rating =("rating",       "mean"),
            Minutes    =("minutes_played","sum"),
        )
        .sort_values("Goals", ascending=False)
    )
    team_agg["Avg_Rating"] = team_agg["Avg_Rating"].round(2)

    # ── Goals & Assists grouped bar ───────────────────────────────────────────
    st.markdown('<div class="section-title">Goals & Assists per Team</div>', unsafe_allow_html=True)
    melted = team_agg.melt(
        id_vars="team", value_vars=["Goals", "Assists"],
        var_name="Metric", value_name="Count"
    )
    fig_team_bar = px.bar(
        melted, x="team", y="Count", color="Metric",
        barmode="group",
        labels={"team": "Team", "Count": "Total"},
        color_discrete_map={"Goals": "#00ff87", "Assists": "#3b82f6"},
        text_auto=True,
    )
    fig_team_bar.update_layout(**CHART_LAYOUT, title="", xaxis_tickangle=-30)
    fig_team_bar.update_traces(textfont_size=10, textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_team_bar, use_container_width=True)

    col_left, col_right = st.columns(2)

    # ── Player count per team ─────────────────────────────────────────────────
    with col_left:
        st.markdown('<div class="section-title">Squad Size per Team</div>', unsafe_allow_html=True)
        fig_squad = px.bar(
            team_agg.sort_values("Players", ascending=True),
            x="Players", y="team",
            orientation="h",
            labels={"Players": "# Players", "team": "Team"},
            color="Players",
            color_continuous_scale=GREEN_PALETTE,
            text_auto=True,
        )
        fig_squad.update_layout(**CHART_LAYOUT, title="", coloraxis_showscale=False)
        st.plotly_chart(fig_squad, use_container_width=True)

    # ── Avg rating per team ───────────────────────────────────────────────────
    with col_right:
        st.markdown('<div class="section-title">Average Player Rating per Team</div>', unsafe_allow_html=True)
        fig_rating = px.bar(
            team_agg.sort_values("Avg_Rating", ascending=True),
            x="Avg_Rating", y="team",
            orientation="h",
            labels={"Avg_Rating": "Avg Rating", "team": "Team"},
            color="Avg_Rating",
            color_continuous_scale=GREEN_PALETTE,
            text_auto=True,
        )
        fig_rating.update_layout(**CHART_LAYOUT, title="", coloraxis_showscale=False)
        st.plotly_chart(fig_rating, use_container_width=True)

    # ── Summary table ─────────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Team Leaderboard</div>', unsafe_allow_html=True)
    display_team = team_agg.rename(columns={
        "team": "Team", "Goals": "Goals", "Assists": "Assists",
        "Players": "Players", "Avg_Rating": "Avg Rating", "Minutes": "Total Minutes"
    })
    display_team.insert(0, "#", range(1, len(display_team) + 1))
    st.dataframe(display_team, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — POSITION ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════
def render_position_analysis(df: pd.DataFrame):
    show_disclaimer()

    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar selections.")
        return

    POS_ORDER = ["GK", "DEF", "MID", "FWD"]
    pos_agg = (
        df.groupby("position", as_index=False)
        .agg(
            Players      =("player_id",      "nunique"),
            Avg_Goals    =("goals",          "mean"),
            Avg_Assists  =("assists",        "mean"),
            Avg_Rating   =("rating",         "mean"),
            Avg_Shots    =("shots",          "mean"),
            Avg_Pass_Acc =("pass_accuracy",  "mean"),
            Avg_Minutes  =("minutes_played", "mean"),
        )
    )
    # Round floats
    for c in pos_agg.columns:
        if pos_agg[c].dtype == float:
            pos_agg[c] = pos_agg[c].round(2)
    # Sort by defined order (only include present positions)
    present_order = [p for p in POS_ORDER if p in pos_agg["position"].values]
    pos_agg = pos_agg.set_index("position").reindex(present_order).reset_index()

    col_a, col_b = st.columns(2)

    # ── Position distribution pie ─────────────────────────────────────────────
    with col_a:
        st.markdown('<div class="section-title">Position Distribution</div>', unsafe_allow_html=True)
        fig_pie = px.pie(
            pos_agg, values="Players", names="position",
            hole=0.45,
            color_discrete_sequence=["#00ff87", "#3b82f6", "#f0a500", "#ef4444"],
        )
        fig_pie.update_traces(
            textinfo="percent+label",
            hovertemplate="<b>%{label}</b><br>Players: %{value}<br>%{percent}<extra></extra>",
        )
        fig_pie.update_layout(**CHART_LAYOUT, title="", showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    # ── Position radar ────────────────────────────────────────────────────────
    with col_b:
        st.markdown('<div class="section-title">Avg Stats by Position (Radar)</div>', unsafe_allow_html=True)
        RADAR_COLS   = ["Avg_Goals", "Avg_Assists", "Avg_Shots", "Avg_Pass_Acc", "Avg_Rating"]
        RADAR_LABELS = ["Avg Goals", "Avg Assists", "Avg Shots", "Pass Acc %", "Avg Rating"]
        POS_COLORS   = {"GK": "#3b82f6", "DEF": "#00ff87", "MID": "#f0a500", "FWD": "#ef4444"}

        col_maxes = [pos_agg[c].max() for c in RADAR_COLS]

        fig_pos_radar = go.Figure()
        for _, row in pos_agg.iterrows():
            pos = row["position"]
            vals  = [row[c] for c in RADAR_COLS]
            norms = [v / m if m > 0 else 0 for v, m in zip(vals, col_maxes)]
            color = POS_COLORS.get(pos, "#ffffff")
            fig_pos_radar.add_trace(go.Scatterpolar(
                r=norms + [norms[0]],
                theta=RADAR_LABELS + [RADAR_LABELS[0]],
                fill="toself",
                name=pos,
                line=dict(color=color, width=2),
                hovertemplate=(
                    f"<b>{pos}</b><br>"
                    + "<br>".join(f"{lbl}: {v:.1f}" for lbl, v in zip(RADAR_LABELS, vals))
                    + "<extra></extra>"
                ),
            ))
        fig_pos_radar.update_layout(
            **CHART_LAYOUT,
            polar=dict(
                bgcolor="#0d1f3c",
                radialaxis=dict(visible=True, range=[0, 1],
                               tickfont=dict(color="#8aa4c0"), gridcolor="#1e3a5f"),
                angularaxis=dict(tickfont=dict(color="#c8d6e8"), gridcolor="#1e3a5f"),
            ),
            showlegend=True,
            height=420,
        )
        st.plotly_chart(fig_pos_radar, use_container_width=True)

    # ── Per-position KPI bars ─────────────────────────────────────────────────
    st.markdown('<div class="section-title">Average Goals & Assists by Position</div>', unsafe_allow_html=True)
    melted_pos = pos_agg.melt(
        id_vars="position",
        value_vars=["Avg_Goals", "Avg_Assists"],
        var_name="Metric", value_name="Value"
    )
    melted_pos["Metric"] = melted_pos["Metric"].map({"Avg_Goals": "Avg Goals", "Avg_Assists": "Avg Assists"})
    fig_pos_bar = px.bar(
        melted_pos, x="position", y="Value", color="Metric",
        barmode="group",
        labels={"position": "Position", "Value": "Average"},
        color_discrete_map={"Avg Goals": "#00ff87", "Avg Assists": "#3b82f6"},
        text_auto=".1f",
        category_orders={"position": present_order},
    )
    fig_pos_bar.update_layout(**CHART_LAYOUT, title="")
    fig_pos_bar.update_traces(textposition="outside", cliponaxis=False)
    st.plotly_chart(fig_pos_bar, use_container_width=True)

    # ── Dynamic insights ──────────────────────────────────────────────────────
    st.markdown('<div class="section-title">Position Insights</div>', unsafe_allow_html=True)
    insight_cols = st.columns(len(pos_agg))
    for col_widget, (_, row) in zip(insight_cols, pos_agg.iterrows()):
        pos = row["position"]
        label = {"GK": "Goalkeepers", "DEF": "Defenders", "MID": "Midfielders", "FWD": "Forwards"}.get(pos, pos)
        col_widget.markdown(
            f"**{label}**  \n"
            f"Avg Goals: **{row['Avg_Goals']:.1f}**  \n"
            f"Avg Assists: **{row['Avg_Assists']:.1f}**  \n"
            f"Avg Rating: **{row['Avg_Rating']:.2f}**  \n"
            f"Players: **{int(row['Players'])}**"
        )

    # ── Position summary table ────────────────────────────────────────────────
    st.markdown('<div class="section-title">Position Summary Table</div>', unsafe_allow_html=True)
    disp = pos_agg.rename(columns={
        "position": "Position", "Players": "Players",
        "Avg_Goals": "Avg Goals", "Avg_Assists": "Avg Assists",
        "Avg_Rating": "Avg Rating", "Avg_Shots": "Avg Shots",
        "Avg_Pass_Acc": "Pass Acc %", "Avg_Minutes": "Avg Minutes",
    })
    st.dataframe(disp, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — STATS TABLE + CSV DOWNLOAD
# ═══════════════════════════════════════════════════════════════════════════════
def render_stats_table(df: pd.DataFrame):
    show_disclaimer()

    if df.empty:
        st.warning("No data matches the current filters. Please adjust the sidebar selections.")
        return

    st.markdown('<div class="section-title">Player Statistics Table</div>', unsafe_allow_html=True)

    # ── Search ────────────────────────────────────────────────────────────────
    search_col, dl_col = st.columns([3, 1])
    search_term = search_col.text_input("🔍  Search player name…", value="", key="search_input")

    table_df = df.copy()
    if search_term.strip():
        mask = table_df["player_name"].str.contains(search_term.strip(), case=False, na=False)
        table_df = table_df[mask]
        if table_df.empty:
            st.info(f"No players found matching '{search_term}'. Try a different name.")
            return

    # ── Download ──────────────────────────────────────────────────────────────
    csv_bytes = table_df.to_csv(index=False).encode("utf-8")
    dl_col.download_button(
        label="⬇  Download CSV",
        data=csv_bytes,
        file_name="football_stats_filtered.csv",
        mime="text/csv",
        help="Download the currently visible filtered data as a CSV file",
    )

    # Display count
    st.caption(f"Showing {len(table_df):,} rows")

    # Reorder columns for readability
    display_cols = [
        "player_name", "team", "position", "season", "age", "nationality",
        "appearances", "goals", "assists", "shots", "shots_on_target",
        "pass_accuracy", "minutes_played", "yellow_cards", "red_cards",
        "clean_sheets", "rating",
    ]
    display_cols = [c for c in display_cols if c in table_df.columns]
    st.dataframe(
        table_df[display_cols].reset_index(drop=True),
        use_container_width=True,
        hide_index=True,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# SIDEBAR + MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    # ── Load data ─────────────────────────────────────────────────────────────
    raw_df = load_data()

    if raw_df.empty:
        st.error(
            "**Data file not found.**  \n"
            "Run `python generate_data.py` (or `py generate_data.py`) first, "
            "then refresh this page."
        )
        st.stop()

    # ── Sidebar header ────────────────────────────────────────────────────────
    st.sidebar.markdown(
        "## ⚽ Football Analytics\n"
        "<small style='color:#8aa4c0'>Portfolio Dashboard · Synthetic Data</small>",
        unsafe_allow_html=True,
    )
    st.sidebar.markdown("---")

    # ── Sidebar filters ───────────────────────────────────────────────────────
    all_seasons  = sorted(raw_df["season"].unique())
    all_teams    = sorted(raw_df["team"].unique())
    all_positions = ["GK", "DEF", "MID", "FWD"]

    sel_seasons = st.sidebar.multiselect(
        "Season", all_seasons, default=all_seasons, key="f_season"
    )
    sel_teams = st.sidebar.multiselect(
        "Team", all_teams, default=all_teams, key="f_team"
    )
    sel_positions = st.sidebar.multiselect(
        "Position", all_positions, default=all_positions, key="f_position"
    )

    # Apply filters
    df = raw_df.copy()
    if sel_seasons:
        df = df[df["season"].isin(sel_seasons)]
    if sel_teams:
        df = df[df["team"].isin(sel_teams)]
    if sel_positions:
        df = df[df["position"].isin(sel_positions)]

    # Optional single-player filter (shown only on Player Analysis page,
    # but available globally)
    all_players_filtered = sorted(df["player_name"].unique())
    sel_player = st.sidebar.selectbox(
        "Highlight Player (optional)",
        ["All Players"] + all_players_filtered,
        key="f_player",
    )
    if sel_player != "All Players":
        df = df[df["player_name"] == sel_player]

    st.sidebar.markdown("---")
    st.sidebar.caption(
        "⚠️ All data is synthetic and does not represent real athletes or competitions."
    )

    # ── Navigation tabs ───────────────────────────────────────────────────────
    st.markdown(
        "<h1 style='text-align:center; color:#00ff87; margin-bottom:4px;'>"
        "⚽ Football Analytics Dashboard</h1>"
        "<p style='text-align:center; color:#8aa4c0; margin-top:0; font-size:0.85rem;'>"
        "Interactive Player & Team Performance Analysis · Synthetic Dataset</p>",
        unsafe_allow_html=True,
    )

    tab_overview, tab_player, tab_team, tab_position, tab_table = st.tabs([
        "📊  Overview",
        "👤  Player Analysis",
        "🏟  Team Analysis",
        "🎯  Position Analysis",
        "📋  Stats Table",
    ])

    with tab_overview:
        render_overview(df)

    with tab_player:
        render_player_analysis(df)

    with tab_team:
        render_team_analysis(df)

    with tab_position:
        render_position_analysis(df)

    with tab_table:
        render_stats_table(df)


if __name__ == "__main__":
    main()
