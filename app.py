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


@st.cache_data(show_spinner="📥 Loading dataset...")
def load_and_prepare_data(force_refresh: bool = False):
    """Full pipeline: load → clean → summarize → segment."""
    raw = load_data(force_refresh=force_refresh)
    clean = clean_data(raw)
    customer_df = create_customer_summary(clean)
    customer_df = calculate_rfm_scores(customer_df)
    customer_df = label_segments_rfm(customer_df)
    return raw, clean, customer_df


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

# ---- Predictive Models ----
with st.spinner("🧠 Training CLV prediction model..."):
    pred_clv_df = compute_clv(customer_df, clean_df)
    st.session_state["pred_clv_df"] = pred_clv_df
    # Extract model metadata from .attrs (avoids hidden st.session_state writes inside utils)
    st.session_state["clv_model_metrics"] = pred_clv_df.attrs.get("model_metrics", {})
    st.session_state["clv_scaler"] = pred_clv_df.attrs.get("clv_scaler", None)
    st.session_state["clv_model"] = pred_clv_df.attrs.get("clv_model", None)

with st.spinner("⚠️ Training churn prediction model..."):
    pred_churn_df = compute_churn_probability(customer_df, clean_df)
    st.session_state["pred_churn_df"] = pred_churn_df
    # Extract model metadata from .attrs
    st.session_state["churn_model_metrics"] = pred_churn_df.attrs.get("churn_model_metrics", {})
    st.session_state["churn_roc_data"] = pred_churn_df.attrs.get("churn_roc_data", None)
    st.session_state["churn_scaler"] = pred_churn_df.attrs.get("churn_scaler", None)
    st.session_state["churn_model"] = pred_churn_df.attrs.get("churn_model", None)

# ---- Month-over-Month Metrics ----
with st.spinner("📈 Computing month-over-month trends..."):
    mom_metrics = compute_mom_metrics(clean_df)
    st.session_state["mom_metrics"] = mom_metrics

# ---- Update customer_df with predictive columns ----
customer_df["Predicted_CLV"] = pred_clv_df["Predicted_CLV"]
customer_df["Churn_Probability"] = pred_churn_df["Churn_Probability"]
customer_df["Churn_Risk_Level"] = pred_churn_df["Churn_Risk_Level"]
st.session_state["customer_df"] = customer_df


# ---- Sidebar ----
st.sidebar.markdown(
    """
    <div style="text-align: center; padding: 1rem 0;">
        <h1 style="font-size: 2.2rem; margin: 0;">📊</h1>
        <h3 style="margin: 0.3rem 0; color: #FF4B4B;">Customer Segmentation</h3>
        <p style="font-size: 0.8rem; color: #888;">RFM Analysis · K-Means Clustering</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.divider()

# Dataset info
st.sidebar.markdown("### 📋 Dataset Info")
st.sidebar.markdown(
    f"""
| Metric | Value |
|--------|-------|
| Transactions | {data_info['rows']:,} |
| Customers | {data_info['customers']:,} |
| Products | {data_info['products']:,} |
| Countries | {data_info['countries']} |
| Date Range | {data_info['date_range'][0]} to {data_info['date_range'][1]} |
"""
)

st.sidebar.divider()

# Global filters
st.sidebar.markdown("### 🔍 Filters")

all_countries = sorted(customer_df.merge(
    clean_df[["CustomerID", "Country"]].drop_duplicates(),
    on="CustomerID",
    how="left"
)["Country"].dropna().unique().tolist())

selected_country = st.sidebar.selectbox(
    "Country",
    options=["All Countries"] + all_countries,
    index=0,
)

# Store filter in session state
st.session_state["selected_country"] = selected_country

# KPI clusters slider (for K-Means page)
st.sidebar.markdown("### ⚙️ Clustering Settings")
n_clusters = st.sidebar.slider(
    "Number of Segments (K-Means)",
    min_value=2,
    max_value=8,
    value=5,
    step=1,
    help="Select how many customer segments to create using K-Means. Use the Elbow Method page to find the optimal K.",
)
st.session_state["n_clusters"] = n_clusters

st.sidebar.divider()
st.sidebar.markdown(
    """
    <div style="font-size: 0.75rem; color: #888; text-align: center;">
        Built with Streamlit · UCI Online Retail II<br>
        RFM + K-Means Segmentation<br>
        © 2025
    </div>
    """,
    unsafe_allow_html=True,
)

# ---- Home page content ----
st.markdown(
    """
    <div style="text-align: center; padding: 3rem 1rem 1rem;">
        <h1 style="font-size: 3rem; margin-bottom: 0.3rem;">📊 Customer Segmentation Dashboard</h1>
        <p style="font-size: 1.2rem; color: #666; max-width: 700px; margin: 0 auto;">
            Analyze <strong>500K+ real transactions</strong> from a UK-based online retailer.
            Segment customers by behavior using RFM analysis and K-Means clustering.
        </p>
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

st.divider()

# Segment overview mini-table
st.subheader("📋 Segment Quick Overview")
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
    st.info(
        "👈 **Navigate** using the sidebar to explore:\n\n"
        "**1.** Segment Overview — distribution & KPIs\n\n"
        "**2.** RFM Analysis — interactive scatter plots\n\n"
        "**3.** Recommendations — actionable insights per segment\n\n"
        "**4.** Predictive Analytics — CLV, churn & MoM trends",
        icon="💡",
    )

st.divider()

# ---- Download PDF Report ----
st.subheader("📄 Download Full Analysis Report")
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
        "Download a comprehensive PDF report including executive summary, "
        "segment breakdown, churn risk analysis, business recommendations, and monthly trends."
    )

st.divider()
st.markdown(
    "<p style='text-align: center; color: #888; font-size: 0.85rem;'>"
    "⬅️ Use the sidebar pages to dive deeper into each analysis view</p>",
    unsafe_allow_html=True,
)
