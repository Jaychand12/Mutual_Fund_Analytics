import pandas as pd
from pathlib import Path

master = pd.read_csv("data/raw/01_fund_master.csv")

files = [
    Path("data/raw/119551_sbi_bluechip.csv"),
    Path("data/raw/120503_icici_bluechip.csv"),
    Path("data/raw/118632_nippon_large_cap.csv"),
    Path("data/raw/119092_axis_bluechip.csv"),
    Path("data/raw/120841_kotak_bluechip.csv"),
    Path("data/raw/125497_hdfc_top_100_direct.csv")
]

print("=" * 75)
print("OFFLINE NAV SCHEME VERIFICATION")
print("=" * 75)

for file in files:
    if not file.exists():
        print(f"\nFILE MISSING: {file}")
        continue

    nav = pd.read_csv(file)

    code = int(nav["scheme_code"].iloc[0])

    expected = master[master["amfi_code"] == code]

    print(f"\nAMFI CODE: {code}")
    print("File:", file.name)

    if expected.empty:
        print("Fund Master: CODE NOT FOUND")
    else:
        print("Expected scheme:", expected["scheme_name"].iloc[0])
        print("Expected fund house:", expected["fund_house"].iloc[0])

    print("API scheme:", nav["scheme_name"].iloc[0])
    print("API fund house:", nav["fund_house"].iloc[0])
    print("NAV records:", len(nav))

    print("-" * 75)