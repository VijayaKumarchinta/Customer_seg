"""
Page 4: Predictive Analytics
CLV prediction distribution, churn probability analysis, and MoM performance trends.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.title("🔮 Predictive Analytics")
st.markdown("### Customer Lifetime Value · Churn Risk · Month-over-Month Trends")

# ---- Ensure data is loaded ----
if "customer_df" not in st.session_state:
    st.error("Data not loaded. Please return to the home page.")
    st.stop()

customer_df = st.session_state["customer_df"]
clean_df = st.session_state["clean_df"]

# Apply country filter
selected_country = st.session_state.get("selected_country", "All Countries")
if selected_country != "All Countries":
    country_customers = clean_df[clean_df["Country"] == selected_country]["CustomerID"].unique()
    customer_df = customer_df[customer_df["CustomerID"].isin(country_customers)]

# ---- Check predictive models are loaded ----
if "pred_clv_df" not in st.session_state:
    st.error("Predictive models not loaded. Please return to the home page and wait for model training.")
    st.stop()

pred_clv_df = st.session_state["pred_clv_df"]
pred_churn_df = st.session_state["pred_churn_df"]
mom_metrics = st.session_state["mom_metrics"]
clv_model_metrics = st.session_state.get("clv_model_metrics", {})
churn_model_metrics = st.session_state.get("churn_model_metrics", {})

# Merge for combined analysis
combined_df = pred_clv_df.copy()
if "Churn_Probability" in pred_churn_df.columns:
    combined_df["Churn_Probability"] = pred_churn_df["Churn_Probability"]
    combined_df["Churn_Risk_Level"] = pred_churn_df["Churn_Risk_Level"]

# ---- Tabs ----
tab1, tab2, tab3, tab4 = st.tabs([
    "💰 CLV Analysis",
    "⚠️ Churn Prediction",
    "🔄 CLV × Churn Matrix",
    "📈 MoM Performance",
])

# ================================================================
# TAB 1: CLV Analysis
# ================================================================
with tab1:
    st.subheader("💰 Customer Lifetime Value — Prediction")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(
            "Avg Predicted CLV",
            f"£{combined_df['Predicted_CLV'].mean():,.2f}",
            delta=f"R² = {clv_model_metrics.get('r2', 'N/A')}",
        )
    with col2:
        st.metric(
            "Median CLV",
            f"£{combined_df['Predicted_CLV'].median():,.2f}",
        )
    with col3:
        high_clv_pct = (combined_df["is_high_clv"].sum() / len(combined_df) * 100) if "is_high_clv" in combined_df.columns else 50
        st.metric(
            "High-Value Customers",
            f"{high_clv_pct:.0f}%",
            delta=f"{combined_df['is_high_clv'].sum():,} customers" if "is_high_clv" in combined_df.columns else None,
        )

    # CLV distribution
    col1, col2 = st.columns(2)

    with col1:
        fig_clv_hist = px.histogram(
            combined_df,
            x="Predicted_CLV",
            nbins=60,
            color_discrete_sequence=["#FF4B4B"],
            title="CLV Distribution Across All Customers",
            labels={"Predicted_CLV": "Predicted Lifetime Value (£)"},
        )
        fig_clv_hist.add_vline(
            x=combined_df["Predicted_CLV"].median(),
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Median: £{combined_df['Predicted_CLV'].median():,.0f}",
        )
        fig_clv_hist.update_layout(height=400, xaxis_range=[0, combined_df["Predicted_CLV"].quantile(0.95)])
        st.plotly_chart(fig_clv_hist, use_container_width=True)

    with col2:
        # CLV by segment
        clv_by_segment = (
            combined_df.groupby("Segment")["Predicted_CLV"]
            .agg(["mean", "median", "count"])
            .round(2)
            .reset_index()
            .sort_values("mean", ascending=False)
        )

        fig_clv_seg = px.bar(
            clv_by_segment,
            x="Segment",
            y="mean",
            error_y=clv_by_segment["mean"] * 0.3,  # approximate std
            color="Segment",
            color_discrete_sequence=px.colors.qualitative.Bold,
            title="Average Predicted CLV by Segment",
            labels={"mean": "Avg CLV (£)", "Segment": ""},
            text_auto=".0f",
        )
        fig_clv_seg.update_layout(height=400, showlegend=False)
        fig_clv_seg.update_traces(
            texttemplate="£%{text:,.0f}",
            hovertemplate="<b>%{x}</b><br>Avg CLV: £%{y:,.2f}<br>Customers: %{customdata[0]:,}<extra></extra>",
            customdata=clv_by_segment[["count"]],
        )
        st.plotly_chart(fig_clv_seg, use_container_width=True)

    # Model info expander
    with st.expander("📖 About the CLV Model"):
        st.markdown(f"""
        **Model:** Linear Regression
        **R² Score:** {clv_model_metrics.get('r2', 'N/A')}
        **Mean Absolute Error:** £{clv_model_metrics.get('mae', 'N/A')}

        **Features used:**
        """)
        features = clv_model_metrics.get("feature_names", [])
        coeffs = clv_model_metrics.get("coefficients", {})
        for feat in features:
            coef = coeffs.get(feat, 0)
            direction = "📈" if coef > 0 else "📉"
            st.markdown(f"- {direction} **{feat}**: {coef:.4f}")

        st.markdown("""
        **Interpretation:** Positive coefficients increase predicted CLV (e.g., higher Frequency = higher CLV).
        Negative coefficients decrease it (e.g., higher Recency = lower CLV).
        """)

# ================================================================
# TAB 2: Churn Prediction
# ================================================================
with tab2:
    st.subheader("⚠️ Churn Probability — Risk Assessment")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Model AUC", f"{churn_model_metrics.get('auc', 'N/A')}",
                  help="Area Under ROC Curve — 1.0 = perfect, 0.5 = random")
    with col2:
        st.metric("Avg Churn Risk", f"{combined_df['Churn_Probability'].mean():.1%}",
                  help="Average predicted churn probability across all customers")
    with col3:
        critical = len(combined_df[combined_df["Churn_Risk_Level"] == "Critical"])
        st.metric("⚠️ Critical Risk", f"{critical:,}",
                  help="Customers with >70% churn probability — act immediately")
    with col4:
        low_risk = len(combined_df[combined_df["Churn_Risk_Level"] == "Low Risk"])
        st.metric("✅ Low Risk", f"{low_risk:,}")

    col1, col2 = st.columns(2)

    with col1:
        # Churn probability distribution
        fig_churn_hist = px.histogram(
            combined_df,
            x="Churn_Probability",
            nbins=40,
            color="Churn_Risk_Level",
            color_discrete_map={
                "Low Risk": "#28a745",
                "Medium Risk": "#ffc107",
                "High Risk": "#dc3545",
                "Critical": "#6d0101",
            },
            title="Churn Probability Distribution",
            labels={"Churn_Probability": "Predicted Churn Probability"},
            category_orders={"Churn_Risk_Level": ["Low Risk", "Medium Risk", "High Risk", "Critical"]},
        )
        fig_churn_hist.update_layout(
            height=400,
            xaxis_title="Churn Probability",
            yaxis_title="Number of Customers",
            legend_title="Risk Level",
        )
        fig_churn_hist.add_vline(x=0.3, line_dash="dash", line_color="orange",
                                  annotation_text="Medium Risk Threshold")
        fig_churn_hist.add_vline(x=0.7, line_dash="dash", line_color="red",
                                  annotation_text="Critical Threshold")
        st.plotly_chart(fig_churn_hist, use_container_width=True)

    with col2:
        # Churn risk by segment
        churn_by_segment = (
            combined_df.groupby("Segment")
            .agg(
                Avg_Churn_Risk=("Churn_Probability", "mean"),
                Customer_Count=("CustomerID", "count"),
                Critical_Pct=("Churn_Risk_Level", lambda x: (x == "Critical").mean() * 100),
            )
            .round(3)
            .reset_index()
            .sort_values("Avg_Churn_Risk", ascending=False)
        )

        fig_churn_seg = px.bar(
            churn_by_segment,
            x="Avg_Churn_Risk",
            y="Segment",
            color="Avg_Churn_Risk",
            color_continuous_scale="RdYlGn_r",
            orientation="h",
            title="Average Churn Risk by Segment (sorted highest to lowest)",
            labels={"Avg_Churn_Risk": "Avg Churn Probability", "Segment": ""},
            text_auto=".0%",
        )
        fig_churn_seg.update_layout(height=450, showlegend=False, xaxis_range=[0, 1])
        fig_churn_seg.update_traces(
            hovertemplate="<b>%{y}</b><br>Avg Churn Risk: %{x:.1%}<br>Customers: %{customdata[0]:,}<br>Critical: %{customdata[1]:.0f}%<extra></extra>",
            customdata=churn_by_segment[["Customer_Count", "Critical_Pct"]],
        )
        st.plotly_chart(fig_churn_seg, use_container_width=True)

    # Churn risk summary table
    st.subheader("📋 Churn Risk Summary")
    risk_summary = (
        combined_df.groupby("Churn_Risk_Level")
        .agg(
            Customers=("CustomerID", "count"),
            Avg_CLV=("Predicted_CLV", "mean"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
        )
        .round(2)
        .reset_index()
    )
    risk_summary.columns = ["Risk Level", "Customers", "Avg CLV (£)", "Avg Recency (days)", "Avg Orders"]
    risk_summary["Avg CLV (£)"] = risk_summary["Avg CLV (£)"].apply(lambda x: f"£{x:,.2f}")
    risk_summary["Avg Recency (days)"] = risk_summary["Avg Recency (days)"].round(0).astype(int)
    risk_summary["Avg Orders"] = risk_summary["Avg Orders"].round(1)

    st.dataframe(risk_summary, use_container_width=True, hide_index=True)

    # Model info
    with st.expander("📖 About the Churn Model"):
        st.markdown(f"""
        **Model:** Logistic Regression (balanced class weights)
        **ROC-AUC:** {churn_model_metrics.get('auc', 'N/A')}
        **Accuracy:** {churn_model_metrics.get('accuracy', 'N/A')}
        **Churn Label Threshold:** >{churn_model_metrics.get('churn_threshold', 180)} days since last purchase
        **Churn Rate:** {churn_model_metrics.get('churn_rate', 'N/A')}

        **Feature Importance (coefficients):**
        """)
        features = churn_model_metrics.get("feature_names", [])
        coeffs = churn_model_metrics.get("coefficients", {})
        for feat in features:
            coef = coeffs.get(feat, 0)
            direction = "⬆️" if coef > 0 else "⬇️"
            st.markdown(f"- {direction} **{feat}**: {coef:.4f} "
                       f"(higher {'increases' if coef > 0 else 'decreases'} churn risk)")

# ================================================================
# TAB 3: CLV × Churn Matrix
# ================================================================
with tab3:
    st.subheader("🔄 CLV vs Churn Risk — Strategic Matrix")

    st.markdown("""
    This quadrant chart places every customer by their **predicted CLV** and **churn probability**.
    Use it to prioritize marketing actions:
    """)

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown("**🟢 High CLV · Low Churn**")
        st.caption("Protect & nurture")
    with col2:
        st.markdown("**🔵 High CLV · High Churn**")
        st.caption("🚨 Critical — retain immediately")
    with col3:
        st.markdown("**🟡 Low CLV · Low Churn**")
        st.caption("Grow & upsell")
    with col4:
        st.markdown("**🔴 Low CLV · High Churn**")
        st.caption("Evaluate — may not be worth saving")

    # Sample for performance
    max_dots = st.slider("Max customers to show", 500, 5000, 2000, step=100,
                         help="More points = slower rendering. Full data used for calculations.")
    plot_sample = combined_df.sample(n=min(max_dots, len(combined_df)), random_state=42)

    # Determine quadrant thresholds
    clv_median = combined_df["Predicted_CLV"].median()
    churn_median = combined_df["Churn_Probability"].median()

    fig_matrix = px.scatter(
        plot_sample,
        x="Predicted_CLV",
        y="Churn_Probability",
        color="Segment",
        size="Frequency",
        hover_data=["CustomerID", "Recency", "Monetary", "Predicted_CLV", "Churn_Probability"],
        color_discrete_sequence=px.colors.qualitative.Bold,
        size_max=20,
        title=f"Strategic Matrix — CLV vs Churn Risk (n={min(max_dots, len(combined_df)):,})",
        labels={
            "Predicted_CLV": "Predicted Customer Lifetime Value (£)",
            "Churn_Probability": "Churn Probability",
        },
    )

    # Add quadrant lines
    fig_matrix.add_hline(y=churn_median, line_dash="dash", line_color="gray", opacity=0.5)
    fig_matrix.add_vline(x=clv_median, line_dash="dash", line_color="gray", opacity=0.5)

    # Add quadrant labels
    fig_matrix.add_annotation(x=clv_median * 1.6, y=churn_median * 0.4,
                               text="🟢 Protect & Nurture", showarrow=False, font=dict(color="green", size=11))
    fig_matrix.add_annotation(x=clv_median * 0.4, y=churn_median * 0.4,
                               text="🟡 Grow & Upsell", showarrow=False, font=dict(color="orange", size=11))
    fig_matrix.add_annotation(x=clv_median * 1.6, y=churn_median * 1.5,
                               text="🔵 Retain Immediately", showarrow=False, font=dict(color="blue", size=11))
    fig_matrix.add_annotation(x=clv_median * 0.4, y=churn_median * 1.5,
                               text="🔴 Evaluate", showarrow=False, font=dict(color="red", size=11))

    fig_matrix.update_layout(
        height=600,
        xaxis_type="log",
        hovermode="closest",
    )
    fig_matrix.update_traces(
        hovertemplate=(
            "<b>CustomerID:</b> %{customdata[0]}<br>"
            "CLV: £%{customdata[3]:,.2f}<br>"
            "Churn: %{customdata[4]:.1%}<br>"
            "Frequency: %{customdata[2]} orders<br>"
            "<b>Segment:</b> %{marker.color}<extra></extra>"
        ),
    )
    st.plotly_chart(fig_matrix, use_container_width=True)

    # Segment counts in each quadrant
    st.subheader("📊 Quadrant Summary")
    quad_data = combined_df.copy()
    quad_data["Quadrant"] = "Unknown"
    quad_data.loc[(quad_data["Predicted_CLV"] >= clv_median) & (quad_data["Churn_Probability"] < churn_median), "Quadrant"] = "🟢 Protect & Nurture"
    quad_data.loc[(quad_data["Predicted_CLV"] >= clv_median) & (quad_data["Churn_Probability"] >= churn_median), "Quadrant"] = "🔵 Retain Immediately"
    quad_data.loc[(quad_data["Predicted_CLV"] < clv_median) & (quad_data["Churn_Probability"] < churn_median), "Quadrant"] = "🟡 Grow & Upsell"
    quad_data.loc[(quad_data["Predicted_CLV"] < clv_median) & (quad_data["Churn_Probability"] >= churn_median), "Quadrant"] = "🔴 Evaluate"

    quad_summary = (
        quad_data.groupby("Quadrant")
        .agg(
            Customers=("CustomerID", "count"),
            Avg_CLV=("Predicted_CLV", "mean"),
            Avg_Churn=("Churn_Probability", "mean"),
            Avg_Spend=("Monetary", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Customers", ascending=False)
    )
    quad_summary["Avg CLV (£)"] = quad_summary["Avg_CLV"].apply(lambda x: f"£{x:,.2f}")
    quad_summary["Avg Churn Risk"] = quad_summary["Avg_Churn"].apply(lambda x: f"{x:.1%}")
    quad_summary["Avg Spend (£)"] = quad_summary["Avg_Spend"].apply(lambda x: f"£{x:,.2f}")

    st.dataframe(
        quad_summary[["Quadrant", "Customers", "Avg CLV (£)", "Avg Churn Risk", "Avg Spend (£)"]],
        use_container_width=True,
        hide_index=True,
    )

# ================================================================
# TAB 4: MoM Performance
# ================================================================
with tab4:
    st.subheader("📈 Month-over-Month Performance")

    if mom_metrics.get("current_month") is None:
        st.warning("Not enough monthly data to compute MoM trends.")
        st.stop()

    # MoM KPI cards
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        delta_str = f"{mom_metrics['revenue_delta']:+.1f}%" if mom_metrics["revenue_delta"] is not None else None
        st.metric(
            f"Revenue ({mom_metrics['current_month']})",
            f"£{mom_metrics['current_revenue']:,.0f}",
            delta=delta_str,
            delta_color="normal",
        )

    with col2:
        delta_str = f"{mom_metrics['orders_delta']:+.1f}%" if mom_metrics["orders_delta"] is not None else None
        st.metric(
            f"Orders ({mom_metrics['current_month']})",
            f"{mom_metrics['current_orders']:,}",
            delta=delta_str,
            delta_color="normal",
        )

    with col3:
        delta_str = f"{mom_metrics['customers_delta']:+.1f}%" if mom_metrics["customers_delta"] is not None else None
        st.metric(
            f"Customers ({mom_metrics['current_month']})",
            f"{mom_metrics['current_customers']:,}",
            delta=delta_str,
            delta_color="normal",
        )

    with col4:
        delta_str = f"{mom_metrics['aov_delta']:+.1f}%" if mom_metrics["aov_delta"] is not None else None
        st.metric(
            f"Avg Order Value ({mom_metrics['current_month']})",
            f"£{mom_metrics['current_aov']:.2f}",
            delta=delta_str,
            delta_color="normal",
        )

    st.caption(f"Comparing {mom_metrics['current_month']} vs {mom_metrics['prev_month']}")

    # Monthly trends chart
    monthly_df = mom_metrics["monthly_data"]

    if len(monthly_df) > 1:
        st.subheader("📊 Historical Monthly Trends")

        metric_choice = st.selectbox(
            "Select metric to chart:",
            options=["Revenue", "Orders", "Customers", "AvgOrderValue"],
            index=0,
        )

        y_label_map = {
            "Revenue": "Revenue (£)",
            "Orders": "Number of Orders",
            "Customers": "Active Customers",
            "AvgOrderValue": "Avg Order Value (£)",
        }

        fig_trend = px.line(
            monthly_df,
            x="Month",
            y=metric_choice,
            markers=True,
            color_discrete_sequence=["#FF4B4B"],
            title=f"{metric_choice} Over Time",
            labels={"Month": "", metric_choice: y_label_map.get(metric_choice, metric_choice)},
        )

        # Add trendline
        if len(monthly_df) >= 3:
            fig_trend.add_trace(
                go.Scatter(
                    x=monthly_df["Month"],
                    y=monthly_df[metric_choice].rolling(3, min_periods=1).mean(),
                    mode="lines",
                    name="3-Month Rolling Avg",
                    line=dict(color="#4B8BFF", width=2, dash="dot"),
                )
            )

        fig_trend.update_layout(
            height=450,
            hovermode="x unified",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        # Format hover based on metric
        if metric_choice in ("Revenue", "AvgOrderValue"):
            fig_trend.update_traces(hovertemplate="%{x}<br>£%{y:,.2f}<extra></extra>")
        else:
            fig_trend.update_traces(hovertemplate="%{x}<br>%{y:,}<extra></extra>")

        st.plotly_chart(fig_trend, use_container_width=True)

        # Full monthly table
        st.subheader("📋 Monthly Performance Table")
        display_monthly = monthly_df.copy()
        display_monthly.columns = ["Month", "Revenue (£)", "Orders", "Customers", "Avg Order Value (£)"]
        display_monthly["Revenue (£)"] = display_monthly["Revenue (£)"].apply(lambda x: f"£{x:,.2f}")
        display_monthly["Avg Order Value (£)"] = display_monthly["Avg Order Value (£)"].apply(lambda x: f"£{x:,.2f}")

        st.dataframe(display_monthly, use_container_width=True, hide_index=True)
