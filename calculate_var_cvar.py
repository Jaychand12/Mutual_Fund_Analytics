
import pandas as pd
from pathlib import Path

# File paths
NAV_FILE = "data/processed/02_nav_history.csv"
PERF_FILE = "data/processed/07_scheme_performance.csv"
OUTPUT_FILE = "var_cvar_report.csv"

print("=" * 65)
print("HISTORICAL VaR AND CVaR ANALYSIS")
print("=" * 65)

# Load datasets
nav = pd.read_csv(NAV_FILE)
performance = pd.read_csv(PERF_FILE)

# Convert dates and NAV values
nav["date"] = pd.to_datetime(nav["date"])
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

# Sort data by scheme and date
nav = nav.sort_values(["amfi_code", "date"])

# Calculate daily percentage returns separately for each scheme
nav["daily_return_pct"] = (
    nav.groupby("amfi_code")["nav"].pct_change() * 100
)

# Calculate VaR and CVaR for every scheme
results = []

for code, group in nav.groupby("amfi_code"):

    returns = group["daily_return_pct"].dropna()

    if returns.empty:
        continue

    # Historical VaR: 5th percentile
    var_95 = returns.quantile(0.05)

    # Historical CVaR: average returns at or below VaR
    tail_returns = returns[returns <= var_95]
    cvar_95 = tail_returns.mean()

    results.append({
        "amfi_code": code,
        "observations": len(returns),
        "VaR_95_pct": round(var_95, 4),
        "CVaR_95_pct": round(cvar_95, 4)
    })

# Convert results into DataFrame
var_report = pd.DataFrame(results)

# Add fund information
fund_columns = [
    "amfi_code",
    "scheme_name",
    "fund_house",
    "risk_grade"
]

var_report = var_report.merge(
    performance[fund_columns],
    on="amfi_code",
    how="left"
)

# Arrange columns
var_report = var_report[
    [
        "amfi_code",
        "scheme_name",
        "fund_house",
        "risk_grade",
        "observations",
        "VaR_95_pct",
        "CVaR_95_pct"
    ]
]

# Sort by VaR: worst downside risk first
var_report = var_report.sort_values("VaR_95_pct")

# Save report
var_report.to_csv(OUTPUT_FILE, index=False)

# Display results
print("\nNumber of schemes analysed:", len(var_report))
print("\nHighest downside risk (lowest VaR):")
print(
    var_report[
        ["scheme_name", "risk_grade", "VaR_95_pct", "CVaR_95_pct"]
    ].head(5).to_string(index=False)
)

print("\nComplete VaR and CVaR report:")
print(var_report.to_string(index=False))

print("\nReport saved to:", OUTPUT_FILE)
print("\nTASK 1 COMPLETED")