
import requests
import pandas as pd
from pathlib import Path
import re
import time

# Six mutual fund schemes
schemes = {
    103504: "SBI Large Cap Regular Growth",
    108466: "ICICI Prudential Large Cap Regular Growth",
    106235: "Nippon India Large Cap Regular Growth",
    112277: "Axis Large Cap Regular Growth",
    114458: "Kotak Large Cap Regular Growth",
    119018: "HDFC Large Cap Direct Growth"
}


# Output directory
output_dir = Path("data/raw")
output_dir.mkdir(parents=True, exist_ok=True)

# Store download summary
summary = []

for code, fund_name in schemes.items():

    print("\n" + "=" * 55)
    print(f"Fetching: {fund_name} ({code})")
    print("=" * 55)

    url = f"https://api.mfapi.in/mf/{code}"

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        result = response.json()

        if result.get("status") != "SUCCESS":
            raise ValueError("API response was not successful")

        meta = result["meta"]
        nav_data = pd.DataFrame(result["data"])

        # Verify API scheme identity
        api_code = meta.get("scheme_code")

        print("Requested code:", code)
        print("API reported code:", api_code)
        print("API scheme name:", meta.get("scheme_name"))
        print("API fund house:", meta.get("fund_house"))

        if api_code is None or str(api_code) != str(code):
            raise ValueError(
                f"Scheme code mismatch: requested {code}, "
                f"API returned {api_code}"
            )

        # Verify NAV data exists
        if nav_data.empty:
            raise ValueError("No NAV records available")

        # Add verified fund information
        nav_data["scheme_code"] = code
        nav_data["scheme_name"] = meta.get("scheme_name")
        nav_data["fund_house"] = meta.get("fund_house")

        # Convert NAV into numeric values
        nav_data["nav"] = pd.to_numeric(
            nav_data["nav"], errors="coerce"
        )

        # Save CSV
        safe_name = re.sub(
            r"[^a-zA-Z0-9]+", "_", fund_name
        ).strip("_").lower()

        output_file = output_dir / f"{code}_{safe_name}.csv"

        nav_data.to_csv(output_file, index=False)

        print("Records:", len(nav_data))
        print("Latest NAV data:")
        print(nav_data.head(1))
        print("Saved:", output_file)

        summary.append({
            "scheme_code": code,
            "fund_name": fund_name,
            "records": len(nav_data),
            "status": "SUCCESS"
        })

    except Exception as error:

        print("ERROR:", error)

        summary.append({
            "scheme_code": code,
            "fund_name": fund_name,
            "records": 0,
            "status": f"FAILED: {error}"
        })

    time.sleep(0.5)

# Final report
print("\n" + "=" * 55)
print("NAV DOWNLOAD SUMMARY")
print("=" * 55)

summary_df = pd.DataFrame(summary)
print(summary_df.to_string(index=False))

summary_df.to_csv(
    output_dir / "nav_download_summary.csv",
    index=False
)

print("\nNAV fetching process completed.")
