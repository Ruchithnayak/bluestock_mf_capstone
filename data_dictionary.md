# Bluestock Mutual Fund Capstone
## Data Dictionary

---

# 1. dim_fund

| Column | Data Type | Description | Source |
|----------|-----------|-------------|--------|
| amfi_code | TEXT | Unique AMFI mutual fund code | 01_fund_master.csv |
| scheme_name | TEXT | Name of mutual fund scheme | 01_fund_master.csv |
| fund_house | TEXT | Asset Management Company | 01_fund_master.csv |
| category | TEXT | Mutual fund category | 01_fund_master.csv |
| expense_ratio_pct | REAL | Annual expense ratio (%) | 01_fund_master.csv |
| risk_grade | TEXT | Risk classification | 01_fund_master.csv |
| fund_manager | TEXT | Fund manager name | 01_fund_master.csv |
| launch_date | DATE | Fund launch date | 01_fund_master.csv |

---

# 2. dim_date

| Column | Data Type | Description |
|----------|-----------|-------------|
| date_id | INTEGER | YYYYMMDD surrogate key |
| date | DATE | Calendar date |
| year | INTEGER | Year |
| month | INTEGER | Month number |
| quarter | INTEGER | Quarter |
| month_name | TEXT | Month name |
| is_weekday | BOOLEAN | Weekday flag |

---

# 3. fact_nav

| Column | Data Type | Description |
|----------|-----------|-------------|
| amfi_code | TEXT | Fund identifier |
| date | DATE | NAV date |
| nav | REAL | Net Asset Value |
| daily_return_pct | REAL | Daily percentage return |

Source: 02_nav_history.csv

---

# 4. fact_transactions

| Column | Data Type | Description |
|----------|-----------|-------------|
| tx_id | TEXT | Transaction ID |
| investor_id | TEXT | Investor identifier |
| amfi_code | TEXT | Fund identifier |
| date | DATE | Transaction date |
| amount | REAL | Transaction amount |
| transaction_type | TEXT | SIP / Lumpsum / Redemption |
| state | TEXT | Investor state |
| city | TEXT | Investor city |
| tier | TEXT | City tier |
| age | INTEGER | Investor age |
| gender | TEXT | Gender |
| income_slab | TEXT | Income category |
| kyc_status | TEXT | KYC verification status |

Source: 08_investor_transactions.csv

---

# 5. fact_performance

| Column | Data Type | Description |
|----------|-----------|-------------|
| amfi_code | TEXT | Fund identifier |
| as_of_date | DATE | Performance calculation date |
| return_1yr_pct | REAL | One-year return (%) |
| return_3yr_pct | REAL | Three-year return (%) |
| return_5yr_pct | REAL | Five-year return (%) |
| cagr_pct | REAL | Compound Annual Growth Rate |
| sharpe_ratio | REAL | Risk-adjusted return |
| sortino_ratio | REAL | Downside risk ratio |
| alpha_pct | REAL | Alpha (%) |
| beta | REAL | Beta |
| max_drawdown_pct | REAL | Maximum drawdown |
| std_dev_pct | REAL | Standard deviation |

---

# 6. fact_portfolio

| Column | Data Type | Description |
|----------|-----------|-------------|
| amfi_code | TEXT | Fund identifier |
| stock_symbol | TEXT | Stock ticker |
| sector | TEXT | Business sector |
| weight_pct | REAL | Portfolio allocation (%) |
| as_of_date | DATE | Portfolio reporting date |

Source: 09_portfolio_holdings.csv

---

# 7. fact_aum

| Column | Data Type | Description |
|----------|-----------|-------------|
| fund_house | TEXT | Asset Management Company |
| quarter_end_date | DATE | Quarter end |
| aum_crore | REAL | Assets Under Management (₹ Crore) |
| num_schemes | INTEGER | Number of schemes |

Source: 03_aum_by_fund_house.csv

---

# 8. fact_sip_industry

| Column | Data Type | Description |
|----------|-----------|-------------|
| month | DATE | Month |
| sip_inflow_crore | REAL | SIP inflow (₹ Crore) |
| active_sip_accounts_lakh | REAL | Active SIP accounts |
| new_sip_registrations_lakh | REAL | New SIP registrations |
| sip_aum_crore | REAL | SIP Assets Under Management |

Source: 04_monthly_sip_inflows.csv

---

# 9. fact_category_inflows

| Column | Data Type | Description |
|----------|-----------|-------------|
| month | DATE | Month |
| category | TEXT | Fund category |
| net_inflow_crore | REAL | Net inflow (₹ Crore) |
| number_of_folios_lakh | REAL | Number of folios |

Source: 05_category_inflows.csv

---

# 10. fact_industry_folio

| Column | Data Type | Description |
|----------|-----------|-------------|
| as_of_date | DATE | Reporting date |
| equity_folios_crore | REAL | Equity folios |
| debt_folios_crore | REAL | Debt folios |
| hybrid_folios_crore | REAL | Hybrid folios |
| total_folios_crore | REAL | Total folios |

Source: 06_industry_folio_count.csv

---

# 11. fact_benchmark

| Column | Data Type | Description |
|----------|-----------|-------------|
| index_name | TEXT | Benchmark index |
| date | DATE | Market date |
| close_value | REAL | Closing index value |

Source: 10_benchmark_indices.csv