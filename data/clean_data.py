import os
import pandas as pd
from sqlalchemy import create_engine

# ===========================
# Create folders
# ===========================
os.makedirs("data/processed", exist_ok=True)

# ===========================
# 1. CLEAN nav_history.csv
# ===========================

print("Cleaning nav_history.csv...")

nav = pd.read_csv("data/raw/02_nav_history.csv")

nav["date"] = pd.to_datetime(nav["date"], errors="coerce")

nav = nav.sort_values(["amfi_code", "date"])

# Forward-fill missing NAV values for each fund
nav["nav"] = nav.groupby("amfi_code")["nav"].ffill()

# Remove duplicate rows
nav = nav.drop_duplicates()

# Keep only valid NAV values
nav = nav[nav["nav"] > 0]

nav.to_csv(
    "data/processed/nav_history_clean.csv",
    index=False
)

print(f"✓ NAV rows: {len(nav)}")


# ===========================
# 2. CLEAN investor_transactions.csv
# ===========================

print("Cleaning investor_transactions.csv...")

txn = pd.read_csv("data/raw/08_investor_transactions.csv")

# Convert dates
txn["transaction_date"] = pd.to_datetime(
    txn["transaction_date"],
    errors="coerce",
    dayfirst=True
)

# Standardize transaction type
txn["transaction_type"] = (
    txn["transaction_type"]
    .astype(str)
    .str.strip()
    .str.upper()
)

mapping = {
    "SIP": "SIP",
    "LUMPSUM": "Lumpsum",
    "LUMP SUM": "Lumpsum",
    "REDEMPTION": "Redemption"
}

txn["transaction_type"] = txn["transaction_type"].replace(mapping)

# Remove invalid amounts
txn = txn[txn["amount"] > 0]

# Validate KYC
valid_kyc = [
    "Verified",
    "Pending",
    "Rejected"
]

txn = txn[
    txn["kyc_status"].isin(valid_kyc)
]

txn.to_csv(
    "data/processed/investor_transactions_clean.csv",
    index=False
)

print(f"✓ Transaction rows: {len(txn)}")


# ===========================
# 3. CLEAN scheme_performance.csv
# ===========================

print("Cleaning scheme_performance.csv...")

perf = pd.read_csv("data/raw/07_scheme_performance.csv")

return_cols = [
    "return_1y",
    "return_3y",
    "return_5y"
]

for col in return_cols:
    perf[col] = pd.to_numeric(
        perf[col],
        errors="coerce"
    )

perf["expense_ratio"] = pd.to_numeric(
    perf["expense_ratio"],
    errors="coerce"
)

# Flag anomalies
anomalies = perf[
    (perf["expense_ratio"] < 0.1) |
    (perf["expense_ratio"] > 2.5)
]

if len(anomalies) > 0:
    anomalies.to_csv(
        "data/processed/expense_ratio_anomalies.csv",
        index=False
    )
    print(f"✓ Anomalies found: {len(anomalies)}")
else:
    print("✓ No expense ratio anomalies")

perf.to_csv(
    "data/processed/scheme_performance_clean.csv",
    index=False
)

print(f"✓ Performance rows: {len(perf)}")


# ===========================
# 4. LOAD INTO SQLITE
# ===========================

print("Creating SQLite database...")

engine = create_engine("sqlite:///bluestock_mf.db")

nav.to_sql(
    "fact_nav",
    engine,
    if_exists="replace",
    index=False
)

txn.to_sql(
    "fact_transactions",
    engine,
    if_exists="replace",
    index=False
)

perf.to_sql(
    "fact_performance",
    engine,
    if_exists="replace",
    index=False
)

print("✓ SQLite database created successfully.")


# ===========================
# 5. VERIFY ROW COUNTS
# ===========================

print("\n========== ROW COUNTS ==========")
print(f"NAV History       : {len(nav)}")
print(f"Transactions      : {len(txn)}")
print(f"Performance       : {len(perf)}")
print("================================")

print("\nTask completed successfully!")