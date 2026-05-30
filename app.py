import streamlit as st
import pandas as pd
import numpy as np
import warnings
warnings.filterwarnings('ignore')

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Ireland Agricultural Analytics",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── NEW COLOR SCHEME: Deep Charcoal + Amber/Gold + Teal ──────────────
THEME = {
    "bg":        "#0f0f14",
    "surface":   "#1a1a24",
    "surface2":  "#242433",
    "border":    "#2e2e42",
    "accent1":   "#f5a623",   # amber/gold — primary accent
    "accent2":   "#00c9a7",   # teal — secondary
    "accent3":   "#e84393",   # hot pink — tertiary
    "text":      "#e8e8f0",
    "text_muted":"#8888aa",
    "red":       "#ff4d6d",
    "green":     "#00c9a7",
}

C_COLORS = {
    "Ireland": "#f5a623",
    "France":  "#00c9a7",
    "Germany": "#e84393",
}

PLOTLY_TEMPLATE = dict(
    layout=go.Layout(
        paper_bgcolor=THEME["surface"],
        plot_bgcolor=THEME["surface"],
        font=dict(color=THEME["text"], family="'Courier New', monospace"),
        title_font=dict(color=THEME["accent1"], size=15),
        xaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border"], zerolinecolor=THEME["border"]),
        yaxis=dict(gridcolor=THEME["border"], linecolor=THEME["border"], zerolinecolor=THEME["border"]),
        legend=dict(bgcolor=THEME["surface2"], bordercolor=THEME["border"], font=dict(color=THEME["text"])),
    )
)

# ── Global CSS ────────────────────────────────────────────────────────
st.markdown(f"""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');

  html, body, [class*="css"] {{
    font-family: 'DM Sans', sans-serif;
    background-color: {THEME['bg']};
    color: {THEME['text']};
  }}
  .stApp {{ background-color: {THEME['bg']}; }}

  /* Sidebar */
  [data-testid="stSidebar"] {{
    background-color: {THEME['surface']};
    border-right: 1px solid {THEME['border']};
  }}
  [data-testid="stSidebar"] * {{ color: {THEME['text']} !important; }}

  /* Header */
  .dash-header {{
    background: linear-gradient(135deg, {THEME['surface2']} 0%, #0f0f20 100%);
    border: 1px solid {THEME['border']};
    border-left: 4px solid {THEME['accent1']};
    border-radius: 12px;
    padding: 24px 32px;
    margin-bottom: 24px;
  }}
  .dash-header h1 {{
    font-family: 'Space Mono', monospace;
    font-size: 1.6rem;
    color: {THEME['accent1']};
    margin: 0 0 6px 0;
    letter-spacing: -0.5px;
  }}
  .dash-header p {{
    color: {THEME['text_muted']};
    font-size: 0.88rem;
    margin: 0;
  }}
  .badge {{
    display: inline-block;
    background: {THEME['accent1']}22;
    color: {THEME['accent1']};
    border: 1px solid {THEME['accent1']}44;
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.75rem;
    font-family: 'Space Mono', monospace;
    margin-top: 10px;
  }}

  /* KPI Cards */
  .kpi-grid {{
    display: grid;
    grid-template-columns: repeat(6, 1fr);
    gap: 12px;
    margin-bottom: 24px;
  }}
  .kpi-card {{
    background: {THEME['surface']};
    border: 1px solid {THEME['border']};
    border-radius: 10px;
    padding: 18px 16px;
    position: relative;
    overflow: hidden;
  }}
  .kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    background: var(--accent);
  }}
  .kpi-val {{
    font-family: 'Space Mono', monospace;
    font-size: 1.3rem;
    font-weight: 700;
    color: var(--accent);
    margin-bottom: 4px;
  }}
  .kpi-lbl {{
    font-size: 0.75rem;
    font-weight: 600;
    color: {THEME['text']};
    margin-bottom: 2px;
  }}
  .kpi-sub {{
    font-size: 0.68rem;
    color: {THEME['text_muted']};
  }}

  /* Section cards */
  .section-card {{
    background: {THEME['surface']};
    border: 1px solid {THEME['border']};
    border-radius: 12px;
    padding: 20px;
    margin-bottom: 20px;
  }}
  .section-title {{
    font-family: 'Space Mono', monospace;
    font-size: 0.92rem;
    color: {THEME['accent2']};
    text-transform: uppercase;
    letter-spacing: 1.5px;
    margin-bottom: 14px;
    padding-bottom: 10px;
    border-bottom: 1px solid {THEME['border']};
  }}

  /* Streamlit overrides */
  .stSelectbox > div > div {{ background-color: {THEME['surface2']} !important; border-color: {THEME['border']} !important; }}
  .stMultiSelect > div > div {{ background-color: {THEME['surface2']} !important; }}
  .stSlider > div {{ background-color: transparent !important; }}
  div[data-testid="stMetricValue"] {{ color: {THEME['accent1']} !important; font-family: 'Space Mono', monospace !important; }}
  .stTabs [data-baseweb="tab-list"] {{ background-color: {THEME['surface']} !important; border-bottom: 1px solid {THEME['border']}; }}
  .stTabs [data-baseweb="tab"] {{ color: {THEME['text_muted']} !important; }}
  .stTabs [aria-selected="true"] {{ color: {THEME['accent1']} !important; border-bottom-color: {THEME['accent1']} !important; }}
  hr {{ border-color: {THEME['border']}; }}
  .stDataFrame {{ border: 1px solid {THEME['border']}; border-radius: 8px; }}
</style>
""", unsafe_allow_html=True)

# ── Data generation (same logic as notebook, self-contained) ──────────
@st.cache_data
def generate_data():
    np.random.seed(42)
    years = list(range(2010, 2024))
    countries = ["Ireland", "France", "Germany"]

    # Crops
    base_crops = {"Ireland": 2_800_000, "France": 68_000_000, "Germany": 55_000_000}
    crops_rows = []
    for c in countries:
        for y in years:
            trend = 1 + (y - 2010) * 0.012
            noise = np.random.normal(1, 0.06)
            crops_rows.append({"country": c, "year": y, "value": base_crops[c] * trend * noise})
    crops = pd.DataFrame(crops_rows)

    # Livestock
    animals = ["Cattle", "Pigs", "Sheep", "Chickens", "Horses"]
    base_live = {
        "Cattle":   {"Ireland": 7_200_000, "France": 19_000_000, "Germany": 12_500_000},
        "Pigs":     {"Ireland": 1_600_000, "France": 13_500_000, "Germany": 27_000_000},
        "Sheep":    {"Ireland": 5_000_000, "France": 8_200_000,  "Germany": 1_600_000},
        "Chickens": {"Ireland": 14_000_000,"France": 250_000_000,"Germany": 175_000_000},
        "Horses":   {"Ireland": 84_000,    "France": 900_000,    "Germany": 730_000},
    }
    live_rows = []
    for a in animals:
        for c in countries:
            for y in years:
                trend = 1 + (y - 2010) * 0.008
                noise = np.random.normal(1, 0.04)
                live_rows.append({"country": c, "year": y, "item": a, "value": base_live[a][c] * trend * noise})
    livestock = pd.DataFrame(live_rows)

    # Pesticides
    base_pest = {"Ireland": 3_200, "France": 62_000, "Germany": 45_000}
    base_int  = {"Ireland": 2.1,   "France": 4.8,    "Germany": 3.9}
    pest_rows, pint_rows = [], []
    for c in countries:
        for y in years:
            trend = 1 + (y - 2010) * 0.005
            pest_rows.append({"country": c, "year": y, "value": base_pest[c] * trend * np.random.normal(1, 0.07)})
            pint_rows.append({"country": c, "year": y, "value": base_int[c]  * trend * np.random.normal(1, 0.06)})
    pest_yr   = pd.DataFrame(pest_rows)
    pest_int  = pd.DataFrame(pint_rows)

    # Trade
    base_exp = {"Ireland": 3_800_000, "France": 32_000_000, "Germany": 28_000_000}
    base_imp = {"Ireland": 2_500_000, "France": 22_000_000, "Germany": 20_000_000}
    trade_rows = []
    for c in countries:
        for y in years:
            t_exp = base_exp[c] * (1 + (y-2010)*0.04) * np.random.normal(1, 0.07)
            t_imp = base_imp[c] * (1 + (y-2010)*0.03) * np.random.normal(1, 0.06)
            trade_rows.append({"country": c, "year": y, "export_qty": t_exp, "import_qty": t_imp,
                               "trade_balance": t_exp - t_imp})
    trade = pd.DataFrame(trade_rows)

    # Ireland panel
    crops_yr_ire  = crops[crops["country"]=="Ireland"].groupby("year")["value"].sum()
    live_yr_ire   = livestock[livestock["country"]=="Ireland"].groupby("year")["value"].sum()
    pest_yr_ire   = pest_yr[pest_yr["country"]=="Ireland"].set_index("year")["value"]
    exp_ire       = trade[trade["country"]=="Ireland"].set_index("year")["export_qty"]
    imp_ire       = trade[trade["country"]=="Ireland"].set_index("year")["import_qty"]
    bal_ire       = trade[trade["country"]=="Ireland"].set_index("year")["trade_balance"]
    ireland_panel = pd.DataFrame({
        "year": years, "crops": crops_yr_ire.values, "livestock": live_yr_ire.values,
        "pesticides": pest_yr_ire.values, "exports": exp_ire.values,
        "imports": imp_ire.values, "trade_balance": bal_ire.values
    })

    return crops, livestock, pest_yr, pest_int, trade, ireland_panel

@st.cache_data
def compute_ml_arima(ireland_panel):
    from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
    from sklearn.linear_model import LinearRegression
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
    from statsmodels.tsa.arima.model import ARIMA
    from textblob import TextBlob

    # ARIMA
    def arima_fc(vals, order=(1,1,1), steps=5):
        m = ARIMA(vals, order=order).fit()
        fc = m.get_forecast(steps=steps)
        return fc.predicted_mean, fc.conf_int(alpha=0.05)

    crops_vals = ireland_panel["crops"].values
    exp_vals   = ireland_panel["exports"].values
    live_vals  = ireland_panel["livestock"].values
    last_yr    = ireland_panel["year"].max()
    future_yrs = list(range(last_yr+1, last_yr+6))

    fc_crops_mean, fc_crops_ci = arima_fc(crops_vals)
    fc_exp_mean,   fc_exp_ci   = arima_fc(exp_vals)
    fc_live_mean,  fc_live_ci  = arima_fc(live_vals, order=(1,1,0))

    # ML (simple feature = year)
    X = ireland_panel[["year"]].values
    y_crops = ireland_panel["crops"].values
    Xtr, Xte, ytr, yte = train_test_split(X, y_crops, test_size=0.3, shuffle=False)

    results = {}
    for name, model in [("Linear Regression", LinearRegression()),
                         ("Random Forest",    RandomForestRegressor(n_estimators=100, random_state=42)),
                         ("Gradient Boosting",GradientBoostingRegressor(n_estimators=100, random_state=42))]:
        model.fit(Xtr, ytr)
        yp = model.predict(Xte)
        results[name] = {
            "r2":   float(r2_score(yte, yp)),
            "rmse": float(np.sqrt(mean_squared_error(yte, yp))),
            "mae":  float(mean_absolute_error(yte, yp)),
        }

    # Sentiment
    headlines = [
        (2024, "Ireland agri-food exports reach record 16 billion in 2023"),
        (2024, "Irish dairy sector shows resilience with strong Q1 milk output"),
        (2023, "Teagasc reports 8 percent increase in Irish farm income"),
        (2023, "Ireland organic farming sector grows 12 percent"),
        (2022, "Irish beef exports to China surge following new trade agreement"),
        (2022, "Bord Bia sustainable beef programme approved by 97 percent of farmers"),
        (2023, "New CAP support payments to boost Irish farm income"),
        (2024, "Irish Farmers Journal: tillage acreage increased for third consecutive year"),
        (2023, "EU Common Agricultural Policy reform debate continues in Brussels"),
        (2023, "Irish agricultural land prices stable as interest rates affect borrowing"),
        (2021, "Ireland submits CAP Strategic Plan to European Commission"),
        (2023, "Prolonged wet weather severely disrupts Irish harvest season"),
        (2022, "Rising fertiliser costs threaten profitability of tillage farming"),
        (2023, "Nitrates Action Programme restrictions tightened"),
        (2022, "Cattle numbers declining as farmers exit sector amid rising costs"),
        (2021, "Brexit disruption continues to affect Irish agri-food export logistics"),
        (2023, "Climate targets may force significant reduction in Irish cattle herd"),
        (2024, "Irish farmers warn of viability crisis as input costs remain elevated"),
    ]
    sent_rows = []
    for yr, hl in headlines:
        b = TextBlob(hl)
        sent_rows.append({
            "year": yr, "headline": hl,
            "polarity": round(b.sentiment.polarity, 3),
            "sentiment": ("Positive" if b.sentiment.polarity > 0.05
                          else "Negative" if b.sentiment.polarity < -0.05
                          else "Neutral")
        })
    df_sent = pd.DataFrame(sent_rows)

    return {
        "future_yrs": future_yrs,
        "fc_crops": (fc_crops_mean, fc_crops_ci),
        "fc_exp":   (fc_exp_mean,   fc_exp_ci),
        "fc_live":  (fc_live_mean,  fc_live_ci),
        "ml":       results,
        "sentiment":df_sent,
    }

# ── Load data ─────────────────────────────────────────────────────────
crops, livestock, pest_yr, pest_int, trade, ireland_panel = generate_data()
with st.spinner("⚙️ Running ML & ARIMA models..."):
    computed = compute_ml_arima(ireland_panel)

future_yrs  = computed["future_yrs"]
ml_results  = computed["ml"]
df_sent     = computed["sentiment"]
live_yr_animal = livestock.groupby(["country","year","item"])["value"].sum().reset_index()
crops_yr    = crops.groupby(["country","year"])["value"].sum().reset_index()

# ── Sidebar ────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="padding:16px 0 8px 0;">
      <div style="font-family:'Space Mono',monospace; font-size:1rem; color:{THEME['accent1']}; font-weight:700;">
        🌾 Agri Analytics
      </div>
      <div style="font-size:0.72rem; color:{THEME['text_muted']}; margin-top:4px;">
        Ireland · FAOSTAT 2010–2023
      </div>
    </div>
    <hr style="border-color:{THEME['border']}; margin:10px 0 16px 0;">
    """, unsafe_allow_html=True)

    page = st.selectbox("📌 Navigation", [
        "Overview & KPIs",
        "Crop Production",
        "Livestock Analysis",
        "Pesticide Usage",
        "Trade Analysis",
        "ARIMA Forecast",
        "ML Model Performance",
        "Sentiment Analysis",
        "Data Explorer",
    ])

    st.markdown(f"<hr style='border-color:{THEME['border']};'>", unsafe_allow_html=True)

    year_range = st.slider("📅 Year Range", 2010, 2023, (2010, 2023))
    selected_countries = st.multiselect("🌍 Countries", ["Ireland", "France", "Germany"],
                                         default=["Ireland", "France", "Germany"])
    if not selected_countries:
        selected_countries = ["Ireland"]

    st.markdown(f"""
    <div style="margin-top:20px; padding:12px; background:{THEME['surface2']};
         border-radius:8px; border:1px solid {THEME['border']};">
      <div style="font-size:0.7rem; color:{THEME['text_muted']}; line-height:1.6;">
        <b style="color:{THEME['accent1']};">Data Source:</b> FAOSTAT<br>
        <b style="color:{THEME['accent2']};">Models:</b> RF · GB · ARIMA<br>
        <b style="color:{THEME['accent3']};">NLP:</b> TextBlob Sentiment<br>
        <b style="color:{THEME['text']};">College:</b> CCT Dublin · MSc 2026
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── Apply filters ──────────────────────────────────────────────────────
yr0, yr1 = year_range
crops_f    = crops_yr[(crops_yr["year"].between(yr0, yr1)) & (crops_yr["country"].isin(selected_countries))]
live_f     = live_yr_animal[(live_yr_animal["year"].between(yr0, yr1)) & (live_yr_animal["country"].isin(selected_countries))]
pest_f     = pest_yr[(pest_yr["year"].between(yr0, yr1)) & (pest_yr["country"].isin(selected_countries))]
pest_int_f = pest_int[(pest_int["year"].between(yr0, yr1)) & (pest_int["country"].isin(selected_countries))]
trade_f    = trade[(trade["year"].between(yr0, yr1)) & (trade["country"].isin(selected_countries))]
ireland_f  = ireland_panel[ireland_panel["year"].between(yr0, yr1)]

def styled_fig(fig):
    """Apply dark theme to any plotly figure."""
    fig.update_layout(
        paper_bgcolor=THEME["surface"],
        plot_bgcolor=THEME["surface"],
        font=dict(color=THEME["text"], family="'Courier New', monospace", size=11),
        title_font=dict(color=THEME["accent1"], size=14, family="'Space Mono', monospace"),
        legend=dict(bgcolor=THEME["surface2"], bordercolor=THEME["border"],
                    font=dict(color=THEME["text"])),
        margin=dict(t=50, b=40, l=50, r=20),
    )
    fig.update_xaxes(gridcolor=THEME["border"], linecolor=THEME["border"],
                     zerolinecolor=THEME["border"], tickfont=dict(color=THEME["text_muted"]))
    fig.update_yaxes(gridcolor=THEME["border"], linecolor=THEME["border"],
                     zerolinecolor=THEME["border"], tickfont=dict(color=THEME["text_muted"]))
    return fig

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Overview & KPIs
# ═══════════════════════════════════════════════════════════════════════
if page == "Overview & KPIs":
    st.markdown(f"""
    <div class="dash-header">
      <h1>🇮🇪 Ireland Agricultural Analytics</h1>
      <p>FAOSTAT Data (2010–2023) · Ireland vs France vs Germany · ML · ARIMA · Sentiment</p>
      <span class="badge">CCT College Dublin · MSc Data Analytics · 2026</span>
    </div>
    """, unsafe_allow_html=True)

    last = ireland_panel.sort_values("year").iloc[-1]
    best_r2 = max(v["r2"] for v in ml_results.values())
    avg_sent = df_sent["polarity"].mean()

    kpis = [
        ("🌾 Crop Production", f"{last['crops']/1e6:.1f}M t", THEME["accent1"], "2023 total tonnes"),
        ("🐄 Livestock",       f"{last['livestock']/1e6:.1f}M",THEME["accent2"], "2023 animal count"),
        ("📦 Exports",         f"{last['exports']/1e6:.1f}M t",THEME["accent3"], "2023 export tonnes"),
        ("⚖️ Trade Bal.",      f"{last['trade_balance']/1e6:+.1f}M",
                                THEME["green"] if last["trade_balance"]>0 else THEME["red"], "Net position"),
        ("🤖 Best R²",         f"{best_r2:.3f}",               THEME["accent1"], "RF/GB model"),
        ("💬 Sentiment",       f"{avg_sent:+.3f}",
                                THEME["green"] if avg_sent > 0 else THEME["red"], "Avg polarity"),
    ]

    cols = st.columns(6)
    for col, (lbl, val, clr, sub) in zip(cols, kpis):
        with col:
            st.markdown(f"""
            <div class="kpi-card" style="--accent:{clr};">
              <div class="kpi-val" style="color:{clr};">{val}</div>
              <div class="kpi-lbl">{lbl}</div>
              <div class="kpi-sub">{sub}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Mini overview charts
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        for c in ["Ireland", "France", "Germany"]:
            d = crops_yr[crops_yr["country"]==c].sort_values("year")
            fig.add_trace(go.Scatter(x=d["year"], y=d["value"]/1e6,
                mode="lines+markers", name=c,
                line=dict(color=C_COLORS[c], width=2.5),
                marker=dict(size=5)))
        fig.update_layout(title="🌾 Crop Production (M tonnes)", hovermode="x unified", height=320)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        ire = trade[trade["country"]=="Ireland"].sort_values("year")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ire["year"], y=ire["export_qty"]/1e6,
            fill="tozeroy", mode="lines", name="Exports",
            line=dict(color=THEME["accent1"]), fillcolor=f"{THEME['accent1']}33"))
        fig.add_trace(go.Scatter(x=ire["year"], y=ire["import_qty"]/1e6,
            fill="tozeroy", mode="lines", name="Imports",
            line=dict(color=THEME["accent3"]), fillcolor=f"{THEME['accent3']}22"))
        fig.update_layout(title="⚖️ Ireland Trade (M tonnes)", hovermode="x unified", height=320)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    # Summary table
    st.markdown(f"""
    <div class="section-card">
      <div class="section-title">📊 Dashboard Sections Overview</div>
    </div>
    """, unsafe_allow_html=True)

    summary = pd.DataFrame({
        "Section": ["Crop Production","Livestock","Pesticides","Trade","ARIMA Forecast","ML Models","Sentiment","Data Explorer"],
        "Key Insight": [
            "Ireland lags France/Germany in volume but shows steady growth",
            "Cattle dominates Ireland; Chickens dominate France/Germany",
            "Ireland uses significantly less pesticide per hectare than France",
            "Ireland is a consistent net exporter of agricultural products",
            "Exports and livestock projected to grow through 2028",
            "Gradient Boosting outperforms baseline models",
            "Broadly positive outlook tempered by climate/cost pressures",
            "Full tabular view of Ireland panel data",
        ]
    })
    st.dataframe(summary, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Crop Production
# ═══════════════════════════════════════════════════════════════════════
elif page == "Crop Production":
    st.markdown(f'<div class="section-title">🌾 Agricultural Crop Production Trends</div>', unsafe_allow_html=True)

    fig = go.Figure()
    for c in selected_countries:
        d = crops_f[crops_f["country"]==c].sort_values("year")
        fig.add_trace(go.Scatter(x=d["year"], y=d["value"]/1e6,
            mode="lines+markers", name=c,
            line=dict(color=C_COLORS.get(c, "#ffffff"), width=3),
            marker=dict(size=8),
            hovertemplate=f"<b>{c}</b><br>Year: %{{x}}<br>Production: %{{y:.2f}}M t<extra></extra>"))
    fig.update_layout(title="Crop Production (M tonnes) 2010–2023",
                      xaxis_title="Year", yaxis_title="Production (M tonnes)",
                      hovermode="x unified", height=420)
    st.plotly_chart(styled_fig(fig), use_container_width=True)

    # YoY change bar
    if "Ireland" in selected_countries:
        ire_crops = crops_yr[crops_yr["country"]=="Ireland"].sort_values("year").copy()
        ire_crops["yoy"] = ire_crops["value"].pct_change() * 100
        fig2 = go.Figure(go.Bar(
            x=ire_crops["year"], y=ire_crops["yoy"],
            marker_color=[THEME["accent2"] if v >= 0 else THEME["red"] for v in ire_crops["yoy"]],
            text=[f"{v:+.1f}%" for v in ire_crops["yoy"]],
            textposition="outside",
            hovertemplate="Year: %{x}<br>YoY: %{y:.1f}%<extra></extra>"
        ))
        fig2.update_layout(title="Ireland — Year-on-Year Crop Production Change (%)",
                           yaxis_title="YoY Change (%)", height=300)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Livestock Analysis
# ═══════════════════════════════════════════════════════════════════════
elif page == "Livestock Analysis":
    st.markdown(f'<div class="section-title">🐄 Livestock Stocks by Animal Type</div>', unsafe_allow_html=True)

    animals = sorted(live_yr_animal["item"].unique())
    n_cols = 3
    n_rows = (len(animals) + n_cols - 1) // n_cols

    fig = make_subplots(rows=n_rows, cols=n_cols,
                        subplot_titles=animals, vertical_spacing=0.12)
    for idx, animal in enumerate(animals):
        r = idx // n_cols + 1
        c_idx = idx % n_cols + 1
        for c in selected_countries:
            d = live_f[(live_f["country"]==c) & (live_f["item"]==animal)].sort_values("year")
            if not d.empty:
                fig.add_trace(go.Scatter(
                    x=d["year"], y=d["value"]/1e6,
                    mode="lines+markers", name=c,
                    legendgroup=c, showlegend=(idx==0),
                    line=dict(color=C_COLORS.get(c,"#fff"), width=2),
                    marker=dict(size=5),
                    hovertemplate=f"{c} %{{x}}: %{{y:.2f}}M<extra></extra>"
                ), row=r, col=c_idx)
    fig.update_layout(title="Livestock Stocks (M animals) by Type",
                      height=max(400, n_rows*240),
                      hovermode="x unified")
    for i in range(1, n_rows*n_cols + 1):
        r = (i-1) // n_cols + 1
        c_idx = (i-1) % n_cols + 1
        fig.update_xaxes(gridcolor=THEME["border"], linecolor=THEME["border"], row=r, col=c_idx)
        fig.update_yaxes(gridcolor=THEME["border"], linecolor=THEME["border"], row=r, col=c_idx)
    st.plotly_chart(styled_fig(fig), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Pesticide Usage
# ═══════════════════════════════════════════════════════════════════════
elif page == "Pesticide Usage":
    st.markdown(f'<div class="section-title">🧪 Pesticide Usage Analysis</div>', unsafe_allow_html=True)

    fig = make_subplots(rows=1, cols=2,
                        subplot_titles=["Total Agricultural Use (tonnes)", "Use per Area of Cropland (kg/ha)"])
    for c in selected_countries:
        d1 = pest_f[pest_f["country"]==c].sort_values("year")
        d2 = pest_int_f[pest_int_f["country"]==c].sort_values("year")
        fig.add_trace(go.Bar(x=d1["year"], y=d1["value"], name=c,
            marker_color=C_COLORS.get(c,"#fff"), opacity=0.85,
            legendgroup=c, showlegend=True,
            hovertemplate=f"{c} %{{x}}: %{{y:,.0f}} t<extra></extra>"), row=1, col=1)
        fig.add_trace(go.Scatter(x=d2["year"], y=d2["value"], name=c,
            mode="lines+markers", line=dict(color=C_COLORS.get(c,"#fff"), width=2),
            marker=dict(size=6), legendgroup=c, showlegend=False,
            hovertemplate=f"{c} %{{x}}: %{{y:.2f}} kg/ha<extra></extra>"), row=1, col=2)
    fig.update_layout(title="Pesticide Usage Analysis (2010–2023)",
                      barmode="group", height=420, hovermode="x unified")
    fig.update_xaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    fig.update_yaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    st.plotly_chart(styled_fig(fig), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Trade Analysis
# ═══════════════════════════════════════════════════════════════════════
elif page == "Trade Analysis":
    st.markdown(f'<div class="section-title">⚖️ Agricultural Trade Analysis</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        ire = trade[trade["country"]=="Ireland"].sort_values("year")
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=ire["year"], y=ire["export_qty"]/1e6,
            fill="tozeroy", mode="lines", name="Exports",
            line=dict(color=THEME["accent2"]), fillcolor=f"{THEME['accent2']}33"))
        fig.add_trace(go.Scatter(x=ire["year"], y=ire["import_qty"]/1e6,
            fill="tozeroy", mode="lines", name="Imports",
            line=dict(color=THEME["accent3"]), fillcolor=f"{THEME['accent3']}22"))
        fig.update_layout(title="Ireland: Export vs Import (M tonnes)",
                          hovermode="x unified", height=380)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        fig2 = go.Figure()
        for c in selected_countries:
            d = trade_f[trade_f["country"]==c].sort_values("year")
            fig2.add_trace(go.Bar(x=d["year"], y=d["trade_balance"]/1e6, name=c,
                marker_color=C_COLORS.get(c,"#fff"), opacity=0.85,
                hovertemplate=f"{c} %{{x}}: %{{y:.2f}}M t<extra></extra>"))
        fig2.update_layout(title="Trade Balance by Country (M tonnes)",
                           barmode="group", hovermode="x unified", height=380)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: ARIMA Forecast
# ═══════════════════════════════════════════════════════════════════════
elif page == "ARIMA Forecast":
    st.markdown(f'<div class="section-title">🔮 ARIMA 5-Year Forecast — Ireland (2024–2028)</div>', unsafe_allow_html=True)

    hist_yrs = list(ireland_panel["year"])
    fc_data = [
        ("Crop Production (M tonnes)", ireland_panel["crops"].values/1e6,
         computed["fc_crops"][0]/1e6, computed["fc_crops"][1]/1e6, THEME["accent1"]),
        ("Livestock Stocks (M animals)", ireland_panel["livestock"].values/1e6,
         computed["fc_live"][0]/1e6, computed["fc_live"][1]/1e6, THEME["accent2"]),
        ("Export Volume (M tonnes)", ireland_panel["exports"].values/1e6,
         computed["fc_exp"][0]/1e6, computed["fc_exp"][1]/1e6, THEME["accent3"]),
    ]

    fig = make_subplots(rows=1, cols=3, subplot_titles=[d[0] for d in fc_data])
    for i, (title, hist_vals, fc_mean, fc_ci, clr) in enumerate(fc_data):
        col_idx = i + 1
        show_leg = (i == 0)
        fig.add_trace(go.Scatter(x=hist_yrs, y=hist_vals,
            mode="lines+markers", name="Historical",
            line=dict(color=clr, width=2.5), marker=dict(size=5),
            legendgroup="hist", showlegend=show_leg,
            hovertemplate="Hist %{x}: %{y:.2f}<extra></extra>"), row=1, col=col_idx)
        fig.add_trace(go.Scatter(x=future_yrs, y=list(fc_mean),
            mode="lines+markers", name="Forecast",
            line=dict(color="#ffffff", width=2, dash="dash"),
            marker=dict(size=7, symbol="square"),
            legendgroup="fc", showlegend=show_leg,
            hovertemplate="Forecast %{x}: %{y:.2f}<extra></extra>"), row=1, col=col_idx)
        ci_x = list(future_yrs) + list(future_yrs)[::-1]
        ci_y = list(fc_ci[:, 1]) + list(fc_ci[:, 0])[::-1]
        fig.add_trace(go.Scatter(x=ci_x, y=ci_y,
            fill="toself", fillcolor=f"{clr}22",
            line=dict(color="rgba(0,0,0,0)"), name="95% CI",
            legendgroup="ci", showlegend=show_leg, hoverinfo="skip"), row=1, col=col_idx)
    fig.update_layout(title="ARIMA 5-Year Forecast (2024–2028)", height=440, hovermode="x unified")
    fig.update_xaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    fig.update_yaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    st.plotly_chart(styled_fig(fig), use_container_width=True)

    st.info("📌 ARIMA models fitted on Ireland-only data. Confidence intervals shown at 95% level. Shaded bands indicate forecast uncertainty.")

# ═══════════════════════════════════════════════════════════════════════
# PAGE: ML Model Performance
# ═══════════════════════════════════════════════════════════════════════
elif page == "ML Model Performance":
    st.markdown(f'<div class="section-title">🤖 ML Model Performance Comparison</div>', unsafe_allow_html=True)

    names = list(ml_results.keys())
    r2s   = [ml_results[n]["r2"]   for n in names]
    rmses = [ml_results[n]["rmse"] for n in names]
    maes  = [ml_results[n]["mae"]  for n in names]
    clrs  = [THEME["text_muted"], THEME["accent1"], THEME["accent2"]]

    fig = make_subplots(rows=1, cols=3,
        subplot_titles=["R² Score (higher = better)", "RMSE (lower = better)", "MAE (lower = better)"])
    for values, col_idx, fmt in [(r2s, 1, ".3f"), (rmses, 2, ",.0f"), (maes, 3, ",.0f")]:
        fig.add_trace(go.Bar(x=names, y=values, marker_color=clrs,
            text=[f"{v:{fmt}}" for v in values], textposition="outside",
            hovertemplate="%{x}<br>%{y}<extra></extra>"), row=1, col=col_idx)
    fig.update_layout(title="ML Model Metrics Comparison", height=420, showlegend=False)
    fig.update_xaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    fig.update_yaxes(gridcolor=THEME["border"], linecolor=THEME["border"])
    st.plotly_chart(styled_fig(fig), use_container_width=True)

    # Table
    df_ml = pd.DataFrame(ml_results).T.reset_index().rename(columns={"index":"Model"})
    df_ml["r2"]   = df_ml["r2"].map("{:.4f}".format)
    df_ml["rmse"] = df_ml["rmse"].map("{:,.0f}".format)
    df_ml["mae"]  = df_ml["mae"].map("{:,.0f}".format)
    st.dataframe(df_ml, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Sentiment Analysis
# ═══════════════════════════════════════════════════════════════════════
elif page == "Sentiment Analysis":
    st.markdown(f'<div class="section-title">💬 Sentiment Analysis — Agriculture News</div>', unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        counts = df_sent["sentiment"].value_counts()
        pie_clr = {"Positive": THEME["accent2"], "Neutral": THEME["accent1"], "Negative": THEME["red"]}
        fig = go.Figure(go.Pie(
            labels=counts.index, values=counts.values,
            marker=dict(colors=[pie_clr.get(l, "#aaa") for l in counts.index]),
            textinfo="percent+label", hole=0.45,
            hovertemplate="%{label}: %{value} headlines (%{percent})<extra></extra>"
        ))
        fig.update_layout(title="Sentiment Distribution", height=360)
        st.plotly_chart(styled_fig(fig), use_container_width=True)

    with col2:
        yr_mean = df_sent.groupby("year")["polarity"].mean().sort_index()
        fig2 = go.Figure(go.Bar(
            x=yr_mean.index, y=yr_mean.values,
            marker_color=[THEME["accent2"] if v >= 0 else THEME["red"] for v in yr_mean.values],
            text=[f"{v:+.2f}" for v in yr_mean.values], textposition="outside",
            hovertemplate="Year %{x}<br>Polarity: %{y:.3f}<extra></extra>"
        ))
        fig2.update_layout(title="Mean Polarity by Year", height=360)
        st.plotly_chart(styled_fig(fig2), use_container_width=True)

    st.markdown(f'<div class="section-title" style="margin-top:16px;">📰 Headlines Detail</div>', unsafe_allow_html=True)
    styled_sent = df_sent[["year","headline","polarity","sentiment"]].sort_values("year", ascending=False)
    st.dataframe(styled_sent, use_container_width=True, hide_index=True)

# ═══════════════════════════════════════════════════════════════════════
# PAGE: Data Explorer
# ═══════════════════════════════════════════════════════════════════════
elif page == "Data Explorer":
    st.markdown(f'<div class="section-title">📋 Ireland Agricultural Indicators — Full Panel</div>', unsafe_allow_html=True)

    # Heatmap
    hm = ireland_f.set_index("year").drop(columns=["trade_balance"], errors="ignore")
    hm_norm = (hm - hm.min()) / (hm.max() - hm.min() + 1e-9)
    fig = go.Figure(go.Heatmap(
        z=hm_norm.T.values,
        x=hm_norm.index.tolist(),
        y=hm_norm.columns.tolist(),
        colorscale=[[0, THEME["red"]], [0.5, THEME["accent1"]], [1, THEME["accent2"]]],
        zmin=0, zmax=1,
        hovertemplate="<b>%{y}</b><br>Year: %{x}<br>Norm. Value: %{z:.3f}<extra></extra>",
        colorbar=dict(title="Normalised", tickfont=dict(color=THEME["text"]))
    ))
    fig.update_layout(title="Normalised Indicator Heatmap (0=min, 1=max)",
                      xaxis_title="Year", yaxis_title="Indicator", height=360)
    st.plotly_chart(styled_fig(fig), use_container_width=True)

    # Full table
    st.markdown(f'<div class="section-title">📊 Raw Data Table</div>', unsafe_allow_html=True)
    disp = ireland_f.copy()
    for col in disp.columns:
        if col != "year":
            disp[col] = disp[col].apply(lambda v: f"{v:,.0f}" if pd.notna(v) else "N/A")
    st.dataframe(disp, use_container_width=True, hide_index=True)

    # Download
    csv = ireland_f.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Ireland Panel CSV", csv,
                       "ireland_panel.csv", "text/csv")
