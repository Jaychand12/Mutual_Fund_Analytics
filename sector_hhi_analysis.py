
import pandas as pd

HOLDINGS_FILE = "data/processed/09_portfolio_holdings.csv"
PERFORMANCE_FILE = "data/processed/07_scheme_performance.csv"
OUTPUT_FILE = "sector_hhi_report.csv"

print("=" * 65)
print("SECTOR HHI CONCENTRATION ANALYSIS")
print("=" * 65)

# Load datasets
holdings = pd.read_csv(HOLDINGS_FILE)
performance = pd.read_csv(PERFORMANCE_FILE)

# Convert weights to numeric
holdings["weight_pct"] = pd.to_numeric(
    holdings["weight_pct"], errors="coerce"
)

# Keep valid sector and weight records
holdings = holdings.dropna(
    subset=["amfi_code", "sector", "weight_pct"]
)

# Keep equity funds only
equity_categories = [
    "Large Cap",
    "Mid Cap",
    "Small Cap",
    "Flexi Cap",
    "Value",
    "Index/ETF",
    "Index",
    "Large & Mid Cap",
    "ELSS"
]

equity_funds = performance[
    performance["category"].isin(equity_categories)
].copy()

# Restrict holdings to equity funds
holdings = holdings[
    holdings["amfi_code"].isin(equity_funds["amfi_code"])
].copy()

# Combine stock weights belonging to the same sector
sector_weights = (
    holdings.groupby(["amfi_code", "sector"])["weight_pct"]
    .sum()
    .reset_index()
)

# Calculate each scheme's total represented sector weight
sector_weights["total_weight"] = (
    sector_weights.groupby("amfi_code")["weight_pct"]
    .transform("sum")
)

# Normalise weights to 100% to handle small rounding differences
sector_weights["normalised_weight"] = (
    sector_weights["weight_pct"]
    / sector_weights["total_weight"] * 100
)

# Square normalised sector weights
sector_weights["squared_weight"] = (
    sector_weights["normalised_weight"] / 100
) ** 2

# Calculate HHI for each scheme
hhi_report = (
    sector_weights.groupby("amfi_code")["squared_weight"]
    .sum()
    .reset_index(name="HHI")
)

# Add fund details
hhi_report = hhi_report.merge(
    equity_funds[
        ["amfi_code", "scheme_name", "fund_house", "category"]
    ],
    on="amfi_code",
    how="left"
)

# Concentration classification (descriptive project thresholds)
hhi_report["concentration_level"] = pd.cut(
    hhi_report["HHI"],
    bins=[0, 0.15, 0.25, 1.01],
    labels=["Low", "Moderate", "High"],
    include_lowest=True
)

# Sort from highest to lowest concentration
hhi_report = hhi_report.sort_values(
    "HHI", ascending=False
)

# Save report
hhi_report.to_csv(OUTPUT_FILE, index=False)

# Display results
print("\nEquity funds in performance dataset:",
      len(equity_funds))

print("Equity funds with portfolio holdings:",
      len(hhi_report))

print("\nTOP 10 MOST CONCENTRATED FUNDS")
print(
    hhi_report[
        ["scheme_name", "category", "HHI", "concentration_level"]
    ].head(10).to_string(index=False)
)

print("\nTOP 10 MOST DIVERSIFIED FUNDS")
print(
    hhi_report[
        ["scheme_name", "category", "HHI", "concentration_level"]
    ].sort_values("HHI").head(10).to_string(index=False)
)

print("\nConcentration level distribution:")
print(hhi_report["concentration_level"].value_counts())

print("\nReport saved:", OUTPUT_FILE)
print("\nTASK 6 COMPLETED")
