
import pandas as pd
from pathlib import Path

# Load fund master dataset
file_path = Path("data/raw/01_fund_master.csv")

if not file_path.exists():
    raise FileNotFoundError(f"Dataset not found: {file_path}")

df = pd.read_csv(file_path)

print("=" * 65)
print("BLUESTOCK - FUND MASTER ANALYSIS")
print("=" * 65)

# Basic information
print("\n1. DATASET SHAPE")
print(df.shape)

print("\n2. COLUMN NAMES")
print(df.columns.tolist())

print("\n3. DATA TYPES")
print(df.dtypes)

# Explore categorical columns
keywords = [
    "fund_house",
    "category",
    "sub_category",
    "risk",
    "amfi_code"
]

print("\n4. UNIQUE VALUES")

for keyword in keywords:
    matching_columns = [
        col for col in df.columns
        if keyword in col.lower().replace(" ", "_")
    ]

    for col in matching_columns:
        print(f"\n{col}:")
        print("Unique count:", df[col].nunique(dropna=True))
        print(df[col].dropna().unique()[:30])
# Distribution of funds
print("\n5. FUND HOUSE DISTRIBUTION")
print(df["fund_house"].value_counts().to_string())

print("\n6. CATEGORY DISTRIBUTION")
print(df["category"].value_counts().to_string())

print("\n7. SUB-CATEGORY DISTRIBUTION")
print(df["sub_category"].value_counts().to_string())

print("\n8. RISK CATEGORY DISTRIBUTION")
print(df["risk_category"].value_counts().to_string())
# Missing values
print("\n5. MISSING VALUES")
print(df.isnull().sum())

# Duplicate records
print("\n6. DUPLICATE RECORDS")
print(df.duplicated().sum())

# Display sample records
print("\n7. FIRST FIVE RECORDS")
print(df.head().to_string(index=False))

print("\nFund Master Analysis Completed!")
