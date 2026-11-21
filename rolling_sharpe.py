
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

NAV_FILE = "data/processed/02_nav_history.csv"
PERF_FILE = "data/processed/07_scheme_performance.csv"
OUTPUT_FILE = "rolling_sharpe_chart.png"

print("=" * 65)
print("ROLLING 90-DAY SHARPE RATIO ANALYSIS")
print("=" * 65)

# Load datasets
nav = pd.read_csv(NAV_FILE)
performance = pd.read_csv(PERF_FILE)

nav["date"] = pd.to_datetime(nav["date"])
nav["nav"] = pd.to_numeric(nav["nav"], errors="coerce")

# Select five funds with the highest AUM
key_funds = (
    performance.sort_values("aum_crore", ascending=False)
    .head(5)[["amfi_code", "scheme_name", "aum_crore"]]
)

print("\nSelected five funds:")
print(key_funds.to_string(index=False))

# Sort NAV history
nav = nav.sort_values(["amfi_code", "date"])

# Calculate daily returns as decimals
nav["daily_return"] = (
    nav.groupby("amfi_code")["nav"].pct_change()
)

# Calculate rolling Sharpe for each selected fund
nav["rolling_mean"] = (
    nav.groupby("amfi_code")["daily_return"]
    .transform(lambda x: x.rolling(90, min_periods=90).mean())
)

nav["rolling_std"] = (
    nav.groupby("amfi_code")["daily_return"]
    .transform(lambda x: x.rolling(90, min_periods=90).std())
)

nav["rolling_sharpe"] = (
    nav["rolling_mean"] / nav["rolling_std"]
) * np.sqrt(252)

# Plot
plt.figure(figsize=(14, 7))

for _, fund in key_funds.iterrows():
    fund_data = nav[nav["amfi_code"] == fund["amfi_code"]].copy()

    fund_data = fund_data.dropna(subset=["rolling_sharpe"])

    plt.plot(
        fund_data["date"],
        fund_data["rolling_sharpe"],
        label=fund["scheme_name"]
    )

plt.title("Rolling 90-Day Sharpe Ratio – Top 5 Funds by AUM")
plt.xlabel("Date")
plt.ylabel("Annualised Rolling Sharpe Ratio")
plt.axhline(y=0, linestyle="--", linewidth=1)
plt.legend(fontsize=8, loc="best")
plt.grid(True, alpha=0.3)
plt.tight_layout()

plt.savefig(OUTPUT_FILE, dpi=300)
plt.show()

print("\nChart saved to:", OUTPUT_FILE)
print("TASK 2 COMPLETED")
