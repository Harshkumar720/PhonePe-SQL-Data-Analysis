# ─── Standard Library ────────────────────────────────────────────────────────
import sqlite3
import os
import sys

# ─── Third-Party ──────────────────────────────────────────────────────────────
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

try:
    from streamlit_option_menu import option_menu
except ImportError:
    st.error("Missing dependency: streamlit-option-menu. Run: pip install streamlit-option-menu")
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# PAGE CONFIGURATION
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="PhonePe Pulse Dashboard",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# GLOBAL CONSTANTS
# ══════════════════════════════════════════════════════════════════════════════
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "phonepe.db")

REQUIRED_TABLES = [
    "agg_transaction",
    "agg_user",
    "agg_insurance",
    "map_transaction",
    "map_user",
    "map_insurance",
    "top_transaction",
    "top_user",
    "top_insurance",
]

# PhonePe brand palette
PURPLE  = "#5f259f"
VIOLET  = "#7b2fbe"
LIGHT_P = "#a259d9"
TEAL    = "#00c6a2"
ORANGE  = "#ff6b35"
YELLOW  = "#ffd166"
DARK_BG = "#0e0e1a"
CARD_BG = "#1a1a2e"
TEXT    = "#e0e0e0"

# Plotly template used throughout
TEMPLATE = "plotly_dark"

# Quarter label mapping
Q_LABEL = {1: "Q1 (Jan–Mar)", 2: "Q2 (Apr–Jun)", 3: "Q3 (Jul–Sep)", 4: "Q4 (Oct–Dec)"}


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE VALIDATION
# ══════════════════════════════════════════════════════════════════════════════
def validate_database() -> bool:
    """Check if the database file exists and required tables are present."""
    if not os.path.isfile(DB_PATH):
        st.error(
            f"❌ **Database not found.**\n\n"
            f"Expected path: `{DB_PATH}`\n\n"
            f"Please place `phonepe.db` in the same directory as `app.py` and restart."
        )
        return False
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        existing = {row[0] for row in cursor.fetchall()}
        conn.close()
        missing = [t for t in REQUIRED_TABLES if t not in existing]
        if missing:
            st.warning(
                f"⚠️ **Some expected tables are missing from the database:**\n\n"
                + "\n".join(f"- `{t}`" for t in missing)
                + "\n\nSome dashboard sections may not function correctly."
            )
        return True
    except sqlite3.DatabaseError as e:
        st.error(f"❌ **Database error during validation:** {e}")
        return False


# ══════════════════════════════════════════════════════════════════════════════
# CUSTOM CSS
# ══════════════════════════════════════════════════════════════════════════════
def inject_css() -> None:
    st.markdown(
        f"""
        <style>
        /* ── Global ── */
        html, body, [data-testid="stAppViewContainer"] {{
            background: {DARK_BG};
            color: {TEXT};
            font-family: 'Segoe UI', sans-serif;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #12002a 0%, #1e0050 100%);
            border-right: 1px solid {PURPLE};
        }}

        /* ── KPI Cards ── */
        .kpi-card {{
            background: linear-gradient(135deg, {CARD_BG} 0%, #16213e 100%);
            border: 1px solid {PURPLE};
            border-radius: 14px;
            padding: 20px 22px;
            margin-bottom: 12px;
            box-shadow: 0 4px 20px rgba(95,37,159,.35);
            transition: transform .2s, box-shadow .2s;
        }}
        .kpi-card:hover {{
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(95,37,159,.55);
        }}
        .kpi-label {{
            font-size: 0.80rem;
            color: #a0a0c0;
            letter-spacing: .08em;
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .kpi-value {{
            font-size: 1.80rem;
            font-weight: 700;
            background: linear-gradient(90deg, {PURPLE}, {TEAL});
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .kpi-delta {{
            font-size: 0.78rem;
            color: {TEAL};
            margin-top: 4px;
        }}
        .kpi-icon {{
            font-size: 1.6rem;
            float: right;
            margin-top: -38px;
        }}

        /* ── Section headers ── */
        .section-header {{
            font-size: 1.5rem;
            font-weight: 700;
            color: {LIGHT_P};
            border-left: 4px solid {TEAL};
            padding-left: 12px;
            margin: 18px 0 14px;
        }}
        .page-title {{
            font-size: 2.2rem;
            font-weight: 800;
            background: linear-gradient(90deg, {PURPLE} 0%, {TEAL} 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 4px;
        }}
        .page-subtitle {{
            font-size: 0.95rem;
            color: #7a7aaa;
            margin-bottom: 20px;
        }}

        /* ── Insight boxes ── */
        .insight-box {{
            background: linear-gradient(135deg, #1a0035 0%, #001535 100%);
            border: 1px solid {PURPLE}66;
            border-radius: 10px;
            padding: 14px 18px;
            margin: 8px 0;
            font-size: 0.88rem;
            color: #ccd;
        }}
        .insight-box strong {{ color: {TEAL}; }}

        /* ── Rank badge ── */
        .rank-badge {{
            display: inline-block;
            background: {PURPLE};
            color: #fff;
            border-radius: 50%;
            width: 26px;
            height: 26px;
            text-align: center;
            line-height: 26px;
            font-size: 0.78rem;
            font-weight: 700;
            margin-right: 8px;
        }}

        /* ── Streamlit widget tweaks ── */
        div[data-testid="stMetricValue"] {{
            font-size: 1.5rem !important;
            font-weight: 700 !important;
        }}
        .stDataFrame {{ border-radius: 10px; }}
        div.block-container {{ padding-top: 1.5rem; }}
        </style>
        """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# DATABASE HELPERS
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner=False)
def get_connection() -> sqlite3.Connection:
    """Return a cached SQLite connection."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn
    except sqlite3.DatabaseError as e:
        st.error(f"❌ Failed to connect to database: {e}")
        st.stop()


@st.cache_data(ttl=300, show_spinner=False)
def run_query(sql: str) -> pd.DataFrame:
    """Execute a SQL query and return a DataFrame (cached 5 min)."""
    try:
        conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        df = pd.read_sql_query(sql, conn)
        conn.close()
        return df
    except sqlite3.OperationalError as e:
        st.error(f"SQL OperationalError: {e}\n\nQuery: `{sql.strip()[:200]}`")
        return pd.DataFrame()
    except sqlite3.DatabaseError as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Unexpected query error: {e}")
        return pd.DataFrame()


# ══════════════════════════════════════════════════════════════════════════════
# UTILITY / FORMATTING
# ══════════════════════════════════════════════════════════════════════════════
def fmt_crore(val) -> str:
    """Format a rupee value in crores (e.g. ₹1,23,456 Cr)."""
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "N/A"
    cr = val / 1e7
    if cr >= 1e5:
        return f"₹{cr/1e5:,.2f} L Cr"
    return f"₹{cr:,.0f} Cr"


def fmt_count(val) -> str:
    """Format a large count (e.g. 1.23 Bn / 45.6 Mn)."""
    try:
        val = float(val)
    except (TypeError, ValueError):
        return "N/A"
    if val >= 1e9:
        return f"{val/1e9:.2f} Bn"
    if val >= 1e6:
        return f"{val/1e6:.1f} Mn"
    if val >= 1e3:
        return f"{val/1e3:.1f} K"
    return f"{val:,.0f}"


def kpi_card(label: str, value: str, icon: str, delta: str = "") -> None:
    """Render a single KPI card using custom HTML."""
    delta_html = f'<div class="kpi-delta">▲ {delta}</div>' if delta else ""
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
            {delta_html}
            <div class="kpi-icon">{icon}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def section_header(title: str) -> None:
    st.markdown(f'<div class="section-header">{title}</div>', unsafe_allow_html=True)


def insight_box(text: str) -> None:
    st.markdown(f'<div class="insight-box">{text}</div>', unsafe_allow_html=True)


def normalize_state(s: str) -> str:
    """Convert slug-style state names to Title Case (for agg_ tables)."""
    return s.replace("-", " ").title()


def safe_val(df: pd.DataFrame, row: int, col: str, default=0):
    """Safely extract a scalar from a DataFrame, returning default on failure."""
    try:
        v = df.iloc[row][col]
        return v if v is not None else default
    except Exception:
        return default


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR NAVIGATION
# ══════════════════════════════════════════════════════════════════════════════
def render_sidebar() -> str:
    with st.sidebar:
        st.markdown(
            f"""
            <div style="text-align:center; padding: 16px 0 8px;">
                <span style="font-size:2.4rem;">📱</span>
                <h2 style="color:{LIGHT_P}; margin:0; font-size:1.3rem;">PhonePe Pulse</h2>
                <p style="color:#7070a0; font-size:0.78rem; margin-top:4px;">Analytics Dashboard</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("---")

        page = option_menu(
            menu_title=None,
            options=[
                "🏠 Home",
                "💳 Transactions",
                "👤 Users",
                "🛡️ Insurance",
                "🗺️ Geo Map",
                "🏆 Top Insights",
                "🔍 SQL Insights",
            ],
            icons=["house", "credit-card", "person", "shield", "map", "trophy", "database"],
            default_index=0,
            styles={
                "container": {"background": "transparent", "padding": "0"},
                "icon": {"color": TEAL, "font-size": "16px"},
                "nav-link": {
                    "color": "#b0b0d0",
                    "font-size": "14px",
                    "border-radius": "8px",
                    "margin": "2px 0",
                },
                "nav-link-selected": {
                    "background": f"linear-gradient(90deg,{PURPLE},{VIOLET})",
                    "color": "#fff",
                    "font-weight": "700",
                },
            },
        )

        st.markdown("---")
        st.markdown(
            f'<p style="color:#505070;font-size:0.72rem;text-align:center;">'
            f"Data: 2018 – 2024 · 9 tables · SQLite</p>",
            unsafe_allow_html=True,
        )
    return page


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 1 — HOME
# ══════════════════════════════════════════════════════════════════════════════
def page_home() -> None:
    st.markdown('<div class="page-title">📱 PhonePe Pulse Analytics</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Comprehensive Digital Payments Intelligence · India · 2018–2024</div>',
        unsafe_allow_html=True,
    )

    # ── Overall KPIs ──────────────────────────────────────────────────────────
    df_txn   = run_query("SELECT SUM(Count) AS v FROM map_transaction")
    df_amt   = run_query("SELECT SUM(Amount) AS v FROM map_transaction")
    df_users = run_query("SELECT SUM(RegisteredUsers) AS v FROM map_user")
    df_opens = run_query("SELECT SUM(AppOpens) AS v FROM map_user")
    df_ins_c = run_query("SELECT SUM(Count) AS v FROM map_insurance")
    df_ins_a = run_query("SELECT SUM(Amount) AS v FROM map_insurance")

    total_txn   = safe_val(df_txn,   0, "v")
    total_amt   = safe_val(df_amt,   0, "v")
    total_users = safe_val(df_users, 0, "v")
    total_opens = safe_val(df_opens, 0, "v")
    total_ins_c = safe_val(df_ins_c, 0, "v")
    total_ins_a = safe_val(df_ins_a, 0, "v")

    c1, c2, c3 = st.columns(3)
    with c1:
        kpi_card("Total Transactions", fmt_count(total_txn), "💳", "2018–2024")
    with c2:
        kpi_card("Total Payment Value", fmt_crore(total_amt), "💰", "All States")
    with c3:
        kpi_card("Registered Users", fmt_count(total_users), "👤", "Across India")

    c4, c5, c6 = st.columns(3)
    with c4:
        kpi_card("App Opens", fmt_count(total_opens), "📲", "Engagement metric")
    with c5:
        kpi_card("Insurance Policies", fmt_count(total_ins_c), "🛡️", "2020–2024")
    with c6:
        kpi_card("Insurance Value", fmt_crore(total_ins_a), "📋", "All States")

    st.markdown("---")

    # ── Year-over-Year growth chart ────────────────────────────────────────────
    section_header("📈 Year-over-Year Growth")
    yoy = run_query("""
        SELECT Year,
               SUM(Count)  AS Transactions,
               SUM(Amount) AS Amount
        FROM   map_transaction
        GROUP  BY Year
        ORDER  BY Year
    """)

    if not yoy.empty:
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=yoy["Year"], y=yoy["Transactions"],
                name="Transaction Count", marker_color=PURPLE, opacity=0.85
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=yoy["Year"], y=yoy["Amount"],
                name="Payment Value (₹)",
                mode="lines+markers",
                line=dict(color=TEAL, width=3),
                marker=dict(size=8)
            ),
            secondary_y=True,
        )
        fig.update_layout(
            template=TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            legend=dict(orientation="h", y=1.08),
            height=350,
            margin=dict(l=0, r=0, t=20, b=0),
        )
        fig.update_yaxes(title_text="Transaction Count", secondary_y=False, gridcolor="#2a2a4a")
        fig.update_yaxes(title_text="Payment Value (₹)", secondary_y=True, gridcolor="#2a2a4a")
        st.plotly_chart(fig, use_container_width=True)

    # ── Highlights ────────────────────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        section_header("💡 Key Insights")
        insight_box("<strong>91× Growth:</strong> From 1.08 Bn txns in 2018 → 99.3 Bn in 2024 — remarkable adoption curve.")
        insight_box("<strong>Maharashtra & Telangana</strong> dominate by transaction value; <strong>Maharashtra</strong> leads in count.")
        insight_box("<strong>Peer-to-peer</strong> and <strong>Merchant payments</strong> are the highest-growing categories YoY.")
        insight_box("<strong>Insurance</strong> grew from negligible in 2020 to millions of policies by 2024.")
        insight_box("<strong>Xiaomi & Samsung</strong> are the top device brands powering PhonePe transactions.")

    with col_b:
        section_header("📊 About This Dataset")
        st.markdown(
            f"""
            <div class="insight-box">
            The <strong>PhonePe Pulse</strong> dataset is an open-source initiative by PhonePe providing
            granular digital payment statistics across India from <strong>2018–2024</strong>.<br><br>
            <strong>9 tables</strong> spanning three data families:<br>
            • <strong>Aggregated</strong> — Category/Brand-level rollups per State + Quarter<br>
            • <strong>Map</strong> — State-level hover data for geo visualizations<br>
            • <strong>Top</strong> — District-level top performers per State + Quarter<br><br>
            Total records: <strong>~37,000+ rows</strong> across all tables.
            </div>
            """,
            unsafe_allow_html=True,
        )

    # ── Transaction category share ─────────────────────────────────────────────
    section_header("🥧 Transaction Category Mix (All Years)")
    cat_df = run_query("""
        SELECT Category, SUM(Count) AS cnt, SUM(Amount) AS amt
        FROM   agg_transaction
        GROUP  BY Category
        ORDER  BY cnt DESC
    """)

    if not cat_df.empty:
        c_l, c_r = st.columns(2)
        with c_l:
            fig2 = px.pie(
                cat_df, names="Category", values="cnt",
                title="By Transaction Count",
                color_discrete_sequence=[PURPLE, TEAL, ORANGE, YELLOW, LIGHT_P],
                hole=0.45, template=TEMPLATE
            )
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=320, margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig2, use_container_width=True)
        with c_r:
            fig3 = px.pie(
                cat_df, names="Category", values="amt",
                title="By Transaction Amount",
                color_discrete_sequence=[TEAL, PURPLE, ORANGE, YELLOW, LIGHT_P],
                hole=0.45, template=TEMPLATE
            )
            fig3.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=320, margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig3, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 2 — TRANSACTION ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_transactions() -> None:
    st.markdown('<div class="page-title">💳 Transaction Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Deep-dive into payment volumes, amounts, and patterns</div>',
        unsafe_allow_html=True,
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    years_df = run_query("SELECT DISTINCT Year FROM map_transaction ORDER BY Year")
    years = years_df["Year"].tolist() if not years_df.empty else []

    f1, f2, f3 = st.columns([2, 2, 3])
    with f1:
        sel_year = st.selectbox("📅 Year", ["All"] + [str(y) for y in years], key="txn_year")
    with f2:
        sel_qtr = st.selectbox("🗓️ Quarter", ["All", "Q1", "Q2", "Q3", "Q4"], key="txn_qtr")
    with f3:
        cats_df = run_query("SELECT DISTINCT Category FROM agg_transaction ORDER BY Category")
        cats = cats_df["Category"].tolist() if not cats_df.empty else []
        sel_cat = st.multiselect("📂 Category", cats, default=cats, key="txn_cat")

    # Build WHERE clauses
    where_mt = "WHERE 1=1"
    where_at = "WHERE 1=1"
    if sel_year != "All":
        where_mt += f" AND Year = {int(sel_year)}"
        where_at += f" AND Year = {int(sel_year)}"
    if sel_qtr != "All":
        q_num = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}[sel_qtr]
        where_mt += f" AND Quarter = {q_num}"
        where_at += f" AND Quarter = {q_num}"
    if sel_cat:
        cats_str = "','".join([c.replace("'", "''") for c in sel_cat])
        where_at += f" AND Category IN ('{cats_str}')"

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpi_df  = run_query(f"SELECT SUM(Count) AS cnt, SUM(Amount) AS amt FROM map_transaction {where_mt}")
    cnt_v   = safe_val(kpi_df, 0, "cnt")
    amt_v   = safe_val(kpi_df, 0, "amt")
    avg_txn = (float(amt_v) / float(cnt_v)) if cnt_v else 0

    k1, k2, k3 = st.columns(3)
    with k1: kpi_card("Total Transactions", fmt_count(cnt_v), "🔢")
    with k2: kpi_card("Total Amount", fmt_crore(amt_v), "💰")
    with k3: kpi_card("Avg Transaction Value", f"₹{avg_txn:,.0f}", "📊")

    st.markdown("---")

    # ── Year-wise trend ───────────────────────────────────────────────────────
    section_header("📈 Year-wise Transaction Trend")
    yoy_df = run_query("""
        SELECT Year, SUM(Count) AS Transactions, SUM(Amount) AS Amount
        FROM   map_transaction
        GROUP  BY Year
        ORDER  BY Year
    """)

    if not yoy_df.empty:
        tab1, tab2 = st.tabs(["Transaction Count", "Transaction Amount"])
        with tab1:
            fig = px.bar(
                yoy_df, x="Year", y="Transactions",
                text_auto=True,
                color_discrete_sequence=[PURPLE], template=TEMPLATE
            )
            fig.update_traces(texttemplate="%{y:.2s}", textposition="outside")
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=350, margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig, use_container_width=True)
        with tab2:
            fig = px.area(
                yoy_df, x="Year", y="Amount",
                color_discrete_sequence=[TEAL], template=TEMPLATE
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=350, margin=dict(l=0, r=0, t=10, b=0),
                yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig, use_container_width=True)

    # ── Quarter-wise analysis ──────────────────────────────────────────────────
    section_header("🗓️ Quarter-wise Distribution")
    qtr_df = run_query("""
        SELECT Year, Quarter, SUM(Count) AS Transactions, SUM(Amount) AS Amount
        FROM   map_transaction
        GROUP  BY Year, Quarter
        ORDER  BY Year, Quarter
    """)

    if not qtr_df.empty:
        qtr_df["Period"] = qtr_df["Year"].astype(str) + " Q" + qtr_df["Quarter"].astype(str)
        fig_q = px.line(
            qtr_df, x="Period", y="Transactions", markers=True,
            color_discrete_sequence=[LIGHT_P], template=TEMPLATE,
            title="Quarterly Transaction Count Over Time"
        )
        fig_q.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(tickangle=45, gridcolor="#2a2a4a"),
            yaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_q, use_container_width=True)

    # ── Category analysis ──────────────────────────────────────────────────────
    section_header("📂 Category Analysis")
    cat_df = run_query(f"""
        SELECT Category,
               SUM(Count)  AS Transactions,
               SUM(Amount) AS Amount,
               ROUND(SUM(Amount)*1.0/NULLIF(SUM(Count),0), 2) AS Avg_Value
        FROM   agg_transaction
        {where_at}
        GROUP  BY Category
        ORDER  BY Transactions DESC
    """)

    if not cat_df.empty:
        ca, cb = st.columns(2)
        with ca:
            fig_c1 = px.bar(
                cat_df, x="Transactions", y="Category", orientation="h",
                color="Transactions",
                color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                template=TEMPLATE, title="Transactions by Category"
            )
            fig_c1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_showscale=False, yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_c1, use_container_width=True)
        with cb:
            fig_c2 = px.bar(
                cat_df, x="Avg_Value", y="Category", orientation="h",
                color="Avg_Value",
                color_continuous_scale=[[0, ORANGE], [1, YELLOW]],
                template=TEMPLATE, title="Avg Transaction Value by Category"
            )
            fig_c2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=300, margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_showscale=False, yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_c2, use_container_width=True)

    # ── Category growth over time ──────────────────────────────────────────────
    section_header("📊 Category Growth Over Years")
    cat_year_df = run_query("""
        SELECT Year, Category,
               SUM(Count)  AS Transactions,
               SUM(Amount) AS Amount
        FROM   agg_transaction
        GROUP  BY Year, Category
        ORDER  BY Year
    """)

    if not cat_year_df.empty:
        fig_cg = px.line(
            cat_year_df, x="Year", y="Amount", color="Category",
            markers=True, template=TEMPLATE,
            color_discrete_sequence=[PURPLE, TEAL, ORANGE, YELLOW, LIGHT_P],
            title="Category-wise Amount Growth YoY"
        )
        fig_cg.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=350, margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(gridcolor="#2a2a4a"), yaxis=dict(gridcolor="#2a2a4a"),
            legend=dict(orientation="h", y=1.12)
        )
        st.plotly_chart(fig_cg, use_container_width=True)

    # ── State-wise analysis ────────────────────────────────────────────────────
    section_header("🗺️ State-wise Transaction Performance")
    state_df = run_query(f"""
        SELECT State,
               SUM(Count)  AS Transactions,
               SUM(Amount) AS Amount,
               ROUND(SUM(Amount)*1.0/NULLIF(SUM(Count),0), 2) AS Avg_Value
        FROM   map_transaction
        {where_mt}
        GROUP  BY State
        ORDER  BY Transactions DESC
        LIMIT  20
    """)

    if not state_df.empty:
        state_df["State"] = state_df["State"].str.title()
        metric_opt = st.radio(
            "View by:", ["Transactions", "Amount", "Avg_Value"],
            horizontal=True, key="state_metric"
        )
        fig_s = px.bar(
            state_df.sort_values(metric_opt, ascending=True),
            x=metric_opt, y="State", orientation="h",
            color=metric_opt,
            color_continuous_scale=[[0, CARD_BG], [0.5, PURPLE], [1, TEAL]],
            template=TEMPLATE, height=550
        )
        fig_s.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_s, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 3 — USER ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_users() -> None:
    st.markdown('<div class="page-title">👤 User Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Registered users, app engagement, device brands, and growth</div>',
        unsafe_allow_html=True,
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    years_df = run_query("SELECT DISTINCT Year FROM map_user ORDER BY Year")
    years = years_df["Year"].tolist() if not years_df.empty else []

    f1, f2 = st.columns(2)
    with f1:
        sel_year = st.selectbox("📅 Year", ["All"] + [str(y) for y in years], key="usr_year")
    with f2:
        sel_qtr = st.selectbox("🗓️ Quarter", ["All", "Q1", "Q2", "Q3", "Q4"], key="usr_qtr")

    where = "WHERE 1=1"
    if sel_year != "All":
        where += f" AND Year = {int(sel_year)}"
    if sel_qtr != "All":
        q_num = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}[sel_qtr]
        where += f" AND Quarter = {q_num}"

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpi = run_query(f"SELECT SUM(RegisteredUsers) AS ru, SUM(AppOpens) AS ao FROM map_user {where}")
    ru = safe_val(kpi, 0, "ru")
    ao = safe_val(kpi, 0, "ao")
    eng_rate = (float(ao) / float(ru)) if ru else 0

    k1, k2, k3 = st.columns(3)
    with k1: kpi_card("Registered Users", fmt_count(ru), "👤")
    with k2: kpi_card("App Opens", fmt_count(ao), "📲")
    with k3: kpi_card("Engagement Rate", f"{eng_rate:,.1f}×", "🔥")

    st.markdown("---")

    # ── YoY User Growth ───────────────────────────────────────────────────────
    section_header("📈 Year-wise User Growth")
    yoy_u = run_query("""
        SELECT Year,
               SUM(RegisteredUsers) AS RegUsers,
               SUM(AppOpens)        AS AppOpens
        FROM   map_user
        GROUP  BY Year
        ORDER  BY Year
    """)

    if not yoy_u.empty:
        fig_u = make_subplots(specs=[[{"secondary_y": True}]])
        fig_u.add_trace(
            go.Bar(
                x=yoy_u["Year"], y=yoy_u["RegUsers"],
                name="Registered Users", marker_color=PURPLE, opacity=0.85
            ),
            secondary_y=False,
        )
        fig_u.add_trace(
            go.Scatter(
                x=yoy_u["Year"], y=yoy_u["AppOpens"],
                name="App Opens", mode="lines+markers",
                line=dict(color=TEAL, width=3), marker=dict(size=8)
            ),
            secondary_y=True,
        )
        fig_u.update_layout(
            template=TEMPLATE,
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            height=350,
            margin=dict(l=0, r=0, t=10, b=0),
            legend=dict(orientation="h", y=1.08)
        )
        fig_u.update_yaxes(title_text="Registered Users", secondary_y=False, gridcolor="#2a2a4a")
        fig_u.update_yaxes(title_text="App Opens", secondary_y=True, gridcolor="#2a2a4a")
        st.plotly_chart(fig_u, use_container_width=True)

    # ── State-wise registered users ────────────────────────────────────────────
    col_a, col_b = st.columns(2)
    with col_a:
        section_header("🏆 Top 10 States — Registered Users")
        top_states = run_query(f"""
            SELECT State, SUM(RegisteredUsers) AS Users
            FROM   map_user {where}
            GROUP  BY State
            ORDER  BY Users DESC
            LIMIT  10
        """)
        if not top_states.empty:
            top_states["State"] = top_states["State"].str.title()
            fig_ts = px.bar(
                top_states, x="Users", y="State", orientation="h",
                color="Users",
                color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                template=TEMPLATE
            )
            fig_ts.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=360, margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_ts, use_container_width=True)

    with col_b:
        section_header("📲 Top 10 States — App Opens")
        top_app = run_query(f"""
            SELECT State, SUM(AppOpens) AS AppOpens
            FROM   map_user {where}
            GROUP  BY State
            ORDER  BY AppOpens DESC
            LIMIT  10
        """)
        if not top_app.empty:
            top_app["State"] = top_app["State"].str.title()
            fig_ta = px.bar(
                top_app, x="AppOpens", y="State", orientation="h",
                color="AppOpens",
                color_continuous_scale=[[0, ORANGE], [1, YELLOW]],
                template=TEMPLATE
            )
            fig_ta.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=360, margin=dict(l=0, r=0, t=10, b=0),
                coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_ta, use_container_width=True)

    # ── Device brand analysis ─────────────────────────────────────────────────
    section_header("📱 Device Brand Market Share")
    brand_df = run_query("""
        SELECT Brand,
               SUM(Count)       AS Users,
               AVG(Percentage)  AS Avg_Share
        FROM   agg_user
        WHERE  Brand != 'Others'
        GROUP  BY Brand
        ORDER  BY Users DESC
        LIMIT  15
    """)

    if not brand_df.empty:
        ba, bb = st.columns(2)
        with ba:
            fig_b1 = px.pie(
                brand_df, names="Brand", values="Users", hole=0.4,
                color_discrete_sequence=px.colors.qualitative.Vivid,
                template=TEMPLATE, title="User Share by Brand"
            )
            fig_b1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", height=360,
                margin=dict(l=0, r=0, t=30, b=0)
            )
            st.plotly_chart(fig_b1, use_container_width=True)
        with bb:
            fig_b2 = px.bar(
                brand_df.sort_values("Users", ascending=True),
                x="Users", y="Brand", orientation="h",
                color="Users",
                color_continuous_scale=[[0, CARD_BG], [0.5, LIGHT_P], [1, TEAL]],
                template=TEMPLATE, title="Top Brands by User Count"
            )
            fig_b2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=360, margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_b2, use_container_width=True)

        # ── Brand growth over years ────────────────────────────────────────────
        section_header("📊 Top Brand Growth Over Years")
        top_brands = brand_df["Brand"].head(6).tolist()
        brands_str = "','".join([b.replace("'", "''") for b in top_brands])
        brand_yoy = run_query(f"""
            SELECT Year, Brand, SUM(Count) AS Users
            FROM   agg_user
            WHERE  Brand IN ('{brands_str}')
            GROUP  BY Year, Brand
            ORDER  BY Year
        """)
        if not brand_yoy.empty:
            fig_bg = px.line(
                brand_yoy, x="Year", y="Users", color="Brand",
                markers=True, template=TEMPLATE,
                color_discrete_sequence=px.colors.qualitative.Vivid,
                title="Year-wise User Growth by Top Brands"
            )
            fig_bg.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=350, margin=dict(l=0, r=0, t=30, b=0),
                xaxis=dict(gridcolor="#2a2a4a"), yaxis=dict(gridcolor="#2a2a4a"),
                legend=dict(orientation="h", y=1.12)
            )
            st.plotly_chart(fig_bg, use_container_width=True)

    # ── Registered vs App opens scatter ──────────────────────────────────────
    section_header("🔵 Registered Users vs App Opens (State-level)")
    scatter_df = run_query("""
        SELECT State,
               SUM(RegisteredUsers) AS Users,
               SUM(AppOpens)        AS AppOpens
        FROM   map_user
        GROUP  BY State
    """)

    if not scatter_df.empty:
        scatter_df["State"] = scatter_df["State"].str.title()
        fig_sc = px.scatter(
            scatter_df, x="Users", y="AppOpens", text="State",
            color="AppOpens", size="Users",
            color_continuous_scale=[[0, PURPLE], [1, TEAL]],
            template=TEMPLATE, log_x=True, log_y=True,
            title="Registered Users vs App Opens (log scale)"
        )
        fig_sc.update_traces(textposition="top center", textfont=dict(size=9))
        fig_sc.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=420, margin=dict(l=0, r=0, t=30, b=0),
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#2a2a4a"), yaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_sc, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 4 — INSURANCE ANALYSIS
# ══════════════════════════════════════════════════════════════════════════════
def page_insurance() -> None:
    st.markdown('<div class="page-title">🛡️ Insurance Analysis</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Insurance policy transactions across India · 2020–2024</div>',
        unsafe_allow_html=True,
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    years_df = run_query("SELECT DISTINCT Year FROM map_insurance ORDER BY Year")
    years = years_df["Year"].tolist() if not years_df.empty else []

    f1, f2 = st.columns(2)
    with f1:
        sel_year = st.selectbox("📅 Year", ["All"] + [str(y) for y in years], key="ins_year")
    with f2:
        sel_qtr = st.selectbox("🗓️ Quarter", ["All", "Q1", "Q2", "Q3", "Q4"], key="ins_qtr")

    where = "WHERE 1=1"
    if sel_year != "All":
        where += f" AND Year = {int(sel_year)}"
    if sel_qtr != "All":
        q_num = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}[sel_qtr]
        where += f" AND Quarter = {q_num}"

    # ── KPIs ──────────────────────────────────────────────────────────────────
    kpi = run_query(f"SELECT SUM(Count) AS cnt, SUM(Amount) AS amt FROM map_insurance {where}")
    cnt_v = safe_val(kpi, 0, "cnt")
    amt_v = safe_val(kpi, 0, "amt")
    avg_v = (float(amt_v) / float(cnt_v)) if cnt_v else 0

    k1, k2, k3 = st.columns(3)
    with k1: kpi_card("Total Policies", fmt_count(cnt_v), "🛡️")
    with k2: kpi_card("Total Premium Value", fmt_crore(amt_v), "💰")
    with k3: kpi_card("Avg Premium", f"₹{avg_v:,.0f}", "📋")

    st.markdown("---")

    # ── YoY Insurance growth ───────────────────────────────────────────────────
    section_header("📈 Year-wise Insurance Growth")
    yoy_i = run_query("""
        SELECT Year,
               SUM(Count)  AS Policies,
               SUM(Amount) AS Amount
        FROM   map_insurance
        GROUP  BY Year
        ORDER  BY Year
    """)

    if not yoy_i.empty:
        ia, ib = st.columns(2)
        with ia:
            fig_i1 = px.bar(
                yoy_i, x="Year", y="Policies",
                color_discrete_sequence=[PURPLE], template=TEMPLATE,
                title="Insurance Policies per Year"
            )
            fig_i1.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=320, margin=dict(l=0, r=0, t=30, b=0),
                yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_i1, use_container_width=True)
        with ib:
            fig_i2 = px.area(
                yoy_i, x="Year", y="Amount",
                color_discrete_sequence=[TEAL], template=TEMPLATE,
                title="Insurance Premium Value per Year"
            )
            fig_i2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=320, margin=dict(l=0, r=0, t=30, b=0),
                yaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_i2, use_container_width=True)

    # ── Quarterly trend ────────────────────────────────────────────────────────
    section_header("🗓️ Quarterly Insurance Trend")
    qtr_i = run_query("""
        SELECT Year, Quarter,
               SUM(Count)  AS Policies,
               SUM(Amount) AS Amount
        FROM   map_insurance
        GROUP  BY Year, Quarter
        ORDER  BY Year, Quarter
    """)

    if not qtr_i.empty:
        qtr_i["Period"] = qtr_i["Year"].astype(str) + " Q" + qtr_i["Quarter"].astype(str)
        fig_qi = px.line(
            qtr_i, x="Period", y="Policies", markers=True,
            color_discrete_sequence=[ORANGE], template=TEMPLATE,
            title="Quarterly Insurance Policy Count"
        )
        fig_qi.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=300, margin=dict(l=0, r=0, t=30, b=0),
            xaxis=dict(tickangle=45, gridcolor="#2a2a4a"),
            yaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_qi, use_container_width=True)

    # ── State-wise insurance ───────────────────────────────────────────────────
    section_header("🗺️ State-wise Insurance Performance")
    state_i = run_query(f"""
        SELECT State,
               SUM(Count)  AS Policies,
               SUM(Amount) AS Amount,
               ROUND(SUM(Amount)*1.0/NULLIF(SUM(Count),0), 2) AS Avg_Premium
        FROM   map_insurance
        {where}
        GROUP  BY State
        ORDER  BY Policies DESC
        LIMIT  20
    """)

    if not state_i.empty:
        state_i["State"] = state_i["State"].str.title()
        ins_metric = st.radio(
            "View by:", ["Policies", "Amount", "Avg_Premium"],
            horizontal=True, key="ins_state_metric"
        )
        fig_is = px.bar(
            state_i.sort_values(ins_metric, ascending=True),
            x=ins_metric, y="State", orientation="h",
            color=ins_metric,
            color_continuous_scale=[[0, CARD_BG], [0.5, PURPLE], [1, TEAL]],
            template=TEMPLATE, height=520
        )
        fig_is.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            margin=dict(l=0, r=0, t=10, b=0),
            coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_is, use_container_width=True)

    # ── Top 10 by policies ────────────────────────────────────────────────────
    section_header("🏆 Top 10 Insurance States")
    top10_i = run_query(f"""
        SELECT State,
               SUM(Count)  AS Policies,
               SUM(Amount) AS Amount
        FROM   map_insurance
        {where}
        GROUP  BY State
        ORDER  BY Policies DESC
        LIMIT  10
    """)

    if not top10_i.empty:
        top10_i["State"] = top10_i["State"].str.title()
        fig_t10 = px.bar(
            top10_i, x="State", y="Policies",
            color="Amount",
            color_continuous_scale=[[0, PURPLE], [1, TEAL]],
            template=TEMPLATE
        )
        fig_t10.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            height=350, margin=dict(l=0, r=0, t=10, b=0),
            xaxis=dict(tickangle=30, gridcolor="#2a2a4a"),
            yaxis=dict(gridcolor="#2a2a4a")
        )
        st.plotly_chart(fig_t10, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 5 — GEO VISUALIZATION
# ══════════════════════════════════════════════════════════════════════════════
import requests   # add this at the top of your file with other imports

@st.cache_data(show_spinner=False, ttl=86400)
def load_india_geojson() -> dict:
    """Fetch India state boundaries GeoJSON (cached for 24 h)."""
    url = (
        "https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112"
        "/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    )
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json()
    except Exception as e:
        st.error(f"❌ Could not load India GeoJSON: {e}")
        return {}


# Mapping: your DB state names (lower) → GeoJSON ST_NM property values
STATE_NAME_MAP: dict = {
    "andaman & nicobar islands":               "Andaman & Nicobar Island",
    "andhra pradesh":                          "Andhra Pradesh",
    "arunachal pradesh":                       "Arunachal Pradesh",
    "assam":                                   "Assam",
    "bihar":                                   "Bihar",
    "chandigarh":                              "Chandigarh",
    "chhattisgarh":                            "Chhattisgarh",
    "dadra & nagar haveli & daman & diu":      "Dadra and Nagar Haveli",
    "delhi":                                   "NCT of Delhi",
    "goa":                                     "Goa",
    "gujarat":                                 "Gujarat",
    "haryana":                                 "Haryana",
    "himachal pradesh":                        "Himachal Pradesh",
    "jammu & kashmir":                         "Jammu & Kashmir",
    "jharkhand":                               "Jharkhand",
    "karnataka":                               "Karnataka",
    "kerala":                                  "Kerala",
    "ladakh":                                  "Ladakh",
    "lakshadweep":                             "Lakshadweep",
    "madhya pradesh":                          "Madhya Pradesh",
    "maharashtra":                             "Maharashtra",
    "manipur":                                 "Manipur",
    "meghalaya":                               "Meghalaya",
    "mizoram":                                 "Mizoram",
    "nagaland":                                "Nagaland",
    "odisha":                                  "Odisha",
    "puducherry":                              "Puducherry",
    "punjab":                                  "Punjab",
    "rajasthan":                               "Rajasthan",
    "sikkim":                                  "Sikkim",
    "tamil nadu":                              "Tamil Nadu",
    "telangana":                               "Telangana",
    "tripura":                                 "Tripura",
    "uttar pradesh":                           "Uttar Pradesh",
    "uttarakhand":                             "Uttarakhand",
    "west bengal":                             "West Bengal",
}

STATE_COORDS: dict = {
    "andaman & nicobar islands": (11.7, 92.6),
    "andhra pradesh":            (15.9, 79.7),
    "arunachal pradesh":         (28.2, 94.7),
    "assam":                     (26.2, 92.9),
    "bihar":                     (25.1, 85.3),
    "chandigarh":                (30.7, 76.8),
    "chhattisgarh":              (21.3, 81.9),
    "dadra & nagar haveli & daman & diu": (20.2, 73.0),
    "delhi":                     (28.7, 77.1),
    "goa":                       (15.3, 74.0),
    "gujarat":                   (22.3, 72.6),
    "haryana":                   (29.1, 76.1),
    "himachal pradesh":          (31.1, 77.2),
    "jammu & kashmir":           (33.7, 76.9),
    "jharkhand":                 (23.6, 85.3),
    "karnataka":                 (15.3, 75.7),
    "kerala":                    (10.9, 76.3),
    "ladakh":                    (34.2, 77.6),
    "lakshadweep":               (10.6, 72.6),
    "madhya pradesh":            (23.5, 77.6),
    "maharashtra":               (19.7, 75.7),
    "manipur":                   (24.7, 93.9),
    "meghalaya":                 (25.5, 91.4),
    "mizoram":                   (23.2, 92.7),
    "nagaland":                  (26.2, 94.1),
    "odisha":                    (20.9, 85.1),
    "puducherry":                (11.9, 79.8),
    "punjab":                    (31.1, 75.3),
    "rajasthan":                 (27.0, 74.2),
    "sikkim":                    (27.5, 88.5),
    "tamil nadu":                (11.1, 78.7),
    "telangana":                 (17.4, 79.0),
    "tripura":                   (23.7, 91.7),
    "uttar pradesh":             (27.0, 80.9),
    "uttarakhand":               (30.1, 79.5),
    "west bengal":               (22.9, 87.9),
}


def page_geo() -> None:
    st.markdown('<div class="page-title">🗺️ Geo Visualization</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Interactive India choropleth maps — state-level insights</div>',
        unsafe_allow_html=True,
    )

    # Load GeoJSON
    india_geojson = load_india_geojson()
    if not india_geojson:
        st.error("India GeoJSON could not be loaded. Check your internet connection.")
        return

    # ── Controls ──────────────────────────────────────────────────────────────
    g1, g2, g3 = st.columns(3)
    with g1:
        dataset = st.selectbox("📊 Dataset", ["Transactions", "Users", "Insurance"], key="geo_ds")
    with g2:
        years_geo_df = run_query("SELECT DISTINCT Year FROM map_transaction ORDER BY Year")
        years_geo = years_geo_df["Year"].tolist() if not years_geo_df.empty else []
        sel_y = st.selectbox("📅 Year", ["All"] + [str(y) for y in years_geo], key="geo_yr")
    with g3:
        sel_q = st.selectbox("🗓️ Quarter", ["All", "Q1", "Q2", "Q3", "Q4"], key="geo_qt")

    where_g = "WHERE 1=1"
    if sel_y != "All":
        where_g += f" AND Year = {int(sel_y)}"
    if sel_q != "All":
        q_num = {"Q1": 1, "Q2": 2, "Q3": 3, "Q4": 4}[sel_q]
        where_g += f" AND Quarter = {q_num}"

    # ── Fetch data ────────────────────────────────────────────────────────────
    if dataset == "Transactions":
        geo_df = run_query(f"""
            SELECT State, SUM(Count) AS Transactions, SUM(Amount) AS Amount
            FROM   map_transaction {where_g} GROUP BY State
        """)
        metric_col = st.radio("Color by:", ["Transactions", "Amount"], horizontal=True, key="geo_m1")

    elif dataset == "Users":
        geo_df = run_query(f"""
            SELECT State, SUM(RegisteredUsers) AS RegisteredUsers, SUM(AppOpens) AS AppOpens
            FROM   map_user {where_g} GROUP BY State
        """)
        metric_col = st.radio("Color by:", ["RegisteredUsers", "AppOpens"], horizontal=True, key="geo_m2")

    else:
        geo_df = run_query(f"""
            SELECT State, SUM(Count) AS Policies, SUM(Amount) AS Amount
            FROM   map_insurance {where_g} GROUP BY State
        """)
        metric_col = st.radio("Color by:", ["Policies", "Amount"], horizontal=True, key="geo_m3")

    if geo_df.empty:
        st.warning("No data available for the selected filters.")
        return

    # ── Map state names to GeoJSON property values ────────────────────────────
    geo_df["state_lower"]  = geo_df["State"].str.lower().str.strip()
    geo_df["geo_name"]     = geo_df["state_lower"].map(STATE_NAME_MAP)
    geo_df["State_Title"]  = geo_df["State"].str.title()
    geo_df["color_val"]    = geo_df[metric_col]

    unmapped = geo_df[geo_df["geo_name"].isna()]["State"].tolist()
    if unmapped:
        st.warning(f"⚠️ Could not map these states to GeoJSON: {unmapped}")

    geo_df = geo_df.dropna(subset=["geo_name"])

    if geo_df.empty:
        st.warning("No states could be matched to the India GeoJSON. Check state name formatting.")
        return

    # ── Choropleth (GeoJSON-based — actually renders India!) ──────────────────
    fig_map = px.choropleth(
        geo_df,
        geojson=india_geojson,
        featureidkey="properties.ST_NM",   # match against GeoJSON property
        locations="geo_name",
        color="color_val",
        hover_name="State_Title",
        color_continuous_scale=[[0, "#1a0035"], [0.3, PURPLE], [0.7, LIGHT_P], [1, TEAL]],
        template=TEMPLATE,
        title=f"India — {dataset} {metric_col} ({sel_y if sel_y != 'All' else '2018–2024'})",
    )
    fig_map.update_geos(
        fitbounds="locations",   # auto-zoom to India
        visible=False,
        bgcolor="rgba(0,0,0,0)",
    )
    fig_map.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        geo_bgcolor="rgba(0,0,0,0)",
        height=600,
        margin=dict(l=0, r=0, t=40, b=0),
        coloraxis_colorbar=dict(title=metric_col, tickfont=dict(color="#ccc")),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    # ── Bubble map overlay ────────────────────────────────────────────────────
    section_header("🟣 State Bubble Chart")
    geo_df["lat"] = geo_df["state_lower"].map(lambda s: STATE_COORDS.get(s, (None, None))[0])
    geo_df["lon"] = geo_df["state_lower"].map(lambda s: STATE_COORDS.get(s, (None, None))[1])
    geo_df_coords = geo_df.dropna(subset=["lat", "lon"])

    if not geo_df_coords.empty:
        fig_bbl = px.scatter_geo(
            geo_df_coords,
            lat="lat", lon="lon",
            size="color_val",
            hover_name="State_Title",
            color="color_val",
            color_continuous_scale=[[0, PURPLE], [1, TEAL]],
            template=TEMPLATE,
            title=f"Bubble Map — {metric_col} by State",
        )
        fig_bbl.update_geos(
            fitbounds="locations",
            visible=False,
            bgcolor="rgba(0,0,0,0)",
            showland=True, landcolor="#1a1a2e",
            showocean=True, oceancolor="#0e0e1a",
            showcountries=True, countrycolor="#3a3a5a",
        )
        fig_bbl.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            height=550,
            margin=dict(l=0, r=0, t=40, b=0),
            coloraxis_showscale=False,
        )
        st.plotly_chart(fig_bbl, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 6 — TOP INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
def page_top_insights() -> None:
    st.markdown('<div class="page-title">🏆 Top Insights</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Rankings, leaders, and standout performers across all dimensions</div>',
        unsafe_allow_html=True,
    )

    # ── Filters ───────────────────────────────────────────────────────────────
    years_df = run_query("SELECT DISTINCT Year FROM map_transaction ORDER BY Year")
    years = years_df["Year"].tolist() if not years_df.empty else []

    fi1, fi2 = st.columns(2)
    with fi1:
        sel_y = st.selectbox("📅 Year", ["All"] + [str(y) for y in years], key="top_yr")
    with fi2:
        n_top = st.slider("🔢 Show Top N", 5, 20, 10, key="top_n")

    where = "WHERE 1=1"
    if sel_y != "All":
        where += f" AND Year = {int(sel_y)}"

    tab_txn, tab_usr, tab_ins, tab_brand = st.tabs(
        ["💳 Transactions", "👤 Users", "🛡️ Insurance", "📱 Brands"]
    )

    # ── Transactions tab ──────────────────────────────────────────────────────
    with tab_txn:
        col1, col2 = st.columns(2)
        with col1:
            section_header(f"Top {n_top} States — Transaction Amount")
            df = run_query(f"""
                SELECT State, SUM(Amount) AS Amount
                FROM   map_transaction {where}
                GROUP  BY State ORDER BY Amount DESC LIMIT {n_top}
            """)
            if not df.empty:
                df["State"] = df["State"].str.title()
                df["Rank"] = range(1, len(df) + 1)
                fig = px.bar(
                    df, x="Amount", y="State", orientation="h",
                    color="Amount",
                    color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                    template=TEMPLATE, height=400
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig, use_container_width=True)
                display_df = df[["Rank", "State", "Amount"]].copy()
                display_df["Amount"] = display_df["Amount"].apply(fmt_crore)
                st.dataframe(display_df, use_container_width=True, hide_index=True)

        with col2:
            section_header(f"Top {n_top} States — Transaction Count")
            df2 = run_query(f"""
                SELECT State, SUM(Count) AS Transactions
                FROM   map_transaction {where}
                GROUP  BY State ORDER BY Transactions DESC LIMIT {n_top}
            """)
            if not df2.empty:
                df2["State"] = df2["State"].str.title()
                df2["Rank"] = range(1, len(df2) + 1)
                fig2 = px.bar(
                    df2, x="Transactions", y="State", orientation="h",
                    color="Transactions",
                    color_continuous_scale=[[0, ORANGE], [1, YELLOW]],
                    template=TEMPLATE, height=400
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig2, use_container_width=True)
                display_df2 = df2[["Rank", "State", "Transactions"]].copy()
                display_df2["Transactions"] = display_df2["Transactions"].apply(fmt_count)
                st.dataframe(display_df2, use_container_width=True, hide_index=True)

        section_header(f"Top {n_top} States — Average Transaction Value")
        df_avg = run_query(f"""
            SELECT State,
                   ROUND(SUM(Amount)*1.0/NULLIF(SUM(Count),0), 2) AS Avg_Value
            FROM   map_transaction {where}
            GROUP  BY State ORDER BY Avg_Value DESC LIMIT {n_top}
        """)
        if not df_avg.empty:
            df_avg["State"] = df_avg["State"].str.title()
            fig_avg = px.funnel(
                df_avg, x="Avg_Value", y="State",
                color_discrete_sequence=[LIGHT_P],
                template=TEMPLATE
            )
            fig_avg.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=380, margin=dict(l=0, r=0, t=10, b=0)
            )
            st.plotly_chart(fig_avg, use_container_width=True)

    # ── Users tab ──────────────────────────────────────────────────────────────
    with tab_usr:
        col1, col2 = st.columns(2)
        with col1:
            section_header(f"Top {n_top} States — Registered Users")
            df = run_query(f"""
                SELECT State, SUM(RegisteredUsers) AS Users
                FROM   map_user {where}
                GROUP  BY State ORDER BY Users DESC LIMIT {n_top}
            """)
            if not df.empty:
                df["State"] = df["State"].str.title()
                fig = px.bar(
                    df, x="Users", y="State", orientation="h",
                    color="Users",
                    color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                    template=TEMPLATE, height=380
                )
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig, use_container_width=True)

        with col2:
            section_header(f"Top {n_top} States — App Opens")
            df2 = run_query(f"""
                SELECT State, SUM(AppOpens) AS AppOpens
                FROM   map_user {where}
                GROUP  BY State ORDER BY AppOpens DESC LIMIT {n_top}
            """)
            if not df2.empty:
                df2["State"] = df2["State"].str.title()
                fig2 = px.bar(
                    df2, x="AppOpens", y="State", orientation="h",
                    color="AppOpens",
                    color_continuous_scale=[[0, ORANGE], [1, YELLOW]],
                    template=TEMPLATE, height=380
                )
                fig2.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig2, use_container_width=True)

        section_header("🚀 Fastest Growing States — User Growth")
        growth_df = run_query("""
            SELECT State,
                   SUM(CASE WHEN Year=2018 THEN RegisteredUsers ELSE 0 END) AS Users_2018,
                   SUM(CASE WHEN Year=2024 THEN RegisteredUsers ELSE 0 END) AS Users_2024
            FROM   map_user
            GROUP  BY State
            HAVING Users_2018 > 0 AND Users_2024 > 0
        """)
        if not growth_df.empty:
            growth_df["Growth_X"] = growth_df["Users_2024"] / growth_df["Users_2018"]
            growth_df = growth_df.sort_values("Growth_X", ascending=False).head(n_top)
            growth_df["State"] = growth_df["State"].str.title()
            fig_gr = px.bar(
                growth_df, x="Growth_X", y="State", orientation="h",
                color="Growth_X",
                color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                template=TEMPLATE, title="User Growth Multiple (2018→2024)"
            )
            fig_gr.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                height=400, margin=dict(l=0, r=0, t=30, b=0),
                coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
            )
            st.plotly_chart(fig_gr, use_container_width=True)

    # ── Insurance tab ─────────────────────────────────────────────────────────
    with tab_ins:
        where_i = "WHERE 1=1" + (f" AND Year = {int(sel_y)}" if sel_y != "All" else "")
        col1, col2 = st.columns(2)
        with col1:
            section_header(f"Top {n_top} States — Insurance Policies")
            df_i = run_query(f"""
                SELECT State, SUM(Count) AS Policies
                FROM   map_insurance {where_i}
                GROUP  BY State ORDER BY Policies DESC LIMIT {n_top}
            """)
            if not df_i.empty:
                df_i["State"] = df_i["State"].str.title()
                fig_i = px.bar(
                    df_i, x="Policies", y="State", orientation="h",
                    color="Policies",
                    color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                    template=TEMPLATE, height=380
                )
                fig_i.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig_i, use_container_width=True)

        with col2:
            section_header(f"Top {n_top} States — Insurance Amount")
            df_ia = run_query(f"""
                SELECT State, SUM(Amount) AS Amount
                FROM   map_insurance {where_i}
                GROUP  BY State ORDER BY Amount DESC LIMIT {n_top}
            """)
            if not df_ia.empty:
                df_ia["State"] = df_ia["State"].str.title()
                fig_ia = px.bar(
                    df_ia, x="Amount", y="State", orientation="h",
                    color="Amount",
                    color_continuous_scale=[[0, ORANGE], [1, YELLOW]],
                    template=TEMPLATE, height=380
                )
                fig_ia.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    margin=dict(l=0, r=0, t=10, b=0),
                    coloraxis_showscale=False, xaxis=dict(gridcolor="#2a2a4a")
                )
                st.plotly_chart(fig_ia, use_container_width=True)

    # ── Brands tab ────────────────────────────────────────────────────────────
    with tab_brand:
        section_header(f"Top {n_top} Device Brands by User Count")
        where_b = "WHERE 1=1" + (f" AND Year = {int(sel_y)}" if sel_y != "All" else "")
        df_b = run_query(f"""
            SELECT Brand, SUM(Count) AS Users
            FROM   agg_user {where_b}
            GROUP  BY Brand ORDER BY Users DESC LIMIT {n_top}
        """)

        if not df_b.empty:
            ba, bb = st.columns(2)
            with ba:
                fig_b = px.bar(
                    df_b, x="Brand", y="Users",
                    color="Users",
                    color_continuous_scale=[[0, PURPLE], [1, TEAL]],
                    template=TEMPLATE
                )
                fig_b.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                    height=380, margin=dict(l=0, r=0, t=10, b=0),
                    xaxis=dict(tickangle=30, gridcolor="#2a2a4a"),
                    coloraxis_showscale=False
                )
                st.plotly_chart(fig_b, use_container_width=True)
            with bb:
                fig_bp = px.pie(
                    df_b, names="Brand", values="Users", hole=0.4,
                    color_discrete_sequence=px.colors.qualitative.Vivid,
                    template=TEMPLATE
                )
                fig_bp.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", height=380,
                    margin=dict(l=0, r=0, t=10, b=0)
                )
                st.plotly_chart(fig_bp, use_container_width=True)

            # Brand × State heatmap
            section_header("🔥 Brand × State Heatmap (Top 8 Brands × Top 10 States)")
            top8_brands = df_b["Brand"].head(8).tolist()
            top10_states_df = run_query("""
                SELECT State FROM map_user
                GROUP BY State ORDER BY SUM(RegisteredUsers) DESC LIMIT 10
            """)
            if not top10_states_df.empty:
                top10_states = top10_states_df["State"].tolist()
                brands_sql = "','".join([b.replace("'", "''") for b in top8_brands])
                states_sql = "','".join([s.replace("'", "''") for s in top10_states])
                hmap_df = run_query(f"""
                    SELECT Brand, State, SUM(Count) AS Users
                    FROM   agg_user
                    WHERE  Brand IN ('{brands_sql}')
                      AND  State IN ('{states_sql}')
                    GROUP  BY Brand, State
                """)
                if not hmap_df.empty:
                    hmap_pivot = hmap_df.pivot(
                        index="Brand", columns="State", values="Users"
                    ).fillna(0)
                    fig_hm = px.imshow(
                        hmap_pivot,
                        color_continuous_scale=[[0, DARK_BG], [0.5, PURPLE], [1, TEAL]],
                        template=TEMPLATE, aspect="auto",
                        title="Device Brand Usage by State (Users)"
                    )
                    fig_hm.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                        height=380, margin=dict(l=0, r=0, t=40, b=0)
                    )
                    st.plotly_chart(fig_hm, use_container_width=True)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE 7 — SQL INSIGHTS
# ══════════════════════════════════════════════════════════════════════════════
def page_sql_insights() -> None:
    st.markdown('<div class="page-title">🔍 SQL Insights</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="page-subtitle">Business questions answered directly from the database</div>',
        unsafe_allow_html=True,
    )

    QUERIES: list = [
        {
            "title": "Q1 — Which 10 states have the highest total transaction amount?",
            "sql": """
SELECT State,
       SUM(Count)  AS Total_Transactions,
       ROUND(SUM(Amount)/1e7, 2) AS Amount_Cr
FROM   map_transaction
GROUP  BY State
ORDER  BY Amount_Cr DESC
LIMIT  10
""",
            "chart": "bar", "x": "Amount_Cr", "y": "State", "color": PURPLE,
            "insight": "Maharashtra, Telangana & Karnataka lead. High urbanisation + fintech penetration.",
        },
        {
            "title": "Q2 — What is the year-wise growth in total transaction count?",
            "sql": """
SELECT Year,
       SUM(Count)                             AS Transactions,
       ROUND(SUM(Count)/1e9, 3)               AS Bn_Transactions,
       ROUND(SUM(Amount)/1e12, 2)             AS Trillion_Rs
FROM   map_transaction
GROUP  BY Year
ORDER  BY Year
""",
            "chart": "line", "x": "Year", "y": "Bn_Transactions", "color": TEAL,
            "insight": "91× growth from 2018→2024 — CAGR of ~90%, driven by smartphone & UPI adoption.",
        },
        {
            "title": "Q3 — Which transaction category generates the most revenue?",
            "sql": """
SELECT Category,
       SUM(Count)                  AS Total_Count,
       ROUND(SUM(Amount)/1e7, 1)   AS Amount_Cr,
       ROUND(SUM(Amount)/NULLIF(SUM(Count),0), 0) AS Avg_Value_Rs
FROM   agg_transaction
GROUP  BY Category
ORDER  BY Amount_Cr DESC
""",
            "chart": "bar", "x": "Category", "y": "Amount_Cr", "color": ORANGE,
            "insight": "Peer-to-peer payments generate the most revenue; merchant payments have highest count.",
        },
        {
            "title": "Q4 — Which states have the most registered users?",
            "sql": """
SELECT State,
       SUM(RegisteredUsers)    AS Total_Users,
       SUM(AppOpens)           AS Total_AppOpens,
       ROUND(SUM(AppOpens)*1.0/NULLIF(SUM(RegisteredUsers),0), 2) AS Engagement_Ratio
FROM   map_user
GROUP  BY State
ORDER  BY Total_Users DESC
LIMIT  10
""",
            "chart": "bar", "x": "Total_Users", "y": "State", "color": LIGHT_P,
            "insight": "Maharashtra & Uttar Pradesh have the most users; smaller states show higher engagement ratios.",
        },
        {
            "title": "Q5 — Quarter-wise split of transactions across all years",
            "sql": """
SELECT Quarter,
       SUM(Count)                           AS Total_Transactions,
       ROUND(SUM(Amount)/1e7, 0)            AS Amount_Cr,
       COUNT(DISTINCT Year)                 AS Years_Covered
FROM   map_transaction
GROUP  BY Quarter
ORDER  BY Quarter
""",
            "chart": "bar", "x": "Quarter", "y": "Total_Transactions", "color": YELLOW,
            "insight": "Q3 & Q4 tend to have higher volumes — festive season (Diwali, New Year) boosts UPI usage.",
        },
        {
            "title": "Q6 — Top 10 states by average transaction value",
            "sql": """
SELECT State,
       ROUND(SUM(Amount)*1.0/NULLIF(SUM(Count),0), 2) AS Avg_Txn_Value
FROM   map_transaction
GROUP  BY State
ORDER  BY Avg_Txn_Value DESC
LIMIT  10
""",
            "chart": "bar", "x": "Avg_Txn_Value", "y": "State", "color": TEAL,
            "insight": "Smaller/island territories often show higher avg values due to fewer but larger transfers.",
        },
        {
            "title": "Q7 — Which device brand has the most PhonePe users?",
            "sql": """
SELECT Brand,
       SUM(Count)                AS Total_Users,
       ROUND(AVG(Percentage)*100, 2) AS Avg_Market_Share_Pct
FROM   agg_user
WHERE  Brand != 'Others'
GROUP  BY Brand
ORDER  BY Total_Users DESC
LIMIT  10
""",
            "chart": "bar", "x": "Total_Users", "y": "Brand", "color": PURPLE,
            "insight": "Xiaomi dominates PhonePe's device base (~25%), followed by Samsung and Vivo.",
        },
        {
            "title": "Q8 — Insurance growth by year (policies & premium)",
            "sql": """
SELECT Year,
       SUM(Count)               AS Policies,
       ROUND(SUM(Amount)/1e7,2) AS Premium_Cr
FROM   map_insurance
GROUP  BY Year
ORDER  BY Year
""",
            "chart": "line", "x": "Year", "y": "Policies", "color": ORANGE,
            "insight": "Insurance saw 100× growth from 2020→2024, reflecting rapid fintech insurance adoption.",
        },
        {
            "title": "Q9 — States where app opens exceed registered users",
            "sql": """
SELECT State,
       SUM(RegisteredUsers)     AS Reg_Users,
       SUM(AppOpens)            AS App_Opens,
       ROUND(SUM(AppOpens)*1.0/NULLIF(SUM(RegisteredUsers),0), 2) AS Opens_Per_User
FROM   map_user
GROUP  BY State
HAVING App_Opens > Reg_Users
ORDER  BY Opens_Per_User DESC
""",
            "chart": "bar", "x": "Opens_Per_User", "y": "State", "color": TEAL,
            "insight": "High app-opens-per-user indicates very active daily usage — signals strong retention.",
        },
        {
            "title": "Q10 — Correlation: transactions vs registered users per year",
            "sql": """
SELECT t.Year,
       SUM(t.Count)             AS Transactions,
       SUM(u.RegisteredUsers)   AS Reg_Users,
       ROUND(SUM(t.Amount)/1e7, 1) AS Amount_Cr
FROM   map_transaction t
JOIN   map_user u
  ON   t.Year = u.Year
  AND  t.State = u.State
  AND  t.Quarter = u.Quarter
GROUP  BY t.Year
ORDER  BY t.Year
""",
            "chart": "scatter", "x": "Reg_Users", "y": "Transactions", "color": LIGHT_P,
            "insight": "Strong positive correlation — more registered users directly drives more transactions.",
        },
        {
            "title": "Q11 — Top insurance states by average premium size",
            "sql": """
SELECT State,
       SUM(Count)                             AS Policies,
       ROUND(SUM(Amount)/NULLIF(SUM(Count),0), 2) AS Avg_Premium_Rs
FROM   map_insurance
GROUP  BY State
HAVING Policies > 100
ORDER  BY Avg_Premium_Rs DESC
LIMIT  10
""",
            "chart": "bar", "x": "Avg_Premium_Rs", "y": "State", "color": ORANGE,
            "insight": "States with fewer but higher-value insurance policies likely target urban HNI customers.",
        },
        {
            "title": "Q12 — Year-over-year growth rate (%) for transactions",
            "sql": """
WITH yearly AS (
    SELECT Year, SUM(Count) AS cnt
    FROM   map_transaction
    GROUP  BY Year
)
SELECT a.Year,
       a.cnt AS Transactions,
       b.cnt AS Prev_Year,
       ROUND((a.cnt - b.cnt)*100.0/NULLIF(b.cnt,0), 2) AS Growth_Pct
FROM   yearly a
LEFT   JOIN yearly b ON a.Year = b.Year + 1
ORDER  BY a.Year
""",
            "chart": "bar", "x": "Year", "y": "Growth_Pct", "color": TEAL,
            "insight": "Peak growth ~140% in 2019→2020 (COVID pushed digital payments). Moderating to ~50% in 2024.",
        },
    ]

    for i, q in enumerate(QUERIES):
        with st.expander(q["title"], expanded=(i == 0)):
            df = run_query(q["sql"])
            if df.empty:
                st.warning("No data returned.")
                continue

            col_data, col_chart = st.columns([1, 1.6])
            with col_data:
                st.dataframe(df, use_container_width=True, hide_index=True)
                insight_box(f"<strong>💡 Insight:</strong> {q['insight']}")

            with col_chart:
                x_col = q["x"]
                y_col = q["y"]
                ctype = q["chart"]
                clr   = q["color"]

                try:
                    if ctype == "bar":
                        if y_col in df.columns and x_col in df.columns:
                            orient = "h" if df[y_col].dtype == object else "v"
                            if orient == "h":
                                fig = px.bar(
                                    df, x=x_col, y=y_col, orientation="h",
                                    color_discrete_sequence=[clr], template=TEMPLATE
                                )
                            else:
                                fig = px.bar(
                                    df, x=x_col, y=y_col,
                                    color_discrete_sequence=[clr], template=TEMPLATE
                                )
                        else:
                            num_cols = df.select_dtypes("number").columns.tolist()
                            cat_cols = df.select_dtypes("object").columns.tolist()
                            if num_cols and cat_cols:
                                fig = px.bar(
                                    df, x=cat_cols[0], y=num_cols[0],
                                    color_discrete_sequence=[clr], template=TEMPLATE
                                )
                            else:
                                st.info("Chart not renderable for this result set.")
                                continue

                    elif ctype == "line":
                        fig = px.line(
                            df, x=x_col, y=y_col, markers=True,
                            color_discrete_sequence=[clr], template=TEMPLATE
                        )

                    elif ctype == "scatter":
                        fig = px.scatter(
                            df, x=x_col, y=y_col,
                            color_discrete_sequence=[clr],
                            template=TEMPLATE, size_max=15
                        )
                    else:
                        fig = px.bar(df, template=TEMPLATE, color_discrete_sequence=[clr])

                    fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=300,
                        margin=dict(l=0, r=0, t=10, b=0),
                        xaxis=dict(gridcolor="#2a2a4a"),
                        yaxis=dict(gridcolor="#2a2a4a")
                    )
                    st.plotly_chart(fig, use_container_width=True)

                except Exception as chart_err:
                    st.warning(f"Chart render error: {chart_err}")

    # ── Custom SQL Runner ─────────────────────────────────────────────────────
    st.markdown("---")
    section_header("⌨️ Custom SQL Query Runner")
    st.markdown(
        '<div class="insight-box">Run any SELECT query against the <strong>phonepe (1).db</strong> database. '
        'Tables: <code>agg_transaction</code>, <code>agg_user</code>, <code>agg_insurance</code>, '
        '<code>map_transaction</code>, <code>map_user</code>, <code>map_insurance</code>, '
        '<code>top_transaction</code>, <code>top_user</code>, <code>top_insurance</code></div>',
        unsafe_allow_html=True,
    )
    custom_sql = st.text_area(
        "Enter SQL (SELECT only):",
        value="SELECT State, SUM(Amount) AS Total FROM map_transaction GROUP BY State ORDER BY Total DESC LIMIT 5",
        height=100,
        key="custom_sql",
    )
    if st.button("▶ Run Query", type="primary"):
        stripped = custom_sql.strip()
        if stripped.upper().startswith("SELECT"):
            result = run_query(stripped)
            if result is not None and not result.empty:
                st.success(f"✅ {len(result)} rows returned")
                st.dataframe(result, use_container_width=True, hide_index=True)
                num_cols = result.select_dtypes("number").columns.tolist()
                cat_cols = result.select_dtypes("object").columns.tolist()
                if num_cols and len(result) > 1:
                    auto_fig = px.bar(
                        result,
                        x=cat_cols[0] if cat_cols else result.columns[0],
                        y=num_cols[0],
                        color_discrete_sequence=[PURPLE],
                        template=TEMPLATE
                    )
                    auto_fig.update_layout(
                        paper_bgcolor="rgba(0,0,0,0)",
                        plot_bgcolor="rgba(0,0,0,0)",
                        height=300,
                        margin=dict(l=0, r=0, t=10, b=0)
                    )
                    st.plotly_chart(auto_fig, use_container_width=True)
            else:
                st.info("Query returned no results.")
        else:
            st.error("⚠️ Only SELECT queries are permitted.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    inject_css()

    # Validate DB before rendering anything else
    if not validate_database():
        st.stop()

    page = render_sidebar()

    if page == "🏠 Home":
        page_home()
    elif page == "💳 Transactions":
        page_transactions()
    elif page == "👤 Users":
        page_users()
    elif page == "🛡️ Insurance":
        page_insurance()
    elif page == "🗺️ Geo Map":
        page_geo()
    elif page == "🏆 Top Insights":
        page_top_insights()
    elif page == "🔍 SQL Insights":
        page_sql_insights()

    st.markdown(
        f"""
        <hr style="border-color:{PURPLE}44; margin-top:40px;">
        <p style="text-align:center; color:#404060; font-size:0.75rem;">
        PhonePe Pulse Analytics Dashboard · Built with Streamlit &amp; Plotly ·
        Data: 2018–2024 · <span style="color:{PURPLE};">©</span> 2024
        </p>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
