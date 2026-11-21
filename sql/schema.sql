
PRAGMA foreign_keys = ON;

-- 1. Fund dimension
CREATE TABLE IF NOT EXISTS dim_fund (
    amfi_code INTEGER PRIMARY KEY,
    fund_house TEXT NOT NULL,
    scheme_name TEXT NOT NULL,
    category TEXT,
    sub_category TEXT,
    plan TEXT,
    launch_date TEXT,
    benchmark TEXT,
    expense_ratio_pct REAL,
    exit_load_pct REAL,
    min_sip_amount REAL,
    min_lumpsum_amount REAL,
    fund_manager TEXT,
    risk_category TEXT,
    sebi_category_code TEXT
);

-- 2. Fund house dimension
CREATE TABLE IF NOT EXISTS dim_fund_house (
    fund_house_id INTEGER PRIMARY KEY AUTOINCREMENT,
    fund_house TEXT NOT NULL UNIQUE
);

-- 3. Date dimension
CREATE TABLE IF NOT EXISTS dim_date (
    date_key INTEGER PRIMARY KEY,
    full_date TEXT NOT NULL UNIQUE,
    year INTEGER,
    quarter INTEGER,
    month INTEGER,
    month_name TEXT,
    day INTEGER,
    day_of_week TEXT
);

-- 4. NAV fact table
CREATE TABLE IF NOT EXISTS fact_nav (
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    nav REAL NOT NULL CHECK (nav > 0),
    PRIMARY KEY (amfi_code, date_key),
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- 5. Transaction fact table
CREATE TABLE IF NOT EXISTS fact_transactions (
    transaction_id INTEGER PRIMARY KEY AUTOINCREMENT,
    investor_id TEXT NOT NULL,
    amfi_code INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    transaction_type TEXT NOT NULL,
    amount_inr REAL NOT NULL CHECK (amount_inr > 0),
    state TEXT,
    city TEXT,
    city_tier TEXT,
    age_group TEXT,
    gender TEXT,
    annual_income_lakh REAL,
    payment_mode TEXT,
    kyc_status TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- 6. Performance fact table
CREATE TABLE IF NOT EXISTS fact_performance (
    amfi_code INTEGER PRIMARY KEY,
    return_1yr_pct REAL,
    return_3yr_pct REAL,
    return_5yr_pct REAL,
    benchmark_3yr_pct REAL,
    alpha REAL,
    beta REAL,
    sharpe_ratio REAL,
    sortino_ratio REAL,
    std_dev_ann_pct REAL,
    max_drawdown_pct REAL,
    aum_crore REAL,
    expense_ratio_pct REAL,
    morningstar_rating INTEGER,
    risk_grade TEXT,
    FOREIGN KEY (amfi_code) REFERENCES dim_fund(amfi_code)
);

-- 7. AUM fact table
CREATE TABLE IF NOT EXISTS fact_aum (
    fund_house_id INTEGER NOT NULL,
    date_key INTEGER NOT NULL,
    aum_lakh_crore REAL,
    aum_crore REAL,
    num_schemes INTEGER,
    PRIMARY KEY (fund_house_id, date_key),
    FOREIGN KEY (fund_house_id)
        REFERENCES dim_fund_house(fund_house_id),
    FOREIGN KEY (date_key) REFERENCES dim_date(date_key)
);

-- Useful indexes
CREATE INDEX IF NOT EXISTS idx_nav_date
ON fact_nav(date_key);

CREATE INDEX IF NOT EXISTS idx_transactions_date
ON fact_transactions(date_key);

CREATE INDEX IF NOT EXISTS idx_transactions_type
ON fact_transactions(transaction_type);

CREATE INDEX IF NOT EXISTS idx_aum_date
ON fact_aum(date_key);
