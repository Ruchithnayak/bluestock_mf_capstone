-- =====================================================
-- Bluestock MF Capstone
-- 10 Analytical SQL Queries
-- =====================================================

---------------------------------------------------------
-- 1. Top 5 Fund Houses by AUM
---------------------------------------------------------
SELECT
    fund_house,
    SUM(aum_crore) AS total_aum
FROM fact_aum
GROUP BY fund_house
ORDER BY total_aum DESC
LIMIT 5;

---------------------------------------------------------
-- 2. Average Monthly NAV
---------------------------------------------------------
SELECT
    strftime('%Y-%m', date) AS month,
    ROUND(AVG(nav),2) AS average_nav
FROM fact_nav
GROUP BY month
ORDER BY month;

---------------------------------------------------------
-- 3. Year-wise SIP Inflow
---------------------------------------------------------
SELECT
    strftime('%Y', month) AS year,
    SUM(sip_inflow_crore) AS total_sip_inflow
FROM fact_sip_industry
GROUP BY year
ORDER BY year;

---------------------------------------------------------
-- 4. Transactions by State
---------------------------------------------------------
SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount),2) AS total_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;

---------------------------------------------------------
-- 5. Funds with Expense Ratio below 1%
---------------------------------------------------------
SELECT
    scheme_name,
    fund_house,
    category,
    expense_ratio_pct
FROM dim_fund
WHERE expense_ratio_pct < 1
ORDER BY expense_ratio_pct;

---------------------------------------------------------
-- 6. Top 10 Funds by CAGR
---------------------------------------------------------
SELECT
    amfi_code,
    cagr_pct
FROM fact_performance
ORDER BY cagr_pct DESC
LIMIT 10;

---------------------------------------------------------
-- 7. Highest Sharpe Ratio Funds
---------------------------------------------------------
SELECT
    amfi_code,
    sharpe_ratio
FROM fact_performance
ORDER BY sharpe_ratio DESC
LIMIT 10;

---------------------------------------------------------
-- 8. Transaction Type Distribution
---------------------------------------------------------
SELECT
    transaction_type,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount),2) AS total_amount
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_transactions DESC;

---------------------------------------------------------
-- 9. Top 10 Portfolio Holdings
---------------------------------------------------------
SELECT
    stock_symbol,
    sector,
    ROUND(AVG(weight_pct),2) AS avg_weight
FROM fact_portfolio
GROUP BY stock_symbol, sector
ORDER BY avg_weight DESC
LIMIT 10;

---------------------------------------------------------
-- 10. Benchmark Performance Summary
---------------------------------------------------------
SELECT
    index_name,
    MIN(close_value) AS lowest_value,
    MAX(close_value) AS highest_value,
    ROUND(AVG(close_value),2) AS average_close
FROM fact_benchmark
GROUP BY index_name;