
import requests

search_terms = ["SBI", "ICICI", "Nippon", "Axis", "Kotak", "HDFC"]

for term in search_terms:

    print("\n" + "=" * 65)
    print("SEARCH:", term)
    print("=" * 65)

    try:
        response = requests.get(
            "https://api.mfapi.in/mf/search",
            params={"q": term},
            timeout=30
        )
        response.raise_for_status()

        results = response.json()

        print("Total results returned:", len(results))

        for item in results[:20]:
            print(
                item.get("schemeCode"),
                "|",
                item.get("schemeName")
            )

    except Exception as error:
        print("ERROR:", error)
