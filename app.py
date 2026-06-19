"""
Customer Segmentation & Reporting Dashboard
Main entry point — sets up page config, loads data, and provides shared state.
"""

import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="Customer Segmentation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Global Custom CSS ───────────────────────────────────────────
st.markdown("""
<style>
    /* ─── Design Tokens ─── */
    :root {
        --primary: #FF4B4B;
        --primary-dark: #E03E3E;
        --primary-light: #FFF0F0;
        --dark: #0F172A;
        --medium: #475569;
        --light: #F8FAFC;
        --border: #E2E8F0;
        --accent-gold: #F59E0B;
        --accent-green: #10B981;
        --accent-blue: #3B82F6;
        --shadow-sm: 0 1px 2px rgba(0,0,0,0.05);
        --shadow-md: 0 4px 6px -1px rgba(0,0,0,0.1), 0 2px 4px -2px rgba(0,0,0,0.1);
        --shadow-lg: 0 10px 15px -3px rgba(0,0,0,0.1), 0 4px 6px -4px rgba(0,0,0,0.1);
        --radius: 12px;
        --radius-sm: 8px;
        --transition: all 0.2s ease;
    }

    /* ─── Page Transition Animation ───
       The .block-container wrapper persists between Streamlit widget
       interactions — it only gets recreated on actual page navigation.
       So a subtle fade+slide plays just once per page visit, then
       stays visible during normal widget use.
       Other elements (hero banners, section titles) are recreated
       on every rerender, so we deliberately avoid animating them
       to prevent flicker when using filters and sliders.
       ─── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(8px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .main > .block-container {
        animation: fadeSlideUp 0.35s ease-out both;
        padding-top: 1.5rem;
    }

    /* Reduce motion preference — respect user accessibility settings */
    @media (prefers-reduced-motion: reduce) {
        *,
        *::before,
        *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ─── Typography ─── */
    html { font-size: 16px; }
    h1, h2, h3, h4 { font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif; }

    /* ─── Focus / Keyboard Accessibility ───
       Scoped to interactive elements only — divs, spans, headings and other
       non-interactive elements should not receive a focus ring.
       ─── */
    button:focus-visible,
    a:focus-visible,
    select:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    [tabindex]:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
    }
    .stButton button:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
        box-shadow: 0 0 0 3px rgba(255,75,75,0.3);
    }

    /* ─── Sidebar ─── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F172A 0%, #1E293B 100%);
        border-right: none;
    }
    section[data-testid="stSidebar"] > div:first-child { padding: 1rem 0.75rem; }
    section[data-testid="stSidebar"] p { color: #CBD5E1; }
    section[data-testid="stSidebar"] h3 { color: #F1F5F9; font-weight: 600; }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.08);
        margin: 1rem 0;
    }

    /* Sidebar select boxes */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        border-color: rgba(255,255,255,0.12) !important;
        background: rgba(255,255,255,0.05) !important;
        color: #E2E8F0;
        border-radius: var(--radius-sm);
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: var(--primary) !important;
    }

    /* Sidebar metric table */
    section[data-testid="stSidebar"] table {
        background: rgba(255,255,255,0.05);
        border-radius: var(--radius-sm);
        color: #E2E8F0;
        font-size: 0.8rem;
    }
    section[data-testid="stSidebar"] td {
        padding: 4px 8px;
        border-color: rgba(255,255,255,0.06);
    }



    /* ─── KPI Cards ─── */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #FFFFFF 0%, #F8FAFC 100%);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 0.75rem;
        box-shadow: var(--shadow-sm);
        transition: var(--transition);
        position: relative;
        overflow: hidden;
    }
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: var(--primary);
        border-radius: var(--radius) var(--radius) 0 0;
    }
    div[data-testid="metric-container"]:hover {
        box-shadow: var(--shadow-md);
        transform: translateY(-2px);
        border-color: var(--primary);
    }
    div[data-testid="metric-container"] label {
        font-size: 0.8rem;
        font-weight: 600;
        color: var(--medium);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--dark);
        line-height: 1.2;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-size: 0.8rem;
    }

    /* ─── Buttons ─── */
    .stButton button {
        border-radius: var(--radius-sm);
        transition: var(--transition);
        font-weight: 600;
        border: none;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 4px 12px rgba(255,75,75,0.4);
    }

    /* ─── DataFrames ─── */
    .stDataFrame {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border);
        overflow: hidden;
    }
    .stDataFrame table {
        font-size: 0.85rem;
    }
    .stDataFrame thead tr th {
        background: linear-gradient(135deg, var(--dark), #1E293B);
        color: white;
        font-weight: 600;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.03em;
        padding: 0.6rem 0.75rem;
    }
    .stDataFrame tbody tr:hover {
        background-color: #F1F5F9;
        transition: var(--transition);
    }

    /* ─── Tabs ─── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: var(--light);
        padding: 0.4rem;
        border-radius: var(--radius);
        border: 1px solid var(--border);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: var(--transition);
        color: var(--medium);
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,75,75,0.08);
        color: var(--primary);
    }
    .stTabs [aria-selected="true"] {
        background: white;
        box-shadow: var(--shadow-sm);
        color: var(--primary);
        font-weight: 600;
    }

    /* ─── Dividers ─── */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border), transparent);
        margin: 1.5rem 0;
    }

    /* ─── Info/Success/Warning boxes ─── */
    .stAlert {
        border-radius: var(--radius-sm);
        border: none !important;
        box-shadow: var(--shadow-sm);
    }
    .stAlert [data-testid="stAlertContainer"] {
        border-radius: var(--radius-sm);
    }

    /* ─── Headers ─── */
    .main h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--dark);
        letter-spacing: -0.02em;
    }
    .main h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--dark);
    }
    .main h3 {
        font-size: 1.2rem;
        font-weight: 600;
        color: var(--medium);
    }

    /* ─── Expanders ─── */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--medium);
        border-radius: var(--radius-sm);
        transition: var(--transition);
    }
    .streamlit-expanderHeader:hover {
        color: var(--primary);
    }

    /* ─── Captions ─── */
    .stCaption {
        color: #94A3B8;
        font-size: 0.8rem;
    }

    /* ─── Multi-select ─── */
    .stMultiSelect [data-baseweb="select"] > div {
        border-radius: var(--radius-sm);
        border-color: var(--border);
    }
    .stMultiSelect [data-baseweb="select"] > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(255,75,75,0.1);
    }

    /* ─── Download buttons ─── */
    .stDownloadButton button {
        border-radius: var(--radius-sm);
        transition: var(--transition);
        font-weight: 600;
    }
    .stDownloadButton button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    /* ─── Progress / Spinner ─── */
    .stSpinner {
        text-align: center;
        padding: 2rem;
    }
    .stSpinner > div {
        border-top-color: var(--primary);
    }

    /* ═══════════════════════════════════════════════════════════
       RESPONSIVE BREAKPOINTS
       ═══════════════════════════════════════════════════════════ */

    /* ─── Tablet: 768px–1024px ─── */
    @media screen and (max-width: 1024px) {
        /* Reduce hero banner padding */
        .hero-banner { padding: 1.25rem !important; }
        .hero-title { font-size: 1.5rem !important; }
        .hero-subtitle { font-size: 0.85rem !important; }

        /* Smaller headings */
        .main h1 { font-size: 1.8rem; }
        .main h2 { font-size: 1.3rem; }
        .main h3 { font-size: 1.05rem; }
        .section-title { font-size: 1.05rem !important; }

        /* KPI cards shrink */
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.4rem;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.7rem;
        }

        /* Smaller table text */
        .stDataFrame table { font-size: 0.75rem; }
        .stDataFrame thead tr th { font-size: 0.7rem; padding: 0.4rem 0.5rem; }

        /* Reduce spacing */
        hr { margin: 1rem 0; }
        .main > .block-container { padding-top: 1rem; }
    }

    /* ─── Mobile: <768px ─── */
    @media screen and (max-width: 768px) {
        /* Base font */
        html { font-size: 14px; }

        /* Hero banner compact */
        .hero-banner { padding: 1rem !important; margin-bottom: 1rem !important; }
        .hero-title { font-size: 1.3rem !important; }
        .hero-subtitle { font-size: 0.8rem !important; }

        /* Headings */
        .main h1 { font-size: 1.5rem; letter-spacing: -0.01em; }
        .main h2 { font-size: 1.15rem; }
        .main h3 { font-size: 0.95rem; }
        .section-title { font-size: 0.95rem !important; }

        /* KPI cards */
        div[data-testid="metric-container"] {
            padding: 0.75rem 0.5rem;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.2rem;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.65rem;
        }

        /* Tables — scrollable horizontally */
        .stDataFrame {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
        }
        .stDataFrame table { font-size: 0.7rem; }
        .stDataFrame thead tr th {
            font-size: 0.65rem;
            padding: 0.35rem 0.4rem;
            white-space: nowrap;
        }
        .stDataFrame tbody td {
            padding: 0.3rem 0.4rem;
            white-space: nowrap;
        }

        /* Tabs — scrollable */
        .stTabs [data-baseweb="tab-list"] {
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch;
            flex-wrap: nowrap !important;
            gap: 0.3rem;
            padding: 0.3rem;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 0.35rem 0.6rem !important;
            font-size: 0.8rem;
            white-space: nowrap;
        }

        /* Sidebar */
        section[data-testid="stSidebar"] > div:first-child {
            padding: 0.5rem 0.5rem;
        }
        section[data-testid="stSidebar"] table {
            font-size: 0.7rem;
        }

        /* Reduce spacing */
        hr { margin: 0.75rem 0; }
        .main > .block-container { padding-top: 0.75rem; }

        /* Home page hero banner */
        .home-hero-title {
            font-size: 1.8rem !important;
        }
    }

    /* ─── Small Mobile: <480px ─── */
    @media screen and (max-width: 480px) {
        html { font-size: 13px; }

        .hero-banner { padding: 0.75rem !important; }
        .hero-title { font-size: 1.1rem !important; }
        .hero-subtitle { font-size: 0.75rem !important; }

        .home-hero-title {
            font-size: 1.3rem !important;
        }

        .main h1 { font-size: 1.3rem; }
        .main h2 { font-size: 1rem; }
        .main h3, .section-title { font-size: 0.85rem !important; }

        div[data-testid="metric-container"] {
            padding: 0.5rem 0.4rem;
            overflow-wrap: break-word;
            word-break: break-word;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1rem;
        }
        div[data-testid="metric-container"] label {
            font-size: 0.6rem;
        }

        .stDataFrame table { font-size: 0.65rem; }
        .stDataFrame thead tr th { font-size: 0.6rem; padding: 0.25rem 0.3rem; }

        hr { margin: 0.5rem 0; }
    }
</style>
""", unsafe_allow_html=True)

import pandas as pd
from utils.data_loader import load_data, get_data_info
from utils.preprocessing import clean_data, create_customer_summary
from utils.segmentation import (
    calculate_rfm_scores,
    label_segments_rfm,
    get_segment_summary,
)
from utils.predictive import (
    compute_clv,
    compute_churn_probability,
    compute_mom_metrics,
)
from utils.ui_components import hero_header, section_header


@st.cache_data(show_spinner="📥 Loading dataset...")
def load_and_prepare_data(force_refresh: bool = False):
    """Full pipeline: load → clean → summarize → segment."""
    raw = load_data(force_refresh=force_refresh)
    clean = clean_data(raw)
    customer_df = create_customer_summary(clean)
    customer_df = calculate_rfm_scores(customer_df)
    customer_df = label_segments_rfm(customer_df)
    return raw, clean, customer_df


@st.cache_data(show_spinner="🧠 Training CLV prediction model...")
def train_clv_model(customer_df, clean_df):
    """Train CLV model with caching so it doesn't re-run on every page visit."""
    return compute_clv(customer_df, clean_df)


@st.cache_data(show_spinner="⚠️ Training churn prediction model...")
def train_churn_model(customer_df, clean_df):
    """Train churn model with caching so it doesn't re-run on every page visit."""
    return compute_churn_probability(customer_df, clean_df)


@st.cache_data(show_spinner="📈 Computing month-over-month trends...")
def compute_mom(clean_df):
    """Compute MoM metrics with caching."""
    return compute_mom_metrics(clean_df)


# ---- Load data ----
with st.spinner("📊 Preparing customer segmentation data..."):
    raw_df, clean_df, customer_df = load_and_prepare_data()

# ---- Compute summary tables ----
segment_summary = get_segment_summary(customer_df)
data_info = get_data_info(raw_df)

# ---- Store in session state for pages ----
st.session_state["raw_df"] = raw_df
st.session_state["clean_df"] = clean_df
st.session_state["customer_df"] = customer_df
st.session_state["segment_summary"] = segment_summary
st.session_state["data_info"] = data_info
st.session_state["data_loaded"] = True

# ---- Predictive Models (cached — only retrain when input data changes) ----
pred_clv_df = train_clv_model(customer_df, clean_df)
st.session_state["pred_clv_df"] = pred_clv_df
# Extract model metadata from .attrs (avoids hidden st.session_state writes inside utils)
st.session_state["clv_model_metrics"] = pred_clv_df.attrs.get("model_metrics", {})
st.session_state["clv_scaler"] = pred_clv_df.attrs.get("clv_scaler", None)
st.session_state["clv_model"] = pred_clv_df.attrs.get("clv_model", None)

pred_churn_df = train_churn_model(customer_df, clean_df)
st.session_state["pred_churn_df"] = pred_churn_df
# Extract model metadata from .attrs
st.session_state["churn_model_metrics"] = pred_churn_df.attrs.get("churn_model_metrics", {})
st.session_state["churn_roc_data"] = pred_churn_df.attrs.get("churn_roc_data", None)
st.session_state["churn_scaler"] = pred_churn_df.attrs.get("churn_scaler", None)
st.session_state["churn_model"] = pred_churn_df.attrs.get("churn_model", None)

# ---- Month-over-Month Metrics (cached) ----
mom_metrics = compute_mom(clean_df)
st.session_state["mom_metrics"] = mom_metrics

# ---- Update customer_df with predictive columns ----
customer_df["Predicted_CLV"] = pred_clv_df["Predicted_CLV"]
customer_df["Churn_Probability"] = pred_churn_df["Churn_Probability"]
customer_df["Churn_Risk_Level"] = pred_churn_df["Churn_Risk_Level"]
st.session_state["customer_df"] = customer_df


# ---- Sidebar ----
st.sidebar.markdown(
    """
    <div role="img" aria-label="Customer Segmentation Dashboard logo" style="text-align: center; padding: 1.5rem 0.5rem;">
        <div aria-hidden="true" style="font-size: 2.5rem; margin-bottom: 0.3rem;">📊</div>
        <h3 style="margin: 0.2rem 0; color: #FF4B4B; font-weight: 700; font-size: 1.2rem;">Customer<br>Segmentation</h3>
        <p style="font-size: 0.75rem; color: #64748B; margin-top: 0.2rem;">RFM Analysis · K-Means</p>
        <div style="margin-top: 0.75rem; padding: 0.3rem 0.75rem; background: rgba(255,75,75,0.12); border-radius: 20px; display: inline-block;">
            <span style="font-size: 0.7rem; color: #FF4B4B; font-weight: 600;">LIVE DASHBOARD</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()

# Dataset info
st.sidebar.markdown("<h3 id='sidebar-dataset-info' style='font-size: 0.85rem; font-weight: 600; letter-spacing: 0.03em;'>📋 Dataset Info</h3>", unsafe_allow_html=True)
st.sidebar.markdown(
    f"""
<div role="region" aria-labelledby="sidebar-dataset-info">
<table aria-label="Dataset statistics">
<tr><td>📦 Transactions</td><td>{data_info['rows']:,}</td></tr>
<tr><td>👥 Customers</td><td>{data_info['customers']:,}</td></tr>
<tr><td>🏷️ Products</td><td>{data_info['products']:,}</td></tr>
<tr><td>🌍 Countries</td><td>{data_info['countries']}</td></tr>
<tr><td>📅 Period</td><td>{data_info['date_range'][0]} to {data_info['date_range'][1]}</td></tr>
</table>
</div>"""
)

st.sidebar.divider()

# Global filters
st.sidebar.markdown("<h3 id='sidebar-filters' style='font-size: 0.85rem; font-weight: 600; letter-spacing: 0.03em;'>🔍 Filters</h3>", unsafe_allow_html=True)

all_countries = sorted(customer_df.merge(
    clean_df[["CustomerID", "Country"]].drop_duplicates(),
    on="CustomerID",
    how="left"
)["Country"].dropna().unique().tolist())

selected_country = st.sidebar.selectbox(
    "Country",
    options=["All Countries"] + all_countries,
    index=0,
    key="sidebar_country_filter",
)

# Store filter in session state
st.session_state["selected_country"] = selected_country

# KPI clusters slider (for K-Means page)
st.sidebar.markdown("<h3 id='sidebar-clustering' style='font-size: 0.85rem; font-weight: 600; letter-spacing: 0.03em; margin-top: 1rem;'>⚙️ Clustering Settings</h3>", unsafe_allow_html=True)
n_clusters = st.sidebar.slider(
    "Number of Segments (K-Means)",
    min_value=2,
    max_value=8,
    value=5,
    step=1,
    key="sidebar_clusters_slider",
    help="Select how many customer segments to create using K-Means. Use the Elbow Method page to find the optimal K.",
)
st.session_state["n_clusters"] = n_clusters

st.sidebar.divider()
st.sidebar.markdown(
    """
    <div role="contentinfo" aria-label="Dashboard footer" style="font-size: 0.7rem; color: #94A3B8; text-align: center; line-height: 1.6;">
        Built with Streamlit<br>
        UCI Online Retail II Dataset<br>
        RFM + K-Means Segmentation<br>
        © 2025
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Home page content ----
st.markdown(
    """
    <div class="card" role="region" aria-label="Dashboard introduction"
         style="text-align: center; padding: 2.5rem 2rem; margin-bottom: 1.5rem; background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: none;">
        <h1 class="home-hero-title" style="font-size: 2.8rem; margin-bottom: 0.3rem; color: #FFFFFF; font-weight: 700;">📊 Customer Segmentation Dashboard</h1>
        <p style="font-size: 1.1rem; color: #94A3B8; max-width: 650px; margin: 0.5rem auto 0;">
            Analyze <strong style="color: #FF4B4B;">500K+ real transactions</strong> from a UK-based online retailer.
            Segment customers by behavior using <strong style="color: #F59E0B;">RFM analysis</strong> and <strong style="color: #3B82F6;">K-Means clustering</strong>.
        </p>
        <div style="margin-top: 1rem; display: flex; justify-content: center; gap: 1.5rem; flex-wrap: wrap;">
            <span style="background: rgba(255,75,75,0.15); color: #FF4B4B; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;" aria-label="11 segments">🏆 11 Segments</span>
            <span style="background: rgba(16,185,129,0.15); color: #10B981; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;" aria-label="CLV prediction">📈 CLV Prediction</span>
            <span style="background: rgba(59,130,246,0.15); color: #3B82F6; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;" aria-label="Churn analysis">🔮 Churn Analysis</span>
            <span style="background: rgba(245,158,11,0.15); color: #F59E0B; padding: 0.2rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600;" aria-label="PDF reports">📄 PDF Reports</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Quick KPI row
col1, col2, col3, col4, col5 = st.columns(5)

mom = mom_metrics
mom_rev_delta = f"{mom['revenue_delta']:+.1f}% MoM" if mom.get('revenue_delta') is not None else None
mom_cust_delta = f"{mom['customers_delta']:+.1f}% MoM" if mom.get('customers_delta') is not None else None
mom_aov_delta = f"{mom['aov_delta']:+.1f}% MoM" if mom.get('aov_delta') is not None else None
mom_orders_delta = f"{mom['orders_delta']:+.1f}% MoM" if mom.get('orders_delta') is not None else None

with col1:
    st.metric("Total Customers", f"{data_info['customers']:,}", delta=mom_cust_delta)
with col2:
    st.metric("Total Transactions", f"{data_info['rows']:,}", delta=mom_orders_delta)
with col3:
    st.metric("Avg Order Value", f"£{clean_df['TotalPrice'].mean():.2f}", delta=mom_aov_delta)
with col4:
    st.metric("Total Revenue", f"£{clean_df['TotalPrice'].sum():,.0f}", delta=mom_rev_delta)
with col5:
    avg_churn = customer_df['Churn_Probability'].mean()
    st.metric("Avg Churn Risk", f"{avg_churn:.1%}", delta=f"{segment_summary['Segment'].nunique()} segments")

# Segment overview mini-table
st.markdown(section_header("📋 Segment Quick Overview"), unsafe_allow_html=True)

col1, col2 = st.columns([2, 1])

with col1:
    display_cols = ["Segment", "Customer_Count", "Avg_Monetary", "Avg_Frequency", "Pct_of_Customers", "Pct_of_Revenue"]
    display_df = segment_summary[display_cols].copy()
    display_df.columns = ["Segment", "Customers", "Avg Spend (£)", "Avg Orders", "% of Customers", "% of Revenue"]
    display_df["Avg Spend (£)"] = display_df["Avg Spend (£)"].apply(lambda x: f"£{x:,.2f}")
    display_df["Avg Orders"] = display_df["Avg Orders"].round(1)
    display_df["% of Customers"] = display_df["% of Customers"].apply(lambda x: f"{x}%")
    display_df["% of Revenue"] = display_df["% of Revenue"].apply(lambda x: f"{x}%")

    st.dataframe(
        display_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Segment": st.column_config.TextColumn("Segment", width="medium"),
            "Customers": st.column_config.NumberColumn("Customers", format="%d"),
            "Avg Spend (£)": st.column_config.TextColumn("Avg Spend (£)"),
            "Avg Orders": st.column_config.TextColumn("Avg Orders"),
            "% of Customers": st.column_config.TextColumn("% of Customers"),
            "% of Revenue": st.column_config.TextColumn("% of Revenue"),
        },
    )

with col2:
    st.markdown(
        """
        <div role="complementary" aria-label="Quick navigation guide"
         style="background: linear-gradient(135deg, #FFF0F0, #FFE4E4); border: 1px solid #FFD0D0; border-radius: 12px; padding: 1.25rem; height: 100%;">
            <h4 style="margin: 0 0 0.75rem 0; color: #991B1B; font-size: 0.9rem;">💡 Quick Navigation</h4>
            <p style="font-size: 0.85rem; color: #7F1D1D; line-height: 1.7; margin: 0;">
                👈 Use the <strong>sidebar</strong> to explore:<br><br>
                <b>📊 1. Segment Overview</b> — Distribution &amp; KPIs<br>
                <b>🔬 2. RFM Analysis</b> — Interactive scatter plots<br>
                <b>🎯 3. Recommendations</b> — Actionable insights<br>
                <b>🔮 4. Predictive Analytics</b> — CLV, churn &amp; trends
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

# Download PDF Report section
st.markdown(section_header("📄 Download Full Analysis Report"), unsafe_allow_html=True)

col1, col2 = st.columns([1, 2])
with col1:
    if st.button("📄 Generate PDF Report", type="primary", use_container_width=True):
        with st.spinner("Generating PDF report..."):
            from utils.report_generator import generate_report
            pdf_bytes = generate_report(
                customer_df=customer_df,
                segment_summary=segment_summary,
                clean_df=clean_df,
                data_info=data_info,
                mom_metrics=mom_metrics,
                churn_metrics=st.session_state.get("churn_model_metrics"),
            )
            st.download_button(
                label="📥 Download PDF Report",
                data=pdf_bytes,
                file_name="customer_segmentation_report.pdf",
                mime="application/pdf",
                use_container_width=True,
            )
with col2:
    st.markdown(
        """
        <div role="region" aria-label="Download report description" style="padding: 0.5rem 0;">
            <p style="color: #475569; font-size: 0.95rem; margin: 0;">
                <strong>📥 Download a comprehensive PDF report</strong> including: executive summary,
                segment breakdown, churn risk analysis, business recommendations, and monthly trends.
            </p>
            <p style="color: #94A3B8; font-size: 0.8rem; margin-top: 0.5rem;">
                ⚡ Generated on-the-fly with your latest data — includes all current filters and segments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="text-align: center; padding: 2rem 0 0.5rem;">
        <p style="color: #94A3B8; font-size: 0.85rem;">
            ⬅️ Use the sidebar pages to dive deeper into each analysis view
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
