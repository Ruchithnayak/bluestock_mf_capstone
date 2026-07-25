# Bluestock Fintech - Mutual Fund Analytics Capstone

End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard for Indian Mutual Fund Analytics.

## Project Overview

This capstone project builds a full-stack Mutual Fund Analytics Platform that:
- Ingests publicly available data from AMFI India, mfapi.in, NSE/BSE
- Transforms data through a robust ETL pipeline
- Stores data in a normalized SQLite star schema
- Computes risk-adjusted return metrics (Sharpe, Sortino, Alpha, Beta, Max Drawdown)
- Benchmarks fund performance against Nifty 50, Nifty 100, Nifty Midcap 150, BSE SmallCap
- Provides an interactive Streamlit dashboard for fund selection and investor insights

## Repository Structure

```
bluestock_mf_capstone/
├── data/
│   ├── raw/                    # 10 generated CSV datasets
│   └── processed/              # Cleaned CSVs from ETL
├── sql/
│   └── schema.sql              # Star schema DDL
├── src/
│   ├── generate_datasets.py    # Generate all 10 datasets
│   ├── etl_pipeline.py         # Extract, Transform, Load to SQLite
│   └── analytics.py            # EDA, risk metrics, chart generation
├── dashboard/
│   └── app.py                  # Streamlit interactive dashboard
├── reports/
│   ├── figures/                # Generated charts
│   └── Bluestock_MF_Capstone_Report.pdf
├── notebooks/                  # Jupyter notebooks (optional)
├── bluestock_mf.db             # SQLite database
├── requirements.txt
└── README.md
```

## Datasets (10)

1. `01_fund_master.csv` - 40 mutual fund schemes
2. `02_nav_history.csv` - ~46,000 daily NAV records (Jan 2022 - May 2026)
3. `03_aum_by_fund_house.csv` - Quarterly AUM for 10 fund houses
4. `04_monthly_sip_inflows.csv` - 48 months of SIP data
5. `05_category_inflows.csv` - Net inflows by category (FY 2024-25)
6. `06_industry_folio_count.csv` - Industry folio milestones
7. `07_scheme_performance.csv` - Risk-return metrics per scheme
8. `08_investor_transactions.csv` - ~35,000 simulated transactions
9. `09_portfolio_holdings.csv` - Top equity holdings
10. `10_benchmark_indices.csv` - Daily benchmark index values

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Generate Datasets

```bash
python src/generate_datasets.py
```

### 3. Run ETL Pipeline

```bash
python src/etl_pipeline.py
```

This creates `bluestock_mf.db` with the star schema and computed risk metrics.

### 4. Run Analytics & Generate Charts

```bash
python src/analytics.py
```

Charts are saved to `reports/figures/`.

### 5. Launch Dashboard

```bash
cd dashboard
streamlit run app.py
```

## Database Schema

Star schema with the following tables:
- `dim_fund` - Fund master data
- `dim_date` - Date dimension
- `fact_nav` - Daily NAV and returns
- `fact_transactions` - Investor transactions
- `fact_performance` - Computed risk-return metrics
- `fact_portfolio` - Equity holdings
- `fact_aum` - AUM by fund house
- `fact_sip_industry` - Monthly SIP inflows
- `fact_category_inflows` - Category-wise inflows
- `fact_industry_folio` - Industry folio counts
- `fact_benchmark` - Benchmark index values

## Risk Metrics Computed

- **CAGR**: Compound Annual Growth Rate
- **Sharpe Ratio**: Risk-adjusted return
- **Sortino Ratio**: Downside risk-adjusted return
- **Alpha**: Excess return vs benchmark
- **Beta**: Sensitivity to market movements
- **Max Drawdown**: Largest peak-to-trough decline
- **Standard Deviation**: Volatility measure

## Technologies

- Python 3.10+
- Pandas, NumPy
- SQLite, SQLAlchemy
- Matplotlib, Seaborn, Plotly
- Streamlit
- Jupyter Notebooks

## Data Sources

- AMFI India (www.amfiindia.com)
- mfapi.in API
- NSE India / BSE India
- AMFI Monthly Notes

## Disclaimer

All data is sourced from publicly available information. This project is for educational purposes only and does not constitute financial advice. Mutual Fund investments are subject to market risks.

## Author

Prepared as part of Bluestock Fintech Data Analyst Internship Capstone.
