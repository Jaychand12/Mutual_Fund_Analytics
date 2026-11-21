
import pandas as pd

INPUT_FILE = "data/processed/08_investor_transactions.csv"

print("=" * 65)
print("INVESTOR COHORT ANALYSIS")
print("=" * 65)

# Load transactions
df = pd.read_csv(INPUT_FILE)

df["transaction_date"] = pd.to_datetime(df["transaction_date"])
df["amount_inr"] = pd.to_numeric(df["amount_inr"], errors="coerce")

# Identify each investor's first transaction date
first_transactions = (
    df.groupby("investor_id")["transaction_date"]
    .min()
    .reset_index()
)

first_transactions["cohort_year"] = (
    first_transactions["transaction_date"].dt.year
)

# Attach cohort year to every transaction
df = df.merge(
    first_transactions[["investor_id", "cohort_year"]],
    on="investor_id",
    how="left"
)

# Consider SIP and Lumpsum as investments
investments = df[
    df["transaction_type"].isin(["SIP", "Lumpsum"])
].copy()

# Average SIP amount for each cohort
sip_transactions = investments[
    investments["transaction_type"] == "SIP"
]

avg_sip = (
    sip_transactions.groupby("cohort_year")["amount_inr"]
    .mean()
    .reset_index(name="avg_sip_amount_inr")
)

# Total invested amount for each cohort
total_invested = (
    investments.groupby("cohort_year")["amount_inr"]
    .sum()
    .reset_index(name="total_invested_inr")
)

# Count unique investors in each cohort
investor_counts = (
    first_transactions.groupby("cohort_year")["investor_id"]
    .nunique()
    .reset_index(name="investor_count")
)

# Find most preferred fund by investment transaction count
fund_preference = (
    investments.groupby(["cohort_year", "amfi_code"])
    .size()
    .reset_index(name="transaction_count")
)

top_funds = (
    fund_preference.sort_values(
        ["cohort_year", "transaction_count"],
        ascending=[True, False]
    )
    .drop_duplicates("cohort_year")
    .rename(columns={
        "amfi_code": "top_preferred_amfi_code",
        "transaction_count": "top_fund_transaction_count"
    })
)

# Combine cohort results
cohort_report = (
    investor_counts
    .merge(avg_sip, on="cohort_year", how="left")
    .merge(total_invested, on="cohort_year", how="left")
    .merge(top_funds, on="cohort_year", how="left")
)

# Add preferred fund names
fund_master = pd.read_csv(
    "data/processed/01_fund_master.csv"
)

cohort_report = cohort_report.merge(
    fund_master[["amfi_code", "scheme_name"]],
    left_on="top_preferred_amfi_code",
    right_on="amfi_code",
    how="left"
)

cohort_report = cohort_report.drop(columns=["amfi_code"])

# Display report
print("\nCOHORT ANALYSIS RESULTS")
print(cohort_report.to_string(index=False))

# Save report
cohort_report.to_csv(
    "investor_cohort_report.csv",
    index=False
)

print("\nReport saved: investor_cohort_report.csv")
print("\nTASK 3 COMPLETED")
