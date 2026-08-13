# Bluestock MF Power BI Dashboard — D5 Build Map

## Data
Import the SQLite tables or cleaned CSVs:
dim_fund, fact_nav, fact_performance, fact_aum, fact_sip_industry,
fact_industry_folio, fact_benchmark, fact_category_inflows,
fact_transactions, fact_portfolio.

## Relationships
- dim_fund[amfi_code] 1 -> * fact_nav[amfi_code]
- dim_fund[amfi_code] 1 -> * fact_performance[amfi_code]
- dim_fund[amfi_code] 1 -> * fact_aum[amfi_code]
- dim_fund[amfi_code] 1 -> * fact_portfolio[amfi_code]
- Date fields should use a dedicated Date table where possible.

## Page 1 — Industry Overview
Cards:
Total AUM (₹ Cr), SIP Inflows (₹ Cr), Total Folios (Cr), Scheme Count
Line: fact_aum[quarter_end_date] vs Total AUM
Bar: fact_aum[fund_house] vs Total AUM
Slicers: fund_house, quarter_end_date

## Page 2 — Fund Performance
Scatter:
X = return_1yr_pct
Y = std_dev_pct
Size = AUM
Legend = risk_grade
Table:
scheme_name, fund_house, category, return_1yr_pct, std_dev_pct,
sharpe_ratio, max_drawdown_pct, risk_grade
Line:
fact_nav[date] + NAV, filtered by selected fund
Benchmark line from fact_benchmark
Slicers: fund_house, category, plan_type
Drill-through: create NAV Detail page using dim_fund[scheme_name].

## Page 3 — Investor Analytics
Bar: state vs transaction amount
Donut: transaction_type vs amount
Bar: age_group vs average SIP amount
Line: date/month vs transaction count
Slicers: state, age_group, city_tier

## Page 4 — SIP & Market Trends
Combo chart:
SIP inflow as columns + Nifty 50 close as line
Heatmap/matrix:
category x month, values net_inflow_crore
Bar: Top 5 categories by net inflow
Slicers: category, month

## Branding
Import dashboard/Bluestock_Theme.json.
Use white/light background, blue headings, consistent KPI cards.
Add Bluestock logo to each page if available.

## Export
After validation in Power BI Desktop:
File > Export > PDF
For PNGs use page screenshots/export workflow.
Save:
dashboard/bluestock_mf_dashboard.pbix
reports/Dashboard.pdf
reports/page1_industry_overview.png
reports/page2_fund_performance.png
reports/page3_investor_analytics.png
reports/page4_sip_market_trends.png
