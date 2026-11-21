import sqlite3
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# --------------------------------------------------
# Configuration
# --------------------------------------------------

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "database" / "bluestock_mf.db"

st.set_page_config(
    page_title="Bluestock | Mutual Fund Analytics",
    page_icon="📊",
    layout="wide"
)

st.title("📊 Bluestock Mutual Fund Analytics")
st.caption("Data-driven mutual fund performance, risk and investor insights")

# --------------------------------------------------
# Database and report loading
# --------------------------------------------------

@st.cache_data
def load_data(query):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(query, conn)


def load_report(filename):
    path = ROOT / filename
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()


if not DB_PATH.exists():
    st.error("Database file not found. Check database/bluestock_mf.db.")
    st.stop()

try:
    funds = load_data("SELECT * FROM dim_fund")
    performance = load_data("""
        SELECT f.scheme_name, f.fund_house, f.category,
               f.risk_category, p.*
        FROM fact_performance p
        JOIN dim_fund f ON p.amfi_code = f.amfi_code
    """)

    nav = load_data("""
        SELECT f.scheme_name, d.full_date, n.nav
        FROM fact_nav n
        JOIN dim_fund f ON n.amfi_code = f.amfi_code
        JOIN dim_date d ON n.date_key = d.date_key
    """)

    aum = load_data("""
        SELECT d.full_date, h.fund_house, a.aum_crore
        FROM fact_aum a
        JOIN dim_date d ON a.date_key = d.date_key
        JOIN dim_fund_house h ON a.fund_house_id = h.fund_house_id
    """)

    transactions = load_data("""
        SELECT t.*, d.full_date
        FROM fact_transactions t
        JOIN dim_date d ON t.date_key = d.date_key
    """)

    sip = load_data("SELECT * FROM monthly_sip_inflows")
    categories = load_data("SELECT * FROM category_inflows")

except Exception as error:
    st.error(f"Unable to load database data: {error}")
    st.stop()

var_report = load_report("var_cvar_report.csv")
cohort_report = load_report("investor_cohort_report.csv")
continuity_report = load_report("sip_continuity_report.csv")
hhi_report = load_report("sector_hhi_report.csv")

# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------

st.sidebar.header("Dashboard Filters")

category_options = sorted(
    funds["category"].dropna().unique().tolist()
)
selected_category = st.sidebar.multiselect(
    "Fund Category",
    category_options,
    default=category_options
)

filtered_funds = funds[
    funds["category"].isin(selected_category)
]

filtered_performance = performance[
    performance["category"].isin(selected_category)
]

st.sidebar.caption("Data source: Project SQLite database and analysis reports")

# --------------------------------------------------
# Dashboard tabs
# --------------------------------------------------

overview, performance_tab, risk_tab, investor_tab, sip_tab = st.tabs([
    "Overview",
    "Fund Performance",
    "Risk Analysis",
    "Investor Analytics",
    "SIP Analytics"
])

# --------------------------------------------------
# 1. Overview
# --------------------------------------------------

with overview:
    st.header("Mutual Fund Market Overview")

    latest_aum = 0
    if not aum.empty:
        latest_date = aum["full_date"].max()
        latest_aum = aum.loc[
            aum["full_date"] == latest_date, "aum_crore"
        ].sum()

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Schemes", f"{len(funds):,}")
    c2.metric("Fund Houses", f"{funds['fund_house'].nunique():,}")
    c3.metric("Latest Recorded AUM", f"₹{latest_aum:,.0f} Cr")
    c4.metric("Investor Transactions", f"{len(transactions):,}")

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Fund Category Distribution")
        category_counts = (
            filtered_funds.groupby("category")
            .size().reset_index(name="schemes")
        )
        if not category_counts.empty:
            fig = px.pie(
                category_counts,
                names="category",
                values="schemes",
                hole=0.45
            )
            st.plotly_chart(fig, use_container_width=True)

    with right:
        st.subheader("Assets Under Management by Fund House")
        if not aum.empty:
            latest = aum[aum["full_date"] == aum["full_date"].max()]
            house_aum = (
                latest.groupby("fund_house")["aum_crore"]
                .sum().reset_index()
                .sort_values("aum_crore", ascending=False)
            )
            fig = px.bar(
                house_aum,
                x="fund_house",
                y="aum_crore",
                title="Latest available AUM"
            )
            st.plotly_chart(fig, use_container_width=True)

    st.subheader("Historical NAV Trend")
    scheme_options = sorted(nav["scheme_name"].dropna().unique())
    if scheme_options:
        selected_scheme = st.selectbox(
            "Select a mutual fund",
            scheme_options
        )
        scheme_nav = nav[nav["scheme_name"] == selected_scheme].copy()
        scheme_nav["full_date"] = pd.to_datetime(scheme_nav["full_date"])
        scheme_nav = scheme_nav.sort_values("full_date")

        fig = px.line(
            scheme_nav,
            x="full_date",
            y="nav",
            title=f"NAV History: {selected_scheme}"
        )
        st.plotly_chart(fig, use_container_width=True)

# --------------------------------------------------
# 2. Fund Performance
# --------------------------------------------------

with performance_tab:
    st.header("Fund Performance Analysis")

    if not filtered_performance.empty:
        metric_options = [
            "return_1yr_pct",
            "return_3yr_pct",
            "return_5yr_pct",
            "sharpe_ratio",
            "sortino_ratio"
        ]

        selected_metric = st.selectbox(
            "Choose performance metric",
            metric_options,
            index=1
        )

        top_funds = filtered_performance.nlargest(
            10, selected_metric
        )

        fig = px.bar(
            top_funds.sort_values(selected_metric),
            x=selected_metric,
            y="scheme_name",
            orientation="h",
            color="risk_grade",
            title=f"Top 10 Funds by {selected_metric}"
        )
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("Performance Comparison")
        st.dataframe(
            filtered_performance[
                [
                    "scheme_name", "category", "risk_grade",
                    "return_1yr_pct", "return_3yr_pct",
                    "return_5yr_pct", "sharpe_ratio",
                    "max_drawdown_pct"
                ]
            ].sort_values("return_3yr_pct", ascending=False),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No performance records for this category selection.")

# --------------------------------------------------
# 3. Risk Analysis
# --------------------------------------------------

with risk_tab:
    st.header("Risk Analysis")

    if not var_report.empty:
        st.subheader("Historical VaR and CVaR")
        st.caption(
            "Historical 95% VaR and CVaR are based on the "
            "daily return analysis of 40 schemes."
        )

        risk_columns = [
            c for c in [
                "scheme_name", "risk_grade",
                "VaR_95_pct", "CVaR_95_pct"
            ] if c in var_report.columns
        ]

        if "VaR_95_pct" in var_report.columns:
            fig = px.bar(
                var_report.nsmallest(10, "VaR_95_pct"),
                x="VaR_95_pct",
                y="scheme_name",
                orientation="h",
                color="risk_grade" if "risk_grade" in var_report.columns else None,
                title="10 Funds with Highest Historical Downside Risk"
            )
            st.plotly_chart(fig, use_container_width=True)

        st.dataframe(
            var_report[risk_columns],
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("VaR/CVaR report not found.")

    st.subheader("Sector Concentration (HHI)")
    if not hhi_report.empty:
        hhi_columns = hhi_report.columns.tolist()
        hhi_col = next(
            (c for c in hhi_columns if "hhi" in c.lower()),
            None
        )
        if hhi_col:
            st.dataframe(
                hhi_report.sort_values(hhi_col, ascending=False),
                use_container_width=True,
                hide_index=True
            )
        else:
            st.dataframe(hhi_report, use_container_width=True)
    else:
        st.info("Sector HHI report not found.")

    st.subheader("Fund Risk Metrics")
    st.dataframe(
        filtered_performance[
            [
                c for c in [
                    "scheme_name", "risk_grade", "beta",
                    "std_dev_ann_pct", "max_drawdown_pct",
                    "sharpe_ratio", "sortino_ratio"
                ] if c in filtered_performance.columns
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

# --------------------------------------------------
# 4. Investor Analytics
# --------------------------------------------------

with investor_tab:
    st.header("Investor Analytics")

    c1, c2, c3 = st.columns(3)
    c1.metric("Unique Investors", f"{transactions['investor_id'].nunique():,}")
    c2.metric("Total Transactions", f"{len(transactions):,}")

    invested = transactions[
        transactions["transaction_type"].isin(["SIP", "Lumpsum"])
    ]["amount_inr"].sum()

    c3.metric("Investment Transactions", f"₹{invested:,.0f}")

    st.subheader("Transactions by State")
    state_data = (
        transactions.groupby("state")
        .size().reset_index(name="transactions")
        .sort_values("transactions", ascending=False)
        .head(10)
    )
    fig = px.bar(
        state_data,
        x="state",
        y="transactions",
        title="Top 10 States by Transaction Count"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Investor Cohort Analysis")
    if not cohort_report.empty:
        st.dataframe(
            cohort_report,
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("Investor cohort report not found.")

    st.subheader("SIP Continuity Analysis")
    if not continuity_report.empty:
        if "continuity_status" in continuity_report.columns:
            st.plotly_chart(
                px.pie(
                    continuity_report,
                    names="continuity_status",
                    title="SIP Continuity Status"
                ),
                use_container_width=True
            )
        st.dataframe(
            continuity_report.head(20),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("SIP continuity report not found.")

# --------------------------------------------------
# 5. SIP Analytics
# --------------------------------------------------

with sip_tab:
    st.header("Systematic Investment Plan Analytics")

    sip = sip.copy()
    sip["month"] = pd.to_datetime(sip["month"])
    sip = sip.sort_values("month")

    c1, c2 = st.columns(2)
    c1.metric(
        "Latest SIP Inflow",
        f"₹{sip.iloc[-1]['sip_inflow_crore']:,.0f} Cr"
    )
    c2.metric(
        "Latest Active SIP Accounts",
        f"{sip.iloc[-1]['active_sip_accounts_crore']:,.2f} Cr"
    )

    fig = px.line(
        sip,
        x="month",
        y="sip_inflow_crore",
        markers=True,
        title="Monthly SIP Inflows"
    )
    st.plotly_chart(fig, use_container_width=True)

    fig = px.line(
        sip,
        x="month",
        y="active_sip_accounts_crore",
        markers=True,
        title="Active SIP Accounts"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("SIP Growth by Category")
    fig = px.line(
        categories,
        x="month",
        y="net_inflow_crore",
        color="category",
        title="Monthly Category-wise Net Inflows"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(sip, use_container_width=True, hide_index=True)

# --------------------------------------------------
# Footer
# --------------------------------------------------

st.divider()
st.caption(
    "Bluestock Mutual Fund Analytics Capstone | "
    "Educational analytical dashboard | "
    "Data sourced from the project datasets"
)
