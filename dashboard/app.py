"""
Bluestock MF Analytics Platform
Advanced Streamlit Application

Run:
python -m streamlit run dashboard/app.py
"""

import os
import sqlite3
import hashlib
import secrets
import random
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


# ============================================================
# CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Bluestock MF Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "bluestock_mf.db")


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    .main {
        background-color: #f7f9fc;
    }

    .block-container {
        padding-top: 1.5rem;
    }

    .hero {
        padding: 25px;
        border-radius: 18px;
        background: linear-gradient(
            135deg,
            #0D47A1,
            #1565C0,
            #42A5F5
        );
        color: white;
        margin-bottom: 25px;
    }

    .hero h1 {
        font-size: 38px;
        margin-bottom: 5px;
    }

    .hero p {
        font-size: 17px;
        opacity: 0.9;
    }

    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 3px 12px rgba(0,0,0,0.08);
        border-left: 5px solid #1565C0;
    }

    .auth-box {
        max-width: 500px;
        margin: auto;
        padding: 30px;
        background: white;
        border-radius: 20px;
        box-shadow: 0 5px 25px rgba(0,0,0,0.12);
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# DATABASE
# ============================================================

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def initialize_users():

    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE,
            phone TEXT UNIQUE,
            password_hash TEXT,
            role TEXT DEFAULT 'user',
            created_at TEXT
        )
        """
    )

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS watchlist (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            amfi_code INTEGER,
            created_at TEXT
        )
        """
    )

    conn.commit()
    conn.close()


initialize_users()


# ============================================================
# PASSWORD SECURITY
# ============================================================

def hash_password(password):

    salt = secrets.token_hex(16)

    pwd_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode(),
        salt.encode(),
        100000
    ).hex()

    return f"{salt}${pwd_hash}"


def verify_password(password, stored):

    try:

        salt, saved_hash = stored.split("$")

        pwd_hash = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode(),
            salt.encode(),
            100000
        ).hex()

        return secrets.compare_digest(
            pwd_hash,
            saved_hash
        )

    except Exception:

        return False


# ============================================================
# USER FUNCTIONS
# ============================================================

def create_user(name, email, phone, password):

    conn = get_connection()

    try:

        conn.execute(
            """
            INSERT INTO users
            (name, email, phone, password_hash, role, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                name,
                email.lower().strip(),
                phone.strip(),
                hash_password(password),
                "user",
                datetime.now().isoformat()
            )
        )

        conn.commit()

        return True, "Account created successfully."

    except sqlite3.IntegrityError:

        return False, "Email or phone number already exists."

    finally:

        conn.close()


def login_email(email, password):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT id, name, email, phone, password_hash, role
        FROM users
        WHERE email = ?
        """,
        (email.lower().strip(),)
    ).fetchone()

    conn.close()

    if user and verify_password(password, user[4]):

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3],
            "role": user[5]
        }

    return None


def login_phone(phone):

    conn = get_connection()

    user = conn.execute(
        """
        SELECT id, name, email, phone, role
        FROM users
        WHERE phone = ?
        """,
        (phone.strip(),)
    ).fetchone()

    conn.close()

    if user:

        return {
            "id": user[0],
            "name": user[1],
            "email": user[2],
            "phone": user[3],
            "role": user[4]
        }

    return None


# ============================================================
# OTP
# ============================================================

def generate_otp():

    return str(random.randint(100000, 999999))


# ============================================================

# ============================================================
# DATA LOADING (COMBINED ADVANCED DATASET)
# ============================================================


def load_data():

    with sqlite3.connect(DB_PATH) as conn:

        fund = pd.read_sql(
            "SELECT * FROM dim_fund",
            conn
        )

        nav = pd.read_sql(
            "SELECT * FROM fact_nav",
            conn,
            parse_dates=["date"]
        )

        perf = pd.read_sql(
            """
            SELECT
                f.scheme_name,
                f.fund_house,
                f.category,
                p.*
            FROM fact_performance p
            JOIN dim_fund f
                ON p.amfi_code = f.amfi_code
            """,
            conn
        )

        tx = pd.read_sql(
            "SELECT * FROM fact_transactions",
            conn,
            parse_dates=["date"]
        )

        aum = pd.read_sql(
            "SELECT * FROM fact_aum",
            conn,
            parse_dates=["quarter_end_date"]
        )

        sip = pd.read_sql(
            "SELECT * FROM fact_sip_industry",
            conn,
            parse_dates=["month"]
        )

        bench = pd.read_sql(
            "SELECT * FROM fact_benchmark",
            conn,
            parse_dates=["date"]
        )

        cat_inflows = pd.read_sql(
            "SELECT * FROM fact_category_inflows",
            conn,
            parse_dates=["month"]
        )

    return (
        fund,
        nav,
        perf,
        tx,
        aum,
        sip,
        bench,
        cat_inflows
    )




# Load all datasets
fund, nav, perf, tx, aum, sip, bench, cat_inflows = load_data()

# ============================================================
# DATA COMPATIBILITY / DERIVED COLUMNS
# ============================================================
# Some Bluestock datasets do not contain risk_grade directly.
# Derive it from standard deviation so all dashboard pages can
# use the same field safely.

if "risk_grade" not in perf.columns:
    if "std_dev_pct" in perf.columns:
        perf["risk_grade"] = pd.to_numeric(
            perf["std_dev_pct"], errors="coerce"
        ).apply(
            lambda x: (
                "Unknown" if pd.isna(x)
                else "Low" if x < 10
                else "Moderate" if x < 20
                else "High"
            )
        )
    else:
        perf["risk_grade"] = "Unknown"

if "risk_grade" not in fund.columns:
    if "amfi_code" in fund.columns and "amfi_code" in perf.columns:
        risk_lookup = (
            perf[["amfi_code", "risk_grade"]]
            .drop_duplicates("amfi_code")
        )
        fund = fund.merge(
            risk_lookup,
            on="amfi_code",
            how="left"
        )
    else:
        fund["risk_grade"] = "Unknown"

fund["risk_grade"] = (
    fund["risk_grade"]
    .fillna("Unknown")
    .astype(str)
)



# SESSION STATE
# ============================================================

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "user" not in st.session_state:
    st.session_state.user = None

if "otp" not in st.session_state:
    st.session_state.otp = None

if "otp_phone" not in st.session_state:
    st.session_state.otp_phone = None


# ============================================================
# AUTHENTICATION PAGE
# ============================================================

def authentication_page():

    st.markdown(
        """
        <div class="hero">

        <h1>📊 Bluestock MF</h1>

        <p>
        Advanced Mutual Fund Intelligence Platform
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    left, center, right = st.columns([1, 2, 1])

    with center:

        st.markdown(
            '<div class="auth-box">',
            unsafe_allow_html=True
        )

        tab_login, tab_register, tab_phone = st.tabs(
            [
                "🔐 Login",
                "📝 Register",
                "📱 Phone OTP"
            ]
        )

        # ----------------------------------------------------
        # EMAIL LOGIN
        # ----------------------------------------------------

        with tab_login:

            st.subheader("Welcome back")

            email = st.text_input(
                "Email",
                key="login_email"
            )

            password = st.text_input(
                "Password",
                type="password",
                key="login_password"
            )

            if st.button(
                "Login",
                type="primary",
                use_container_width=True
            ):

                user = login_email(
                    email,
                    password
                )

                if user:

                    st.session_state.logged_in = True
                    st.session_state.user = user

                    st.rerun()

                else:

                    st.error(
                        "Invalid email or password."
                    )

        # ----------------------------------------------------
        # REGISTER
        # ----------------------------------------------------

        with tab_register:

            st.subheader("Create your account")

            name = st.text_input(
                "Full Name"
            )

            email = st.text_input(
                "Email Address"
            )

            phone = st.text_input(
                "Phone Number",
                placeholder="+91XXXXXXXXXX"
            )

            password = st.text_input(
                "Password",
                type="password"
            )

            confirm = st.text_input(
                "Confirm Password",
                type="password"
            )

            if st.button(
                "Create Account",
                type="primary",
                use_container_width=True
            ):

                if not name or not email or not phone:

                    st.error(
                        "Please fill all required fields."
                    )

                elif len(password) < 6:

                    st.error(
                        "Password must contain at least 6 characters."
                    )

                elif password != confirm:

                    st.error(
                        "Passwords do not match."
                    )

                else:

                    success, message = create_user(
                        name,
                        email,
                        phone,
                        password
                    )

                    if success:

                        st.success(message)

                    else:

                        st.error(message)

        # ----------------------------------------------------
        # PHONE OTP
        # ----------------------------------------------------

        with tab_phone:

            st.subheader("Phone verification")

            phone = st.text_input(
                "Phone Number",
                placeholder="+91XXXXXXXXXX",
                key="otp_phone_input"
            )

            if st.button(
                "Send OTP",
                use_container_width=True
            ):

                user_exists = login_phone(phone)

                if user_exists:

                    otp = generate_otp()

                    st.session_state.otp = otp
                    st.session_state.otp_phone = phone

                    st.success(
                        "OTP generated successfully."
                    )

                    # Development mode only
                    st.info(
                        f"Development OTP: {otp}"
                    )

                else:

                    st.warning(
                        "No account found with this phone number."
                    )

            if st.session_state.otp:

                entered = st.text_input(
                    "Enter OTP",
                    max_chars=6
                )

                if st.button(
                    "Verify OTP",
                    type="primary",
                    use_container_width=True
                ):

                    if entered == st.session_state.otp:

                        user = login_phone(
                            st.session_state.otp_phone
                        )

                        st.session_state.logged_in = True
                        st.session_state.user = user

                        st.session_state.otp = None

                        st.rerun()

                    else:

                        st.error(
                            "Invalid OTP."
                        )

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )


# ============================================================

# SIDEBAR
# ============================================================

def sidebar():

    user = st.session_state.user

    st.sidebar.markdown(
        "## 📊 Bluestock MF"
    )

    st.sidebar.success(
        f"Welcome, {user['name']}"
    )

    st.sidebar.caption(
        user["email"]
    )

    if user["role"] == "admin":

        st.sidebar.info(
            "👑 Administrator"
        )

    page = st.sidebar.radio(
        "Navigation",
        [
            "🏠 Home",
            "🚀 Advanced Dashboard",
            "📊 Industry Analytics",
            "📈 Fund Performance",
            "🔎 Fund Explorer",
            "⚖️ Fund Comparison",
            "💰 SIP Calculator",
            "🎯 Goal Planner",
            "👤 Investor Analytics",
            "⭐ My Watchlist",
            "🤖 AI Insights",
            "⚙️ Profile"
        ]
    )

    st.sidebar.divider()

    if st.sidebar.button(
        "🚪 Logout",
        use_container_width=True
    ):

        st.session_state.logged_in = False
        st.session_state.user = None

        st.rerun()

    return page


# ============================================================

# HOME
# ============================================================

def home_page():

    st.markdown(
        """
        <div class="hero">

        <h1>Mutual Fund Intelligence</h1>

        <p>
        Analyze funds, understand risk, compare performance,
        plan SIPs and make data-driven investment decisions.
        </p>

        </div>
        """,
        unsafe_allow_html=True
    )

    latest_aum = (
        aum["aum_crore"].sum()
        if "aum_crore" in aum.columns
        else 0
    )

    latest_sip = (
        sip["sip_inflow_crore"].sum()
        if "sip_inflow_crore" in sip.columns
        else 0
    )

    schemes = len(fund)

    investors = (
        tx["investor_id"].nunique()
        if "investor_id" in tx.columns
        else 0
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Total AUM",
        f"₹{latest_aum:,.0f} Cr"
    )

    c2.metric(
        "SIP Inflows",
        f"₹{latest_sip:,.0f} Cr"
    )

    c3.metric(
        "Schemes",
        f"{schemes:,}"
    )

    c4.metric(
        "Investors",
        f"{investors:,}"
    )

    st.divider()

    st.subheader(
        "🚀 Platform Features"
    )

    features = [
        ("📊", "Industry Analytics"),
        ("📈", "Fund Performance"),
        ("⚖️", "Fund Comparison"),
        ("💰", "SIP Calculator"),
        ("🎯", "Goal Planner"),
        ("🤖", "AI Insights")
    ]

    cols = st.columns(3)

    for i, (icon, title) in enumerate(features):

        with cols[i % 3]:

            st.info(
                f"{icon} **{title}**"
            )


# ============================================================
# INDUSTRY ANALYTICS
# ============================================================

def industry_page():

    st.title("📊 Industry Analytics")

    if "quarter_end_date" in aum.columns:

        trend = (
            aum.groupby("quarter_end_date")["aum_crore"]
            .sum()
            .reset_index()
        )

        fig = px.line(
            trend,
            x="quarter_end_date",
            y="aum_crore",
            markers=True,
            title="Industry AUM Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "fund_house" in aum.columns:

        house = (
            aum.groupby("fund_house")["aum_crore"]
            .sum()
            .reset_index()
            .sort_values(
                "aum_crore",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            house,
            x="aum_crore",
            y="fund_house",
            orientation="h",
            title="AUM by Fund House"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# FUND PERFORMANCE
# ============================================================

def performance_page():

    st.title("📈 Fund Performance")

    # --------------------------------------------------------
    # Merge performance + fund information
    # --------------------------------------------------------

    if "amfi_code" not in perf.columns:
        st.error("fact_performance does not contain amfi_code.")
        return

    if "amfi_code" not in fund.columns:
        st.error("dim_fund does not contain amfi_code.")
        return

    # perf already contains scheme_name, fund_house and category
    # in the SQL query, but merge missing fund fields only.
    merged = perf.copy()

    for column in ["scheme_name", "fund_house", "category"]:
        if column not in merged.columns and column in fund.columns:
            merged = merged.merge(
                fund[["amfi_code", column]].drop_duplicates("amfi_code"),
                on="amfi_code",
                how="left"
            )

    # --------------------------------------------------------
    # Ensure Risk Grade exists
    # --------------------------------------------------------

    if "risk_grade" not in merged.columns:

        if "std_dev_pct" in merged.columns:

            std_values = pd.to_numeric(
                merged["std_dev_pct"],
                errors="coerce"
            )

            merged["risk_grade"] = std_values.apply(
                lambda x: (
                    "Unknown" if pd.isna(x)
                    else "Low" if x < 10
                    else "Moderate" if x < 20
                    else "High"
                )
            )

        else:

            merged["risk_grade"] = "Unknown"

    merged["risk_grade"] = (
        merged["risk_grade"]
        .fillna("Unknown")
        .astype(str)
    )

    # --------------------------------------------------------
    # Filters
    # --------------------------------------------------------

    c1, c2, c3 = st.columns(3)

    if "fund_house" in merged.columns:
        houses = sorted(
            merged["fund_house"]
            .dropna()
            .astype(str)
            .unique()
        )
    else:
        houses = []

    if "category" in merged.columns:
        categories = sorted(
            merged["category"]
            .dropna()
            .astype(str)
            .unique()
        )
    else:
        categories = []

    selected_house = c1.multiselect(
        "Fund House",
        houses
    )

    selected_category = c2.multiselect(
        "Category",
        categories
    )

    risk_options = sorted(
        merged["risk_grade"].unique()
    )

    selected_risk = c3.multiselect(
        "Risk Grade",
        risk_options
    )

    # --------------------------------------------------------
    # Apply filters
    # --------------------------------------------------------

    filtered = merged.copy()

    if selected_house and "fund_house" in filtered.columns:
        filtered = filtered[
            filtered["fund_house"].isin(selected_house)
        ]

    if selected_category and "category" in filtered.columns:
        filtered = filtered[
            filtered["category"].isin(selected_category)
        ]

    if selected_risk:
        filtered = filtered[
            filtered["risk_grade"].isin(selected_risk)
        ]

    # --------------------------------------------------------
    # Risk vs Return Scatter
    # --------------------------------------------------------

    st.subheader("📊 Risk vs Return")

    if (
        "return_1yr_pct" in filtered.columns
        and "std_dev_pct" in filtered.columns
    ):

        plot_data = filtered.copy()

        plot_data["return_1yr_pct"] = pd.to_numeric(
            plot_data["return_1yr_pct"],
            errors="coerce"
        )

        plot_data["std_dev_pct"] = pd.to_numeric(
            plot_data["std_dev_pct"],
            errors="coerce"
        )

        plot_data = plot_data.dropna(
            subset=[
                "return_1yr_pct",
                "std_dev_pct"
            ]
        )

        if not plot_data.empty:

            scatter_args = {
                "data_frame": plot_data,
                "x": "return_1yr_pct",
                "y": "std_dev_pct",
                "title": "Risk vs 1-Year Return",
            }

            if "category" in plot_data.columns:
                scatter_args["color"] = "category"

            if "scheme_name" in plot_data.columns:
                scatter_args["hover_name"] = "scheme_name"

            if "sharpe_ratio" in plot_data.columns:

                bubble = pd.to_numeric(
                    plot_data["sharpe_ratio"],
                    errors="coerce"
                ).fillna(0)

                # Plotly bubble sizes must be positive.
                plot_data["_bubble_size"] = (
                    bubble.abs() + 0.05
                )

                scatter_args["size"] = "_bubble_size"

            hover_fields = [
                column
                for column in [
                    "fund_house",
                    "category",
                    "sharpe_ratio",
                    "max_drawdown_pct",
                    "risk_grade"
                ]
                if column in plot_data.columns
            ]

            if hover_fields:
                scatter_args["hover_data"] = hover_fields

            fig = px.scatter(
                **scatter_args
            )

            fig.update_traces(
                marker=dict(
                    size=12,
                    opacity=0.80
                )
            )

            fig.update_layout(
                xaxis_title="1-Year Return (%)",
                yaxis_title="Standard Deviation (%)",
                hovermode="closest",
                height=550
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.warning(
                "No valid risk/return records match the selected filters."
            )

    else:

        st.warning(
            "The performance dataset does not contain "
            "return_1yr_pct and/or std_dev_pct."
        )

    # --------------------------------------------------------
    # Fund Scorecard
    # --------------------------------------------------------

    st.subheader("🏆 Fund Scorecard")

    score = filtered.copy()

    # Return
    if "return_1yr_pct" in score.columns:
        score["return_score"] = pd.to_numeric(
            score["return_1yr_pct"],
            errors="coerce"
        ).fillna(0)
    else:
        score["return_score"] = 0

    # Sharpe
    if "sharpe_ratio" in score.columns:
        score["sharpe_score"] = pd.to_numeric(
            score["sharpe_ratio"],
            errors="coerce"
        ).fillna(0)
    else:
        score["sharpe_score"] = 0

    # Risk
    if "std_dev_pct" in score.columns:
        score["risk_score"] = pd.to_numeric(
            score["std_dev_pct"],
            errors="coerce"
        ).fillna(0)
    else:
        score["risk_score"] = 0

    score["fund_score"] = (
        score["return_score"] * 0.50
        + score["sharpe_score"] * 10 * 0.30
        - score["risk_score"] * 0.20
    )

    score = score.sort_values(
        "fund_score",
        ascending=False
    )

    display_columns = [
        "scheme_name",
        "fund_house",
        "category",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "cagr_pct",
        "std_dev_pct",
        "sharpe_ratio",
        "max_drawdown_pct",
        "risk_grade",
        "fund_score"
    ]

    display_columns = [
        column
        for column in display_columns
        if column in score.columns
    ]

    if display_columns:

        st.dataframe(
            score[display_columns],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning(
            "No performance columns are available to display."
        )



# ============================================================
# FUND EXPLORER
# ============================================================

def explorer_page():

    st.title("🔎 Fund Explorer")

    search = st.text_input(
        "Search fund"
    )

    data = fund.copy()

    if search:

        mask = (
            data["scheme_name"]
            .str.contains(
                search,
                case=False,
                na=False
            )
        )

        data = data[mask]

    category = st.selectbox(
        "Category",
        ["All"] +
        sorted(
            fund["category"].dropna().unique()
        )
    )

    if category != "All":

        data = data[
            data["category"] == category
        ]

    st.dataframe(
        data,
        use_container_width=True,
        hide_index=True
    )


# ============================================================
# FUND COMPARISON
# ============================================================

def comparison_page():

    st.title("⚖️ Fund Comparison")

    names = fund["scheme_name"].dropna().tolist()

    selected = st.multiselect(
        "Select up to 4 funds",
        names,
        max_selections=4
    )

    if not selected:

        st.info(
            "Select funds to compare."
        )

        return

    selected_codes = fund[
        fund["scheme_name"].isin(selected)
    ]["amfi_code"]

    data = perf[
        perf["amfi_code"].isin(
            selected_codes
        )
    ].copy()

    cols = [
        "scheme_name",
        "category",
        "return_1yr_pct",
        "return_3yr_pct",
        "return_5yr_pct",
        "cagr_pct",
        "sharpe_ratio",
        "std_dev_pct",
        "max_drawdown_pct"
    ]

    st.dataframe(
        data[cols],
        use_container_width=True,
        hide_index=True
    )

    fig = px.bar(
        data,
        x="scheme_name",
        y="return_1yr_pct",
        color="category",
        title="1-Year Return Comparison"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# SIP CALCULATOR
# ============================================================

def sip_page():

    st.title("💰 SIP Calculator")

    monthly = st.number_input(
        "Monthly SIP (₹)",
        min_value=500,
        value=5000,
        step=500
    )

    annual_return = st.slider(
        "Expected annual return (%)",
        1.0,
        30.0,
        12.0
    )

    years = st.slider(
        "Investment period (years)",
        1,
        40,
        10
    )

    months = years * 12

    monthly_rate = annual_return / 100 / 12

    future_value = (
        monthly *
        (
            ((1 + monthly_rate) ** months - 1)
            / monthly_rate
        ) *
        (1 + monthly_rate)
    )

    invested = monthly * months

    profit = future_value - invested

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Invested",
        f"₹{invested:,.0f}"
    )

    c2.metric(
        "Estimated Value",
        f"₹{future_value:,.0f}"
    )

    c3.metric(
        "Estimated Gain",
        f"₹{profit:,.0f}"
    )

    data = []

    balance = 0

    for month in range(1, months + 1):

        balance = (
            balance * (1 + monthly_rate)
            + monthly
        )

        data.append(
            {
                "Month": month,
                "Value": balance
            }
        )

    chart = pd.DataFrame(data)

    fig = px.line(
        chart,
        x="Month",
        y="Value",
        title="SIP Growth Projection"
    )

    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ============================================================
# GOAL PLANNER
# ============================================================

def goal_page():

    st.title("🎯 Goal Planner")

    goal = st.number_input(
        "Financial goal amount (₹)",
        min_value=10000,
        value=1000000,
        step=10000
    )

    years = st.slider(
        "Years to goal",
        1,
        40,
        10
    )

    return_rate = st.slider(
        "Expected annual return (%)",
        1.0,
        30.0,
        12.0
    )

    r = return_rate / 100 / 12
    n = years * 12

    sip = goal * r / (
        ((1 + r) ** n - 1)
        * (1 + r)
    )

    st.metric(
        "Required Monthly SIP",
        f"₹{sip:,.0f}"
    )

    st.info(
        "This is a mathematical projection, not investment advice."
    )


# ============================================================
# INVESTOR ANALYTICS
# ============================================================

def investor_page():

    st.title("👤 Investor Analytics")

    c1, c2, c3 = st.columns(3)

    if "state" in tx.columns:

        state = (
            tx.groupby("state")["amount"]
            .sum()
            .reset_index()
            .sort_values(
                "amount",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            state,
            x="amount",
            y="state",
            orientation="h",
            title="Transaction Amount by State"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "transaction_type" in tx.columns:

        split = (
            tx.groupby(
                "transaction_type"
            )["amount"]
            .sum()
            .reset_index()
        )

        fig = px.pie(
            split,
            names="transaction_type",
            values="amount",
            hole=0.5,
            title="Transaction Type Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    if "age" in tx.columns:

        tx2 = tx.copy()

        tx2["age_group"] = pd.cut(
            tx2["age"],
            bins=[0, 25, 35, 45, 55, 100],
            labels=[
                "<25",
                "25-35",
                "36-45",
                "46-55",
                "55+"
            ]
        )

        age = (
            tx2.groupby(
                "age_group",
                observed=False
            )["amount"]
            .mean()
            .reset_index()
        )

        fig = px.bar(
            age,
            x="age_group",
            y="amount",
            title="Average Transaction by Age Group"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


# ============================================================
# WATCHLIST
# ============================================================

def watchlist_page():

    st.title("⭐ My Watchlist")

    user_id = st.session_state.user["id"]

    conn = get_connection()

    rows = conn.execute(
        """
        SELECT w.amfi_code,
               f.scheme_name,
               f.fund_house,
               f.category
        FROM watchlist w
        JOIN dim_fund f
        ON w.amfi_code = f.amfi_code
        WHERE w.user_id = ?
        """,
        (user_id,)
    ).fetchall()

    conn.close()

    if not rows:

        st.info(
            "Your watchlist is empty."
        )

    else:

        df = pd.DataFrame(
            rows,
            columns=[
                "AMFI Code",
                "Fund",
                "Fund House",
                "Category"
            ]
        )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# AI INSIGHTS
# ============================================================

def ai_page():

    st.title("🤖 AI Fund Insights")

    merged = perf.copy()

    selected = st.selectbox(
        "Choose a fund",
        merged["scheme_name"].dropna().tolist()
    )

    row = merged[
        merged["scheme_name"] == selected
    ].iloc[0]

    ret = row["return_1yr_pct"]
    risk = row["std_dev_pct"]
    sharpe = row["sharpe_ratio"]

    st.subheader(
        "📋 Fund Analysis"
    )

    if ret >= 15:

        performance_text = (
            "The fund has shown strong recent performance."
        )

    elif ret >= 8:

        performance_text = (
            "The fund has delivered moderate recent performance."
        )

    else:

        performance_text = (
            "The fund's recent return has been relatively weak."
        )

    if risk >= 20:

        risk_text = (
            "Volatility is relatively high."
        )

    elif risk >= 12:

        risk_text = (
            "The fund has moderate volatility."
        )

    else:

        risk_text = (
            "The fund has relatively lower volatility."
        )

    if sharpe >= 1:

        efficiency_text = (
            "Risk-adjusted performance is strong."
        )

    elif sharpe >= 0.5:

        efficiency_text = (
            "Risk-adjusted performance is reasonable."
        )

    else:

        efficiency_text = (
            "Risk-adjusted performance needs careful evaluation."
        )

    st.success(
        f"""
        **Performance:** {performance_text}

        **Risk:** {risk_text}

        **Risk-adjusted return:** {efficiency_text}
        """
    )

    st.metric(
        "1-Year Return",
        f"{ret:.2f}%"
    )

    st.metric(
        "Volatility",
        f"{risk:.2f}%"
    )

    st.metric(
        "Sharpe Ratio",
        f"{sharpe:.2f}"
    )

    st.warning(
        "These insights are based on historical data and are not personalized financial advice."
    )


# ============================================================
# PROFILE
# ============================================================

def profile_page():

    st.title("⚙️ Profile")

    user = st.session_state.user

    st.write(
        f"### 👤 {user['name']}"
    )

    st.write(
        f"**Email:** {user['email']}"
    )

    st.write(
        f"**Phone:** {user['phone']}"
    )

    st.write(
        f"**Role:** {user['role']}"
    )


# ============================================================

# ============================================================
# ADVANCED DASHBOARD
# ============================================================


def advanced_dashboard_page():


    # =========================================================
    # HEADER
    # =========================================================

    st.title("📈 Bluestock Fintech - Mutual Fund Analytics Platform")

    st.markdown(
        """
        **End-to-End Data Engineering, Mutual Fund Analytics,
        Investor Intelligence & Business Intelligence Dashboard**
        """
    )


    # =========================================================
    # SIDEBAR
    # =========================================================

    st.sidebar.markdown("## 📊 Bluestock Analytics")

    st.sidebar.caption(
        "Mutual Fund Intelligence Platform"
    )

    st.sidebar.markdown("---")


    # =========================================================
    # FUND FILTERS
    # =========================================================

    st.sidebar.markdown("### 🔍 Fund Filters")


    # Search fund
    fund_search = st.sidebar.text_input(
        "Search Fund",
        placeholder="Enter scheme name..."
    )


    # Fund House
    fund_houses = sorted(
        fund["fund_house"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_house = st.sidebar.multiselect(
        "Fund House",
        fund_houses,
        placeholder="All Fund Houses"
    )


    # Category
    categories = sorted(
        fund["category"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_category = st.sidebar.multiselect(
        "Category",
        categories,
        placeholder="All Categories"
    )


    # Risk Grade
    risk_grades = sorted(
        fund["risk_grade"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_risk = st.sidebar.multiselect(
        "Risk Grade",
        risk_grades,
        placeholder="All Risk Grades"
    )


    # Fund Manager
    fund_managers = sorted(
        fund["fund_manager"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_manager = st.sidebar.multiselect(
        "Fund Manager",
        fund_managers,
        placeholder="All Fund Managers"
    )


    # =========================================================
    # PERFORMANCE FILTERS
    # =========================================================

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 💰 Cost & Performance"
    )


    # Expense Ratio
    expense_values = fund[
        "expense_ratio_pct"
    ].dropna()

    expense_min = float(
        expense_values.min()
    )

    expense_max = float(
        expense_values.max()
    )

    expense_range = st.sidebar.slider(
        "Expense Ratio (%)",
        min_value=expense_min,
        max_value=expense_max,
        value=(
            expense_min,
            expense_max
        ),
        step=0.05
    )


    # 1-Year Return
    valid_returns = perf[
        "return_1yr_pct"
    ].dropna()

    if not valid_returns.empty:

        return_min = float(
            valid_returns.min()
        )

        return_max = float(
            valid_returns.max()
        )

        return_range = st.sidebar.slider(
            "1-Year Return (%)",
            min_value=return_min,
            max_value=return_max,
            value=(
                return_min,
                return_max
            ),
            step=0.5
        )

    else:
        return_range = None


    # Sharpe Ratio
    valid_sharpe = perf[
        "sharpe_ratio"
    ].dropna()

    if not valid_sharpe.empty:

        sharpe_min = float(
            valid_sharpe.min()
        )

        sharpe_max = float(
            valid_sharpe.max()
        )

        sharpe_range = st.sidebar.slider(
            "Sharpe Ratio",
            min_value=sharpe_min,
            max_value=sharpe_max,
            value=(
                sharpe_min,
                sharpe_max
            ),
            step=0.05
        )

    else:
        sharpe_range = None


    # =========================================================
    # DATE FILTER
    # =========================================================

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 📅 NAV Date Filter"
    )

    min_date = nav[
        "date"
    ].min().date()

    max_date = nav[
        "date"
    ].max().date()

    date_range = st.sidebar.date_input(
        "Date Range",
        value=(
            min_date,
            max_date
        ),
        min_value=min_date,
        max_value=max_date
    )


    # =========================================================
    # INVESTOR FILTERS
    # =========================================================

    st.sidebar.markdown("---")

    st.sidebar.markdown(
        "### 👥 Investor Filters"
    )


    # State
    states = sorted(
        tx["state"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_states = st.sidebar.multiselect(
        "State",
        states,
        placeholder="All States"
    )


    # Tier
    tiers = sorted(
        tx["tier"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_tiers = st.sidebar.multiselect(
        "City Tier",
        tiers,
        placeholder="All Tiers"
    )


    # Gender
    genders = sorted(
        tx["gender"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_gender = st.sidebar.multiselect(
        "Gender",
        genders,
        placeholder="All"
    )


    # Income
    income_slabs = sorted(
        tx["income_slab"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_income = st.sidebar.multiselect(
        "Income Slab",
        income_slabs,
        placeholder="All Income Groups"
    )


    # KYC
    kyc_values = sorted(
        tx["kyc_status"]
        .dropna()
        .unique()
        .tolist()
    )

    selected_kyc = st.sidebar.multiselect(
        "KYC Status",
        kyc_values,
        placeholder="All"
    )


    # Age
    age_values = tx[
        "age"
    ].dropna()

    age_min = int(
        age_values.min()
    )

    age_max = int(
        age_values.max()
    )

    age_range = st.sidebar.slider(
        "Investor Age",
        min_value=age_min,
        max_value=age_max,
        value=(
            age_min,
            age_max
        )
    )


    # =========================================================
    # APPLY FUND FILTERS
    # =========================================================

    filtered_fund = fund.copy()


    if fund_search:

        filtered_fund = filtered_fund[
            filtered_fund[
                "scheme_name"
            ].str.contains(
                fund_search,
                case=False,
                na=False
            )
        ]


    if selected_house:

        filtered_fund = filtered_fund[
            filtered_fund[
                "fund_house"
            ].isin(
                selected_house
            )
        ]


    if selected_category:

        filtered_fund = filtered_fund[
            filtered_fund[
                "category"
            ].isin(
                selected_category
            )
        ]


    if selected_risk:

        filtered_fund = filtered_fund[
            filtered_fund[
                "risk_grade"
            ].isin(
                selected_risk
            )
        ]


    if selected_manager:

        filtered_fund = filtered_fund[
            filtered_fund[
                "fund_manager"
            ].isin(
                selected_manager
            )
        ]


    filtered_fund = filtered_fund[
        filtered_fund[
            "expense_ratio_pct"
        ].between(
            expense_range[0],
            expense_range[1]
        )
    ]


    # =========================================================
    # FILTER PERFORMANCE
    # =========================================================

    amfi_codes = filtered_fund[
        "amfi_code"
    ].tolist()


    filtered_perf = perf[
        perf[
            "amfi_code"
        ].isin(
            amfi_codes
        )
    ].copy()


    if return_range is not None:

        filtered_perf = filtered_perf[
            filtered_perf[
                "return_1yr_pct"
            ].between(
                return_range[0],
                return_range[1]
            )
        ]


    if sharpe_range is not None:

        filtered_perf = filtered_perf[
            filtered_perf[
                "sharpe_ratio"
            ].between(
                sharpe_range[0],
                sharpe_range[1]
            )
        ]


    performance_codes = filtered_perf[
        "amfi_code"
    ].tolist()


    filtered_fund = filtered_fund[
        filtered_fund[
            "amfi_code"
        ].isin(
            performance_codes
        )
    ]


    amfi_codes = filtered_fund[
        "amfi_code"
    ].tolist()


    # =========================================================
    # FILTER NAV
    # =========================================================

    if len(date_range) == 2:

        start_date = pd.Timestamp(
            date_range[0]
        )

        end_date = pd.Timestamp(
            date_range[1]
        )

    else:

        start_date = nav[
            "date"
        ].min()

        end_date = nav[
            "date"
        ].max()


    filtered_nav = nav[
        (
            nav[
                "amfi_code"
            ].isin(
                amfi_codes
            )
        )
        &
        (
            nav[
                "date"
            ] >= start_date
        )
        &
        (
            nav[
                "date"
            ] <= end_date
        )
    ].copy()


    # =========================================================
    # FILTER INVESTOR TRANSACTIONS
    # =========================================================

    filtered_tx = tx.copy()


    if selected_states:

        filtered_tx = filtered_tx[
            filtered_tx[
                "state"
            ].isin(
                selected_states
            )
        ]


    if selected_tiers:

        filtered_tx = filtered_tx[
            filtered_tx[
                "tier"
            ].isin(
                selected_tiers
            )
        ]


    if selected_gender:

        filtered_tx = filtered_tx[
            filtered_tx[
                "gender"
            ].isin(
                selected_gender
            )
        ]


    if selected_income:

        filtered_tx = filtered_tx[
            filtered_tx[
                "income_slab"
            ].isin(
                selected_income
            )
        ]


    if selected_kyc:

        filtered_tx = filtered_tx[
            filtered_tx[
                "kyc_status"
            ].isin(
                selected_kyc
            )
        ]


    filtered_tx = filtered_tx[
        filtered_tx[
            "age"
        ].between(
            age_range[0],
            age_range[1]
        )
    ]


    # =========================================================
    # FILTER SUMMARY
    # =========================================================

    st.caption(
        f"📊 Showing "
        f"{len(filtered_fund):,} funds • "
        f"{len(filtered_tx):,} transactions • "
        f"{len(filtered_nav):,} NAV records"
    )


    # =========================================================
    # EXECUTIVE KPIs
    # =========================================================

    st.header(
        "Executive KPIs"
    )


    col1, col2, col3, col4 = st.columns(
        4
    )


    # Latest AUM
    if not aum.empty:

        latest_aum_date = aum[
            "quarter_end_date"
        ].max()

        latest_aum = aum.loc[
            aum[
                "quarter_end_date"
            ] == latest_aum_date,
            "aum_crore"
        ].sum()

    else:
        latest_aum = 0


    # Latest SIP
    if not sip.empty:

        latest_sip_date = sip[
            "month"
        ].max()

        latest_sip = sip.loc[
            sip[
                "month"
            ] == latest_sip_date,
            "sip_inflow_crore"
        ].sum()

    else:
        latest_sip = 0


    col1.metric(
        "Latest Industry AUM",
        f"₹{latest_aum:,.0f} Cr"
    )

    col2.metric(
        "Latest SIP Inflow",
        f"₹{latest_sip:,.0f} Cr"
    )

    col3.metric(
        "Schemes Selected",
        len(filtered_fund)
    )

    col4.metric(
        "Investors",
        filtered_tx[
            "investor_id"
        ].nunique()
    )


    # =========================================================
    # SECOND KPI ROW
    # =========================================================

    k1, k2, k3, k4 = st.columns(
        4
    )


    avg_return = (
        filtered_perf[
            "return_1yr_pct"
        ].mean()
        if not filtered_perf.empty
        else 0
    )


    avg_sharpe = (
        filtered_perf[
            "sharpe_ratio"
        ].mean()
        if not filtered_perf.empty
        else 0
    )


    avg_expense = (
        filtered_fund[
            "expense_ratio_pct"
        ].mean()
        if not filtered_fund.empty
        else 0
    )


    transaction_value = filtered_tx[
        "amount"
    ].sum()


    k1.metric(
        "Avg 1Y Return",
        f"{avg_return:.2f}%"
    )

    k2.metric(
        "Avg Sharpe Ratio",
        f"{avg_sharpe:.2f}"
    )

    k3.metric(
        "Avg Expense Ratio",
        f"{avg_expense:.2f}%"
    )

    k4.metric(
        "Transaction Value",
        f"₹{transaction_value:,.0f}"
    )


    # =========================================================
    # ANALYTICS TABS
    # =========================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📊 Fund Performance",
            "📈 NAV Trends",
            "👥 Investor Insights",
            "🏦 Industry Trends"
        ]
    )


     # =========================================================
    # TAB 1 - FUND PERFORMANCE
    # =========================================================

    with tab1:

        st.subheader("Risk-Return Analysis")

        if not filtered_perf.empty:

            fig = px.scatter(
                filtered_perf,
                x="std_dev_pct",
                y="return_1yr_pct",
                color="category",
                hover_name="scheme_name",
                hover_data=[
                    "fund_house",
                    "sharpe_ratio",
                    "alpha_pct",
                    "beta"
                ],
                title="Risk vs 1-Year Return"
            )

            fig.update_traces(
                marker=dict(
                    size=12,
                    opacity=0.8,
                    line=dict(width=1)
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:
            st.warning("No funds match the selected filters.")

            # =========================================================
    # TAB 2 - NAV TRENDS
    # =========================================================

    with tab2:

        st.subheader("📈 NAV Trends & Market Comparison")

        if filtered_nav.empty:

            st.warning(
                "No NAV data available for the selected filters."
            )

        else:

            # Add scheme names to NAV data
            nav_chart = filtered_nav.merge(
                fund[
                    [
                        "amfi_code",
                        "scheme_name",
                        "fund_house",
                        "category"
                    ]
                ],
                on="amfi_code",
                how="left"
            )

            # =================================================
            # NAV KPIs
            # =================================================

            latest_nav_data = (
                nav_chart
                .sort_values("date")
                .groupby("amfi_code")
                .tail(1)
            )

            nav1, nav2, nav3, nav4 = st.columns(4)

            nav1.metric(
                "NAV Records",
                f"{len(nav_chart):,}"
            )

            nav2.metric(
                "Funds Tracked",
                f"{nav_chart['amfi_code'].nunique():,}"
            )

            nav3.metric(
                "Average Latest NAV",
                f"₹{latest_nav_data['nav'].mean():,.2f}"
            )

            nav4.metric(
                "Highest Latest NAV",
                f"₹{latest_nav_data['nav'].max():,.2f}"
            )

            st.markdown("---")

            # =================================================
            # FUND SELECTOR
            # =================================================

            available_funds = sorted(
                nav_chart["scheme_name"]
                .dropna()
                .unique()
                .tolist()
            )

            default_funds = available_funds[:5]

            selected_nav_funds = st.multiselect(
                "Select Funds to Compare",
                options=available_funds,
                default=default_funds,
                key="nav_fund_selector"
            )

            if selected_nav_funds:

                nav_display = nav_chart[
                    nav_chart["scheme_name"].isin(
                        selected_nav_funds
                    )
                ].copy()

            else:

                nav_display = nav_chart.copy()

            # =================================================
            # NAV MOVEMENT
            # =================================================

            st.subheader("NAV Movement")

            fig = px.line(
                nav_display,
                x="date",
                y="nav",
                color="scheme_name",
                hover_data=[
                    "fund_house",
                    "category",
                    "amfi_code"
                ],
                title="Mutual Fund NAV Over Time",
                labels={
                    "date": "Date",
                    "nav": "NAV (₹)",
                    "scheme_name": "Fund"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                legend_title="Scheme",
                height=550
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # NORMALIZED FUND PERFORMANCE
            # =================================================

            st.subheader("Normalized Fund Performance")

            normalized_nav = (
                nav_display
                .sort_values(
                    [
                        "amfi_code",
                        "date"
                    ]
                )
                .copy()
            )

            normalized_nav["normalized_nav"] = (
                normalized_nav
                .groupby("amfi_code")["nav"]
                .transform(
                    lambda x: (
                        x / x.iloc[0] * 100
                        if len(x) > 0
                        else x
                    )
                )
            )

            fig = px.line(
                normalized_nav,
                x="date",
                y="normalized_nav",
                color="scheme_name",
                title="Fund Growth — Starting Value = 100",
                labels={
                    "normalized_nav":
                        "Normalized Value",
                    "date":
                        "Date",
                    "scheme_name":
                        "Fund"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # DAILY RETURNS
            # =================================================

            st.subheader("Daily Return Analysis")

            if "daily_return_pct" in nav_display.columns:

                return_data = nav_display.dropna(
                    subset=["daily_return_pct"]
                )

                if not return_data.empty:

                    fig = px.line(
                        return_data,
                        x="date",
                        y="daily_return_pct",
                        color="scheme_name",
                        title="Daily NAV Return (%)",
                        labels={
                            "daily_return_pct":
                                "Daily Return (%)",
                            "scheme_name":
                                "Fund"
                        }
                    )

                    fig.add_hline(
                        y=0,
                        line_dash="dash"
                    )

                    fig.update_layout(
                        hovermode="x unified",
                        height=450
                    )

                    st.plotly_chart(
                        fig,
                        use_container_width=True
                    )

            # =================================================
            # BENCHMARK COMPARISON
            # =================================================

            st.subheader("📊 Market Benchmark Comparison")

            benchmark_names = [
                "Nifty 50",
                "Nifty 100",
                "Nifty Midcap 150",
                "BSE SmallCap"
            ]

            available_benchmarks = [
                name
                for name in benchmark_names
                if name in bench["index_name"].unique()
            ]

            selected_benchmarks = st.multiselect(
                "Select Benchmarks",
                available_benchmarks,
                default=available_benchmarks,
                key="benchmark_selector"
            )

            bench_selected = bench[
                bench["index_name"].isin(
                    selected_benchmarks
                )
            ].copy()

            # Use same date range as NAV
            bench_selected = bench_selected[
                (bench_selected["date"] >= start_date)
                &
                (bench_selected["date"] <= end_date)
            ]

            if not bench_selected.empty:

                bench_selected = (
                    bench_selected
                    .sort_values(
                        [
                            "index_name",
                            "date"
                        ]
                    )
                )

                bench_selected["normalized"] = (
                    bench_selected
                    .groupby(
                        "index_name"
                    )["close_value"]
                    .transform(
                        lambda x:
                        x / x.iloc[0] * 100
                    )
                )

                fig = px.line(
                    bench_selected,
                    x="date",
                    y="normalized",
                    color="index_name",
                    title="Benchmark Performance — Starting Value = 100",
                    labels={
                        "normalized":
                            "Normalized Value",
                        "index_name":
                            "Benchmark"
                    }
                )

                fig.update_layout(
                    hovermode="x unified",
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "No benchmark data available for this date range."
                )

            # =================================================
            # LATEST NAV TABLE
            # =================================================

            st.subheader("Latest NAV Snapshot")

            latest_table = (
                nav_chart
                .sort_values("date")
                .groupby("amfi_code")
                .tail(1)
                [
                    [
                        "scheme_name",
                        "fund_house",
                        "category",
                        "date",
                        "nav",
                        "daily_return_pct"
                    ]
                ]
                .sort_values(
                    "nav",
                    ascending=False
                )
            )

            st.dataframe(
                latest_table,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "⬇️ Download NAV Data",
                data=nav_display.to_csv(
                    index=False
                ),
                file_name="nav_analysis.csv",
                mime="text/csv",
                key="download_nav"
            )

            # =========================================================
    # TAB 3 - INVESTOR INSIGHTS
    # =========================================================

    with tab3:

        st.subheader("👥 Investor Intelligence & Transaction Analytics")

        if filtered_tx.empty:

            st.warning(
                "No transactions match the selected investor filters."
            )

        else:

            # =================================================
            # INVESTOR KPIs
            # =================================================

            total_investors = filtered_tx[
                "investor_id"
            ].nunique()

            total_transactions = len(
                filtered_tx
            )

            total_value = filtered_tx[
                "amount"
            ].sum()

            avg_transaction = filtered_tx[
                "amount"
            ].mean()

            i1, i2, i3, i4 = st.columns(4)

            i1.metric(
                "Unique Investors",
                f"{total_investors:,}"
            )

            i2.metric(
                "Transactions",
                f"{total_transactions:,}"
            )

            i3.metric(
                "Transaction Value",
                f"₹{total_value:,.0f}"
            )

            i4.metric(
                "Avg Transaction",
                f"₹{avg_transaction:,.0f}"
            )

            st.markdown("---")

            # =================================================
            # TRANSACTION TYPE
            # =================================================

            left, right = st.columns(2)

            with left:

                st.subheader(
                    "Transaction Mix"
                )

                tx_type = (
                    filtered_tx
                    .groupby(
                        "transaction_type"
                    )["amount"]
                    .sum()
                    .reset_index()
                )

                fig = px.pie(
                    tx_type,
                    names="transaction_type",
                    values="amount",
                    hole=0.55,
                    title="Investment Value by Transaction Type"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # =================================================
            # CITY TIER
            # =================================================

            with right:

                st.subheader(
                    "City Tier Analysis"
                )

                tier_data = (
                    filtered_tx
                    .groupby("tier")["amount"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "amount",
                        ascending=False
                    )
                )

                fig = px.bar(
                    tier_data,
                    x="tier",
                    y="amount",
                    title="Transaction Value by City Tier",
                    labels={
                        "amount":
                            "Transaction Amount (₹)",
                        "tier":
                            "City Tier"
                    }
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # =================================================
            # GEOGRAPHIC DISTRIBUTION
            # =================================================

            st.subheader(
                "🗺️ Geographic Investor Distribution"
            )

            geo = (
                filtered_tx
                .groupby("state")
                .agg(
                    transaction_value=(
                        "amount",
                        "sum"
                    ),
                    transactions=(
                        "tx_id",
                        "count"
                    ),
                    investors=(
                        "investor_id",
                        "nunique"
                    )
                )
                .reset_index()
                .sort_values(
                    "transaction_value",
                    ascending=False
                )
                .head(15)
            )

            fig = px.bar(
                geo,
                x="transaction_value",
                y="state",
                orientation="h",
                hover_data=[
                    "investors",
                    "transactions"
                ],
                title="Top 15 States by Investment Value",
                labels={
                    "transaction_value":
                        "Transaction Value (₹)",
                    "state":
                        "State"
                }
            )

            fig.update_layout(
                yaxis={
                    "categoryorder":
                        "total ascending"
                },
                height=550
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # DEMOGRAPHIC ANALYSIS
            # =================================================

            st.subheader(
                "Investor Demographics"
            )

            demo1, demo2 = st.columns(2)

            # Gender
            with demo1:

                gender_data = (
                    filtered_tx
                    .groupby("gender")
                    .agg(
                        amount=(
                            "amount",
                            "sum"
                        ),
                        investors=(
                            "investor_id",
                            "nunique"
                        )
                    )
                    .reset_index()
                )

                fig = px.pie(
                    gender_data,
                    names="gender",
                    values="amount",
                    hole=0.5,
                    title="Investment Value by Gender"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # Income
            with demo2:

                income_data = (
                    filtered_tx
                    .groupby(
                        "income_slab"
                    )["amount"]
                    .sum()
                    .reset_index()
                    .sort_values(
                        "amount",
                        ascending=False
                    )
                )

                fig = px.bar(
                    income_data,
                    x="income_slab",
                    y="amount",
                    title="Investment Value by Income Slab",
                    labels={
                        "income_slab":
                            "Income Slab",
                        "amount":
                            "Investment Value (₹)"
                    }
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # =================================================
            # AGE ANALYSIS
            # =================================================

            st.subheader(
                "Age Distribution"
            )

            fig = px.histogram(
                filtered_tx,
                x="age",
                nbins=20,
                title="Investor Age Distribution",
                labels={
                    "age":
                        "Investor Age"
                }
            )

            fig.update_layout(
                bargap=0.05
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # KYC ANALYSIS
            # =================================================

            kyc1, kyc2 = st.columns(2)

            with kyc1:

                st.subheader(
                    "KYC Status"
                )

                kyc_data = (
                    filtered_tx
                    .groupby("kyc_status")
                    .agg(
                        transactions=(
                            "tx_id",
                            "count"
                        ),
                        amount=(
                            "amount",
                            "sum"
                        )
                    )
                    .reset_index()
                )

                fig = px.pie(
                    kyc_data,
                    names="kyc_status",
                    values="transactions",
                    hole=0.55,
                    title="KYC Status Distribution"
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # =================================================
            # SIP VS LUMPSUM VS REDEMPTION
            # =================================================

            with kyc2:

                st.subheader(
                    "Investment Behaviour"
                )

                behaviour = (
                    filtered_tx
                    .groupby(
                        "transaction_type"
                    )
                    .agg(
                        transaction_count=(
                            "tx_id",
                            "count"
                        ),
                        total_amount=(
                            "amount",
                            "sum"
                        )
                    )
                    .reset_index()
                )

                fig = px.bar(
                    behaviour,
                    x="transaction_type",
                    y="transaction_count",
                    title="Transactions by Investment Type",
                    labels={
                        "transaction_type":
                            "Transaction Type",
                        "transaction_count":
                            "Transactions"
                    }
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            # =================================================
            # MONTHLY TRANSACTION TREND
            # =================================================

            st.subheader(
                "📈 Investor Activity Over Time"
            )

            tx_trend = filtered_tx.copy()

            tx_trend["month"] = (
                tx_trend["date"]
                .dt.to_period("M")
                .dt.to_timestamp()
            )

            monthly_tx = (
                tx_trend
                .groupby("month")
                .agg(
                    transaction_value=(
                        "amount",
                        "sum"
                    ),
                    transaction_count=(
                        "tx_id",
                        "count"
                    ),
                    active_investors=(
                        "investor_id",
                        "nunique"
                    )
                )
                .reset_index()
            )

            fig = px.line(
                monthly_tx,
                x="month",
                y="transaction_value",
                markers=True,
                title="Monthly Transaction Value",
                hover_data=[
                    "transaction_count",
                    "active_investors"
                ],
                labels={
                    "month":
                        "Month",
                    "transaction_value":
                        "Transaction Value (₹)"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

            # =================================================
            # TOP INVESTORS
            # =================================================

            st.subheader(
                "Top Investor Activity"
            )

            investor_summary = (
                filtered_tx
                .groupby("investor_id")
                .agg(
                    total_investment=(
                        "amount",
                        "sum"
                    ),
                    transactions=(
                        "tx_id",
                        "count"
                    ),
                    state=(
                        "state",
                        "first"
                    ),
                    tier=(
                        "tier",
                        "first"
                    ),
                    age=(
                        "age",
                        "first"
                    ),
                    kyc_status=(
                        "kyc_status",
                        "first"
                    )
                )
                .reset_index()
                .sort_values(
                    "total_investment",
                    ascending=False
                )
                .head(20)
            )

            st.dataframe(
                investor_summary,
                use_container_width=True,
                hide_index=True
            )

            # =================================================
            # DOWNLOAD
            # =================================================

            st.download_button(
                "⬇️ Download Investor Analytics",
                data=filtered_tx.to_csv(
                    index=False
                ),
                file_name="investor_analytics.csv",
                mime="text/csv",
                key="download_investor"
            )

            # TAB 4 - INDUSTRY TRENDS
    # =========================================================

    with tab4:

        st.subheader("🏦 Mutual Fund Industry Trends")

        # =====================================================
        # INDUSTRY KPI CARDS
        # =====================================================

        latest_aum_date = aum["quarter_end_date"].max()

        latest_aum_data = aum[
            aum["quarter_end_date"] == latest_aum_date
        ]

        total_latest_aum = latest_aum_data[
            "aum_crore"
        ].sum()

        latest_sip_date = sip["month"].max()

        latest_sip_data = sip[
            sip["month"] == latest_sip_date
        ]

        latest_sip_value = latest_sip_data[
            "sip_inflow_crore"
        ].sum()

        total_fund_houses = aum[
            "fund_house"
        ].nunique()

        total_schemes = fund[
            "amfi_code"
        ].nunique()

        ind1, ind2, ind3, ind4 = st.columns(4)

        ind1.metric(
            "Industry AUM",
            f"₹{total_latest_aum:,.0f} Cr"
        )

        ind2.metric(
            "Latest SIP Inflow",
            f"₹{latest_sip_value:,.0f} Cr"
        )

        ind3.metric(
            "Fund Houses",
            f"{total_fund_houses:,}"
        )

        ind4.metric(
            "Schemes Tracked",
            f"{total_schemes:,}"
        )

        st.markdown("---")

        # =====================================================
        # AUM TREND
        # =====================================================

        st.subheader("📈 Industry AUM Growth")

        industry_aum = (
            aum
            .groupby("quarter_end_date")["aum_crore"]
            .sum()
            .reset_index()
            .sort_values("quarter_end_date")
        )

        fig = px.line(
            industry_aum,
            x="quarter_end_date",
            y="aum_crore",
            markers=True,
            title="Total Mutual Fund Industry AUM",
            labels={
                "quarter_end_date": "Quarter",
                "aum_crore": "AUM (₹ Crore)"
            }
        )

        fig.update_layout(
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # FUND HOUSE AUM
        # =====================================================

        st.subheader("🏦 Top Fund Houses by AUM")

        latest_fund_house_aum = (
            latest_aum_data
            .groupby("fund_house")["aum_crore"]
            .sum()
            .reset_index()
            .sort_values(
                "aum_crore",
                ascending=False
            )
            .head(15)
        )

        fig = px.bar(
            latest_fund_house_aum,
            x="aum_crore",
            y="fund_house",
            orientation="h",
            title="Top 15 Fund Houses by Latest AUM",
            labels={
                "aum_crore": "AUM (₹ Crore)",
                "fund_house": "Fund House"
            }
        )

        fig.update_layout(
            yaxis={
                "categoryorder": "total ascending"
            },
            height=550
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # FUND HOUSE MARKET SHARE
        # =====================================================

        st.subheader("📊 Fund House Market Share")

        market_share = latest_fund_house_aum.copy()

        fig = px.pie(
            market_share,
            names="fund_house",
            values="aum_crore",
            hole=0.5,
            title="AUM Market Share by Fund House"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # SIP TREND
        # =====================================================

        st.subheader("💰 SIP Industry Growth")

        sip_sorted = sip.sort_values(
            "month"
        ).copy()

        fig = px.line(
            sip_sorted,
            x="month",
            y="sip_inflow_crore",
            markers=True,
            title="Monthly SIP Inflow Trend",
            labels={
                "month": "Month",
                "sip_inflow_crore":
                    "SIP Inflow (₹ Crore)"
            }
        )

        fig.update_layout(
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # SIP ACCOUNT GROWTH
        # =====================================================

        if "active_sip_accounts_lakh" in sip.columns:

            st.subheader(
                "👥 Active SIP Account Growth"
            )

            fig = px.area(
                sip_sorted,
                x="month",
                y="active_sip_accounts_lakh",
                title="Active SIP Accounts",
                labels={
                    "month": "Month",
                    "active_sip_accounts_lakh":
                        "Active SIP Accounts (Lakh)"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                height=450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # =====================================================
        # SIP AUM
        # =====================================================

        if "sip_aum_crore" in sip.columns:

            st.subheader("📈 SIP AUM Growth")

            fig = px.line(
                sip_sorted,
                x="month",
                y="sip_aum_crore",
                markers=True,
                title="SIP Assets Under Management",
                labels={
                    "month": "Month",
                    "sip_aum_crore":
                        "SIP AUM (₹ Crore)"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                height=450
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # =====================================================
        # CATEGORY INFLOWS
        # =====================================================

        st.subheader(
            "📊 Category-wise Fund Flows"
        )

        category_summary = (
            cat_inflows
            .groupby("category")["net_inflow_crore"]
            .sum()
            .reset_index()
            .sort_values(
                "net_inflow_crore",
                ascending=False
            )
        )

        fig = px.bar(
            category_summary,
            x="category",
            y="net_inflow_crore",
            title="Net Inflows by Mutual Fund Category",
            labels={
                "category": "Fund Category",
                "net_inflow_crore":
                    "Net Inflow (₹ Crore)"
            }
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # CATEGORY INFLOW TREND
        # =====================================================

        st.subheader(
            "📈 Category Inflow Trend"
        )

        category_trend = (
            cat_inflows
            .sort_values("month")
            .copy()
        )

        fig = px.line(
            category_trend,
            x="month",
            y="net_inflow_crore",
            color="category",
            markers=True,
            title="Monthly Net Inflows by Category",
            labels={
                "month": "Month",
                "net_inflow_crore":
                    "Net Inflow (₹ Crore)",
                "category":
                    "Category"
            }
        )

        fig.update_layout(
            hovermode="x unified",
            height=500
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # =====================================================
        # INDUSTRY DASHBOARD - TWO COLUMN VIEW
        # =====================================================

        industry_col1, industry_col2 = st.columns(2)

        # =====================================================
        # AUM GROWTH BY FUND HOUSE
        # =====================================================

        with industry_col1:

            st.subheader(
                "Fund House AUM Growth"
            )

            selected_industry_houses = (
                latest_fund_house_aum[
                    "fund_house"
                ]
                .head(8)
                .tolist()
            )

            aum_trend = aum[
                aum["fund_house"].isin(
                    selected_industry_houses
                )
            ].copy()

            fig = px.line(
                aum_trend,
                x="quarter_end_date",
                y="aum_crore",
                color="fund_house",
                title="AUM Growth - Leading Fund Houses",
                labels={
                    "quarter_end_date":
                        "Quarter",
                    "aum_crore":
                        "AUM (₹ Crore)",
                    "fund_house":
                        "Fund House"
                }
            )

            fig.update_layout(
                hovermode="x unified",
                height=500
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        # =====================================================
        # NEW SIP REGISTRATIONS
        # =====================================================

        with industry_col2:

            st.subheader(
                "New SIP Registrations"
            )

            if "new_sip_registrations_lakh" in sip.columns:

                fig = px.bar(
                    sip_sorted,
                    x="month",
                    y="new_sip_registrations_lakh",
                    title="Monthly New SIP Registrations",
                    labels={
                        "month":
                            "Month",
                        "new_sip_registrations_lakh":
                            "New SIPs (Lakh)"
                    }
                )

                fig.update_layout(
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            else:

                st.info(
                    "New SIP registration data is not available."
                )

        # =====================================================
        # INDUSTRY SUMMARY TABLE
        # =====================================================

        st.subheader(
            "📋 Fund House Industry Snapshot"
        )

        industry_table = (
            latest_aum_data[
                [
                    "fund_house",
                    "quarter_end_date",
                    "aum_crore",
                    "num_schemes"
                ]
            ]
            .sort_values(
                "aum_crore",
                ascending=False
            )
        )

        st.dataframe(
            industry_table,
            use_container_width=True,
            hide_index=True
        )

        # =====================================================
        # DOWNLOAD
        # =====================================================

        st.download_button(
            "⬇️ Download Industry AUM Data",
            data=aum.to_csv(
                index=False
            ),
            file_name="industry_aum_analysis.csv",
            mime="text/csv",
            key="download_industry_aum"
        )


    with tab4:
        pass

# ============================================================
# MAIN APPLICATION
# ============================================================

if not st.session_state.logged_in:
    authentication_page()
else:
    page = sidebar()

    if page == "🚀 Advanced Dashboard":
        advanced_dashboard_page()
    elif page == "🏠 Home":
        home_page()
    elif page == "📊 Industry Analytics":
        industry_page()
    elif page == "📈 Fund Performance":
        performance_page()
    elif page == "🔎 Fund Explorer":
        explorer_page()
    elif page == "⚖️ Fund Comparison":
        comparison_page()
    elif page == "💰 SIP Calculator":
        sip_page()
    elif page == "🎯 Goal Planner":
        goal_page()
    elif page == "👤 Investor Analytics":
        investor_page()
    elif page == "⭐ My Watchlist":
        watchlist_page()
    elif page == "🤖 AI Insights":
        ai_page()
    elif page == "⚙️ Profile":
        profile_page()