

\# Bluestock Mutual Fund Analytics

\# Data Dictionary



\## 1. Project Overview



This document describes the datasets used in the Bluestock Mutual Fund Analytics project.



The project uses mutual fund information, NAV history, AUM, SIP inflows, investor transactions, scheme performance, portfolio holdings, and benchmark index data.



Original datasets are stored in `data/raw/`.



Cleaned datasets are stored in `data/processed/`.



The SQLite database is stored at `database/bluestock\_mf.db`.



\## 2. Data Cleaning Standards



The following cleaning operations were performed:



\- Removed unnecessary leading and trailing spaces from text fields.

\- Standardised date columns to YYYY-MM-DD format.

\- Removed exact duplicate records.

\- Sorted NAV records by scheme code and date.

\- Standardised transaction types to SIP, Lumpsum, and Redemption.

\- Standardised KYC status to Verified and Pending.

\- Checked transaction amounts to ensure they are greater than zero.

\- Converted scheme performance metrics into numeric values.

\- Checked expense ratios against the required range of 0.1% to 2.5%.

\- Checked NAV values to ensure they are greater than zero.



No duplicate rows or invalid records were found in the inspected datasets.



Total original records: 87,533  

Total cleaned records: 87,533



Missing SIP year-on-year growth values for January–December 2022 were retained as NULL because the previous year's baseline data was unavailable.



\---



\## 3. Dataset Descriptions



\### 3.1 Fund Master



\*\*Source:\*\* `data/raw/01\_fund\_master.csv`  

\*\*Cleaned file:\*\* `data/processed/01\_fund\_master.csv`  

\*\*Records:\*\* 40  

\*\*Columns:\*\* 15



| Column | Data Type | Business Definition |

|---|---|---|

| amfi\_code | INTEGER | Unique AMFI scheme identifier |

| fund\_house | TEXT | Name of the mutual fund company |

| scheme\_name | TEXT | Full mutual fund scheme name |

| category | TEXT | Main fund category |

| sub\_category | TEXT | Specific investment category |

| plan | TEXT | Scheme plan type |

| launch\_date | DATE | Scheme launch date |

| benchmark | TEXT | Benchmark index used for comparison |

| expense\_ratio\_pct | REAL | Annual expense ratio percentage |

| exit\_load\_pct | REAL | Exit load percentage |

| min\_sip\_amount | REAL | Minimum SIP investment amount |

| min\_lumpsum\_amount | REAL | Minimum lump-sum investment amount |

| fund\_manager | TEXT | Name of the fund manager |

| risk\_category | TEXT | Risk classification of the scheme |

| sebi\_category\_code | TEXT | SEBI category identifier |



\*\*Purpose:\*\* Stores basic information about mutual fund schemes.



\### 3.2 NAV History



\*\*Source:\*\* `data/raw/02\_nav\_history.csv`  

\*\*Cleaned file:\*\* `data/processed/02\_nav\_history.csv`  

\*\*Records:\*\* 46,000  

\*\*Columns:\*\* 3



| Column | Data Type | Business Definition |

|---|---|---|

| amfi\_code | INTEGER | Mutual fund scheme identifier |

| date | DATE | NAV record date |

| nav | REAL | Net Asset Value of the scheme |



\*\*Purpose:\*\* Stores historical NAV values for mutual fund schemes.



\*\*Validation:\*\* Records are sorted by scheme code and date. NAV must be greater than zero. No missing or invalid NAV values were found.



\### 3.3 AUM by Fund House



\*\*Source:\*\* `data/raw/03\_aum\_by\_fund\_house.csv`  

\*\*Cleaned file:\*\* `data/processed/03\_aum\_by\_fund\_house.csv`  

\*\*Records:\*\* 90  

\*\*Columns:\*\* 5



| Column | Data Type | Business Definition |

|---|---|---|

| date | DATE | Reporting date |

| fund\_house | TEXT | Mutual fund company name |

| aum\_lakh\_crore | REAL | Assets under management in lakh crore |

| aum\_crore | REAL | Assets under management in crore |

| num\_schemes | INTEGER | Number of schemes managed |



\*\*Purpose:\*\* Tracks assets managed by different mutual fund companies.



\### 3.4 Monthly SIP Inflows



\*\*Source:\*\* `data/raw/04\_monthly\_sip\_inflows.csv`  

\*\*Cleaned file:\*\* `data/processed/04\_monthly\_sip\_inflows.csv`  

\*\*Records:\*\* 48  

\*\*Columns:\*\* 6



| Column | Data Type | Business Definition |

|---|---|---|

| month | DATE | Reporting month |

| sip\_inflow\_crore | REAL | Total SIP investment inflow in crore |

| active\_sip\_accounts\_crore | REAL | Number of active SIP accounts in crore |

| new\_sip\_accounts\_lakh | REAL | Number of new SIP accounts in lakh |

| sip\_aum\_lakh\_crore | REAL | SIP assets under management in lakh crore |

| yoy\_growth\_pct | REAL | Year-on-year SIP growth percentage |



\*\*Purpose:\*\* Analyses monthly SIP investment trends.



\*\*Data note:\*\* The `yoy\_growth\_pct` values for 2022 are NULL because 2021 comparison data is not available in the dataset.



\### 3.5 Category Inflows



\*\*Source:\*\* `data/raw/05\_category\_inflows.csv`  

\*\*Cleaned file:\*\* `data/processed/05\_category\_inflows.csv`  

\*\*Records:\*\* 144  

\*\*Columns:\*\* 3



| Column | Data Type | Business Definition |

|---|---|---|

| month | DATE | Reporting month |

| category | TEXT | Mutual fund investment category |

| net\_inflow\_crore | REAL | Net investment inflow in crore |



\*\*Purpose:\*\* Compares investment inflows across mutual fund categories.



\### 3.6 Industry Folio Count



\*\*Source:\*\* `data/raw/06\_industry\_folio\_count.csv`  

\*\*Cleaned file:\*\* `data/processed/06\_industry\_folio\_count.csv`  

\*\*Records:\*\* 21  

\*\*Columns:\*\* 6



| Column | Data Type | Business Definition |

|---|---|---|

| month | DATE | Reporting month |

| total\_folios\_crore | REAL | Total mutual fund folios in crore |

| equity\_folios\_crore | REAL | Equity folios in crore |

| debt\_folios\_crore | REAL | Debt folios in crore |

| hybrid\_folios\_crore | REAL | Hybrid folios in crore |

| others\_folios\_crore | REAL | Other category folios in crore |



\*\*Purpose:\*\* Tracks mutual fund folio growth across investment categories.



\### 3.7 Scheme Performance



\*\*Source:\*\* `data/raw/07\_scheme\_performance.csv`  

\*\*Cleaned file:\*\* `data/processed/07\_scheme\_performance.csv`  

\*\*Records:\*\* 40  

\*\*Columns:\*\* 19



| Column | Data Type | Business Definition |

|---|---|---|

| amfi\_code | INTEGER | Mutual fund scheme identifier |

| scheme\_name | TEXT | Scheme name |

| fund\_house | TEXT | Mutual fund company |

| category | TEXT | Fund category |

| plan | TEXT | Scheme plan |

| return\_1yr\_pct | REAL | One-year return percentage |

| return\_3yr\_pct | REAL | Three-year return percentage |

| return\_5yr\_pct | REAL | Five-year return percentage |

| benchmark\_3yr\_pct | REAL | Three-year benchmark return percentage |

| alpha | REAL | Risk-adjusted excess return measure |

| beta | REAL | Measure of market sensitivity |

| sharpe\_ratio | REAL | Risk-adjusted return ratio |

| sortino\_ratio | REAL | Downside-risk-adjusted return ratio |

| std\_dev\_ann\_pct | REAL | Annualised standard deviation percentage |

| max\_drawdown\_pct | REAL | Maximum observed peak-to-trough decline |

| aum\_crore | REAL | Scheme assets under management in crore |

| expense\_ratio\_pct | REAL | Annual expense ratio percentage |

| morningstar\_rating | INTEGER | Morningstar scheme rating |

| risk\_grade | TEXT | Scheme risk grade |



\*\*Purpose:\*\* Evaluates mutual fund scheme performance, returns, and risk measures.



\*\*Validation:\*\* Return fields were converted to numeric values. Expense ratios were checked against the 0.1%–2.5% range.



\### 3.8 Investor Transactions



\*\*Source:\*\* `data/raw/08\_investor\_transactions.csv`  

\*\*Cleaned file:\*\* `data/processed/08\_investor\_transactions.csv`  

\*\*Records:\*\* 32,778  

\*\*Columns:\*\* 13



| Column | Data Type | Business Definition |

|---|---|---|

| investor\_id | TEXT | Unique investor identifier |

| transaction\_date | DATE | Transaction date |

| amfi\_code | INTEGER | Mutual fund scheme identifier |

| transaction\_type | TEXT | SIP, Lumpsum, or Redemption |

| amount\_inr | REAL | Transaction amount in Indian rupees |

| state | TEXT | Investor's state |

| city | TEXT | Investor's city |

| city\_tier | TEXT | City classification |

| age\_group | TEXT | Investor age group |

| gender | TEXT | Investor gender category |

| annual\_income\_lakh | REAL | Annual investor income in lakh |

| payment\_mode | TEXT | Transaction payment method |

| kyc\_status | TEXT | Verified or Pending KYC status |



\*\*Purpose:\*\* Analyses investor transactions, investment amounts, geographical distribution, and KYC status.



\*\*Validation:\*\* Transaction types and KYC statuses were standardised. Transaction amounts must be greater than zero.



\### 3.9 Portfolio Holdings



\*\*Source:\*\* `data/raw/09\_portfolio\_holdings.csv`  

\*\*Cleaned file:\*\* `data/processed/09\_portfolio\_holdings.csv`  

\*\*Records:\*\* 322  

\*\*Columns:\*\* 8



| Column | Data Type | Business Definition |

|---|---|---|

| amfi\_code | INTEGER | Mutual fund scheme identifier |

| stock\_symbol | TEXT | Stock exchange symbol |

| stock\_name | TEXT | Company name |

| sector | TEXT | Industry sector |

| weight\_pct | REAL | Stock weight in the portfolio percentage |

| market\_value\_cr | REAL | Holding market value in crore |

| current\_price\_inr | REAL | Current stock price in rupees |

| portfolio\_date | DATE | Portfolio reporting date |



\*\*Purpose:\*\* Examines the stocks held by mutual fund schemes and their portfolio allocation.



\### 3.10 Benchmark Indices



\*\*Source:\*\* `data/raw/10\_benchmark\_indices.csv`  

\*\*Cleaned file:\*\* `data/processed/10\_benchmark\_indices.csv`  

\*\*Records:\*\* 8,050  

\*\*Columns:\*\* 3



| Column | Data Type | Business Definition |

|---|---|---|

| date | DATE | Index observation date |

| index\_name | TEXT | Benchmark index name |

| close\_value | REAL | Closing index value |



\*\*Purpose:\*\* Stores benchmark index history for market and fund performance comparisons.



\---



\## 4. Database Schema Overview



\*\*Database file:\*\* `database/bluestock\_mf.db`



The project uses a SQLite relational database with dimension and fact tables.



\### Dimension Tables



\- `dim\_fund` – stores mutual fund scheme details.

\- `dim\_fund\_house` – stores fund house details.

\- `dim\_date` – stores calendar date information.



\### Fact Tables



\- `fact\_nav` – stores historical NAV records.

\- `fact\_transactions` – stores investor transaction records.

\- `fact\_performance` – stores scheme performance metrics.

\- `fact\_aum` – stores assets under management by fund house and date.



\### Additional Analytical Tables



\- `monthly\_sip\_inflows`

\- `category\_inflows`

\- `industry\_folio\_count`

\- `portfolio\_holdings`

\- `benchmark\_indices`



Primary keys and foreign keys are defined in `sql/schema.sql`.



The database was loaded using SQLAlchemy and Pandas `to\_sql()`.



Database verification confirmed that the loaded row counts matched the cleaned source datasets, with zero foreign key errors.



\---



\## 5. Data Sources and References



The project uses the following local source files:



1\. `data/raw/01\_fund\_master.csv`

2\. `data/raw/02\_nav\_history.csv`

3\. `data/raw/03\_aum\_by\_fund\_house.csv`

4\. `data/raw/04\_monthly\_sip\_inflows.csv`

5\. `data/raw/05\_category\_inflows.csv`

6\. `data/raw/06\_industry\_folio\_count.csv`

7\. `data/raw/07\_scheme\_performance.csv`

8\. `data/raw/08\_investor\_transactions.csv`

9\. `data/raw/09\_portfolio\_holdings.csv`

10\. `data/raw/10\_benchmark\_indices.csv`



Live NAV data was also retrieved through the MFAPI service using verified scheme codes.



\*\*Note:\*\* Dataset values are used as supplied for this analytics project. They should not automatically be treated as verified real-world investment information.



\---



\## 6. Project Validation Summary



| Validation | Result |

|---|---:|

| Total datasets | 10 |

| Total source records | 87,533 |

| Total cleaned records | 87,533 |

| Duplicate rows removed | 0 |

| Invalid NAV records | 0 |

| Invalid transaction types | 0 |

| Invalid KYC statuses | 0 |

| Invalid transaction amounts | 0 |

| Invalid performance return values | 0 |

| Invalid expense ratios | 0 |

| Database foreign key errors | 0 |

| Analytical SQL queries | 10 |



\## 7. Conclusion



The data dictionary provides a reference for understanding the datasets, their columns, and their business meaning.



The cleaning and validation process prepared the ten datasets for analysis. The cleaned records were successfully loaded into SQLite, and ten analytical SQL queries were executed to examine mutual fund performance, NAV trends, SIP inflows, investor transactions, and portfolio holdings.



