from pathlib import Path

Path("data/processed").mkdir(parents=True, exist_ok=True)
import pandas as pd
from pathlib import Path

# Load datasets
fund_path = Path("data/raw/01_fund_master.csv")
nav_path = Path("data/raw/02_nav_history.csv")

fund = pd.read_csv(fund_path)
nav = pd.read_csv(nav_path)

print("=" * 60)
print("AMFI SCHEME CODE VALIDATION")
print("=" * 60)

# Identify scheme code columns
print("\nFund Master columns:")
print(fund.columns.tolist())

print("\nNAV History columns:")
print(nav.columns.tolist())

# Adjust these names if your CSV uses different column names
fund_code_col = "amfi_code"
nav_code_col = "amfi_code"
if fund_code_col not in fund.columns:
    raise KeyError(f"{fund_code_col} not found in fund master")

if nav_code_col not in nav.columns:
    raise KeyError(f"{nav_code_col} not found in NAV history")

# Normalize scheme codes
fund_codes = set(
    fund[fund_code_col].dropna().astype(str).str.strip()
)

nav_codes = set(
    nav[nav_code_col].dropna().astype(str).str.strip()
)

# Compare scheme codes
matched = fund_codes.intersection(nav_codes)
missing = fund_codes.difference(nav_codes)
extra = nav_codes.difference(fund_codes)

print("\nTOTAL FUND MASTER CODES:", len(fund_codes))
print("TOTAL NAV HISTORY CODES:", len(nav_codes))
print("MATCHED CODES:", len(matched))
print("MISSING IN NAV HISTORY:", len(missing))
print("EXTRA IN NAV HISTORY:", len(extra))

print("\nMissing scheme codes:")
print(sorted(missing)[:50])

print("\nExtra scheme codes:")
print(sorted(extra)[:50])

# Save validation report
report = pd.DataFrame({
    "validation": [
        "Fund master codes",
        "NAV history codes",
        "Matched codes",
        "Missing in NAV",
        "Extra in NAV"
    ],
    "count": [
        len(fund_codes),
        len(nav_codes),
        len(matched),
        len(missing),
        len(extra)
    ]
})

report.to_csv(
    "data/processed/scheme_code_validation.csv",
    index=False
)

print("\nValidation report saved successfully!")
