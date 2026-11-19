
import pandas as pd
from pathlib import Path

folder = Path("data/raw")

schemes = {
    103504: ("SBI Large Cap Fund - Regular Plan - Growth", "SBI Mutual Fund"),
    108466: ("ICICI Prudential Large Cap Fund (erstwhile Bluechip Fund) - Regular Plan - Growth", "ICICI Prudential Mutual Fund"),
    106235: ("Nippon India Large Cap Fund - Regular Plan - Growth Option", "Nippon India Mutual Fund"),
    112277: ("Axis Large Cap Fund - Regular Plan - Growth Option", "Axis Mutual Fund"),
    114458: ("Kotak Large Cap Fund - Regular Plan - Growth", "Kotak Mahindra Mutual Fund"),
    119018: ("HDFC Large Cap Fund - Direct Plan - Growth Option", "HDFC Mutual Fund"),
}

print("=" * 65)
print("LIVE NAV DATA VALIDATION")
print("=" * 65)

all_valid = True

for code, (expected_name, expected_house) in schemes.items():
    files = list(folder.glob(f"{code}_*.csv"))

    if not files:
        print(f"\n{code}: FILE NOT FOUND")
        all_valid = False
        continue

    df = pd.read_csv(files[0])

    required = {"date", "nav", "scheme_code", "scheme_name", "fund_house"}
    if not required.issubset(df.columns):
        print(f"\n{code}: MISSING REQUIRED COLUMNS")
        all_valid = False
        continue

    actual_code = int(df["scheme_code"].iloc[0])
    actual_name = str(df["scheme_name"].iloc[0])
    actual_house = str(df["fund_house"].iloc[0])

    valid = (
        actual_code == code
        and actual_name == expected_name
        and actual_house == expected_house
        and len(df) > 0
        and pd.to_numeric(df["nav"], errors="coerce").notna().all()
    )

    print(f"\nScheme code: {code}")
    print(f"Scheme name: {actual_name}")
    print(f"Fund house: {actual_house}")
    print(f"Records: {len(df)}")
    print(f"Validation: {'PASS' if valid else 'CHECK REQUIRED'}")

    if not valid:
        all_valid = False

print("\n" + "=" * 65)
print("FINAL RESULT:", "ALL FILES VALID" if all_valid else "CHECK ERRORS")
print("=" * 65)
