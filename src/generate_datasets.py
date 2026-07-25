"""
Bluestock MF Capstone - Dataset Generator
Generates 10 realistic datasets for the Mutual Fund Analytics Platform.
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

np.random.seed(42)
RAW_DIR = "data/raw"
os.makedirs(RAW_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# 1. FUND MASTER (40 schemes)
# ---------------------------------------------------------------------------
fund_houses = [
    "SBI Mutual Fund", "ICICI Prudential Mutual Fund", "HDFC Mutual Fund",
    "Nippon India Mutual Fund", "Axis Mutual Fund", "Kotak Mahindra Mutual Fund",
    "Aditya Birla Sun Life Mutual Fund", "UTI Mutual Fund", "DSP Mutual Fund",
    "Franklin Templeton Mutual Fund"
]

categories = ["Large Cap", "Mid Cap", "Small Cap", "ELSS", "Liquid", "Debt", "Hybrid", "Index"]

schemes_data = [
    ("119551", "SBI Bluechip Fund - Direct Plan Growth", "SBI Mutual Fund", "Large Cap", 0.84, "Moderate", "Sohini Andani"),
    ("120503", "ICICI Prudential Bluechip Fund - Direct Growth", "ICICI Prudential Mutual Fund", "Large Cap", 0.92, "Moderate", "Rajat Chandak"),
    ("125497", "HDFC Top 100 Fund - Direct Plan Growth", "HDFC Mutual Fund", "Large Cap", 1.05, "Moderately High", "Prashant Jain"),
    ("118632", "Nippon India Large Cap Fund - Direct Growth", "Nippon India Mutual Fund", "Large Cap", 0.78, "Moderate", "Manish Gunwani"),
    ("119092", "Axis Bluechip Fund - Direct Plan Growth", "Axis Mutual Fund", "Large Cap", 0.65, "Moderate", "Shreyash Devalkar"),
    ("120841", "Kotak Bluechip Fund - Direct Growth", "Kotak Mahindra Mutual Fund", "Large Cap", 0.88, "Moderate", "Harish Krishnan"),
    ("119437", "Aditya Birla Sun Life Frontline Equity Fund - Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Large Cap", 0.95, "Moderate", "Mahesh Patil"),
    ("120716", "UTI Mastershare Unit Scheme - Direct Growth", "UTI Mutual Fund", "Large Cap", 1.10, "Moderate", "Swati Kulkarni"),
    ("120642", "DSP Top 100 Equity Fund - Direct Growth", "DSP Mutual Fund", "Large Cap", 1.15, "Moderately High", "Vinit Sambre"),
    ("118559", "Franklin India Bluechip Fund - Direct Growth", "Franklin Templeton Mutual Fund", "Large Cap", 1.25, "Moderately High", "Anand Radhakrishnan"),
    ("119598", "SBI Magnum Midcap Fund - Direct Growth", "SBI Mutual Fund", "Mid Cap", 0.98, "High", "Sohini Andani"),
    ("120586", "ICICI Prudential Midcap Fund - Direct Growth", "ICICI Prudential Mutual Fund", "Mid Cap", 1.05, "High", "Lalit Kumar"),
    ("125494", "HDFC Mid-Cap Opportunities Fund - Direct Growth", "HDFC Mutual Fund", "Mid Cap", 0.90, "High", "Chirag Setalvad"),
    ("118743", "Nippon India Growth Fund - Direct Growth", "Nippon India Mutual Fund", "Mid Cap", 0.85, "High", "Manish Gunwani"),
    ("119552", "Axis Midcap Fund - Direct Plan Growth", "Axis Mutual Fund", "Mid Cap", 0.72, "High", "Shreyash Devalkar"),
    ("120845", "Kotak Emerging Equity Fund - Direct Growth", "Kotak Mahindra Mutual Fund", "Mid Cap", 0.80, "High", "Pankaj Tibrewal"),
    ("119544", "Aditya Birla Sun Life Midcap Fund - Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Mid Cap", 1.12, "High", "Vinod Narayan"),
    ("120725", "UTI Mid Cap Fund - Direct Growth", "UTI Mutual Fund", "Mid Cap", 1.20, "High", "Ankit Agarwal"),
    ("120645", "DSP Midcap Fund - Direct Growth", "DSP Mutual Fund", "Mid Cap", 0.95, "High", "Vinit Sambre"),
    ("118564", "Franklin India Prima Fund - Direct Growth", "Franklin Templeton Mutual Fund", "Mid Cap", 1.30, "High", "R. Janakiraman"),
    ("119600", "SBI Small Cap Fund - Direct Growth", "SBI Mutual Fund", "Small Cap", 0.90, "Very High", "R. Srinivasan"),
    ("120606", "ICICI Prudential Smallcap Fund - Direct Growth", "ICICI Prudential Mutual Fund", "Small Cap", 0.95, "Very High", "Sankaran Naren"),
    ("125495", "HDFC Small Cap Fund - Direct Growth", "HDFC Mutual Fund", "Small Cap", 0.88, "Very High", "Chirag Setalvad"),
    ("118751", "Nippon India Small Cap Fund - Direct Growth", "Nippon India Mutual Fund", "Small Cap", 0.82, "Very High", "Samir Rachh"),
    ("119553", "Axis Small Cap Fund - Direct Plan Growth", "Axis Mutual Fund", "Small Cap", 0.70, "Very High", "Anupam Tiwari"),
    ("120848", "Kotak Small Cap Fund - Direct Growth", "Kotak Mahindra Mutual Fund", "Small Cap", 0.85, "Very High", "Pankaj Tibrewal"),
    ("119545", "Aditya Birla Sun Life Small Cap Fund - Direct Growth", "Aditya Birla Sun Life Mutual Fund", "Small Cap", 1.05, "Very High", "Vishal Gajwani"),
    ("120727", "UTI Small Cap Fund - Direct Growth", "UTI Mutual Fund", "Small Cap", 1.15, "Very High", "Ankit Agarwal"),
    ("120647", "DSP Small Cap Fund - Direct Growth", "DSP Mutual Fund", "Small Cap", 0.98, "Very High", "Vinit Sambre"),
    ("118566", "Franklin India Smaller Companies Fund - Direct Growth", "Franklin Templeton Mutual Fund", "Small Cap", 1.25, "Very High", "R. Janakiraman"),
    ("119062", "Axis Long Term Equity Fund - Direct Growth", "Axis Mutual Fund", "ELSS", 0.75, "Moderately High", "Jinesh Gopani"),
    ("120505", "ICICI Prudential Long Term Equity Fund - Direct Growth", "ICICI Prudential Mutual Fund", "ELSS", 0.88, "Moderately High", "Harish Bihani"),
    ("119564", "SBI Tax Advantage Fund - Direct Growth", "SBI Mutual Fund", "ELSS", 1.10, "High", "R. Srinivasan"),
    ("125498", "HDFC Taxsaver Fund - Direct Growth", "HDFC Mutual Fund", "ELSS", 1.20, "High", "Rakesh Vyas"),
    ("120850", "Kotak Tax Saver Fund - Direct Growth", "Kotak Mahindra Mutual Fund", "ELSS", 0.80, "Moderately High", "Harsha Upadhyaya"),
    ("119438", "Aditya Birla Sun Life Tax Relief 96 - Direct Growth", "Aditya Birla Sun Life Mutual Fund", "ELSS", 0.92, "Moderately High", "Ajay Garg"),
    ("120728", "UTI Equity Tax Savings Plan - Direct Growth", "UTI Mutual Fund", "ELSS", 1.05, "Moderately High", "Swati Kulkarni"),
    ("120852", "Kotak Liquid Fund - Direct Growth", "Kotak Mahindra Mutual Fund", "Liquid", 0.20, "Low", "Deepak Agrawal"),
    ("119556", "SBI Liquid Fund - Direct Growth", "SBI Mutual Fund", "Liquid", 0.18, "Low", "R. Arun"),
    ("120507", "ICICI Prudential Liquid Fund - Direct Growth", "ICICI Prudential Mutual Fund", "Liquid", 0.22, "Low", "Rahul Goswami"),
]

fund_master = pd.DataFrame(schemes_data, columns=[
    "amfi_code", "scheme_name", "fund_house", "category", "expense_ratio_pct",
    "risk_grade", "fund_manager"
])
fund_master["launch_date"] = pd.to_datetime("2015-01-01") + pd.to_timedelta(np.random.randint(0, 2000, 40), unit="D")
fund_master.to_csv(f"{RAW_DIR}/01_fund_master.csv", index=False)
print(f"01_fund_master.csv: {fund_master.shape}")

# ---------------------------------------------------------------------------
# 2. NAV HISTORY (~46,000 rows)
# ---------------------------------------------------------------------------
dates = pd.date_range(start="2022-01-01", end="2026-05-31", freq="D")
business_days = dates[dates.weekday < 5]  # Mon-Fri only

nav_records = []
base_navs = {
    "Large Cap": 500, "Mid Cap": 350, "Small Cap": 200, "ELSS": 450,
    "Liquid": 1000, "Debt": 300, "Hybrid": 400, "Index": 150
}

for _, row in fund_master.iterrows():
    amfi = row["amfi_code"]
    cat = row["category"]
    base = base_navs[cat] * np.random.uniform(0.8, 1.2)
    returns = np.random.normal(0.0003, 0.012, len(business_days))
    if cat == "Liquid":
        returns = np.random.normal(0.00015, 0.0005, len(business_days))
    elif cat == "Debt":
        returns = np.random.normal(0.0002, 0.004, len(business_days))
    elif cat == "Small Cap":
        returns = np.random.normal(0.0004, 0.018, len(business_days))

    navs = [base]
    for r in returns[1:]:
        navs.append(navs[-1] * (1 + r))

    df_nav = pd.DataFrame({
        "amfi_code": amfi,
        "date": business_days,
        "nav": navs
    })
    nav_records.append(df_nav)

nav_history = pd.concat(nav_records, ignore_index=True)
nav_history["date"] = pd.to_datetime(nav_history["date"]).dt.date
nav_history = nav_history.sort_values(["amfi_code", "date"]).reset_index(drop=True)
nav_history.to_csv(f"{RAW_DIR}/02_nav_history.csv", index=False)
print(f"02_nav_history.csv: {nav_history.shape}")

# ---------------------------------------------------------------------------
# 3. AUM BY FUND HOUSE (quarterly)
# ---------------------------------------------------------------------------
quarters = pd.date_range(start="2022-03-31", end="2025-12-31", freq="QE")
aum_base = {
    "SBI Mutual Fund": 850000, "ICICI Prudential Mutual Fund": 720000,
    "HDFC Mutual Fund": 620000, "Nippon India Mutual Fund": 380000,
    "Axis Mutual Fund": 310000, "Kotak Mahindra Mutual Fund": 290000,
    "Aditya Birla Sun Life Mutual Fund": 270000, "UTI Mutual Fund": 220000,
    "DSP Mutual Fund": 140000, "Franklin Templeton Mutual Fund": 95000
}
aum_records = []
for fh, base in aum_base.items():
    for q in quarters:
        growth = 1 + (q - quarters[0]).days / 365 * 0.12 + np.random.normal(0, 0.03)
        aum_records.append({
            "fund_house": fh,
            "quarter_end_date": q.date(),
            "aum_crore": round(base * growth / 100, 2),  # in crore
            "num_schemes": np.random.randint(25, 80)
        })
aum_by_fund_house = pd.DataFrame(aum_records)
aum_by_fund_house.to_csv(f"{RAW_DIR}/03_aum_by_fund_house.csv", index=False)
print(f"03_aum_by_fund_house.csv: {aum_by_fund_house.shape}")

# ---------------------------------------------------------------------------
# 4. MONTHLY SIP INFLOWS
# ---------------------------------------------------------------------------
months = pd.date_range(start="2022-01-01", end="2025-12-01", freq="MS")
sip_records = []
base_sip = 12500
for m in months:
    idx = (m - months[0]).days / 30
    sip = base_sip + idx * 320 + np.random.normal(0, 400)
    sip_records.append({
        "month": m.date(),
        "sip_inflow_crore": round(sip, 2),
        "active_sip_accounts_lakh": round(450 + idx * 10 + np.random.normal(0, 5), 2),
        "new_sip_registrations_lakh": round(15 + np.random.normal(0, 3), 2),
        "sip_aum_crore": round(sip * (12 + idx * 0.15), 2)
    })
monthly_sip = pd.DataFrame(sip_records)
monthly_sip.to_csv(f"{RAW_DIR}/04_monthly_sip_inflows.csv", index=False)
print(f"04_monthly_sip_inflows.csv: {monthly_sip.shape}")

# ---------------------------------------------------------------------------
# 5. CATEGORY INFLOWS
# ---------------------------------------------------------------------------
categories_full = ["Large Cap", "Mid Cap", "Small Cap", "ELSS", "Liquid", "Debt", "Hybrid", "Index"]
months_fy = pd.date_range(start="2024-04-01", end="2025-03-01", freq="MS")
cat_records = []
for m in months_fy:
    for cat in categories_full:
        base = {"Large Cap": 2500, "Mid Cap": 1800, "Small Cap": 2200, "ELSS": 1200,
                "Liquid": 800, "Debt": 1500, "Hybrid": 900, "Index": 600}[cat]
        cat_records.append({
            "month": m.date(),
            "category": cat,
            "net_inflow_crore": round(base + np.random.normal(0, base * 0.2), 2),
            "number_of_folios_lakh": round(np.random.uniform(5, 45), 2)
        })
category_inflows = pd.DataFrame(cat_records)
category_inflows.to_csv(f"{RAW_DIR}/05_category_inflows.csv", index=False)
print(f"05_category_inflows.csv: {category_inflows.shape}")

# ---------------------------------------------------------------------------
# 6. INDUSTRY FOLIO COUNT
# ---------------------------------------------------------------------------
folio_dates = pd.date_range(start="2020-12-01", end="2025-12-01", freq="3MS")
folio_records = []
for d in folio_dates:
    idx = (d - folio_dates[0]).days / 365
    folio_records.append({
        "as_of_date": d.date(),
        "equity_folios_crore": round(4 + idx * 1.8 + np.random.normal(0, 0.1), 2),
        "debt_folios_crore": round(2 + idx * 0.3 + np.random.normal(0, 0.05), 2),
        "hybrid_folios_crore": round(1.5 + idx * 0.4 + np.random.normal(0, 0.05), 2),
        "total_folios_crore": round(8 + idx * 2.5 + np.random.normal(0, 0.15), 2)
    })
industry_folio = pd.DataFrame(folio_records)
industry_folio.to_csv(f"{RAW_DIR}/06_industry_folio_count.csv", index=False)
print(f"06_industry_folio_count.csv: {industry_folio.shape}")

# ---------------------------------------------------------------------------
# 7. SCHEME PERFORMANCE (computed later properly, but placeholder here)
# ---------------------------------------------------------------------------
perf_records = []
for _, row in fund_master.iterrows():
    cat = row["category"]
    risk_map = {"Low": 0.03, "Moderate": 0.12, "Moderately High": 0.16, "High": 0.20, "Very High": 0.25}
    std = risk_map.get(row["risk_grade"], 0.15)
    ret_1yr = np.random.normal(0.12 if cat != "Liquid" else 0.06, std)
    ret_3yr = np.random.normal(0.14 if cat != "Liquid" else 0.06, std * 0.6)
    ret_5yr = np.random.normal(0.13 if cat != "Liquid" else 0.06, std * 0.5)
    sharpe = (ret_1yr - 0.06) / std if std > 0 else 0
    sortino = (ret_1yr - 0.06) / (std * 0.7) if std > 0 else 0
    alpha = np.random.normal(0.02, 0.04)
    beta = np.random.uniform(0.7, 1.2)
    max_dd = np.random.uniform(-0.15, -0.35) if cat != "Liquid" else np.random.uniform(-0.01, -0.03)
    perf_records.append({
        "amfi_code": row["amfi_code"],
        "as_of_date": "2026-05-31",
        "return_1yr_pct": round(ret_1yr * 100, 2),
        "return_3yr_pct": round(ret_3yr * 100, 2),
        "return_5yr_pct": round(ret_5yr * 100, 2),
        "sharpe_ratio": round(sharpe, 2),
        "sortino_ratio": round(sortino, 2),
        "alpha_pct": round(alpha * 100, 2),
        "beta": round(beta, 2),
        "max_drawdown_pct": round(max_dd * 100, 2),
        "std_dev_pct": round(std * 100, 2)
    })
scheme_performance = pd.DataFrame(perf_records)
scheme_performance.to_csv(f"{RAW_DIR}/07_scheme_performance.csv", index=False)
print(f"07_scheme_performance.csv: {scheme_performance.shape}")

# ---------------------------------------------------------------------------
# 8. INVESTOR TRANSACTIONS (~32,000 rows)
# ---------------------------------------------------------------------------
states = ["Maharashtra", "Karnataka", "Tamil Nadu", "Delhi", "Gujarat", "Telangana",
          "West Bengal", "Rajasthan", "Kerala", "Punjab", "Haryana", "Madhya Pradesh",
          "Uttar Pradesh", "Bihar", "Odisha"]
cities_t30 = ["Mumbai", "Bangalore", "Chennai", "Delhi", "Hyderabad", "Pune", "Kolkata", "Ahmedabad"]
cities_b30 = ["Jaipur", "Lucknow", "Bhopal", "Patna", "Bhubaneswar", "Indore", "Coimbatore", "Nagpur"]

n_investors = 5000
investors = pd.DataFrame({
    "investor_id": [f"INV{i:05d}" for i in range(1, n_investors + 1)],
    "age": np.random.randint(22, 65, n_investors),
    "gender": np.random.choice(["M", "F"], n_investors, p=[0.65, 0.35]),
    "state": np.random.choice(states, n_investors),
    "city": np.random.choice(cities_t30 + cities_b30, n_investors),
    "tier": np.random.choice(["T30", "B30"], n_investors, p=[0.55, 0.45]),
    "kyc_status": np.random.choice(["Completed", "Pending"], n_investors, p=[0.95, 0.05]),
    "income_slab": np.random.choice(["<5L", "5-10L", "10-20L", ">20L"], n_investors, p=[0.25, 0.35, 0.30, 0.10])
})

tx_records = []
tx_id = 1
for _, inv in investors.iterrows():
    n_tx = np.random.poisson(6) + 1
    for _ in range(n_tx):
        amfi = np.random.choice(fund_master["amfi_code"])
        tx_type = np.random.choice(["SIP", "Lumpsum", "Redemption"], p=[0.70, 0.20, 0.10])
        if tx_type == "SIP":
            amount = np.random.choice([500, 1000, 2500, 5000, 10000], p=[0.15, 0.25, 0.30, 0.20, 0.10])
        elif tx_type == "Lumpsum":
            amount = np.random.choice([10000, 25000, 50000, 100000, 250000], p=[0.30, 0.30, 0.25, 0.12, 0.03])
        else:
            amount = np.random.choice([5000, 10000, 25000, 50000], p=[0.25, 0.30, 0.30, 0.15])
        tx_date = pd.Timestamp("2022-01-01") + timedelta(days=np.random.randint(0, 1600))
        tx_records.append({
            "tx_id": f"TX{tx_id:07d}",
            "investor_id": inv["investor_id"],
            "amfi_code": amfi,
            "date": tx_date.date(),
            "amount": amount,
            "transaction_type": tx_type,
            "state": inv["state"],
            "city": inv["city"],
            "tier": inv["tier"],
            "age": inv["age"],
            "gender": inv["gender"],
            "income_slab": inv["income_slab"],
            "kyc_status": inv["kyc_status"]
        })
        tx_id += 1

investor_transactions = pd.DataFrame(tx_records)
investor_transactions.to_csv(f"{RAW_DIR}/08_investor_transactions.csv", index=False)
print(f"08_investor_transactions.csv: {investor_transactions.shape}")

# ---------------------------------------------------------------------------
# 9. PORTFOLIO HOLDINGS
# ---------------------------------------------------------------------------
stocks = [
    ("RELIANCE", "Energy"), ("HDFCBANK", "Financials"), ("INFY", "IT"),
    ("ICICIBANK", "Financials"), ("TCS", "IT"), ("HINDUNILVR", "Consumer"),
    ("SBIN", "Financials"), ("BHARTIARTL", "Telecom"), ("ITC", "Consumer"),
    ("KOTAKBANK", "Financials"), ("LT", "Industrials"), ("AXISBANK", "Financials"),
    ("BAJFINANCE", "Financials"), ("ASIANPAINT", "Consumer"), ("MARUTI", "Auto"),
    ("TITAN", "Consumer"), ("SUNPHARMA", "Healthcare"), ("HCLTECH", "IT"),
    ("WIPRO", "IT"), ("ULTRACEMCO", "Materials")
]
portfolio_records = []
for _, row in fund_master.iterrows():
    if row["category"] in ["Large Cap", "Mid Cap", "Small Cap", "ELSS"]:
        n_holdings = np.random.randint(8, 15)
        weights = np.random.dirichlet(np.ones(n_holdings)) * 100
        selected = np.random.choice(len(stocks), n_holdings, replace=False)
        for i, idx in enumerate(selected):
            portfolio_records.append({
                "amfi_code": row["amfi_code"],
                "stock_symbol": stocks[idx][0],
                "sector": stocks[idx][1],
                "weight_pct": round(weights[i], 2),
                "as_of_date": "2025-12-31"
            })
portfolio_holdings = pd.DataFrame(portfolio_records)
portfolio_holdings.to_csv(f"{RAW_DIR}/09_portfolio_holdings.csv", index=False)
print(f"09_portfolio_holdings.csv: {portfolio_holdings.shape}")

# ---------------------------------------------------------------------------
# 10. BENCHMARK INDICES
# ---------------------------------------------------------------------------
indices = ["Nifty 50", "Nifty 100", "Nifty Midcap 150", "BSE SmallCap", "CRISIL Liquid", "CRISIL Gilt"]
base_values = {"Nifty 50": 17000, "Nifty 100": 18000, "Nifty Midcap 150": 12000,
               "BSE SmallCap": 25000, "CRISIL Liquid": 100, "CRISIL Gilt": 200}
vol_map = {"Nifty 50": 0.010, "Nifty 100": 0.011, "Nifty Midcap 150": 0.014,
           "BSE SmallCap": 0.018, "CRISIL Liquid": 0.0005, "CRISIL Gilt": 0.004}
bench_records = []
for idx_name in indices:
    base = base_values[idx_name]
    vol = vol_map[idx_name]
    rets = np.random.normal(0.0003, vol, len(business_days))
    vals = [base]
    for r in rets[1:]:
        vals.append(vals[-1] * (1 + r))
    bench_records.append(pd.DataFrame({
        "index_name": idx_name,
        "date": business_days,
        "close_value": vals
    }))
benchmark_indices = pd.concat(bench_records, ignore_index=True)
benchmark_indices["date"] = pd.to_datetime(benchmark_indices["date"]).dt.date
benchmark_indices.to_csv(f"{RAW_DIR}/10_benchmark_indices.csv", index=False)
print(f"10_benchmark_indices.csv: {benchmark_indices.shape}")

print("\nAll datasets generated successfully in data/raw/")
