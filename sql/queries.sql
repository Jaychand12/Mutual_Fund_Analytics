
-- =====================================================
-- BLUESTOCK MUTUAL FUND ANALYTICS
-- DAY 2: 10 ANALYTICAL SQL QUERIES
-- =====================================================

-- 1. Top 5 funds by AUM
SELECT
    f.scheme_name,
    f.fund_house,
    p.aum_crore
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY p.aum_crore DESC
LIMIT 5;


-- 2. Average NAV per month
SELECT
    d.year,
    d.month,
    d.month_name,
    ROUND(AVG(n.nav), 4) AS average_nav
FROM fact_nav n
JOIN dim_date d
    ON n.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- 3. Monthly SIP inflows and YoY growth
SELECT
    month,
    sip_inflow_crore,
    yoy_growth_pct
FROM monthly_sip_inflows
ORDER BY month;


-- 4. Number of transactions by state
SELECT
    state,
    COUNT(*) AS total_transactions,
    ROUND(SUM(amount_inr), 2) AS total_transaction_amount
FROM fact_transactions
GROUP BY state
ORDER BY total_transactions DESC;


-- 5. Funds with expense ratio below 1%
SELECT
    f.scheme_name,
    f.fund_house,
    p.expense_ratio_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
WHERE p.expense_ratio_pct < 1.0
ORDER BY p.expense_ratio_pct ASC;


-- 6. Total SIP, Lumpsum and Redemption transactions
SELECT
    transaction_type,
    COUNT(*) AS transaction_count,
    ROUND(SUM(amount_inr), 2) AS total_amount_inr,
    ROUND(AVG(amount_inr), 2) AS average_amount_inr
FROM fact_transactions
GROUP BY transaction_type
ORDER BY total_amount_inr DESC;


-- 7. Average 1-year and 3-year returns by fund category
SELECT
    f.category,
    ROUND(AVG(p.return_1yr_pct), 2) AS avg_1yr_return,
    ROUND(AVG(p.return_3yr_pct), 2) AS avg_3yr_return
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
GROUP BY f.category
ORDER BY avg_3yr_return DESC;


-- 8. Compare fund returns with benchmark returns
SELECT
    f.scheme_name,
    p.return_3yr_pct,
    p.benchmark_3yr_pct,
    ROUND(
        p.return_3yr_pct - p.benchmark_3yr_pct,
        2
    ) AS return_difference_pct
FROM fact_performance p
JOIN dim_fund f
    ON p.amfi_code = f.amfi_code
ORDER BY return_difference_pct DESC;


-- 9. KYC status distribution
SELECT
    kyc_status,
    COUNT(*) AS transaction_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM fact_transactions),
        2
    ) AS percentage
FROM fact_transactions
GROUP BY kyc_status
ORDER BY transaction_count DESC;


-- 10. Top 10 stocks by portfolio weight
SELECT
    stock_symbol,
    stock_name,
    sector,
    ROUND(AVG(weight_pct), 2) AS average_weight_pct
FROM portfolio_holdings
GROUP BY stock_symbol, stock_name, sector
ORDER BY average_weight_pct DESC
LIMIT 10;
