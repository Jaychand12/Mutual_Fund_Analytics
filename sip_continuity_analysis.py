
import pandas as pd

INPUT_FILE = "data/processed/08_investor_transactions.csv"
OUTPUT_FILE = "sip_continuity_report.csv"

print("=" * 65)
print("SIP CONTINUITY ANALYSIS")
print("=" * 65)

df = pd.read_csv(INPUT_FILE)

df["transaction_date"] = pd.to_datetime(df["transaction_date"])

# Keep only SIP transactions
sip = df[df["transaction_type"] == "SIP"].copy()

sip = sip.sort_values(["investor_id", "transaction_date"])

results = []

for investor_id, group in sip.groupby("investor_id"):

    group = group.sort_values("transaction_date")

    # Require at least 6 SIP transactions
    if len(group) < 6:
        continue

    # Calculate gaps between consecutive SIP dates
    gaps = group["transaction_date"].diff().dt.days.dropna()

    if gaps.empty:
        continue

    avg_gap = gaps.mean()

    results.append({
        "investor_id": investor_id,
        "sip_transactions": len(group),
        "avg_gap_days": round(avg_gap, 2),
        "max_gap_days": int(gaps.max()),
        "continuity_status": (
            "At-Risk" if avg_gap > 35 else "Regular"
        )
    })

report = pd.DataFrame(results)

if not report.empty:
    report = report.sort_values(
        "avg_gap_days", ascending=False
    )

    print("\nEligible investors:", len(report))
    print("\nContinuity status:")
    print(report["continuity_status"].value_counts())

    at_risk = report[
        report["continuity_status"] == "At-Risk"
    ]

    print("\nAt-risk investors:", len(at_risk))

    print("\nTop 10 investors with longest average SIP gaps:")
    print(report.head(10).to_string(index=False))

    continuity_rate = (
        (report["continuity_status"] == "Regular").mean() * 100
    )

    print(
        f"\nSIP continuity rate: {continuity_rate:.2f}%"
    )

    report.to_csv(OUTPUT_FILE, index=False)

    print("\nReport saved:", OUTPUT_FILE)

else:
    print("No investors met the 6-SIP transaction requirement.")

print("\nTASK 4 COMPLETED")
