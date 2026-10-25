"""
app.py  –  Retail Sales Intelligence Dashboard
================================================
Author : Ahmed Rizk Gawish
Dataset: AdventureWorks Internet Sales (2010-2014)
Stack  : Streamlit · Pandas · Plotly

Run locally:
    streamlit run app.py

Deploy:
    Push to GitHub, then connect to https://streamlit.io/cloud
"""

from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ──────────────────────────────────────────────
# Page config
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Retail Sales Dashboard · Ahmed Rizk Gawish",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ──────────────────────────────────────────────
# Custom CSS  (dark-mode glass-card style)
# ──────────────────────────────────────────────
st.markdown(
    """
    <style>
    /* ---- Global ---- */
    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 50%, #16213e 100%);
        color: #e0e0e0;
    }
    [data-testid="stSidebar"] {
        background: #14162b;
        border-right: 1px solid rgba(255,255,255,0.08);
    }
    /* ---- Sidebar Labels & Header ---- */
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h2 span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h3 {
        color: #ffffff !important;
        font-weight: 700 !important;
        font-size: 1.4rem !important;
        letter-spacing: 0.5px;
    }
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] label p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] span {
        color: #90cdf4 !important;
        font-size: 0.95rem !important;
        font-weight: 600 !important;
    }
    [data-testid="stSidebar"] div[data-baseweb="select"] > div {
        background-color: #1a1a2e !important;
        border: 1px solid rgba(144, 205, 244, 0.3) !important;
        border-radius: 8px !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] {
        background-color: #253358 !important;
        border: 1px solid #4299e1 !important;
    }
    [data-testid="stSidebar"] [data-baseweb="tag"] span {
        color: #ffffff !important;
    }
    /* ---- Metric cards ---- */
    [data-testid="metric-container"] {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.10);
        border-radius: 12px;
        padding: 1rem 1.2rem;
        backdrop-filter: blur(8px);
    }
    [data-testid="stMetricLabel"] { color: #a0aec0 !important; font-size: 0.82rem; }
    [data-testid="stMetricValue"]  { color: #e2e8f0 !important; font-size: 1.6rem; font-weight: 700; }
    [data-testid="stMetricDelta"]  { font-size: 0.8rem; }
    /* ---- Section headers ---- */
    .section-header {
        font-size: 1.1rem;
        font-weight: 600;
        color: #90cdf4;
        padding: 0.4rem 0 0.2rem;
        border-bottom: 1px solid rgba(144,205,244,0.25);
        margin-bottom: 0.8rem;
    }
    /* ---- Hero banner ---- */
    .hero {
        text-align: center;
        padding: 1.4rem 0 0.6rem;
    }
    .hero h1 { font-size: 2rem; font-weight: 800; color: #fff; margin-bottom: 0.2rem; }
    .hero p  { color: #a0aec0; font-size: 0.95rem; }
    /* ---- Badge ---- */
    .badge {
        display: inline-block;
        background: rgba(99,179,237,0.15);
        border: 1px solid rgba(99,179,237,0.4);
        border-radius: 20px;
        padding: 0.15rem 0.8rem;
        font-size: 0.75rem;
        color: #90cdf4;
        margin: 0.15rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Data loading
# ──────────────────────────────────────────────
DATA_PATH = Path(__file__).resolve().parent / "Data" / "df.csv"

COMMUTE_ORDER = ["0-1 Miles", "1-2 Miles", "2-5 Miles", "5-10 Miles", "10+ Miles"]

PALETTE = px.colors.sequential.Blues[::-1]
ACCENT  = "#63b3ed"

@st.cache_data(show_spinner="Loading dataset …")
def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_PATH, parse_dates=["OrderDate", "DueDate", "ShipDate", "BirthDate"])
    df["CommuteDistance"] = pd.Categorical(df["CommuteDistance"], categories=COMMUTE_ORDER, ordered=True)
    df["Profit"] = df["SalesAmount"] - df["StandardCost"]
    df["ProfitMargin"] = (df["Profit"] / df["SalesAmount"] * 100).round(2)
    return df


df_raw = load_data()

# ──────────────────────────────────────────────
# Sidebar – filters
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🎛️ Filters")

    years = sorted(df_raw["Year"].unique())
    sel_years = st.multiselect("Year", years, default=years)

    categories = sorted(df_raw["ProductCategoryName"].dropna().unique())
    sel_cats = st.multiselect("Product Category", categories, default=categories)

    countries = sorted(df_raw["SalesTerritoryCountry"].dropna().unique())
    sel_countries = st.multiselect("Country", countries, default=countries)

    genders = sorted(df_raw["Gender"].dropna().unique())
    sel_genders = st.multiselect("Gender", genders, default=genders)

    st.markdown("---")
    st.markdown(
        "<div style='color:#718096;font-size:0.78rem;'>"
        "Built by <b style='color:#90cdf4'>Ahmed Rizk Gawish</b><br>"
        "AdventureWorks · 2010–2014"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# Apply filters
# ──────────────────────────────────────────────
mask = (
    df_raw["Year"].isin(sel_years)
    & df_raw["ProductCategoryName"].isin(sel_cats)
    & df_raw["SalesTerritoryCountry"].isin(sel_countries)
    & df_raw["Gender"].isin(sel_genders)
)
df = df_raw[mask].copy()

# ──────────────────────────────────────────────
# Hero
# ──────────────────────────────────────────────
st.markdown(
    """
    <div class='hero'>
        <h1>📊 Retail Sales Intelligence Dashboard</h1>
        <p>AdventureWorks Internet Sales · End-to-End Data Analysis Project</p>
        <span class='badge'>Python</span>
        <span class='badge'>SQL</span>
        <span class='badge'>Streamlit</span>
        <span class='badge'>Plotly</span>
        <span class='badge'>Pandas</span>
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# KPI Row
# ──────────────────────────────────────────────
total_revenue   = df["SalesAmount"].sum()
total_profit    = df["Profit"].sum()
avg_margin      = df["ProfitMargin"].mean()
total_orders    = df["SalesOrderNumber"].nunique()
total_customers = (df["CustomerFirstName"] + " " + df["CustomerLastName"]).nunique()
avg_order_value = df.groupby("SalesOrderNumber")["SalesAmount"].sum().mean()

k1, k2, k3, k4, k5, k6 = st.columns(6)
k1.metric("💰 Total Revenue",      f"${total_revenue:,.0f}")
k2.metric("📈 Total Profit",       f"${total_profit:,.0f}")
k3.metric("🎯 Avg Profit Margin",  f"{avg_margin:.1f}%")
k4.metric("🛒 Total Orders",       f"{total_orders:,}")
k5.metric("👥 Unique Customers",   f"{total_customers:,}")
k6.metric("🧾 Avg Order Value",    f"${avg_order_value:,.0f}")

st.markdown("<br>", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Row 1: Revenue over time  +  Category split
# ──────────────────────────────────────────────
col_l, col_r = st.columns([2, 1])

with col_l:
    st.markdown("<div class='section-header'>Monthly Revenue Trend</div>", unsafe_allow_html=True)
    monthly = (
        df.groupby(["Year", "Month"])["SalesAmount"]
        .sum()
        .reset_index()
        .assign(Period=lambda x: pd.to_datetime(
            x["Year"].astype(str) + "-" + x["Month"].astype(str).str.zfill(2)
        ))
        .sort_values("Period")
    )
    fig_trend = px.area(
        monthly, x="Period", y="SalesAmount",
        color_discrete_sequence=[ACCENT],
        labels={"SalesAmount": "Revenue ($)", "Period": ""},
        template="plotly_dark",
    )
    fig_trend.update_traces(fill="tozeroy", line_width=2)
    fig_trend.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_trend, width='stretch')

with col_r:
    st.markdown("<div class='section-header'>Revenue by Category</div>", unsafe_allow_html=True)
    cat_rev = df.groupby("ProductCategoryName")["SalesAmount"].sum().reset_index()
    fig_pie = px.pie(
        cat_rev, names="ProductCategoryName", values="SalesAmount",
        hole=0.55,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        template="plotly_dark",
    )
    fig_pie.update_traces(textposition="outside", textinfo="label+percent")
    fig_pie.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        showlegend=False,
    )
    st.plotly_chart(fig_pie, width='stretch')

# ──────────────────────────────────────────────
# Row 2: Top subcategories  +  Sales by country (map)
# ──────────────────────────────────────────────
col_a, col_b = st.columns([1, 1])

with col_a:
    st.markdown("<div class='section-header'>Top 10 Subcategories by Revenue</div>", unsafe_allow_html=True)
    sub_rev = (
        df.groupby("ProductSubcategoryName")["SalesAmount"]
        .sum()
        .nlargest(10)
        .reset_index()
        .sort_values("SalesAmount")
    )
    fig_bar = px.bar(
        sub_rev, y="ProductSubcategoryName", x="SalesAmount",
        orientation="h",
        color="SalesAmount",
        color_continuous_scale="Blues",
        labels={"SalesAmount": "Revenue ($)", "ProductSubcategoryName": ""},
        template="plotly_dark",
    )
    fig_bar.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=340,
        coloraxis_showscale=False,
        xaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_bar, width='stretch')

with col_b:
    st.markdown("<div class='section-header'>Revenue by Country</div>", unsafe_allow_html=True)
    country_rev = df.groupby("SalesTerritoryCountry")["SalesAmount"].sum().reset_index()
    fig_map = px.choropleth(
        country_rev,
        locations="SalesTerritoryCountry",
        locationmode="country names",
        color="SalesAmount",
        color_continuous_scale="Blues",
        labels={"SalesAmount": "Revenue ($)"},
        template="plotly_dark",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=340,
        geo=dict(bgcolor="rgba(0,0,0,0)", showframe=False, showcoastlines=True,
                 coastlinecolor="rgba(255,255,255,0.15)", landcolor="rgba(40,40,60,0.8)"),
        coloraxis_colorbar=dict(tickprefix="$"),
    )
    st.plotly_chart(fig_map, width='stretch')

# ──────────────────────────────────────────────
# Row 3: Customer demographics
# ──────────────────────────────────────────────
st.markdown("<div class='section-header'>Customer Demographics & Behaviour</div>", unsafe_allow_html=True)
d1, d2, d3 = st.columns(3)

with d1:
    gender_rev = df.groupby("Gender")["SalesAmount"].sum().reset_index()
    fig_g = px.bar(
        gender_rev, x="Gender", y="SalesAmount",
        color="Gender",
        color_discrete_map={"Male": "#63b3ed", "Female": "#f687b3"},
        labels={"SalesAmount": "Revenue ($)"},
        template="plotly_dark",
        title="Revenue by Gender",
    )
    fig_g.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0), height=280,
        showlegend=False,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_g, width='stretch')

with d2:
    age_rev = df.groupby("AgeGroup", observed=True)["SalesAmount"].sum().reset_index()
    fig_age = px.bar(
        age_rev, x="AgeGroup", y="SalesAmount",
        color="SalesAmount",
        color_continuous_scale="Blues",
        labels={"SalesAmount": "Revenue ($)", "AgeGroup": "Age Group"},
        template="plotly_dark",
        title="Revenue by Age Group",
    )
    fig_age.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0), height=280,
        coloraxis_showscale=False,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_age, width='stretch')

with d3:
    commute_rev = (
        df.groupby("CommuteDistance", observed=True)["SalesAmount"]
        .sum()
        .reset_index()
    )
    fig_cd = px.bar(
        commute_rev, x="CommuteDistance", y="SalesAmount",
        color="SalesAmount",
        color_continuous_scale="Blues",
        labels={"SalesAmount": "Revenue ($)", "CommuteDistance": "Commute Distance"},
        template="plotly_dark",
        title="Revenue by Commute Distance",
    )
    fig_cd.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0), height=280,
        coloraxis_showscale=False,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
    )
    st.plotly_chart(fig_cd, width='stretch')

# ──────────────────────────────────────────────
# Row 4: YoY  +  Income vs Sales scatter
# ──────────────────────────────────────────────
col_p, col_q = st.columns([1, 1])

with col_p:
    st.markdown("<div class='section-header'>Year-over-Year Revenue by Quarter</div>", unsafe_allow_html=True)
    yoy = df.groupby(["Year", "Quarter"])["SalesAmount"].sum().reset_index()
    yoy["Year"] = yoy["Year"].astype(str)
    fig_yoy = px.line(
        yoy, x="Quarter", y="SalesAmount", color="Year",
        markers=True,
        color_discrete_sequence=px.colors.sequential.Blues_r,
        labels={"SalesAmount": "Revenue ($)"},
        template="plotly_dark",
    )
    fig_yoy.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(tickvals=[1,2,3,4], ticktext=["Q1","Q2","Q3","Q4"],
                   gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_yoy, width='stretch')

with col_q:
    st.markdown("<div class='section-header'>Yearly Income vs. Sales Amount</div>", unsafe_allow_html=True)
    sample = df.sample(min(3000, len(df)), random_state=42)
    fig_sc = px.scatter(
        sample, x="YearlyIncome", y="SalesAmount",
        color="ProductCategoryName",
        opacity=0.6,
        color_discrete_sequence=px.colors.qualitative.Safe,
        labels={"YearlyIncome": "Yearly Income ($)", "SalesAmount": "Sales ($)"},
        template="plotly_dark",
    )
    fig_sc.update_traces(marker_size=4)
    fig_sc.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
        xaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_sc, width='stretch')

# ──────────────────────────────────────────────
# Row 5: Profit margin heatmap + Marital status
# ──────────────────────────────────────────────
col_x, col_y = st.columns([1, 1])

with col_x:
    st.markdown("<div class='section-header'>Profit Margin Heatmap (Age × Category)</div>", unsafe_allow_html=True)
    heat_data = (
        df.groupby(["AgeGroup", "ProductCategoryName"], observed=True)["ProfitMargin"]
        .mean()
        .reset_index()
    )
    heat_pivot = heat_data.pivot(index="AgeGroup", columns="ProductCategoryName", values="ProfitMargin")
    fig_heat = go.Figure(
        data=go.Heatmap(
            z=heat_pivot.values,
            x=heat_pivot.columns.tolist(),
            y=heat_pivot.index.tolist(),
            colorscale="Blues",
            text=[[f"{v:.1f}%" for v in row] for row in heat_pivot.values],
            texttemplate="%{text}",
            hovertemplate="Age: %{y}<br>Category: %{x}<br>Margin: %{z:.1f}%<extra></extra>",
        )
    )
    fig_heat.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        xaxis_title="", yaxis_title="",
    )
    st.plotly_chart(fig_heat, width='stretch')

with col_y:
    st.markdown("<div class='section-header'>Revenue by Marital Status & Category</div>", unsafe_allow_html=True)
    ms_cat = df.groupby(["MaritalStatus", "ProductCategoryName"])["SalesAmount"].sum().reset_index()
    ms_cat["MaritalStatus"] = ms_cat["MaritalStatus"].map({"S": "Single", "M": "Married"})
    fig_ms = px.bar(
        ms_cat, x="ProductCategoryName", y="SalesAmount",
        color="MaritalStatus",
        barmode="group",
        color_discrete_map={"Single": "#63b3ed", "Married": "#68d391"},
        labels={"SalesAmount": "Revenue ($)", "ProductCategoryName": "Category"},
        template="plotly_dark",
    )
    fig_ms.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=10, b=0), height=300,
        yaxis=dict(tickprefix="$", gridcolor="rgba(255,255,255,0.06)"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig_ms, width='stretch')

# ──────────────────────────────────────────────
# Raw data explorer
# ──────────────────────────────────────────────
with st.expander("🔍 Explore Raw Data"):
    st.markdown(f"**{len(df):,} rows** after filters")
    cols_show = [
        "SalesOrderNumber", "OrderDate", "ProductName", "ProductCategoryName",
        "SalesAmount", "Profit", "ProfitMargin",
        "Gender", "AgeGroup", "SalesTerritoryCountry",
    ]
    st.dataframe(
        df[cols_show].sort_values("SalesAmount", ascending=False).head(500),
        width='stretch',
        hide_index=True,
    )
