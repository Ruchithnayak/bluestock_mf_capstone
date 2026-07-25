"""
Bluestock MF Capstone - Interactive Dashboard (Streamlit)
Run with: streamlit run dashboard/app.py
"""
import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Bluestock MF Analytics", layout="wide")

DB_PATH = "../bluestock_mf.db"

@st.cache_data
def load_data():
    conn = sqlite3.connect(DB_PATH)
    fund = pd.read_sql("SELECT * FROM dim_fund", conn)
    nav = pd.read_sql("SELECT * FROM fact_nav", conn, parse_dates=["date"])
    perf = pd.read_sql("""
        SELECT f.scheme_name, f.fund_house, f.category, p.*
        FROM fact_performance p JOIN dim_fund f ON p.amfi_code = f.amfi_code
    """, conn)
    tx = pd.read_sql("SELECT * FROM fact_transactions", conn, parse_dates=["date"])
    aum = pd.read_sql("SELECT * FROM fact_aum", conn, parse_dates=["quarter_end_date"])
    sip = pd.read_sql("SELECT * FROM fact_sip_industry", conn, parse_dates=["month"])
    bench = pd.read_sql("SELECT * FROM fact_benchmark", conn, parse_dates=["date"])
    conn.close()
    return fund, nav, perf, tx, aum, sip, bench

fund, nav, perf, tx, aum, sip, bench = load_data()

st.title("Bluestock Fintech - Mutual Fund Analytics Platform")
st.markdown("End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
selected_house = st.sidebar.multiselect("Fund House", sorted(fund["fund_house"].unique()), default=[])
selected_category = st.sidebar.multiselect("Category", sorted(fund["category"].unique()), default=[])
date_range = st.sidebar.date_input("Date Range", [nav["date"].min(), nav["date"].max()])

# Apply filters
filtered_fund = fund.copy()
if selected_house:
    filtered_fund = filtered_fund[filtered_fund["fund_house"].isin(selected_house)]
if selected_category:
    filtered_fund = filtered_fund[filtered_fund["category"].isin(selected_category)]

amfi_codes = filtered_fund["amfi_code"].tolist()
filtered_nav = nav[(nav["amfi_code"].isin(amfi_codes)) &
                   (nav["date"] >= pd.Timestamp(date_range[0])) &
                   (nav["date"] <= pd.Timestamp(date_range[1]))]
filtered_perf = perf[perf["amfi_code"].isin(amfi_codes)]

# KPIs
st.header("Executive KPIs")
col1, col2, col3, col4 = st.columns(4)
latest_aum = aum["aum_crore"].iloc[-1] if not aum.empty else 0
latest_sip = sip["sip_inflow_crore"].iloc[-1] if not sip.empty else 0
col1.metric("Latest AUM (Cr)", f"₹{latest_aum:,.0f}")
col2.metric("Latest SIP Inflow (Cr)", f"₹{latest_sip:,.0f}")
col3.metric("Schemes Tracked", len(fund))
col4.metric("Investors", tx["investor_id"].nunique())

# Tabs
tab1, tab2, tab3, tab4 = st.tabs(["Fund Performance", "NAV Trends", "Investor Insights", "Industry Trends"])

with tab1:
    st.subheader("Risk-Return Analysis")
    fig = px.scatter(filtered_perf, x="std_dev_pct", y="return_1yr_pct",
                     color="category", hover_data=["scheme_name", "sharpe_ratio"],
                     title="Risk vs 1-Year Return")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Performance Metrics Table")
    display_cols = ["scheme_name", "fund_house", "category", "return_1yr_pct",
                    "sharpe_ratio", "alpha_pct", "beta", "max_drawdown_pct"]
    st.dataframe(filtered_perf[display_cols].sort_values("sharpe_ratio", ascending=False),
                 use_container_width=True)

with tab2:
    st.subheader("NAV Movement")
    if not filtered_nav.empty:
        fig = px.line(filtered_nav, x="date", y="nav", color="amfi_code",
                      title="NAV Over Time", labels={"nav": "NAV (Rs.)"})
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Select filters to view NAV trends.")

    st.subheader("Benchmark Comparison")
    bench_selected = bench[bench["index_name"].isin(["Nifty 50", "Nifty 100", "Nifty Midcap 150", "BSE SmallCap"])]
    bench_norm = bench_selected.copy()
    bench_norm["normalized"] = bench_norm.groupby("index_name")["close_value"].transform(lambda x: x / x.iloc[0] * 100)
    fig = px.line(bench_norm, x="date", y="normalized", color="index_name",
                  title="Benchmark Indices (Normalized to 100)")
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.subheader("Transaction Amount by Type")
    tx_summary = tx.groupby(["transaction_type", "tier"])["amount"].sum().reset_index()
    fig = px.bar(tx_summary, x="transaction_type", y="amount", color="tier", barmode="group")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Geographic Distribution")
    geo = tx.groupby("state")["amount"].sum().reset_index().sort_values("amount", ascending=False).head(10)
    fig = px.bar(geo, y="state", x="amount", orientation="h", title="Top 10 States by Transaction Amount")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Demographic Segmentation")
    demo = tx.groupby("income_slab")["amount"].agg(["sum", "count"]).reset_index()
    fig = px.pie(demo, names="income_slab", values="sum", title="Transaction Amount by Income Slab")
    st.plotly_chart(fig, use_container_width=True)

with tab4:
    st.subheader("AUM Growth by Fund House")
    fig = px.line(aum, x="quarter_end_date", y="aum_crore", color="fund_house",
                  title="Quarterly AUM Growth")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("SIP Inflow Trend")
    fig = px.line(sip, x="month", y="sip_inflow_crore", markers=True, title="Monthly SIP Inflow")
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Category-wise Net Inflows (FY 2024-25)")
    cat = pd.read_sql("""
        SELECT category, SUM(net_inflow_crore) AS total_inflow
        FROM fact_category_inflows GROUP BY category
    """, sqlite3.connect(DB_PATH))
    fig = px.bar(cat, x="category", y="total_inflow", title="Net Inflows by Category")
    st.plotly_chart(fig, use_container_width=True)

st.sidebar.markdown("---")
st.sidebar.info("Data sourced from AMFI India, mfapi.in, NSE/BSE. For educational purposes only.")
