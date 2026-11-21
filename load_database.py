
import pandas as pd
import sqlite3
from pathlib import Path
from sqlalchemy import create_engine, event

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
SQL_DIR = Path("sql")
DB_DIR = Path("database")

DB_DIR.mkdir(exist_ok=True)

DB_PATH = DB_DIR / "bluestock_mf.db"
SCHEMA_PATH = SQL_DIR / "schema.sql"

# --------------------------------------------------
# 1. Create a fresh database
# --------------------------------------------------

if DB_PATH.exists():
    DB_PATH.unlink()

print("=" * 60)
print("BLUESTOCK - SQLITE DATABASE LOADER")
print("=" * 60)

# Create tables using schema.sql
with sqlite3.connect(DB_PATH) as connection:
    connection.executescript(
        SCHEMA_PATH.read_text(encoding="utf-8")
    )

# SQLAlchemy engine
engine = create_engine(f"sqlite:///{DB_PATH}")

# Enable foreign key validation on SQLAlchemy connections
@event.listens_for(engine, "connect")
def enable_foreign_keys(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")
    cursor.close()


def load_csv(filename):
    return pd.read_csv(PROCESSED_DIR / filename)


def normalize_dates(series):
    dates = pd.to_datetime(series, errors="coerce")

    if dates.isna().any():
        raise ValueError("Invalid dates found in dataset.")

    return dates.dt.strftime("%Y-%m-%d")


def get_date_key(date_value):
    return int(date_value.replace("-", ""))


def save_table(df, table_name):
    df.to_sql(
        table_name,
        engine,
        if_exists="append",
        index=False
    )
    print(f"Loaded {table_name}: {len(df)} rows")


# --------------------------------------------------
# 2. Load fund dimension
# --------------------------------------------------

funds = load_csv("01_fund_master.csv")

if funds["amfi_code"].duplicated().any():
    raise ValueError("Duplicate AMFI codes in fund master.")

save_table(funds, "dim_fund")


# --------------------------------------------------
# 3. Load fund house dimension
# --------------------------------------------------

aum = load_csv("03_aum_by_fund_house.csv")

fund_houses = pd.concat([
    funds[["fund_house"]],
    aum[["fund_house"]]
]).drop_duplicates().sort_values("fund_house")

fund_houses = fund_houses.reset_index(drop=True)
fund_houses.insert(
    0,
    "fund_house_id",
    range(1, len(fund_houses) + 1)
)

save_table(fund_houses, "dim_fund_house")

fund_house_map = dict(zip(
    fund_houses["fund_house"],
    fund_houses["fund_house_id"]
))


# --------------------------------------------------
# 4. Prepare date dimension
# --------------------------------------------------

date_sources = {
    "02_nav_history.csv": "date",
    "03_aum_by_fund_house.csv": "date",
    "08_investor_transactions.csv": "transaction_date",
    "09_portfolio_holdings.csv": "portfolio_date",
    "10_benchmark_indices.csv": "date",
}

all_dates = []

for filename, column in date_sources.items():
    df = load_csv(filename)
    all_dates.extend(normalize_dates(df[column]).tolist())

unique_dates = sorted(set(all_dates))

date_dim = pd.DataFrame({"full_date": unique_dates})
date_dim["date_key"] = date_dim["full_date"].apply(get_date_key)

date_objects = pd.to_datetime(date_dim["full_date"])

date_dim["year"] = date_objects.dt.year
date_dim["quarter"] = date_objects.dt.quarter
date_dim["month"] = date_objects.dt.month
date_dim["month_name"] = date_objects.dt.month_name()
date_dim["day"] = date_objects.dt.day
date_dim["day_of_week"] = date_objects.dt.day_name()

date_dim = date_dim[
    [
        "date_key",
        "full_date",
        "year",
        "quarter",
        "month",
        "month_name",
        "day",
        "day_of_week",
    ]
]

save_table(date_dim, "dim_date")

date_map = dict(zip(
    date_dim["full_date"],
    date_dim["date_key"]
))


# --------------------------------------------------
# 5. Load NAV fact table
# --------------------------------------------------

nav = load_csv("02_nav_history.csv")
nav["date"] = normalize_dates(nav["date"])
nav["date_key"] = nav["date"].map(date_map)

nav_fact = nav[["amfi_code", "date_key", "nav"]].copy()

save_table(nav_fact, "fact_nav")


# --------------------------------------------------
# 6. Load transaction fact table
# --------------------------------------------------

transactions = load_csv("08_investor_transactions.csv")

transactions["transaction_date"] = normalize_dates(
    transactions["transaction_date"]
)

transactions["date_key"] = transactions[
    "transaction_date"
].map(date_map)

transaction_fact = transactions[
    [
        "investor_id",
        "amfi_code",
        "date_key",
        "transaction_type",
        "amount_inr",
        "state",
        "city",
        "city_tier",
        "age_group",
        "gender",
        "annual_income_lakh",
        "payment_mode",
        "kyc_status",
    ]
].copy()

save_table(transaction_fact, "fact_transactions")


# --------------------------------------------------
# 7. Load performance fact table
# --------------------------------------------------

performance = load_csv("07_scheme_performance.csv")

performance_fact = performance[
    [
        "amfi_code",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "benchmark_3yr_pct",
        "alpha",
        "beta",
        "sharpe_ratio",
        "sortino_ratio",
        "std_dev_ann_pct",
        "max_drawdown_pct",
        "aum_crore",
        "expense_ratio_pct",
        "morningstar_rating",
        "risk_grade",
    ]
].copy()

save_table(performance_fact, "fact_performance")


# --------------------------------------------------
# 8. Load AUM fact table
# --------------------------------------------------

aum["date"] = normalize_dates(aum["date"])
aum["date_key"] = aum["date"].map(date_map)

aum["fund_house_id"] = aum["fund_house"].map(
    fund_house_map
)

aum_fact = aum[
    [
        "fund_house_id",
        "date_key",
        "aum_lakh_crore",
        "aum_crore",
        "num_schemes",
    ]
].copy()

save_table(aum_fact, "fact_aum")


# --------------------------------------------------
# 9. Load remaining analytical datasets
# --------------------------------------------------

additional_datasets = {
    "04_monthly_sip_inflows.csv": "monthly_sip_inflows",
    "05_category_inflows.csv": "category_inflows",
    "06_industry_folio_count.csv": "industry_folio_count",
    "09_portfolio_holdings.csv": "portfolio_holdings",
    "10_benchmark_indices.csv": "benchmark_indices",
}

for filename, table_name in additional_datasets.items():
    df = load_csv(filename)

    for column in df.columns:
        if column in ["month", "date", "portfolio_date"]:
            df[column] = normalize_dates(df[column])

    save_table(df, table_name)


# --------------------------------------------------
# 10. Verify database row counts
# --------------------------------------------------

print("\n" + "=" * 60)
print("DATABASE ROW COUNT VERIFICATION")
print("=" * 60)

verification = {
    "dim_fund": "01_fund_master.csv",
    "fact_nav": "02_nav_history.csv",
    "fact_aum": "03_aum_by_fund_house.csv",
    "monthly_sip_inflows": "04_monthly_sip_inflows.csv",
    "category_inflows": "05_category_inflows.csv",
    "industry_folio_count": "06_industry_folio_count.csv",
    "fact_performance": "07_scheme_performance.csv",
    "fact_transactions": "08_investor_transactions.csv",
    "portfolio_holdings": "09_portfolio_holdings.csv",
    "benchmark_indices": "10_benchmark_indices.csv",
}

all_passed = True

with engine.connect() as connection:
    for table_name, filename in verification.items():
        expected = len(load_csv(filename))

        actual = connection.exec_driver_sql(
            f"SELECT COUNT(*) FROM {table_name}"
        ).scalar()

        status = "PASS" if expected == actual else "FAIL"

        if status == "FAIL":
            all_passed = False

        print(
            f"{table_name:25} "
            f"CSV: {expected:7} | "
            f"DB: {actual:7} | {status}"
        )

    # Check foreign key integrity
    fk_errors = connection.exec_driver_sql(
        "PRAGMA foreign_key_check"
    ).fetchall()

print("\nForeign key errors:", len(fk_errors))
print("Database:", DB_PATH)

if all_passed and not fk_errors:
    print("\nSUCCESS: All database checks passed.")
else:
    print("\nWARNING: Please investigate failed checks.")

engine.dispose()
