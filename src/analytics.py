"""
Bluestock MF Capstone - Analytics & Risk Metrics
Produces summary tables and charts for the dashboard/report.
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
import os

DB_PATH = "bluestock_mf.db"
REPORT_DIR = "reports/figures"
os.makedirs(REPORT_DIR, exist_ok=True)

conn = sqlite3.connect(DB_PATH)

# ---------------------------------------------------------------------------
# Helper queries
# ---------------------------------------------------------------------------
def query(sql):
    return pd.read_sql(sql, conn)

# ---------------------------------------------------------------------------
# 1. Fund Performance Summary
# ---------------------------------------------------------------------------
perf = query("""
SELECT f.scheme_name, f.fund_house, f.category, p.*
FROM fact_performance p
JOIN dim_fund f ON p.amfi_code = f.amfi_code
""")
print("Top 5 funds by Sharpe ratio:")
print(perf.nlargest(5, "sharpe_ratio")[["scheme_name", "category", "sharpe_ratio", "return_1yr_pct", "alpha_pct"]])

# ---------------------------------------------------------------------------
# 2. AUM Growth Trends
# ---------------------------------------------------------------------------
aum = query("""
SELECT fund_house, quarter_end_date, aum_crore
FROM fact_aum
ORDER BY fund_house, quarter_end_date
""")
aum["quarter_end_date"] = pd.to_datetime(aum["quarter_end_date"])
plt.figure(figsize=(12, 6))
for fh in aum["fund_house"].unique()[:5]:
    sub = aum[aum["fund_house"] == fh]
    plt.plot(sub["quarter_end_date"], sub["aum_crore"]/100000, marker="o", label=fh.split()[0])
plt.title("AUM Growth Trend - Top 5 AMCs (Rs. Lakh Crore)")
plt.xlabel("Quarter")
plt.ylabel("AUM (Lakh Crore)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/aum_growth.png")
plt.close()

# ---------------------------------------------------------------------------
# 3. SIP Inflow Trend
# ---------------------------------------------------------------------------
sip = query("SELECT * FROM fact_sip_industry ORDER BY month")
sip["month"] = pd.to_datetime(sip["month"])
plt.figure(figsize=(12, 5))
plt.plot(sip["month"], sip["sip_inflow_crore"], marker="o", color="green")
plt.title("Monthly SIP Inflow Trend")
plt.xlabel("Month")
plt.ylabel("SIP Inflow (Rs. Crore)")
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/sip_trend.png")
plt.close()

# ---------------------------------------------------------------------------
# 4. Category-wise Inflows
# ---------------------------------------------------------------------------
cat = query("""
SELECT category, SUM(net_inflow_crore) AS total_inflow
FROM fact_category_inflows
GROUP BY category
""")
plt.figure(figsize=(10, 5))
sns.barplot(data=cat, x="category", y="total_inflow", palette="viridis")
plt.title("FY 2024-25 Net Inflows by Category")
plt.ylabel("Inflow (Rs. Crore)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/category_inflows.png")
plt.close()

# ---------------------------------------------------------------------------
# 5. Investor Demographics
# ---------------------------------------------------------------------------
tx = query("""
SELECT tier, transaction_type, SUM(amount) AS total_amount, COUNT(*) AS tx_count
FROM fact_transactions
GROUP BY tier, transaction_type
""")
plt.figure(figsize=(10, 5))
sns.barplot(data=tx, x="transaction_type", y="total_amount", hue="tier")
plt.title("Transaction Amount by Type and Tier")
plt.ylabel("Amount (Rs.)")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/investor_tier.png")
plt.close()

# ---------------------------------------------------------------------------
# 6. Geographic Distribution
# ---------------------------------------------------------------------------
geo = query("""
SELECT state, SUM(amount) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_amount DESC
LIMIT 10
""")
plt.figure(figsize=(10, 6))
sns.barplot(data=geo, y="state", x="total_amount", palette="coolwarm")
plt.title("Top 10 States by Transaction Amount")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/geo_distribution.png")
plt.close()

# ---------------------------------------------------------------------------
# 7. Risk-Return Scatter
# ---------------------------------------------------------------------------
plt.figure(figsize=(10, 6))
sns.scatterplot(data=perf, x="std_dev_pct", y="return_1yr_pct", hue="category", s=100)
plt.title("Risk vs Return by Fund Category")
plt.xlabel("Standard Deviation (%)")
plt.ylabel("1-Year Return (%)")
plt.legend(bbox_to_anchor=(1.05, 1), loc="upper left")
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/risk_return.png")
plt.close()

# ---------------------------------------------------------------------------
# 8. Benchmark Comparison
# ---------------------------------------------------------------------------
bench = query("""
SELECT index_name, date, close_value
FROM fact_benchmark
WHERE index_name IN ('Nifty 50', 'Nifty 100', 'Nifty Midcap 150', 'BSE SmallCap')
ORDER BY index_name, date
""")
bench["date"] = pd.to_datetime(bench["date"])
plt.figure(figsize=(12, 6))
for idx in bench["index_name"].unique():
    sub = bench[bench["index_name"] == idx]
    normalized = sub["close_value"] / sub["close_value"].iloc[0] * 100
    plt.plot(sub["date"], normalized, label=idx)
plt.title("Benchmark Index Performance (Normalized)")
plt.xlabel("Date")
plt.ylabel("Index Value (Base = 100)")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig(f"{REPORT_DIR}/benchmark_comparison.png")
plt.close()

# ---------------------------------------------------------------------------
# 9. Summary KPIs
# ---------------------------------------------------------------------------
kpis = query("""
SELECT
    (SELECT SUM(aum_crore) FROM fact_aum WHERE quarter_end_date = (SELECT MAX(quarter_end_date) FROM fact_aum)) AS total_aum_crore,
    (SELECT sip_inflow_crore FROM fact_sip_industry WHERE month = (SELECT MAX(month) FROM fact_sip_industry)) AS latest_sip_crore,
    (SELECT total_folios_crore FROM fact_industry_folio WHERE as_of_date = (SELECT MAX(as_of_date) FROM fact_industry_folio)) AS total_folios_crore,
    (SELECT COUNT(DISTINCT amfi_code) FROM dim_fund) AS num_schemes,
    (SELECT COUNT(DISTINCT investor_id) FROM fact_transactions) AS num_investors
""")
print("\nKey Performance Indicators:")
print(kpis.T)

conn.close()
print(f"\nAnalytics complete. Figures saved to {REPORT_DIR}/")
