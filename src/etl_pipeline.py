"""
Bluestock MF Capstone - ETL Pipeline
Extract -> Transform -> Load into SQLite star schema.
"""
import pandas as pd
import numpy as np
import sqlite3
import os
from sqlalchemy import create_engine

RAW_DIR = "data/raw"
PROCESSED_DIR = "data/processed"
DB_PATH = "bluestock_mf.db"
os.makedirs(PROCESSED_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# EXTRACT
# ---------------------------------------------------------------------------
print("Extracting raw datasets...")
fund_master = pd.read_csv(f"{RAW_DIR}/01_fund_master.csv")
nav_history = pd.read_csv(f"{RAW_DIR}/02_nav_history.csv", parse_dates=["date"])
aum = pd.read_csv(f"{RAW_DIR}/03_aum_by_fund_house.csv", parse_dates=["quarter_end_date"])
sip = pd.read_csv(f"{RAW_DIR}/04_monthly_sip_inflows.csv", parse_dates=["month"])
cat_inflows = pd.read_csv(f"{RAW_DIR}/05_category_inflows.csv", parse_dates=["month"])
folio = pd.read_csv(f"{RAW_DIR}/06_industry_folio_count.csv", parse_dates=["as_of_date"])
performance = pd.read_csv(f"{RAW_DIR}/07_scheme_performance.csv", parse_dates=["as_of_date"])
transactions = pd.read_csv(f"{RAW_DIR}/08_investor_transactions.csv", parse_dates=["date"])
portfolio = pd.read_csv(f"{RAW_DIR}/09_portfolio_holdings.csv", parse_dates=["as_of_date"])
benchmark = pd.read_csv(f"{RAW_DIR}/10_benchmark_indices.csv", parse_dates=["date"])

# ---------------------------------------------------------------------------
# TRANSFORM
# ---------------------------------------------------------------------------
print("Transforming NAV history...")
nav_history = nav_history.sort_values(["amfi_code", "date"])
nav_history["nav"] = nav_history.groupby("amfi_code")["nav"].ffill()
nav_history["daily_return_pct"] = nav_history.groupby("amfi_code")["nav"].pct_change() * 100
nav_history = nav_history.dropna(subset=["daily_return_pct"]).reset_index(drop=True)

print("Transforming transactions...")
transactions["transaction_type"] = transactions["transaction_type"].str.upper().str.strip()
transactions = transactions[transactions["amount"] > 0]
transactions["kyc_status"] = transactions["kyc_status"].str.title()

print("Building date dimension...")
all_dates = pd.concat([
    nav_history["date"], transactions["date"], benchmark["date"]
]).drop_duplicates().dropna().sort_values()
dim_date = pd.DataFrame({"date": all_dates})
dim_date["date_id"] = dim_date["date"].dt.strftime("%Y%m%d").astype(int)
dim_date["year"] = dim_date["date"].dt.year
dim_date["month"] = dim_date["date"].dt.month
dim_date["quarter"] = dim_date["date"].dt.quarter
dim_date["month_name"] = dim_date["date"].dt.month_name()
dim_date["is_weekday"] = dim_date["date"].dt.weekday < 5

print("Computing risk metrics from NAV...")
risk_free_rate = 0.06
perf_records = []
for amfi, grp in nav_history.groupby("amfi_code"):
    grp = grp.sort_values("date")
    navs = grp["nav"].values
    returns = grp["daily_return_pct"].values / 100
    
    # CAGR over full period
    total_years = (grp["date"].max() - grp["date"].min()).days / 365.25
    cagr = (navs[-1] / navs[0]) ** (1 / total_years) - 1 if total_years > 0 else 0
    
    std = np.std(returns) * np.sqrt(252)
    downside = np.std([r for r in returns if r < 0]) * np.sqrt(252)
    sharpe = (cagr - risk_free_rate) / std if std > 0 else 0
    sortino = (cagr - risk_free_rate) / downside if downside > 0 else 0
    
    # Max drawdown
    peak = np.maximum.accumulate(navs)
    mdd = np.min((navs - peak) / peak)
    
    # Rolling 1Y, 3Y, 5Y returns
    end = navs[-1]
    ret_1yr = ret_3yr = ret_5yr = np.nan
    if len(navs) >= 252:
        ret_1yr = (end / navs[-252]) - 1
    if len(navs) >= 756:
        ret_3yr = (end / navs[-756]) ** (1/3) - 1
    if len(navs) >= 1260:
        ret_5yr = (end / navs[-1260]) ** (1/5) - 1
    
    # Beta vs Nifty 50
    bench_50 = benchmark[benchmark["index_name"] == "Nifty 50"].sort_values("date")
    bench_50 = bench_50[bench_50["date"].isin(grp["date"])].sort_values("date")
    fund_merged = grp[grp["date"].isin(bench_50["date"])].sort_values("date")
    beta = alpha = np.nan
    if len(fund_merged) == len(bench_50) and len(fund_merged) > 30:
        bench_rets = bench_50["close_value"].pct_change().dropna().values
        fund_rets = fund_merged["nav"].pct_change().dropna().values
        if len(bench_rets) == len(fund_rets):
            cov = np.cov(fund_rets, bench_rets)[0, 1]
            var = np.var(bench_rets)
            beta = cov / var if var > 0 else np.nan
            alpha = (np.mean(fund_rets) - risk_free_rate/252) - beta * (np.mean(bench_rets) - risk_free_rate/252)
            alpha *= 252
    
    perf_records.append({
        "amfi_code": amfi,
        "as_of_date": grp["date"].max(),
        "return_1yr_pct": round(ret_1yr * 100, 2) if not np.isnan(ret_1yr) else None,
        "return_3yr_pct": round(ret_3yr * 100, 2) if not np.isnan(ret_3yr) else None,
        "return_5yr_pct": round(ret_5yr * 100, 2) if not np.isnan(ret_5yr) else None,
        "cagr_pct": round(cagr * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "alpha_pct": round(alpha * 100, 2) if not np.isnan(alpha) else None,
        "beta": round(beta, 2) if not np.isnan(beta) else None,
        "max_drawdown_pct": round(mdd * 100, 2),
        "std_dev_pct": round(std * 100, 2)
    })

computed_performance = pd.DataFrame(perf_records)

# ---------------------------------------------------------------------------
# LOAD
# ---------------------------------------------------------------------------
print("Loading into SQLite database...")
if os.path.exists(DB_PATH):
    os.remove(DB_PATH)
engine = create_engine(f"sqlite:///{DB_PATH}")

fund_master.to_sql("dim_fund", engine, index=False, if_exists="replace")
dim_date.to_sql("dim_date", engine, index=False, if_exists="replace")
nav_history.to_sql("fact_nav", engine, index=False, if_exists="replace")
transactions.to_sql("fact_transactions", engine, index=False, if_exists="replace")
computed_performance.to_sql("fact_performance", engine, index=False, if_exists="replace")
portfolio.to_sql("fact_portfolio", engine, index=False, if_exists="replace")
aum.to_sql("fact_aum", engine, index=False, if_exists="replace")
sip.to_sql("fact_sip_industry", engine, index=False, if_exists="replace")
cat_inflows.to_sql("fact_category_inflows", engine, index=False, if_exists="replace")
folio.to_sql("fact_industry_folio", engine, index=False, if_exists="replace")
benchmark.to_sql("fact_benchmark", engine, index=False, if_exists="replace")

# Create indexes
with sqlite3.connect(DB_PATH) as conn:
    conn.execute("CREATE INDEX idx_nav ON fact_nav(amfi_code, date)")
    conn.execute("CREATE INDEX idx_tx ON fact_transactions(amfi_code, date)")
    conn.execute("CREATE INDEX idx_perf ON fact_performance(amfi_code)")
    conn.execute("CREATE INDEX idx_bench ON fact_benchmark(index_name, date)")

# Save processed CSVs
fund_master.to_csv(f"{PROCESSED_DIR}/dim_fund.csv", index=False)
dim_date.to_csv(f"{PROCESSED_DIR}/dim_date.csv", index=False)
nav_history.to_csv(f"{PROCESSED_DIR}/fact_nav.csv", index=False)
transactions.to_csv(f"{PROCESSED_DIR}/fact_transactions.csv", index=False)
computed_performance.to_csv(f"{PROCESSED_DIR}/fact_performance.csv", index=False)
portfolio.to_csv(f"{PROCESSED_DIR}/fact_portfolio.csv", index=False)
aum.to_csv(f"{PROCESSED_DIR}/fact_aum.csv", index=False)
sip.to_csv(f"{PROCESSED_DIR}/fact_sip_industry.csv", index=False)
cat_inflows.to_csv(f"{PROCESSED_DIR}/fact_category_inflows.csv", index=False)
folio.to_csv(f"{PROCESSED_DIR}/fact_industry_folio.csv", index=False)
benchmark.to_csv(f"{PROCESSED_DIR}/fact_benchmark.csv", index=False)

print(f"ETL complete. Database: {DB_PATH}")
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table'", engine).name.tolist()
print(f"Tables loaded: {tables}")
