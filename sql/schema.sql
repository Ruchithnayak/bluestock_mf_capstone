-- Bluestock MF Capstone - Star Schema DDL
-- Run after ETL to verify / document schema structure

CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code TEXT PRIMARY KEY,
    scheme_name TEXT,
    fund_house TEXT,
    category TEXT,
    expense_ratio_pct REAL,
    risk_grade TEXT,
    fund_manager TEXT,
    launch_date DATE
);

CREATE TABLE IF NOT EXISTS dim_date (
    date_id INTEGER PRIMARY KEY,
    date DATE,
    year INTEGER,
    month INTEGER,
    quarter INTEGER,
    month_name TEXT,
    is_weekday BOOLEAN
);

CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code TEXT,
    date DATE,
    nav REAL,
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_transactions (
    tx_id TEXT PRIMARY KEY,
    investor_id TEXT,
    amfi_code TEXT,
    date DATE,
    amount REAL,
    transaction_type TEXT,
    state TEXT,
    city TEXT,
    tier TEXT,
    age INTEGER,
    gender TEXT,
    income_slab TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code TEXT,
    as_of_date DATE,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    cagr_pct REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    alpha_pct REAL,
    beta REAL,
    max_drawdown_pct REAL,
    std_dev_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_portfolio (
    amfi_code TEXT,
    stock_symbol TEXT,
    sector TEXT,
    weight_pct REAL,
    as_of_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house TEXT,
    quarter_end_date DATE,
    aum_crore REAL,
    num_schemes INTEGER
);

CREATE TABLE IF NOT EXISTS fact_sip_industry (
    month DATE,
    sip_inflow_crore REAL,
    active_sip_accounts_lakh REAL,
    new_sip_registrations_lakh REAL,
    sip_aum_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    month DATE,
    category TEXT,
    net_inflow_crore REAL,
    number_of_folios_lakh REAL
);

CREATE TABLE IF NOT EXISTS fact_industry_folio (
    as_of_date DATE,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    total_folios_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_benchmark (
    index_name TEXT,
    date DATE,
    close_value REAL
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_nav ON fact_nav(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_tx ON fact_transactions(amfi_code, date);
CREATE INDEX IF NOT EXISTS idx_perf ON fact_performance(amfi_code);
CREATE INDEX IF NOT EXISTS idx_bench ON fact_benchmark(index_name, date);
