
import pandas as pd
from pathlib import Path


# --------------------------------------------------
# 1. FOLDER CONFIGURATION
# --------------------------------------------------

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)


# --------------------------------------------------
# 2. DATASET CONFIGURATION
# --------------------------------------------------

DATASETS = {
    "01_fund_master.csv": [],
    "02_nav_history.csv": ["date"],
    "03_aum_by_fund_house.csv": ["date"],
    "04_monthly_sip_inflows.csv": ["month"],
    "05_category_inflows.csv": ["month"],
    "06_industry_folio_count.csv": ["month"],
    "07_scheme_performance.csv": [],
    "08_investor_transactions.csv": ["transaction_date"],
    "09_portfolio_holdings.csv": ["portfolio_date"],
    "10_benchmark_indices.csv": ["date"]
}


# --------------------------------------------------
# 3. HELPER FUNCTION
# --------------------------------------------------

def clean_general_data(df):
    """Remove unnecessary spaces from text columns."""

    for column in df.select_dtypes(include=["object"]).columns:
        df[column] = df[column].str.strip()

    return df


# --------------------------------------------------
# 4. CLEAN NAV HISTORY
# --------------------------------------------------

def clean_nav_history(df):

    df["date"] = pd.to_datetime(
        df["date"], errors="coerce"
    )

    df["nav"] = pd.to_numeric(
        df["nav"], errors="coerce"
    )

    df = df.sort_values(
        by=["amfi_code", "date"]
    )

    # Remove duplicate scheme/date combinations
    df = df.drop_duplicates(
        subset=["amfi_code", "date"]
    )

    # Validate NAV values
    invalid_nav = df["nav"].isna() | (df["nav"] <= 0)

    print("Invalid NAV records:", invalid_nav.sum())

    # Do not forward-fill weekends or holidays:
    # these are dates when the market may be closed.

    return df


# --------------------------------------------------
# 5. CLEAN INVESTOR TRANSACTIONS
# --------------------------------------------------

def clean_transactions(df):

    df["transaction_date"] = pd.to_datetime(
        df["transaction_date"], errors="coerce"
    )

    df["amount_inr"] = pd.to_numeric(
        df["amount_inr"], errors="coerce"
    )

    # Standardise transaction types
    df["transaction_type"] = (
        df["transaction_type"]
        .str.strip()
        .str.lower()
        .map({
            "sip": "SIP",
            "lumpsum": "Lumpsum",
            "redemption": "Redemption"
        })
    )

    # Standardise KYC status
    df["kyc_status"] = (
        df["kyc_status"]
        .str.strip()
        .str.lower()
        .map({
            "verified": "Verified",
            "pending": "Pending"
        })
    )

    valid_types = ["SIP", "Lumpsum", "Redemption"]
    valid_kyc = ["Verified", "Pending"]

    invalid_types = ~df["transaction_type"].isin(valid_types)
    invalid_kyc = ~df["kyc_status"].isin(valid_kyc)
    invalid_amounts = df["amount_inr"].isna() | (
        df["amount_inr"] <= 0
    )

    print("Invalid transaction types:", invalid_types.sum())
    print("Invalid KYC statuses:", invalid_kyc.sum())
    print("Invalid transaction amounts:", invalid_amounts.sum())

    return df


# --------------------------------------------------
# 6. CLEAN SCHEME PERFORMANCE
# --------------------------------------------------

def clean_scheme_performance(df):

    numeric_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating"
    ]

    for column in numeric_columns:
        df[column] = pd.to_numeric(
            df[column], errors="coerce"
        )

    return_columns = [
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct"
    ]

    invalid_returns = df[return_columns].isna().sum().sum()

    # Check expense ratio range: 0.1% to 2.5%
    invalid_expense = (
        df["expense_ratio_pct"].isna()
        | (df["expense_ratio_pct"] < 0.1)
        | (df["expense_ratio_pct"] > 2.5)
    )

    print("Invalid return values:", invalid_returns)
    print("Invalid expense ratios:", invalid_expense.sum())

    # Flag unusually high or low returns for review.
    # These are flags, not automatic deletions.
    for column in return_columns:
        anomalies = (
            (df[column] < -100)
            | (df[column] > 200)
        )

        print(
            f"Anomalies in {column}:",
            anomalies.sum()
        )

    return df


# --------------------------------------------------
# 7. PROCESS ALL TEN DATASETS
# --------------------------------------------------

def main():

    print("=" * 65)
    print("BLUESTOCK MUTUAL FUND DATA CLEANING")
    print("=" * 65)

    total_before = 0
    total_after = 0

    for filename, date_columns in DATASETS.items():

        input_path = RAW_DIR / filename
        output_path = PROCESSED_DIR / filename

        print("\n" + "-" * 65)
        print("Processing:", filename)

        if not input_path.exists():
            print("ERROR: File not found:", input_path)
            continue

        # Read original CSV
        df = pd.read_csv(input_path)

        original_rows = len(df)
        total_before += original_rows

        # General text cleaning
        df = clean_general_data(df)

        # Convert date columns
        for column in date_columns:
            df[column] = pd.to_datetime(
                df[column], errors="coerce"
            )

        # Dataset-specific cleaning
        if filename == "02_nav_history.csv":
            df = clean_nav_history(df)

        elif filename == "08_investor_transactions.csv":
            df = clean_transactions(df)

        elif filename == "07_scheme_performance.csv":
            df = clean_scheme_performance(df)

        # Remove exact duplicate rows
        duplicates = df.duplicated().sum()
        df = df.drop_duplicates()

        # Sort NAV records
        if filename == "02_nav_history.csv":
            df = df.sort_values(
                by=["amfi_code", "date"]
            )

        # Save dates in standard format
        for column in date_columns:
            df[column] = df[column].dt.strftime("%Y-%m-%d")

        # Save cleaned CSV
        df.to_csv(output_path, index=False)

        cleaned_rows = len(df)
        total_after += cleaned_rows

        print("Original rows:", original_rows)
        print("Duplicates removed:", duplicates)
        print("Cleaned rows:", cleaned_rows)
        print("Saved to:", output_path)

    # --------------------------------------------------
    # 8. FINAL SUMMARY
    # --------------------------------------------------

    print("\n" + "=" * 65)
    print("DATA CLEANING SUMMARY")
    print("=" * 65)

    print("Total original rows:", total_before)
    print("Total cleaned rows:", total_after)
    print("Total rows removed:", total_before - total_after)

    print("\nCleaned datasets are available in:", PROCESSED_DIR)

    print("\nDATA CLEANING COMPLETED")


# --------------------------------------------------
# 9. RUN PROGRAM
# --------------------------------------------------

if __name__ == "__main__":
    main()
