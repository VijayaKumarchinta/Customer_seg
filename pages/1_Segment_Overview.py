"""
Page 1: Segment Overview
Shows segment distribution with interactive charts and KPI cards.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.title("📊 Segment Overview")
st.markdown("### Customer segmentation distribution and key performance indicators")

# ---- Ensure data is loaded ----
if "customer_df" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

customer_df = st.session_state["customer_df"]
segment_summary = st.session_state["segment_summary"]
clean_df = st.session_state["clean_df"]
mom_metrics = st.session_state.get("mom_metrics", {})

# Apply country filter
selected_country = st.session_state.get("selected_country", "All Countries")
if selected_country != "All Countries":
    country_customers = clean_df[clean_df["Country"] == selected_country]["CustomerID"].unique()
    customer_df = customer_df[customer_df["CustomerID"].isin(country_customers)]
    # Recompute segment_summary from filtered data so percentages are accurate
    from utils.segmentation import get_segment_summary
    segment_summary = get_segment_summary(customer_df)

# ---- KPI Cards ----
st.subheader("🎯 Key Metrics")

total_customers = len(customer_df)
avg_recency = customer_df["Recency"].mean()
avg_frequency = customer_df["Frequency"].mean()
avg_monetary = customer_df["Monetary"].mean()
total_revenue = customer_df["Monetary"].sum()

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)

mom = mom_metrics
mom_rev_delta = f"{mom['revenue_delta']:+.1f}% MoM" if mom.get('revenue_delta') is not None else None
mom_cust_delta = f"{mom['customers_delta']:+.1f}% MoM" if mom.get('customers_delta') is not None else None
mom_orders_delta = f"{mom['orders_delta']:+.1f}% MoM" if mom.get('orders_delta') is not None else None

with kpi1:
    st.metric(
        "Total Customers",
        value=f"{total_customers:,}",
        delta=mom_cust_delta,
    )

with kpi2:
    st.metric(
        "Avg Recency",
        value=f"{avg_recency:.0f} days",
        delta=f"{'↓' if avg_recency < customer_df['Recency'].median() else '↑'} Since last purchase",
        delta_color="inverse",
    )

with kpi3:
    st.metric(
        "Avg Orders/Customer",
        value=f"{avg_frequency:.1f}",
        delta=mom_orders_delta,
    )

with kpi4:
    st.metric(
        "Avg Spend/Customer",
        value=f"£{avg_monetary:,.2f}",
        delta=None,
    )

with kpi5:
    st.metric(
        "Total Revenue",
        value=f"£{total_revenue:,.0f}",
        delta=mom_rev_delta,
    )

st.divider()

# ---- Segment Distribution Charts ----
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧩 Customer Distribution by Segment")

    # Donut chart
    fig_donut = px.pie(
        segment_summary,
        names="Segment",
        values="Customer_Count",
        hole=0.5,
        color_discrete_sequence=px.colors.qualitative.Bold,
        title="% of Customers per Segment",
    )
    fig_donut.update_traces(
        textposition="outside",
        textinfo="percent+label",
        hovertemplate="<b>%{label}</b><br>Customers: %{value:,}<br>Percentage: %{percent}<extra></extra>",
    )
    fig_donut.update_layout(
        height=450,
        showlegend=False,
        margin=dict(t=30, b=10, l=10, r=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col2:
    st.subheader("💰 Revenue Contribution by Segment")

    fig_bar = px.bar(
        segment_summary.sort_values("Total_Revenue", ascending=True),
        y="Segment",
        x="Total_Revenue",
        color="Segment",
        color_discrete_sequence=px.colors.qualitative.Bold,
        text="Pct_of_Revenue",
        title="Revenue per Segment",
        orientation="h",
    )
    fig_bar.update_traces(
        texttemplate="%{text}%",
        textposition="outside",
        hovertemplate="<b>%{y}</b><br>Revenue: £%{x:,.0f}<br>% of Total: %{text}%<extra></extra>",
    )
    fig_bar.update_layout(
        height=450,
        showlegend=False,
        xaxis_title="Total Revenue (£)",
        yaxis_title=None,
        margin=dict(t=30, b=10, l=10, r=40),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.divider()

# ---- Segment Metrics Comparison ----
st.subheader("📈 Segment Metrics Comparison")

metrics_to_show = st.multiselect(
    "Select metrics to compare:",
    options=["Avg_Recency_Days", "Avg_Frequency", "Avg_Monetary", "Customer_Count"],
    default=["Avg_Recency_Days", "Avg_Frequency", "Avg_Monetary"],
)

if metrics_to_show:
    fig_metrics = go.Figure()

    for metric in metrics_to_show:
        display_name = metric.replace("_", " ").replace("Avg", "Avg").title()
        fig_metrics.add_trace(
            go.Bar(
                name=display_name,
                x=segment_summary["Segment"],
                y=segment_summary[metric],
                hovertemplate=f"<b>%{{x}}</b><br>{display_name}: %{{y:,.1f}}<extra></extra>",
            )
        )

    fig_metrics.update_layout(
        barmode="group",
        height=450,
        xaxis_title="Segment",
        yaxis_title="Value",
        legend_title="Metric",
        hovermode="x unified",
        margin=dict(t=10, b=80, l=50, r=20),
    )
    st.plotly_chart(fig_metrics, use_container_width=True)

st.divider()

# ---- Detailed Segment Table ----
st.subheader("📋 Detailed Segment Breakdown")

display_cols = [
    "Segment", "Customer_Count", "Avg_Recency_Days", "Avg_Frequency",
    "Avg_Monetary", "Total_Revenue", "Pct_of_Customers", "Pct_of_Revenue"
]

detail_df = segment_summary[display_cols].copy()
detail_df.columns = [
    "Segment", "Customers", "Avg Recency (days)", "Avg Orders",
    "Avg Spend (£)", "Total Revenue (£)", "% Customers", "% Revenue"
]
detail_df["Avg Spend (£)"] = detail_df["Avg Spend (£)"].apply(lambda x: f"£{x:,.2f}")
detail_df["Total Revenue (£)"] = detail_df["Total Revenue (£)"].apply(lambda x: f"£{x:,.2f}")
detail_df["Avg Orders"] = detail_df["Avg Orders"].round(1)
detail_df["Avg Recency (days)"] = detail_df["Avg Recency (days)"].round(0).astype(int)

st.dataframe(
    detail_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Segment": st.column_config.TextColumn("Segment"),
        "Customers": st.column_config.NumberColumn("Customers", format="%d"),
        "Avg Recency (days)": st.column_config.NumberColumn("Avg Recency (days)", format="%d"),
        "Avg Orders": st.column_config.NumberColumn("Avg Orders", format="%.1f"),
        "Avg Spend (£)": st.column_config.TextColumn("Avg Spend (£)"),
        "Total Revenue (£)": st.column_config.TextColumn("Total Revenue (£)"),
        "% Customers": st.column_config.NumberColumn("% Customers", format="%.1f%%"),
        "% Revenue": st.column_config.NumberColumn("% Revenue", format="%.1f%%"),
    },
)

# Download button
csv = segment_summary.to_csv(index=False).encode("utf-8")
st.download_button(
    label="📥 Download Segment Data (CSV)",
    data=csv,
    file_name="customer_segments.csv",
    mime="text/csv",
)
