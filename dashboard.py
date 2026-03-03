import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os

st.set_page_config(
    page_title="🏃 Laufgruppe Dashboard",
    page_icon="🏃",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────
st.markdown("""
<style>
    .main { background-color: #E6F4F1; }
    .podium-card {
        background: white;
        border-radius: 16px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        margin: 8px;
    }
    .gold   { border-top: 5px solid #F59E0B; }
    .silver { border-top: 5px solid #9CA3AF; }
    .bronze { border-top: 5px solid #92400E; }
    .metric-box {
        background: white;
        border-radius: 12px;
        padding: 16px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    .stSelectbox label { font-weight: 600; }
    h1 { color: #00697A !important; }
    [data-testid="stSidebar"] {
    background-color: white !important;
    }   
</style>
""", unsafe_allow_html=True)


# ── Daten laden ─────────────────────────────────────────────────
@st.cache_data
def load_data(path):
    runners_df = pd.read_excel(path, sheet_name="Läufer")
    times_df = pd.read_excel(path, sheet_name="Zeiten", index_col=0)

    # Wide → Long Format umwandeln
    times_df = times_df.reset_index()
    times_df = times_df.melt(id_vars="Name", var_name="Datum", value_name="Zeit")
    times_df = times_df.dropna(subset=["Zeit"])

    # Zeit parsen (bleibt gleich)
    def parse_time(t):
        try:
            t = str(t).strip()
            if ":" in t:
                parts = t.split(":")
                return int(parts[0]) * 60 + int(parts[1])
        except:
            pass
        return None

    times_df["Sekunden"] = times_df["Zeit"].apply(parse_time)
    times_df = times_df.dropna(subset=["Sekunden"])
    times_df["Sekunden"] = times_df["Sekunden"].astype(int)

    times_df["Datum"] = pd.to_datetime(times_df["Datum"], dayfirst=True, errors="coerce")
    times_df = times_df.dropna(subset=["Datum"])
    times_df = times_df.sort_values("Datum")

    return runners_df, times_df

def fmt_time(secs):
    """Sekunden → mm:ss"""
    secs = int(secs)
    return f"{secs//60}:{secs%60:02d}"


EXCEL_FILE = "laufgruppe.xlsx"
if not os.path.exists(EXCEL_FILE):
    st.error(f"❌ Datei **{EXCEL_FILE}** nicht gefunden! Bitte im gleichen Ordner wie dashboard.py ablegen.")
    st.stop()

runners_df, times_df = load_data(EXCEL_FILE)

if times_df.empty:
    st.warning("Noch keine Zeiten eingetragen.")
    st.stop()

# Teilnahmezählung
attendance = times_df.groupby("Name")["Datum"].nunique().reset_index()
attendance.columns = ["Name", "Läufe"]
attendance = attendance.sort_values("Läufe", ascending=False)


# ══════════════════════════════════════════════════════
#  SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.image("Logo.png", width=100)
    st.title("FBC München")
    st.markdown("---")
    page = st.radio("Navigation", ["🏆 Podium & Übersicht", "👤 Einzelne Läufer"])
    st.markdown("---")
    if st.button("🔄 Daten neu laden"):
        st.cache_data.clear()
        st.rerun()


# ══════════════════════════════════════════════════════
#  SEITE 1: PODIUM & ÜBERSICHT
# ══════════════════════════════════════════════════════
if page == "🏆 Podium & Übersicht":
    st.title("🏃 Laufgruppe – Übersicht")

    total_runs = times_df["Datum"].nunique()
    total_kids = times_df["Name"].nunique()
    best_time  = fmt_time(times_df["Sekunden"].min())

    c1, c2, c3 = st.columns(3)
    c1.metric("🗓️ Läufe gesamt", total_runs)
    c2.metric("👦 Aktive Kinder", total_kids)
    c3.metric("⚡ Schnellste Zeit", best_time)

    st.markdown("---")

    # ── Podium ────────────────────────────────────────
    st.subheader("🥇 Teilnahme-Podium")
    st.caption("Die 3 Kinder mit den meisten Starts")

    top3 = attendance.head(3).reset_index(drop=True)

    medals = [
        ("🥇", "gold",   "Platz 1"),
        ("🥈", "silver", "Platz 2"),
        ("🥉", "bronze", "Platz 3"),
    ]

    # Podium-Layout: 2 | 1 | 3
    order = [0, 1, 2] if len(top3) >= 3 else list(range(len(top3)))
    heights = ["120px", "160px", "100px"]

    cols = st.columns(3)
    for display_pos, data_pos in enumerate(order):
        if data_pos >= len(top3):
            continue
        row = top3.iloc[data_pos]
        emoji, css_class, label = medals[data_pos]
        h = heights[display_pos]
        with cols[display_pos]:
            st.markdown(f"""
            <div class="podium-card {css_class}">
                <div style="font-size:2.5rem">{emoji}</div>
                <div style="font-weight:700; font-size:1.1rem; margin:6px 0">{row['Name']}</div>
                <div style="color:#6B7280; font-size:0.85rem">{label}</div>
                <div style="font-size:1.6rem; font-weight:800; color:#1E3A5F; margin-top:8px">
                    {int(row['Läufe'])} Läufe
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Teilnahme Tabelle ─────────────────────────────
    col_left, col_right = st.columns([1.2, 1])

    with col_left:
        st.subheader("📊 Alle Teilnahmen")
        fig_bar = px.bar(
            attendance,
            x="Läufe", y="Name",
            orientation="h",
            color="Läufe",
            color_continuous_scale=["#BFDBFE", "#2563EB"],
            text="Läufe",
        )
        fig_bar.update_layout(
            yaxis=dict(categoryorder="total ascending"),
            showlegend=False,
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=10, b=0),
            height=360,
            plot_bgcolor="white",
            paper_bgcolor="white",
        )
        fig_bar.update_traces(textposition="outside")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_right:
        st.subheader("🏅 Bestzeiten")
        best = times_df.groupby("Name")["Sekunden"].min().reset_index()
        best["Zeit"] = best["Sekunden"].apply(fmt_time)
        best = best.sort_values("Sekunden")
        best["Rang"] = range(1, len(best)+1)
        best["Rang"] = best["Rang"].apply(lambda x: "🥇" if x==1 else ("🥈" if x==2 else ("🥉" if x==3 else str(x))))
        st.dataframe(
            best[["Rang", "Name", "Zeit"]],
            hide_index=True,
            use_container_width=True,
            height=360,
        )

    # ── Verlauf aller Kinder ──────────────────────────
    st.markdown("---")
    st.subheader("📈 Zeitverlauf aller Kinder")

    fig_all = go.Figure()
    for name in times_df["Name"].unique():
        df_n = times_df[times_df["Name"] == name].sort_values("Datum")
        fig_all.add_trace(go.Scatter(
            x=df_n["Datum"],
            y=df_n["Sekunden"],
            mode="lines+markers",
            name=name,
            hovertemplate=f"<b>{name}</b><br>%{{x|%d.%m.%Y}}<br>Zeit: %{{text}}<extra></extra>",
            text=[fmt_time(s) for s in df_n["Sekunden"]],
        ))

    fig_all.update_layout(
        yaxis=dict(
            title="Zeit",
            tickvals=list(range(
                (times_df["Sekunden"].min() // 60) * 60,
                (times_df["Sekunden"].max() // 60 + 2) * 60,
                60
            )),
            ticktext=[fmt_time(s) for s in range(
                (times_df["Sekunden"].min() // 60) * 60,
                (times_df["Sekunden"].max() // 60 + 2) * 60,
                60
            )],
            autorange="reversed",
        ),
        xaxis=dict(title="Datum"),
        hovermode="closest",
        plot_bgcolor="white",
        paper_bgcolor="white",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
        margin=dict(l=0, r=0, t=40, b=0),
        height=420,
    )
    st.plotly_chart(fig_all, use_container_width=True)


# ══════════════════════════════════════════════════════
#  SEITE 2: EINZELNE LÄUFER
# ══════════════════════════════════════════════════════
else:
    st.title("👤 Einzelne Läufer")

    all_names = sorted(times_df["Name"].unique())
    selected = st.selectbox("Kind auswählen:", all_names)

    df_kid = times_df[times_df["Name"] == selected].sort_values("Datum").copy()
    df_kid["Lauf Nr."] = range(1, len(df_kid) + 1)
    df_kid["Zeit"] = df_kid["Sekunden"].apply(fmt_time)

    # Verbesserung berechnen
    df_kid["Diff_sek"] = df_kid["Sekunden"].diff()
    def fmt_diff(d):
        if pd.isna(d):
            return "—"
        d = int(d)
        sign = "▲" if d > 0 else "▼"
        color = "red" if d > 0 else "green"
        return f'<span style="color:{color}">{sign} {fmt_time(abs(d))}</span>'
    df_kid["Verbesserung"] = df_kid["Diff_sek"].apply(fmt_diff)

    # ── Kennzahlen ────────────────────────────────────
    best_s  = df_kid["Sekunden"].min()
    worst_s = df_kid["Sekunden"].max()
    avg_s   = df_kid["Sekunden"].mean()
    n_runs  = len(df_kid)
    total_runs = times_df["Datum"].nunique()
    attend_pct = int(n_runs / total_runs * 100) if total_runs > 0 else 0

    # Overall improvement: first → last
    if n_runs >= 2:
        improv = df_kid["Sekunden"].iloc[0] - df_kid["Sekunden"].iloc[-1]
        improv_str = f"{'▼ ' if improv > 0 else '▲ '}{fmt_time(abs(int(improv)))} {'schneller' if improv > 0 else 'langsamer'}"
        improv_color = "green" if improv > 0 else "red"
    else:
        improv_str = "Noch kein Vergleich"
        improv_color = "gray"

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("🏁 Läufe", f"{n_runs} / {total_runs}")
    c2.metric("📅 Teilnahme", f"{attend_pct}%")
    c3.metric("⚡ Bestzeit", fmt_time(best_s))
    c4.metric("📊 Ø Zeit", fmt_time(avg_s))
    c5.metric("📈 Entwicklung", improv_str)

    st.markdown("---")

    col_l, col_r = st.columns([1.5, 1])

    with col_l:
        st.subheader(f"📈 Zeitverlauf – {selected}")
        fig = go.Figure()

        # Verlauf
        fig.add_trace(go.Scatter(
            x=df_kid["Datum"],
            y=df_kid["Sekunden"],
            mode="lines+markers",
            name="Zeit",
            line=dict(color="#2563EB", width=3),
            marker=dict(size=10, color="#2563EB"),
            hovertemplate="%{x|%d.%m.%Y}<br><b>%{text}</b><extra></extra>",
            text=df_kid["Zeit"],
        ))

        # Bestzeit-Linie
        fig.add_hline(
            y=best_s,
            line_dash="dot",
            line_color="#10B981",
            annotation_text=f"Bestzeit: {fmt_time(best_s)}",
            annotation_position="top right",
        )

        tick_range = list(range(
            (df_kid["Sekunden"].min() // 60) * 60 - 60,
            (df_kid["Sekunden"].max() // 60 + 2) * 60,
            60
        ))

        fig.update_layout(
            yaxis=dict(
                title="Zeit",
                tickvals=tick_range,
                ticktext=[fmt_time(s) for s in tick_range],
                autorange="reversed",
            ),
            xaxis=dict(title=""),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=340,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col_r:
        st.subheader("📋 Alle Zeiten")
        display_df = df_kid[["Lauf Nr.", "Datum", "Zeit", "Verbesserung"]].copy()
        display_df["Datum"] = display_df["Datum"].dt.strftime("%d.%m.%Y")

        # Render HTML table for colored diff
        html = display_df.to_html(escape=False, index=False, classes="time-table")
        st.markdown(html, unsafe_allow_html=True)

    # ── Verbesserung als Bar Chart ─────────────────────
    if n_runs >= 3:
        st.markdown("---")
        st.subheader("📊 Verbesserung pro Lauf (Sekunden)")

        diffs = df_kid["Diff_sek"].dropna().values
        dates = df_kid["Datum"].iloc[1:].dt.strftime("%d.%m.%Y").values
        colors = ["#10B981" if d < 0 else "#EF4444" for d in diffs]
        labels = [fmt_time(abs(int(d))) for d in diffs]

        fig2 = go.Figure(go.Bar(
            x=dates,
            y=[-d for d in diffs],  # positive = improvement
            marker_color=colors,
            text=labels,
            textposition="outside",
            hovertemplate="%{x}<br>%{text}<extra></extra>",
        ))
        fig2.add_hline(y=0, line_color="#374151", line_width=1)
        fig2.update_layout(
            yaxis=dict(title="Sekunden schneller (grün) / langsamer (rot)"),
            xaxis=dict(title=""),
            plot_bgcolor="white",
            paper_bgcolor="white",
            showlegend=False,
            margin=dict(l=0, r=0, t=20, b=0),
            height=280,
        )
        st.plotly_chart(fig2, use_container_width=True)
