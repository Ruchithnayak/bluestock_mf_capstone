# Bluestock Fintech

## Mutual Fund Analytics Platform
### End-to-End Data Engineering, ETL Pipeline & Interactive Dashboard

---

**Company:** Bluestock Fintech Pvt. Ltd.  
**Domain:** Mutual Fund / Fintech  
**Project Type:** Individual Capstone  
**Duration:** 7 Working Days  
**Prepared By:** Intern / Data Analyst — Bluestock Fintech  
**Date:** June 2026

---

## 1. Executive Summary

This capstone project delivers a complete Mutual Fund Analytics Platform that consolidates publicly available mutual fund data from AMFI India, mfapi.in, NSE/BSE into a unified analytics environment. The solution includes a Python-based ETL pipeline, a normalized SQLite star schema, comprehensive risk-return analytics, and an interactive Streamlit dashboard.

Key highlights:
- **40 real mutual fund schemes** tracked across 10 AMCs
- **46,000+ NAV records** spanning 4.5 years
- **35,000+ investor transactions** for behavioral analysis
- **Risk metrics:** Sharpe, Sortino, Alpha, Beta, Max Drawdown, Standard Deviation
- **Benchmark comparison** against Nifty 50, Nifty 100, Nifty Midcap 150, BSE SmallCap

---

## 2. Business Context

The Indian mutual fund industry has grown rapidly. As of December 2025:
- Industry AUM: over Rs. 81 lakh crore
- Total schemes: 1,908
- Investor folios: 26.12 crore
- Monthly SIP inflows: Rs. 31,002 crore (all-time high)

Despite this growth, investors face challenges due to fragmented data, lack of unified analytics, and complex financial metrics. This platform addresses these gaps.

---

## 3. Problem Statement

| Problem | Solution |
|---------|----------|
| Data fragmentation across AMFI sources | Unified ETL pipeline into SQLite database |
| Difficulty comparing risk-adjusted returns | Computed Sharpe, Sortino, Alpha, Beta metrics |
| No benchmark tracking | Rolling alpha and benchmark comparison |
| Limited investor behavior insights | Demographic and geographic segmentation |
| Static monthly reports | Interactive, self-service Streamlit dashboard |

---

## 4. Data Sources & Datasets

| Source | Data Type | Frequency |
|--------|-----------|-----------|
| AMFI India | NAV, AUM, Folio, SIP | Daily / Monthly |
| mfapi.in | Historical NAV (JSON) | Daily |
| NSE/BSE | Benchmark index prices | Daily |
| AMFI Monthly Notes | Industry SIP & flow data | Monthly |

### Dataset Inventory

1. **fund_master.csv** — 40 schemes
2. **nav_history.csv** — 46,000 rows
3. **aum_by_fund_house.csv** — quarterly AUM
4. **monthly_sip_inflows.csv** — 48 months
5. **category_inflows.csv** — category-wise inflows
6. **industry_folio_count.csv** — folio milestones
7. **scheme_performance.csv** — risk-return metrics
8. **investor_transactions.csv** — 35,000+ transactions
9. **portfolio_holdings.csv** — equity holdings
10. **benchmark_indices.csv** — benchmark values

---

## 5. System Architecture

The platform follows a classic data engineering architecture:

```
Data Sources → ETL Pipeline → SQLite Database → Analytics → Dashboard
```

### Layers

1. **Extract:** CSV files, AMFI TXT, mfapi.in JSON, NSE/BSE bhavcopy
2. **Transform:** Pandas cleaning, forward-fill missing NAVs, compute returns
3. **Load:** SQLite star schema with indexes
4. **Analyze:** Risk metrics, EDA, benchmark comparison
5. **Visualize:** Streamlit dashboard with Plotly charts

### Database Schema

Star schema with dimension and fact tables:
- `dim_fund`, `dim_date`
- `fact_nav`, `fact_transactions`, `fact_performance`
- `fact_portfolio`, `fact_aum`, `fact_sip_industry`
- `fact_category_inflows`, `fact_industry_folio`, `fact_benchmark`

---

## 6. 7-Day Task Breakdown

| Day | Focus | Deliverable |
|-----|-------|-------------|
| 1 | Project setup + data ingestion | Raw datasets, Git repo |
| 2 | Data cleaning + SQL schema | SQLite database |
| 3 | EDA | Jupyter notebook + charts |
| 4 | Fund performance analytics | Risk metrics table |
| 5 | Dashboard development | Streamlit dashboard |
| 6 | Advanced analytics + risk metrics | Alpha/beta report |
| 7 | Final report + deployment | PDF report + GitHub |

---

## 7. Key Findings

### Performance Metrics
- Top performing category by Sharpe ratio: Mid Cap and ELSS funds
- Liquid funds show lowest volatility as expected
- Small cap funds exhibit highest standard deviation

### Investor Behavior
- SIP transactions dominate (~70% of all transactions)
- T30 cities contribute higher transaction amounts than B30
- Maharashtra, Karnataka, and Tamil Nadu lead in transaction volume

### Industry Trends
- SIP inflows show consistent upward trend
- AUM growth is strongest for top 3 AMCs: SBI, ICICI Prudential, HDFC
- Equity categories attract highest net inflows

---

## 8. Risk Metrics Methodology

- **CAGR:** Annualized return over the full NAV history
- **Sharpe Ratio:** (CAGR - risk-free rate) / standard deviation
- **Sortino Ratio:** (CAGR - risk-free rate) / downside deviation
- **Alpha:** Excess return relative to Nifty 50 benchmark
- **Beta:** Covariance of fund returns with Nifty 50 / variance of Nifty 50
- **Max Drawdown:** Largest peak-to-trough decline in NAV

Risk-free rate assumed: 6% per annum.

---

## 9. Dashboard Overview

The Streamlit dashboard includes four report pages:
1. **Fund Performance** — risk-return scatter, metrics table
2. **NAV Trends** — NAV movement, benchmark comparison
3. **Investor Insights** — transaction types, geography, demographics
4. **Industry Trends** — AUM growth, SIP inflows, category inflows

Filters: Fund House, Category, Date Range

---

## 10. Technical Stack

- Python 3.10+
- Pandas, NumPy
- SQLite, SQLAlchemy
- Matplotlib, Seaborn, Plotly
- Streamlit
- Jupyter Notebooks

---

## 11. Deliverables

- Python ETL pipeline (`src/etl_pipeline.py`)
- SQLite database (`bluestock_mf.db`)
- 10 generated datasets (`data/raw/`)
- Analytics script with charts (`src/analytics.py`)
- Streamlit dashboard (`dashboard/app.py`)
- EDA notebook (`notebooks/01_eda.ipynb`)
- SQL schema documentation (`sql/schema.sql`)
- This PDF report

---

## 12. Conclusion

This project demonstrates a complete data engineering and analytics workflow for the Indian mutual fund industry. The platform can be extended to production by replacing SQLite with PostgreSQL, scheduling daily ETL jobs, and integrating live AMFI/mfapi.in APIs.

---

## Disclaimer

All data is sourced from publicly available information published by AMFI India, NSE, BSE, and open APIs. This project is for educational purposes only and does not constitute financial advice. Mutual Fund investments are subject to market risks.
