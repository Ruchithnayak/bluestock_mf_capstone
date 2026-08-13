# Bluestock MF Power BI Data Model

## Dimension Tables

### dim_fund
Primary key:
- amfi_code

### dim_date
Primary key:
- date

---

## Fact Tables

### fact_aum
Relationships:
- amfi_code -> dim_fund[amfi_code]
- date -> dim_date[date]

### fact_nav
Relationships:
- amfi_code -> dim_fund[amfi_code]
- date -> dim_date[date]

### fact_performance
Relationships:
- amfi_code -> dim_fund[amfi_code]

### fact_transactions
Relationships:
- amfi_code -> dim_fund[amfi_code]
- date -> dim_date[date]

### fact_sip_industry
Relationships:
- date -> dim_date[date]

### fact_benchmark
Relationships:
- date -> dim_date[date]

### fact_portfolio
Relationships:
- amfi_code -> dim_fund[amfi_code]

### fact_category_inflows
Relationships:
- date -> dim_date[date]

### fact_industry_folio
Relationships:
- date -> dim_date[date]

---

## Recommended Relationship Direction

Use:

One-to-many:

dim_fund
    |
    +---- fact_aum
    +---- fact_nav
    +---- fact_performance
    +---- fact_transactions
    +---- fact_portfolio

dim_date
    |
    +---- fact_aum
    +---- fact_nav
    +---- fact_transactions
    +---- fact_sip_industry
    +---- fact_benchmark
    +---- fact_category_inflows
    +---- fact_industry_folio