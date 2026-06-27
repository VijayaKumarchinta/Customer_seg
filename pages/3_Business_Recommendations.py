"""
Page 3: Business Recommendations
Actionable marketing strategies for each customer segment.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from utils.ui_components import hero_header, section_header


st.markdown(hero_header("🎯 Business Recommendations", "Data-driven marketing strategies for each customer segment"), unsafe_allow_html=True)

# ---- Ensure data is loaded ----
if "customer_df" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

customer_df = st.session_state["customer_df"]
segment_summary = st.session_state["segment_summary"]
clean_df = st.session_state["clean_df"]

# Apply country filter
selected_country = st.session_state.get("selected_country", "All Countries")
if selected_country != "All Countries":
    country_customers = clean_df[clean_df["Country"] == selected_country]["CustomerID"].unique()
    customer_df = customer_df[customer_df["CustomerID"].isin(country_customers)]
    from utils.segmentation import get_segment_summary
    segment_summary = get_segment_summary(customer_df)

# ---- Segment Investment Recommendation ----
st.markdown(section_header("💰 Where to Invest Your Marketing Budget"), unsafe_allow_html=True)

# Calculate a priority score
segment_summary["Priority_Score"] = (
    segment_summary["Pct_of_Revenue"] * 0.5
    + segment_summary["Pct_of_Customers"] * 0.3
    - (segment_summary["Avg_Recency_Days"] / segment_summary["Avg_Recency_Days"].max()) * 0.2
)
segment_summary = segment_summary.sort_values("Priority_Score", ascending=False)

fig_priority = px.bar(
    segment_summary,
    y="Segment",
    x="Priority_Score",
    color="Segment",
    color_discrete_sequence=px.colors.qualitative.Bold,
    orientation="h",
    text_auto=".2f",
    title="Segment Priority Score (higher = more urgent investment)",
)
fig_priority.update_layout(
    height=400,
    showlegend=False,
    xaxis_title="Priority Score",
    yaxis_title=None,
    margin=dict(t=40, b=10, l=10, r=40),
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(size=11),
)
fig_priority.update_traces(
    hovertemplate="<b>%{y}</b><br>Priority Score: %{x:.2f}<extra></extra>"
)
st.plotly_chart(fig_priority, use_container_width=True)

st.caption("Score based on: Revenue contribution (50%), Customer base size (30%), Urgency from recency (20%)")

# ---- Segment Explorer ----
st.markdown(section_header("🔍 Segment Explorer"), unsafe_allow_html=True)
st.markdown('<p style="color: #475569; font-size: 0.9rem; margin: 0 0 0.75rem 0;">Select a segment below to see detailed analysis and strategy recommendations.</p>', unsafe_allow_html=True)

selected_segment = st.selectbox(
    "Select a segment to explore:",
    options=segment_summary["Segment"].unique().tolist(),
    index=0,
    key="recs_segment_select",
)

# Filter to that segment
segment_customers = customer_df[customer_df["Segment"] == selected_segment]
seg_info = segment_summary[segment_summary["Segment"] == selected_segment].iloc[0]

col1, col2 = st.columns([2, 1])

with col1:
    # Profile metrics
    m1, m2, m3, m4 = st.columns(4)
    with m1:
        st.metric("Customers", f"{seg_info['Customer_Count']:,}")
    with m2:
        st.metric("Avg Recency", f"{seg_info['Avg_Recency_Days']:.0f} days")
    with m3:
        st.metric("Avg Frequency", f"{seg_info['Avg_Frequency']:.1f} orders")
    with m4:
        st.metric("Avg Spend", f"£{seg_info['Avg_Monetary']:,.2f}")

    # Top products
    st.markdown("#### 🛍️ Top Products in This Segment")
    segment_invoices = clean_df[
        clean_df["CustomerID"].isin(segment_customers["CustomerID"])
    ]
    top_products = (
        segment_invoices.groupby("Description")["Quantity"]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
    )

    fig_products = px.bar(
        top_products,
        x="Quantity",
        y="Description",
        orientation="h",
        color="Quantity",
        color_continuous_scale="Blues",
        title=f"Top 10 Products — {selected_segment}",
    )
    fig_products.update_layout(
        height=350,
        showlegend=False,
        yaxis_title=None,
        xaxis_title="Total Units Purchased",
        margin=dict(t=40, b=10, l=10, r=10),
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(size=11),
    )
    st.plotly_chart(fig_products, use_container_width=True)

with col2:
    # Strategy card
    st.markdown("#### 🎯 Recommended Strategy")
    recommendation = seg_info.get("Recommendation", "Analyze further.")
    st.info(recommendation, icon="💡")

    # Key insights
    st.markdown("#### 📌 Key Insights")
    insights = []

    recency_avg = customer_df["Recency"].mean()
    freq_avg = customer_df["Frequency"].mean()
    monetary_avg = customer_df["Monetary"].mean()

    if seg_info["Avg_Recency_Days"] < recency_avg * 0.7:
        insights.append("✅ **Low recency** — purchased recently (good engagement)")
    elif seg_info["Avg_Recency_Days"] > recency_avg * 1.3:
        insights.append("⚠️ **High recency** — hasn't purchased in a while (at risk)")
    else:
        insights.append("📊 **Average recency** — typical engagement level")

    if seg_info["Avg_Frequency"] > freq_avg * 1.3:
        insights.append("✅ **High frequency** — loyal, repeat purchasers")
    elif seg_info["Avg_Frequency"] < freq_avg * 0.7:
        insights.append("⚠️ **Low frequency** — infrequent purchasers, need engagement")
    else:
        insights.append("📊 **Average frequency** — standard purchase behavior")

    if seg_info["Avg_Monetary"] > monetary_avg * 1.3:
        insights.append("💰 **High spenders** — above-average transaction value")
    elif seg_info["Avg_Monetary"] < monetary_avg * 0.7:
        insights.append("💸 **Low spenders** — below-average transaction value")
    else:
        insights.append("📊 **Average spend** — typical transaction value")

    for insight in insights:
        st.markdown(f"- {insight}")

    # Revenue impact
    st.markdown("#### 💰 Revenue Impact")
    st.metric(
        "Revenue Contribution",
        f"£{seg_info['Total_Revenue']:,.2f}",
        delta=f"{seg_info['Pct_of_Revenue']}% of total",
    )

# ---- Campaign Planner ----
st.markdown(section_header("📋 Campaign Planner"), unsafe_allow_html=True)
st.markdown('<p style="color: #475569; font-size: 0.9rem; margin: 0 0 0.75rem 0;">Based on the RFM segmentation, here are recommended marketing campaigns for each segment:</p>', unsafe_allow_html=True)

campaigns_data = {
    "Segment": ["Champions", "Loyal Customers", "Potential Loyalists", "Big Spenders",
                 "New Customers", "At Risk - Champions", "At Risk", "Hibernating",
                 "Need Attention", "Lost"],
    "Campaign Type": ["Loyalty Reward", "Upsell / Cross-sell", "Engagement Nurture",
                       "VIP Experience", "Welcome Series", "Urgent Re-engagement",
                       "Win-back Email", "Reactivation", "Personalized Offer", "Last Resort"],
    "Channel": ["Email + SMS", "Email", "Email + Social", "Phone + Email",
                 "Email + Onboarding", "Email + SMS", "Email", "Email + Discount",
                 "Email + Push", "Email + Survey"],
    "Discount Level": ["10%", "15%", "20%", "5% (exclusivity)",
                        "20% first purchase", "30%", "25%", "40%+",
                        "15%", "50%+"],
    "Urgency": ["Low", "Low", "Medium", "Medium",
                 "High", "Critical", "High", "Medium",
                 "Medium", "Low"],
}

campaigns_df = pd.DataFrame(campaigns_data)

def color_urgency(val):
    if val == "Critical":
        return "background-color: #dc3545; color: white; font-weight: 600;"
    elif val == "High":
        return "background-color: #ffc107; color: black; font-weight: 600;"
    elif val == "Medium":
        return "background-color: #17a2b8; color: white; font-weight: 600;"
    elif val == "Low":
        return "background-color: #28a745; color: white; font-weight: 600;"
    return ""

styled_campaigns = campaigns_df.style.map(color_urgency, subset=["Urgency"])
st.dataframe(
    styled_campaigns,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Segment": st.column_config.TextColumn("Segment", width="medium"),
        "Campaign Type": st.column_config.TextColumn("Recommended Campaign"),
        "Channel": st.column_config.TextColumn("Channel"),
        "Discount Level": st.column_config.TextColumn("Discount/Offer"),
        "Urgency": st.column_config.TextColumn("Urgency"),
    },
)

st.caption("💡 These recommendations are based on the RFM characteristics of each segment. "
           "Adjust based on your specific business context and budget.")

# ---- Full Export ----
st.markdown(section_header("📥 Export Analysis"), unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    export_cols = [
        "Segment", "Customer_Count", "Avg_Recency_Days", "Avg_Frequency",
        "Avg_Monetary", "Total_Revenue", "Pct_of_Customers", "Pct_of_Revenue", "Recommendation"
    ]
    export_df = segment_summary[export_cols].copy()
    export_df.columns = [
        "Segment", "Customers", "Avg Recency (days)", "Avg Frequency",
        "Avg Spend (£)", "Total Revenue (£)", "% Customers", "% Revenue", "Recommendation"
    ]

    csv_full = export_df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Segment Report (CSV)",
        data=csv_full,
        file_name="customer_segmentation_report.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col2:
    customer_csv = customer_df[["CustomerID", "Recency", "Frequency", "Monetary",
                                 "R_Score", "F_Score", "M_Score", "RFM_Score", "Segment"]].to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Download Customer Labels (CSV)",
        data=customer_csv,
        file_name="customer_segment_labels.csv",
        mime="text/csv",
        use_container_width=True,
    )

with col3:
    if "rec_pdf_ready" not in st.session_state:
        st.session_state.rec_pdf_ready = False
        st.session_state.rec_pdf_data = None

    def _generate_rec_pdf():
        from utils.report_generator import generate_report

        with st.status("📄 Generating PDF report...", expanded=True) as status:
            st.write("Compiling segment data and recommendations...")
            pdf_bytes = generate_report(
                customer_df=customer_df,
                segment_summary=segment_summary,
                clean_df=clean_df,
                data_info=st.session_state.get("data_info", {}),
                mom_metrics=st.session_state.get("mom_metrics"),
                churn_metrics=st.session_state.get("churn_model_metrics"),
            )
            status.update(label="✅ PDF generated successfully!", state="complete")

        st.session_state.rec_pdf_data = pdf_bytes
        st.session_state.rec_pdf_ready = True

    if st.session_state.rec_pdf_ready:
        st.download_button(
            label="📥 Download PDF Report",
            data=st.session_state.rec_pdf_data,
            file_name="customer_segmentation_report.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary",
        )
        if st.button("🔄 Regenerate", key="rec_regenerate", use_container_width=True):
            st.session_state.rec_pdf_ready = False
            st.session_state.rec_pdf_data = None
            st.rerun()
    else:
        st.button(
            "📥 Generate & Download PDF",
            type="primary",
            on_click=_generate_rec_pdf,
            use_container_width=True,
        )

# ---- Executive Summary ----
st.markdown(section_header("📝 Executive Summary"), unsafe_allow_html=True)

champions_count = segment_summary[segment_summary["Segment"] == "Champions"]["Customer_Count"].sum()
at_risk_count = segment_summary[segment_summary["Segment"].isin(["At Risk", "At Risk - Champions"])]["Customer_Count"].sum()
lost_count = segment_summary[segment_summary["Segment"].isin(["Lost", "Hibernating"])]["Customer_Count"].sum()
new_count = segment_summary[segment_summary["Segment"] == "New Customers"]["Customer_Count"].sum()

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🏆 Champions", f"{champions_count:,}", help="Most valuable customers — reward them")
with col2:
    st.metric("⚠️ At Risk", f"{at_risk_count:,}",
              delta=f"{-at_risk_count if at_risk_count > 0 else 0}" if at_risk_count > 0 else None,
              delta_color="inverse", help="Customers at risk of churning — re-engage them")
with col3:
    st.metric("💤 Lost/Hibernating", f"{lost_count:,}", help="Customers who stopped buying — reactivate")
with col4:
    st.markdown("---")
    st.markdown("**Key Action Items:**")
    if champions_count > 0:
        st.markdown(f"- 🎖️ **Reward** {champions_count:,} Champions with loyalty perks")
    if at_risk_count > 0:
        st.markdown(f"- 📧 **Win back** {at_risk_count:,} at-risk customers ASAP")
    if lost_count > 0:
        st.markdown(f"- 💤 **Re-engage** {lost_count:,} lost/hibernating customers")
    if new_count > 0:
        st.markdown(f"- 🌟 **Nurture** {new_count:,} new customers into loyal ones")
