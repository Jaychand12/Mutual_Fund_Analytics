
import pandas as pd

INPUT_FILE = "data/processed/07_scheme_performance.csv"

print("=" * 65)
print("BLUESTOCK MUTUAL FUND RECOMMENDER")
print("=" * 65)

# Load fund performance data
df = pd.read_csv(INPUT_FILE)

# Risk appetite mapping
risk_mapping = {
    "low": ["Low"],
    "moderate": ["Moderate", "Moderately High"],
    "high": ["High", "Very High"]
}

# Get user input
print("\nAvailable Risk Appetites:")
print("1. Low")
print("2. Moderate")
print("3. High")

choice = input("\nEnter your risk appetite: ").strip().lower()

# Validate input
if choice not in risk_mapping:
    print("\nInvalid choice. Please enter Low, Moderate, or High.")
else:
    # Filter funds by risk grade
    matching_funds = df[
        df["risk_grade"].isin(risk_mapping[choice])
    ].copy()

    # Sort by Sharpe ratio
    matching_funds = matching_funds.sort_values(
        "sharpe_ratio",
        ascending=False
    )

    # Select top 3 funds
    recommendations = matching_funds.head(3)

    print("\nSelected Risk Appetite:", choice.title())
    print("\nTOP 3 RECOMMENDED FUNDS")
    print("-" * 65)

    if recommendations.empty:
        print("No matching funds found.")
    else:
        print(
            recommendations[
                [
                    "scheme_name",
                    "risk_grade",
                    "sharpe_ratio",
                    "return_3yr_pct",
                    "expense_ratio_pct"
                ]
            ].to_string(index=False)
        )

    print("\nRecommendations are based on historical Sharpe ratios.")
    print("Past performance does not guarantee future returns.")

print("\nTASK 5 COMPLETED")
