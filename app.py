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

# ─── Global Custom CSS — Premium Modern Aesthetic ────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ═══════════════════════════════════════════════════════════
       DESIGN TOKENS
       ═══════════════════════════════════════════════════════════ */
    :root {
        --primary: #FF4B4B;
        --primary-dark: #D93636;
        --primary-glow: rgba(255,75,75,0.25);
        --primary-subtle: rgba(255,75,75,0.08);

        --bg-page: #F0F2F5;
        --bg-card: #FFFFFF;
        --bg-card-hover: #FAFBFC;

        --text-primary: #0F1419;
        --text-secondary: #536471;
        --text-tertiary: #8B98A5;

        --border-light: rgba(0,0,0,0.06);
        --border-medium: rgba(0,0,0,0.1);

        --shadow-xs: 0 1px 2px rgba(0,0,0,0.04);
        --shadow-sm: 0 2px 8px rgba(0,0,0,0.06);
        --shadow-md: 0 8px 24px rgba(0,0,0,0.08);
        --shadow-lg: 0 16px 48px rgba(0,0,0,0.12);
        --shadow-glow: 0 8px 32px rgba(255,75,75,0.2);

        --radius-sm: 8px;
        --radius-md: 12px;
        --radius-lg: 16px;
        --radius-xl: 20px;

        --transition-fast: 150ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition: 250ms cubic-bezier(0.4, 0, 0.2, 1);
        --transition-slow: 400ms cubic-bezier(0.4, 0, 0.2, 1);

        --font: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    /* ─── Page Transition ─── */
    @keyframes fadeSlideUp {
        from { opacity: 0; transform: translateY(12px); }
        to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes fadeIn {
        from { opacity: 0; }
        to   { opacity: 1; }
    }
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }

    .main > .block-container {
        animation: fadeIn 0.4s ease-out both;
        padding-top: 1.5rem;
        max-width: 1400px;
        margin: 0 auto;
    }

    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
        }
    }

    /* ─── Base ─── */
    html { font-size: 16px; }
    body { font-family: var(--font); background: var(--bg-page); }

    .main {
        background: var(--bg-page);
    }

    /* ─── Typography ─── */
    h1, h2, h3, h4, h5, h6 {
        font-family: var(--font);
        letter-spacing: -0.02em;
    }
    .main h1 {
        font-size: 2.2rem;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.03em;
    }
    .main h2 {
        font-size: 1.5rem;
        font-weight: 600;
        color: var(--text-primary);
    }
    .main h3 {
        font-size: 1.15rem;
        font-weight: 600;
        color: var(--text-secondary);
    }

    a {
        color: var(--primary);
        text-decoration: none;
        transition: color var(--transition-fast);
    }
    a:hover {
        color: var(--primary-dark);
    }

    /* ─── Focus ─── */
    button:focus-visible,
    a:focus-visible,
    select:focus-visible,
    input:focus-visible,
    textarea:focus-visible,
    [tabindex]:focus-visible {
        outline: 2px solid var(--primary);
        outline-offset: 2px;
        border-radius: 6px;
    }

    /* ═══════════════════════════════════════════════════════════
       SIDEBAR — Premium Dark
       ═══════════════════════════════════════════════════════════ */
    section[data-testid="stSidebar"] {
        background: linear-gradient(175deg, #0A0F1D 0%, #141B2D 100%);
        border-right: 1px solid rgba(255,255,255,0.04);
    }
    section[data-testid="stSidebar"] > div:first-child {
        padding: 1.25rem 1rem;
    }
    section[data-testid="stSidebar"] p {
        color: #94A3B8;
        font-size: 0.85rem;
        line-height: 1.6;
    }
    section[data-testid="stSidebar"] h3 {
        color: #E2E8F0;
        font-weight: 600;
        font-size: 0.8rem !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    section[data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.06);
        margin: 1.25rem 0;
    }

    /* Sidebar navigation links — sized naturally via font inheritance */

    /* Sidebar selects */
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {
        border-color: rgba(255,255,255,0.08) !important;
        background: rgba(255,255,255,0.04) !important;
        color: #E2E8F0;
        border-radius: var(--radius-sm);
        transition: border-color var(--transition-fast);
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:hover {
        border-color: rgba(255,255,255,0.18) !important;
    }
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div:focus-within {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px var(--primary-glow) !important;
    }

    /* Sidebar slider */
    section[data-testid="stSidebar"] .stSlider [data-baseweb="slider"] {
        margin-top: 0.5rem;
    }
    section[data-testid="stSidebar"] .stSlider [role="slider"] {
        background: var(--primary) !important;
        box-shadow: 0 0 0 4px var(--primary-glow) !important;
    }

    /* Sidebar table */
    section[data-testid="stSidebar"] table {
        background: rgba(255,255,255,0.03);
        border-radius: var(--radius-sm);
        color: #CBD5E1;
        font-size: 0.78rem;
        width: 100%;
        border-collapse: collapse;
    }
    section[data-testid="stSidebar"] td {
        padding: 5px 10px;
        border-bottom: 1px solid rgba(255,255,255,0.04);
    }
    section[data-testid="stSidebar"] tr:last-child td {
        border-bottom: none;
    }
    section[data-testid="stSidebar"] td:first-child {
        font-weight: 500;
        color: #94A3B8;
    }
    section[data-testid="stSidebar"] td:last-child {
        text-align: right;
        font-weight: 600;
        color: #E2E8F0;
    }

    /* Sidebar divider customization */
    section[data-testid="stSidebar"] .stMarkdown hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    }

    /* ═══════════════════════════════════════════════════════════
       KPI METRIC CARDS — Glass Premium
       ═══════════════════════════════════════════════════════════ */
    div[data-testid="metric-container"] {
        background: var(--bg-card);
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 1.25rem 1rem;
        box-shadow: var(--shadow-xs);
        transition: transform var(--transition), box-shadow var(--transition), border-color var(--transition);
        position: relative;
        overflow: hidden;
    }
    /* Accent bar */
    div[data-testid="metric-container"]::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--primary), #FF6B6B);
        border-radius: var(--radius-md) var(--radius-md) 0 0;
    }
    /* Subtle shine overlay on hover */
    div[data-testid="metric-container"]::after {
        content: '';
        position: absolute;
        inset: 0;
        background: linear-gradient(105deg, transparent 40%, rgba(255,255,255,0.6) 50%, transparent 60%);
        background-size: 200% 100%;
        background-position: 100% 0;
        transition: background-position 0.6s;
        pointer-events: none;
    }
    div[data-testid="metric-container"]:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow-md);
        border-color: var(--border-medium);
    }
    div[data-testid="metric-container"]:hover::after {
        background-position: -100% 0;
    }
    div[data-testid="metric-container"] label {
        font-size: 0.75rem !important;
        font-weight: 600 !important;
        color: var(--text-secondary) !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
        font-size: 1.75rem !important;
        font-weight: 700 !important;
        color: var(--text-primary) !important;
        line-height: 1.2;
        margin-top: 0.15rem;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-size: 0.8rem !important;
    }
    div[data-testid="metric-container"] div[data-testid="stMetricDelta"] {
        font-weight: 600;
    }

    /* ═══════════════════════════════════════════════════════════
       BUTTONS — Refined
       ═══════════════════════════════════════════════════════════ */
    .stButton button {
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
        font-weight: 600;
        font-size: 0.85rem;
        border: 1px solid var(--border-medium);
        background: var(--bg-card);
        color: var(--text-primary);
        padding: 0.4rem 1rem;
        box-shadow: var(--shadow-xs);
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-sm);
        border-color: var(--primary);
    }
    .stButton button:active {
        transform: translateY(0);
    }
    button[kind="primary"] {
        background: linear-gradient(135deg, var(--primary), #FF6B6B) !important;
        color: white !important;
        border: none !important;
        box-shadow: 0 4px 14px var(--primary-glow) !important;
    }
    button[kind="primary"]:hover {
        box-shadow: 0 6px 20px var(--primary-glow) !important;
        transform: translateY(-2px) !important;
    }
    button[kind="primary"]:active {
        transform: translateY(0) !important;
        box-shadow: 0 2px 8px var(--primary-glow) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       DATAFRAMES — Clean Tables
       ═══════════════════════════════════════════════════════════ */
    .stDataFrame {
        border-radius: var(--radius-md);
        border: 1px solid var(--border-light);
        overflow: hidden;
        box-shadow: var(--shadow-xs);
        transition: box-shadow var(--transition-fast);
    }
    .stDataFrame:hover {
        box-shadow: var(--shadow-sm);
    }
    .stDataFrame table {
        font-size: 0.83rem;
        width: 100%;
        border-collapse: collapse;
    }
    .stDataFrame thead tr th {
        background: #0F1419;
        color: white;
        font-weight: 600;
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        padding: 0.7rem 0.85rem;
        border: none;
    }
    .stDataFrame tbody tr {
        transition: background var(--transition-fast);
    }
    .stDataFrame tbody tr:hover {
        background-color: var(--primary-subtle);
    }
    .stDataFrame tbody td {
        padding: 0.55rem 0.85rem;
        border-bottom: 1px solid var(--border-light);
        color: var(--text-secondary);
    }
    .stDataFrame tbody tr:last-child td {
        border-bottom: none;
    }

    /* ═══════════════════════════════════════════════════════════
       TABS — Pill Design
       ═══════════════════════════════════════════════════════════ */
    .stTabs {
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
        background: rgba(0,0,0,0.03);
        padding: 0.35rem;
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-light);
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: var(--radius-sm);
        padding: 0.45rem 1rem;
        font-weight: 500;
        font-size: 0.85rem;
        transition: all var(--transition-fast);
        color: var(--text-secondary);
        border: 1px solid transparent;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(255,75,75,0.06);
        color: var(--primary);
        border-color: rgba(255,75,75,0.1);
    }
    .stTabs [aria-selected="true"] {
        background: var(--bg-card) !important;
        box-shadow: var(--shadow-sm) !important;
        color: var(--primary) !important;
        font-weight: 600 !important;
        border-color: var(--border-light) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       DIVIDERS — Gradient fade
       ═══════════════════════════════════════════════════════════ */
    hr:not(.stSidebar hr) {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--border-medium), transparent);
        margin: 1.5rem 0;
    }

    /* ═══════════════════════════════════════════════════════════
       ALERTS / INFO BOXES
       ═══════════════════════════════════════════════════════════ */
    .stAlert {
        border-radius: var(--radius-sm);
        border: 1px solid var(--border-light) !important;
        box-shadow: var(--shadow-xs);
        font-size: 0.9rem;
    }
    .stAlert [data-testid="stAlertContainer"] {
        border-radius: var(--radius-sm);
    }
    /* Custom info box styling */
    div[data-baseweb="notification"] {
        border-radius: var(--radius-sm) !important;
        border: 1px solid var(--border-light) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       EXPANDERS
       ═══════════════════════════════════════════════════════════ */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: var(--text-secondary);
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
        padding: 0.5rem 0;
        font-size: 0.9rem;
    }
    .streamlit-expanderHeader:hover {
        color: var(--primary);
    }
    .streamlit-expanderHeader svg {
        transition: transform var(--transition-fast);
    }
    [data-testid="stExpander"] {
        border: 1px solid var(--border-light);
        border-radius: var(--radius-md);
        padding: 0 0.5rem;
        background: var(--bg-card);
        box-shadow: var(--shadow-xs);
        transition: box-shadow var(--transition-fast);
    }
    [data-testid="stExpander"]:hover {
        box-shadow: var(--shadow-sm);
    }

    /* ═══════════════════════════════════════════════════════════
       CAPTIONS
       ═══════════════════════════════════════════════════════════ */
    .stCaption {
        color: var(--text-tertiary);
        font-size: 0.78rem;
        font-weight: 400;
    }

    /* ═══════════════════════════════════════════════════════════
       MULTI-SELECT
       ═══════════════════════════════════════════════════════════ */
    .stMultiSelect [data-baseweb="select"] > div {
        border-radius: var(--radius-sm);
        border-color: var(--border-medium);
        transition: all var(--transition-fast);
        background: var(--bg-card);
    }
    .stMultiSelect [data-baseweb="select"] > div:hover {
        border-color: var(--primary);
    }
    .stMultiSelect [data-baseweb="select"] > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px var(--primary-glow);
    }

    /* ═══════════════════════════════════════════════════════════
       DOWNLOAD BUTTONS
       ═══════════════════════════════════════════════════════════ */
    .stDownloadButton button {
        border-radius: var(--radius-sm);
        transition: all var(--transition-fast);
        font-weight: 600;
        font-size: 0.82rem;
        border: 1px solid var(--border-medium) !important;
        box-shadow: var(--shadow-xs);
    }
    .stDownloadButton button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary) !important;
    }
    .stDownloadButton button:active {
        transform: translateY(0);
    }

    /* ═══════════════════════════════════════════════════════════
       SELECTBOX (main area, not sidebar)
       ═══════════════════════════════════════════════════════════ */
    .row-widget.stSelectbox [data-baseweb="select"] > div {
        border-radius: var(--radius-sm);
        border-color: var(--border-medium);
        transition: all var(--transition-fast);
        background: var(--bg-card);
        box-shadow: var(--shadow-xs);
    }
    .row-widget.stSelectbox [data-baseweb="select"] > div:hover {
        border-color: var(--primary);
    }
    .row-widget.stSelectbox [data-baseweb="select"] > div:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 3px var(--primary-glow);
    }

    /* ═══════════════════════════════════════════════════════════
       SLIDER (main area)
       ═══════════════════════════════════════════════════════════ */
    .stSlider [role="slider"] {
        background: var(--primary) !important;
        box-shadow: 0 0 0 4px var(--primary-glow) !important;
        transition: box-shadow var(--transition-fast);
    }
    .stSlider [role="slider"]:hover {
        box-shadow: 0 0 0 6px var(--primary-glow) !important;
    }

    /* ═══════════════════════════════════════════════════════════
       PROGRESS / SPINNER
       ═══════════════════════════════════════════════════════════ */
    .stSpinner {
        text-align: center;
        padding: 2.5rem;
    }
    .stSpinner > div {
        border-top-color: var(--primary) !important;
        border-width: 3px;
        width: 32px;
        height: 32px;
    }
    .stSpinner p {
        font-size: 0.9rem;
        color: var(--text-secondary);
        margin-top: 0.75rem;
    }

    /* ═══════════════════════════════════════════════════════════
       RESPONSIVE BREAKPOINTS
       ═══════════════════════════════════════════════════════════ */
    @media screen and (max-width: 1024px) {
        .hero-banner { padding: 1.25rem !important; }
        .hero-title { font-size: 1.5rem !important; }
        .hero-subtitle { font-size: 0.85rem !important; }
        .main h1 { font-size: 1.8rem; }
        .main h2 { font-size: 1.3rem; }
        .main h3 { font-size: 1.05rem; }
        .section-title { font-size: 1.05rem !important; }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.4rem !important;
        }
        .stDataFrame table { font-size: 0.75rem; }
        .stDataFrame thead tr th { font-size: 0.7rem; padding: 0.5rem 0.65rem; }
        hr:not(.stSidebar hr) { margin: 1rem 0; }
        .main > .block-container { padding-top: 1rem; }
    }

    @media screen and (max-width: 768px) {
        html { font-size: 14px; }
        .hero-banner { padding: 1rem !important; margin-bottom: 1rem !important; }
        .hero-title { font-size: 1.3rem !important; }
        .hero-subtitle { font-size: 0.8rem !important; }
        .main h1 { font-size: 1.5rem; }
        .main h2 { font-size: 1.15rem; }
        .main h3 { font-size: 0.95rem; }
        .section-title { font-size: 0.95rem !important; }
        div[data-testid="metric-container"] {
            padding: 0.85rem 0.65rem;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            font-size: 1.2rem !important;
        }
        .stDataFrame { overflow-x: auto !important; }
        .stDataFrame table { font-size: 0.7rem; }
        .stDataFrame thead tr th { font-size: 0.65rem; padding: 0.4rem 0.5rem; white-space: nowrap; }
        .stTabs [data-baseweb="tab-list"] { overflow-x: auto !important; flex-wrap: nowrap !important; gap: 0.25rem; padding: 0.25rem; }
        .stTabs [data-baseweb="tab"] { padding: 0.35rem 0.6rem !important; font-size: 0.78rem; white-space: nowrap; }
        section[data-testid="stSidebar"] > div:first-child { padding: 0.75rem 0.6rem; }
        hr:not(.stSidebar hr) { margin: 0.75rem 0; }
        .main > .block-container { padding-top: 0.75rem; }
    }

    @media screen and (max-width: 480px) {
        html { font-size: 13px; }
        .hero-banner { padding: 0.75rem !important; }
        .hero-title { font-size: 1.1rem !important; }
        .hero-subtitle { font-size: 0.75rem !important; }
        .main h1 { font-size: 1.3rem; }
        .main h2 { font-size: 1rem; }
        div[data-testid="metric-container"] { padding: 0.6rem 0.5rem; }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] { font-size: 1rem !important; }
        .stDataFrame table { font-size: 0.65rem; }
        hr:not(.stSidebar hr) { margin: 0.5rem 0; }
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
    <div role="img" aria-label="Customer Segmentation Dashboard logo"
         style="text-align: center; padding: 1.75rem 0.5rem 1rem;">
        <div style="width: 52px; height: 52px; margin: 0 auto 0.75rem;
                    background: linear-gradient(135deg, #FF4B4B 0%, #FF6B6B 100%);
                    border-radius: 14px; display: flex; align-items: center; justify-content: center;
                    box-shadow: 0 8px 24px rgba(255,75,75,0.3);">
            <span style="font-size: 1.6rem; line-height: 1;">📊</span>
        </div>
        <h3 style="margin: 0; color: #F1F5F9; font-weight: 700; font-size: 1.1rem; letter-spacing: -0.01em;">
            Customer Segmentation
        </h3>
        <p style="font-size: 0.7rem; color: #64748B; margin-top: 0.2rem; letter-spacing: 0.02em;">
            RFM Analysis · K-Means
        </p>
        <div style="margin-top: 0.75rem; padding: 0.2rem 0.75rem;
                    background: linear-gradient(135deg, rgba(255,75,75,0.15), rgba(255,75,75,0.08));
                    border: 1px solid rgba(255,75,75,0.15);
                    border-radius: 100px; display: inline-block;">
            <span style="font-size: 0.65rem; color: #FF6B6B; font-weight: 600; letter-spacing: 0.04em;">LIVE DASHBOARD</span>
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
</div>""",
    unsafe_allow_html=True,
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
    <div role="contentinfo" aria-label="Dashboard footer"
         style="font-size: 0.65rem; color: #64748B; text-align: center; line-height: 1.7; padding: 0.5rem 0;">
        <span style="opacity: 0.5;">Built with Streamlit</span><br>
        <span style="opacity: 0.7;">UCI Online Retail II Dataset</span><br>
        <span style="opacity: 0.5;">RFM + K-Means Segmentation</span><br>
        <span style="opacity: 0.4;">© 2025</span>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Home page content ----
st.markdown(
    """
    <div role="region" aria-label="Dashboard introduction"
         style="text-align: center; padding: 3rem 2.5rem; margin-bottom: 2rem;
                background: linear-gradient(145deg, #0A0F1D 0%, #1A2332 50%, #0F172A 100%);
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 20px;
                position: relative; overflow: hidden;">
        <!-- Subtle noise/gradient overlay -->
        <div style="position: absolute; inset: 0;
                    background: radial-gradient(ellipse at 20% 50%, rgba(255,75,75,0.06) 0%, transparent 60%);
                    pointer-events: none;"></div>
        <div style="position: absolute; inset: 0;
                    background: radial-gradient(ellipse at 80% 20%, rgba(59,130,246,0.04) 0%, transparent 50%);
                    pointer-events: none;"></div>
        <h1 class="home-hero-title"
            style="font-size: 2.8rem; margin-bottom: 0.5rem; color: #FFFFFF; font-weight: 800;
                   letter-spacing: -0.03em; position: relative;">
            📊 Customer Segmentation Dashboard
        </h1>
        <p style="font-size: 1.1rem; color: #94A3B8; max-width: 600px; margin: 0.5rem auto 0; line-height: 1.7; position: relative;">
            Analyze <strong style="color: #FF4B4B;">500K+ real transactions</strong> from a UK-based online retailer.
            Segment customers by behavior using <strong style="color: #F59E0B;">RFM analysis</strong> and <strong style="color: #3B82F6;">K-Means clustering</strong>.
        </p>
        <div style="margin-top: 1.25rem; display: flex; justify-content: center; gap: 0.75rem; flex-wrap: wrap; position: relative;">
            <span style="background: rgba(255,75,75,0.12); color: #FF6B6B; padding: 0.25rem 0.9rem;
                         border-radius: 100px; font-size: 0.78rem; font-weight: 600;
                         border: 1px solid rgba(255,75,75,0.15);" aria-label="11 segments">🏆 11 Segments</span>
            <span style="background: rgba(16,185,129,0.12); color: #34D399; padding: 0.25rem 0.9rem;
                         border-radius: 100px; font-size: 0.78rem; font-weight: 600;
                         border: 1px solid rgba(16,185,129,0.15);" aria-label="CLV prediction">📈 CLV Prediction</span>
            <span style="background: rgba(59,130,246,0.12); color: #60A5FA; padding: 0.25rem 0.9rem;
                         border-radius: 100px; font-size: 0.78rem; font-weight: 600;
                         border: 1px solid rgba(59,130,246,0.15);" aria-label="Churn analysis">🔮 Churn Analysis</span>
            <span style="background: rgba(245,158,11,0.12); color: #FBBF24; padding: 0.25rem 0.9rem;
                         border-radius: 100px; font-size: 0.78rem; font-weight: 600;
                         border: 1px solid rgba(245,158,11,0.15);" aria-label="PDF reports">📄 PDF Reports</span>
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
         style="background: linear-gradient(135deg, var(--primary-subtle, rgba(255,75,75,0.05)), rgba(255,75,75,0.02));
                border: 1px solid rgba(255,75,75,0.1); border-radius: 14px; padding: 1.5rem; height: 100%;">
            <h4 style="margin: 0 0 0.75rem 0; color: #DC2626; font-size: 0.9rem; font-weight: 700;">💡 Quick Navigation</h4>
            <p style="font-size: 0.85rem; color: #7F1D1D; line-height: 2; margin: 0;">
                👈 Use the <strong>sidebar</strong> to explore:<br><br>
                <span style="font-weight: 600;">📊 1. Segment Overview</span> — Distribution &amp; KPIs<br>
                <span style="font-weight: 600;">🔬 2. RFM Analysis</span> — Interactive scatter plots<br>
                <span style="font-weight: 600;">🎯 3. Recommendations</span> — Actionable insights<br>
                <span style="font-weight: 600;">🔮 4. Predictive Analytics</span> — CLV, churn &amp; trends
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
        <div role="region" aria-label="Download report description" style="padding: 0.75rem 0;">
            <p style="color: var(--text-secondary, #536471); font-size: 0.95rem; margin: 0; line-height: 1.6;">
                <strong>📥 Download a comprehensive PDF report</strong> including: executive summary,
                segment breakdown, churn risk analysis, business recommendations, and monthly trends.
            </p>
            <p style="color: var(--text-tertiary, #8B98A5); font-size: 0.8rem; margin-top: 0.5rem;">
                ⚡ Generated on-the-fly with your latest data — includes all current filters and segments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <div style="text-align: center; padding: 2.5rem 0 0.5rem;">
        <p style="color: #8B98A5; font-size: 0.85rem;">
            ⬅️ Use the sidebar pages to dive deeper into each analysis view
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
