CREATE TABLE IF NOT EXISTS fact_nav (
    nav_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    date DATE NOT NULL,
    nav REAL NOT NULL,
    daily_return_pct REAL,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
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
    portfolio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    amfi_code TEXT NOT NULL,
    stock_symbol TEXT,
    sector TEXT,
    weight_pct REAL,
    as_of_date DATE,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

CREATE TABLE IF NOT EXISTS fact_aum (
    aum_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT,
    quarter_end_date DATE,
    aum_crore REAL,
    num_schemes INTEGER
);

CREATE TABLE IF NOT EXISTS fact_sip_industry (
    sip_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    sip_inflow_crore REAL,
    active_sip_accounts_lakh REAL,
    new_sip_registrations_lakh REAL,
    sip_aum_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_category_inflows (
    inflow_id INTEGER PRIMARY KEY AUTOINCREMENT,
    month DATE,
    category TEXT,
    net_inflow_crore REAL,
    number_of_folios_lakh REAL
);

CREATE TABLE IF NOT EXISTS fact_industry_folio (
    folio_id INTEGER PRIMARY KEY AUTOINCREMENT,
    as_of_date DATE,
    equity_folios_crore REAL,
    debt_folios_crore REAL,
    hybrid_folios_crore REAL,
    total_folios_crore REAL
);

CREATE TABLE IF NOT EXISTS fact_benchmark (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,
    index_name TEXT,
    date DATE,
    close_value REAL
);