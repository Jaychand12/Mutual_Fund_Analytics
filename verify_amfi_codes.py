
import requests
import re

url = "https://portal.amfiindia.com/spages/NAVAll.txt"

targets = {
    "SBI": ["bluechip", "large cap"],
    "ICICI": ["bluechip", "large cap"],
    "Nippon": ["large cap"],
    "Axis": ["bluechip", "large cap"],
    "Kotak": ["bluechip", "large cap"],
    "HDFC": ["top 100", "large cap"]
}

print("Downloading AMFI NAV data...")

response = requests.get(url, timeout=60)
response.raise_for_status()

current_fund_house = ""
matches = []

for line in response.text.splitlines():
    line = line.strip()

    if not line:
        continue

    parts = [part.strip() for part in line.split(";")]

    # Fund-house and section headings
    if len(parts) == 1:
        if not line.lower().startswith(
            ("open ended schemes", "close ended schemes",
             "interval fund", "scheme code")
        ):
            current_fund_house = line
        continue

    # Only process rows with a numeric scheme code
    if not parts[0].isdigit():
        continue

    if len(parts) >= 8:
        code = parts[0]
        scheme_name = parts[3]
        plan = parts[4]
        option = parts[5]
        nav = parts[6]
        date = parts[7]
    elif len(parts) >= 6:
        code = parts[0]
        scheme_name = parts[3]
        plan = "Not available in this row"
        option = "Not available in this row"
        nav = parts[4]
        date = parts[5]
    else:
        continue

    for fund, keywords in targets.items():
        if fund.lower() in current_fund_house.lower():
            if any(word in scheme_name.lower() for word in keywords):
                matches.append({
                    "fund_house": current_fund_house,
                    "code": code,
                    "scheme": scheme_name,
                    "plan": plan,
                    "option": option,
                    "nav": nav,
                    "date": date
                })

print("\n" + "=" * 90)
print("POSSIBLE MATCHING SCHEMES")
print("=" * 90)

for item in matches:
    print(
        f"\nFund House: {item['fund_house']}"
        f"\nCode: {item['code']}"
        f"\nScheme: {item['scheme']}"
        f"\nPlan: {item['plan']}"
        f"\nOption: {item['option']}"
        f"\nNAV: {item['nav']}"
        f"\nDate: {item['date']}"
    )

print("\nTotal matching records:", len(matches))
