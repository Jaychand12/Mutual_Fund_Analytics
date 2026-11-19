
import pandas as pd
from pathlib import Path

RAW_DIR = Path("data/raw")
REPORT_DIR = Path("reports")

datasets = [
    "01_fund_master.csv",
    "02_nav_history.csv",
    "03_aum_by_fund_house.csv",
    "04_monthly_sip_inflows.csv",
    "05_category_inflows.csv",
    "06_industry_folio_count.csv",
    "07_scheme_performance.csv",
    "08_investor_transactions.csv",
    "09_portfolio_holdings.csv",
    "10_benchmark_indices.csv",
]

report = []

print("=" * 65)
print("BLUESTOCK - DAY 1 DATA QUALITY REPORT")
print("=" * 65)

for filename in datasets:
    filepath = RAW_DIR / filename

    print(f"\nProcessing: {filename}")

    try:
        df = pd.read_csv(filepath)

        missing_cells = int(df.isnull().sum().sum())
        duplicate_rows = int(df.duplicated().sum())

        report.append({
            "dataset": filename,
            "rows": len(df),
            "columns": len(df.columns),
            "missing_cells": missing_cells,
            "duplicate_rows": duplicate_rows,
            "memory_usage_kb": round(
                df.memory_usage(deep=True).sum() / 1024, 2
            ),
            "status": "SUCCESS"
        })

        print("Shape:", df.shape)
        print("Missing cells:", missing_cells)
        print("Duplicate rows:", duplicate_rows)
        print("Column names:", list(df.columns))

    except Exception as e:
        print("ERROR:", e)

        report.append({
            "dataset": filename,
            "rows": None,
            "columns": None,
            "missing_cells": None,
            "duplicate_rows": None,
            "memory_usage_kb": None,
            "status": f"ERROR: {e}"
        })

report_df = pd.DataFrame(report)

REPORT_DIR.mkdir(parents=True, exist_ok=True)

output_file = REPORT_DIR / "data_quality_summary.csv"
report_df.to_csv(output_file, index=False)

print("\n" + "=" * 65)
print("DATA QUALITY SUMMARY")
print("=" * 65)
print(report_df.to_string(index=False))

print("\nReport saved to:", output_file)
