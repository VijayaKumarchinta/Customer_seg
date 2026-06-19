"""
Page 2: RFM Analysis
Interactive RFM scatter plots, cohort heatmap, and K-Means clustering explorer.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.title("🔬 RFM Analysis")
st.markdown("### Recency · Frequency · Monetary — the three dimensions of customer value")

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

# ---- RFM Explanation ----
with st.expander("📖 What is RFM Analysis?", expanded=False):
    st.markdown("""
    **RFM** is a data-driven customer segmentation technique that evaluates customers based on three dimensions:

    - **R - Recency**: How recently did the customer purchase? (days since last transaction)
      - *Lower is better* — recent buyers are more likely to buy again.

    - **F - Frequency**: How often do they purchase? (number of transactions)
      - *Higher is better* — frequent buyers are loyal and engaged.

    - **M - Monetary**: How much do they spend? (total spend in £)
      - *Higher is better* — big spenders drive revenue.

    Each customer gets a score (1-5) in each dimension, which is used to assign them to behavioral segments
    like "Champions", "At Risk", or "Lost".
    """)

st.divider()

# ---- Tabbed layout ----
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 RFM Scatter Plot",
    "📊 Segment Profiles",
    "📈 Cohort Analysis",
    "🧮 K-Means Explorer",
])

# ================================================================
# TAB 1: RFM Scatter Plot
# ================================================================
with tab1:
    st.subheader("Interactive RFM Scatter Plot")

    col1, col2 = st.columns([3, 1])

    with col2:
        x_axis = st.selectbox("X-axis", ["Recency", "Frequency", "Monetary"], index=0)
        y_axis = st.selectbox("Y-axis", ["Frequency", "Monetary", "Recency"], index=1)
        size_by = st.selectbox("Bubble size", ["Monetary", "Frequency", "Recency"], index=0)
        max_points = st.slider("Max customers to show", 500, 5000, 1500, step=100,
                               help="Limit points for better performance. Full data is used for filtering.")

    # Sample for performance
    plot_df = customer_df.sample(n=min(max_points, len(customer_df)), random_state=42)

    with col1:
        fig_scatter = px.scatter(
            plot_df,
            x=x_axis,
            y=y_axis,
            size=size_by,
            color="Segment",
            hover_data=["CustomerID", "Recency", "Frequency", "Monetary", "RFM_Score"],
            color_discrete_sequence=px.colors.qualitative.Bold,
            size_max=30,
            title=f"{y_axis} vs {x_axis} (colored by segment)",
        )
        fig_scatter.update_layout(
            height=600,
            hovermode="closest",
            xaxis_title=x_axis,
            yaxis_title=y_axis,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
        )
        fig_scatter.update_traces(
            hovertemplate=(
                "<b>CustomerID:</b> %{customdata[0]}<br>"
                f"<b>{x_axis}:</b> %{{x:,.0f}}<br>"
                f"<b>{y_axis}:</b> %{{y:,.0f}}<br>"
                "<b>Monetary:</b> £%{customdata[3]:,.2f}<br>"
                "<b>RFM Score:</b> %{customdata[4]}<br>"
                "<b>Segment:</b> %{marker.color}<extra></extra>"
            ),
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    # Segment counts in this view
    st.caption(f"Showing {min(max_points, len(customer_df)):,} of {len(customer_df):,} customers — {plot_df['Segment'].nunique()} segments visible")

# ================================================================
# TAB 2: Segment Profiles (Radar/Polar charts)
# ================================================================
with tab2:
    st.subheader("Segment Profile Comparison")

    # Normalize segment averages to 0-1 for radar chart
    seg_profile = (
        customer_df.groupby("Segment")[["R_Score", "F_Score", "M_Score", "RFM_Score"]]
        .mean()
        .reset_index()
    )
    seg_profile.columns = ["Segment", "Recency Score", "Frequency Score", "Monetary Score", "RFM Score"]

    segments_to_compare = st.multiselect(
        "Select segments to compare:",
        options=seg_profile["Segment"].unique().tolist(),
        default=seg_profile["Segment"].unique().tolist()[:4],
    )

    if segments_to_compare:
        filtered = seg_profile[seg_profile["Segment"].isin(segments_to_compare)]

        fig_radar = go.Figure()
        colors = px.colors.qualitative.Bold

        for i, (_, row) in enumerate(filtered.iterrows()):
            fig_radar.add_trace(go.Scatterpolar(
                r=[row["Recency Score"], row["Frequency Score"], row["Monetary Score"], row["RFM Score"]],
                theta=["Recency", "Frequency", "Monetary", "Overall RFM"],
                name=row["Segment"],
                fill="toself",
                line_color=colors[i % len(colors)],
                opacity=0.7,
            ))

        fig_radar.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 5],
                ),
            ),
            height=500,
            title="Segment Profiles — RFM Score Comparison",
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.08,
                xanchor="right",
                x=1,
            ),
        )
        st.plotly_chart(fig_radar, use_container_width=True)
    else:
        st.info("Select at least one segment to display the radar chart.")

    st.caption("Scores range from 1 (lowest) to 5 (highest) in each dimension.")

# ================================================================
# TAB 3: Cohort Analysis
# ================================================================
with tab3:
    st.subheader("📈 Customer Acquisition Cohorts")

    # Create monthly acquisition cohorts
    clean_df_cohort = clean_df.copy()

    # For performance, sample if too many rows
    if len(clean_df_cohort) > 100000:
        clean_df_cohort = clean_df_cohort.sample(n=100000, random_state=42)

    # Get each customer's first purchase month
    first_purchase = (
        clean_df_cohort.groupby("CustomerID")["InvoiceDate"]
        .min()
        .dt.to_period("M")
        .reset_index()
        .rename(columns={"InvoiceDate": "CohortMonth"})
    )

    # Merge cohort month onto transactions
    cohort_data = clean_df_cohort.merge(first_purchase, on="CustomerID", how="left")

    # Calculate period number (0 = first month, 1 = second, etc.)
    cohort_data["InvoiceMonth"] = cohort_data["InvoiceDate"].dt.to_period("M")
    cohort_data["CohortIndex"] = (cohort_data["InvoiceMonth"] - cohort_data["CohortMonth"]).apply(
        lambda x: x.n if hasattr(x, 'n') else 0
    )

    # Filter to reasonable range
    cohort_data = cohort_data[cohort_data["CohortIndex"].between(0, 12)]

    # Cohort retention: count distinct customers
    cohort_counts = (
        cohort_data.groupby(["CohortMonth", "CohortIndex"])["CustomerID"]
        .nunique()
        .reset_index()
    )

    # Pivot to heatmap format
    cohort_pivot = cohort_counts.pivot_table(
        index="CohortMonth",
        columns="CohortIndex",
        values="CustomerID",
        aggfunc="sum",
    )

    # Convert to percentage of first month
    cohort_pct = cohort_pivot.divide(cohort_pivot[0], axis=0) * 100

    # Format period labels
    cohort_pct.index = cohort_pct.index.astype(str)

    fig_cohort = px.imshow(
        cohort_pct.values,
        x=[f"Month {i}" for i in range(cohort_pct.shape[1])],
        y=cohort_pct.index,
        color_continuous_scale="YlOrRd",
        aspect="auto",
        title="Customer Retention by Acquisition Cohort (%)",
        labels=dict(
            x="Period After First Purchase",
            y="Cohort (First Purchase Month)",
            color="Retention %",
        ),
        text_auto=".0f",
        zmin=0,
        zmax=100,
    )

    fig_cohort.update_layout(
        height=600,
        xaxis=dict(side="bottom"),
    )

    fig_cohort.update_traces(
        hovertemplate="<b>%{y}</b><br>Month %{x}<br>Retention: %{z:.1f}%<extra></extra>"
    )

    st.plotly_chart(fig_cohort, use_container_width=True)

    st.caption("Reading: Each row shows a cohort of customers who first purchased that month. "
               "The percentages show how many of them returned in subsequent months. "
               "Values drop over time but stabilize for engaged customers.")

# ================================================================
# TAB 4: K-Means Explorer
# ================================================================
with tab4:
    st.subheader("🧮 K-Means Clustering Explorer")

    from utils.segmentation import perform_kmeans_clustering, find_optimal_k

    k = st.session_state.get("n_clusters", 5)

    # Run K-Means
    kmeans_df = perform_kmeans_clustering(customer_df, n_clusters=k)

    col1, col2 = st.columns(2)

    with col1:
        # Cluster distribution
        cluster_dist = kmeans_df["Cluster_Segment"].value_counts().reset_index()
        cluster_dist.columns = ["Segment", "Count"]

        fig_cluster_bar = px.bar(
            cluster_dist,
            x="Segment",
            y="Count",
            color="Segment",
            color_discrete_sequence=px.colors.qualitative.Set2,
            title=f"K-Means Segment Distribution (K={k})",
            text_auto=True,
        )
        fig_cluster_bar.update_layout(
            height=400,
            showlegend=False,
            xaxis_title=None,
            yaxis_title="Customers",
        )
        fig_cluster_bar.update_traces(
            hovertemplate="<b>%{x}</b><br>Customers: %{y:,}<extra></extra>"
        )
        st.plotly_chart(fig_cluster_bar, use_container_width=True)

    with col2:
        # Elbow method
        st.subheader("Optimal K — Elbow Method")

        with st.spinner("Computing elbow curve..."):
            elbow_data = find_optimal_k(customer_df, max_k=10)

        fig_elbow = go.Figure()

        fig_elbow.add_trace(
            go.Scatter(
                x=elbow_data["k"],
                y=elbow_data["inertia"],
                mode="lines+markers",
                name="Inertia",
                line=dict(color="#FF4B4B", width=3),
                marker=dict(size=8),
                yaxis="y",
            )
        )

        fig_elbow.add_trace(
            go.Scatter(
                x=elbow_data["k"],
                y=elbow_data["silhouette"],
                mode="lines+markers",
                name="Silhouette Score",
                line=dict(color="#4B8BFF", width=3, dash="dash"),
                marker=dict(size=8),
                yaxis="y2",
            )
        )

        fig_elbow.update_layout(
            height=400,
            title="Elbow Method + Silhouette Score",
            xaxis=dict(title="Number of Clusters (K)", dtick=1),
            yaxis=dict(title="Inertia", side="left", color="#FF4B4B"),
            yaxis2=dict(
                title="Silhouette Score",
                side="right",
                overlaying="y",
                color="#4B8BFF",
                range=[0, 1],
            ),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=1.02,
                xanchor="right",
                x=1,
            ),
            hovermode="x unified",
        )
        st.plotly_chart(fig_elbow, use_container_width=True)

        # Best K suggestion
        best_k = elbow_data["k"][np.argmax(elbow_data["silhouette"])]
        st.info(
            f"💡 **Suggested K = {best_k}** "
            f"(highest Silhouette Score: {max(elbow_data['silhouette']):.3f}). "
            f"The elbow point typically suggests K = {elbow_data['k'][np.argmin(np.diff(elbow_data['inertia']))]}. "
            f"Adjust the slider in the sidebar to experiment with different K values."
        )

    # 3D K-Means scatter
    st.subheader("3D Cluster Visualization")
    fig_3d = px.scatter_3d(
        kmeans_df.sample(n=min(2000, len(kmeans_df)), random_state=42),
        x="Recency",
        y="Frequency",
        z="Monetary",
        color="Cluster_Segment",
        color_discrete_sequence=px.colors.qualitative.Set2,
        opacity=0.6,
        size_max=5,
        title="K-Means Clusters in 3D Space (sampled to 2,000 points)",
        labels={
            "Recency": "Recency (days)",
            "Frequency": "Frequency (orders)",
            "Monetary": "Monetary (£)",
        },
    )
    fig_3d.update_layout(
        height=600,
        scene=dict(
            xaxis_title="Recency (days)",
            yaxis_title="Frequency (orders)",
            zaxis_title="Monetary (£)",
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
    )
    fig_3d.update_traces(
        hovertemplate=(
            "<b>Segment:</b> %{marker.color}<br>"
            "Recency: %{x:.0f} days<br>"
            "Frequency: %{y:.0f} orders<br>"
            "Monetary: £%{z:,.2f}<extra></extra>"
        ),
    )
    st.plotly_chart(fig_3d, use_container_width=True)
