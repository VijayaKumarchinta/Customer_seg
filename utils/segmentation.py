"""
Customer Segmentation — RFM calculation, scoring, and K-Means clustering.
Produces segment labels for each customer.
"""

import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


def calculate_rfm_scores(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate RFM scores (1-5) for each customer using quintile ranking.

    R (Recency):  Lower is better → score 5 = most recent
    F (Frequency): Higher is better → score 5 = most frequent
    M (Monetary):  Higher is better → score 5 = highest spender

    Parameters
    ----------
    customer_df : pd.DataFrame
        Must contain columns: Recency, Frequency, Monetary

    Returns
    -------
    pd.DataFrame
        Original df with added columns: R_Score, F_Score, M_Score, RFM_Score
    """
    df = customer_df.copy()

    # Recency: lower is better, so reverse the quintiles
    # Use rank() first to avoid "Bin edges must be unique" error from qcut
    df["R_Score"] = pd.qcut(
        df["Recency"].rank(method="first"), 5, labels=[5, 4, 3, 2, 1]
    ).astype(int)

    # Frequency: higher is better
    df["F_Score"] = pd.qcut(
        df["Frequency"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Monetary: higher is better
    df["M_Score"] = pd.qcut(
        df["Monetary"].rank(method="first"), 5, labels=[1, 2, 3, 4, 5]
    ).astype(int)

    # Combined RFM score (weighted: R=1, F=1, M=2 for monetary emphasis)
    df["RFM_Score"] = df["R_Score"] + df["F_Score"] + 2 * df["M_Score"]

    return df


def label_segments_rfm(df: pd.DataFrame) -> pd.DataFrame:
    """
    Assign human-readable segment labels based on RFM scores.
    Uses the classic RFM segmentation framework.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: R_Score, F_Score, M_Score

    Returns
    -------
    pd.DataFrame
        Original df with added 'Segment' column.
    """
    df = df.copy()

    conditions = [
        (df["R_Score"] >= 4) & (df["F_Score"] >= 4) & (df["M_Score"] >= 4),  # Champions
        (df["R_Score"] >= 4) & (df["F_Score"] >= 3) & (df["M_Score"] >= 3),  # Loyal
        (df["R_Score"] >= 4) & (df["F_Score"] <= 2) & (df["M_Score"] <= 2),  # New
        (df["R_Score"] >= 3) & (df["F_Score"] >= 3) & (df["M_Score"] >= 3),  # Potential Loyalists
        (df["R_Score"] >= 4) & (df["M_Score"] >= 4) & (df["F_Score"] <= 3),  # Big Spenders
        (df["R_Score"] <= 2) & (df["F_Score"] >= 4) & (df["M_Score"] >= 4),  # At Risk - Champions
        (df["R_Score"] <= 2) & (df["F_Score"] >= 3) & (df["M_Score"] >= 3),  # At Risk
        (df["R_Score"] <= 2) & (df["F_Score"] <= 2) & (df["M_Score"] <= 2),  # Lost
        (df["R_Score"] <= 2) & (df["M_Score"] <= 2),  # Hibernating
        (df["R_Score"] >= 3) & (df["F_Score"] <= 2) & (df["M_Score"] >= 3),  # Need Attention
    ]

    segment_labels = [
        "Champions",
        "Loyal Customers",
        "New Customers",
        "Potential Loyalists",
        "Big Spenders",
        "At Risk - Champions",
        "At Risk",
        "Lost",
        "Hibernating",
        "Need Attention",
    ]

    default_label = "Others"
    df["Segment"] = np.select(conditions, segment_labels, default=default_label)

    return df


def perform_kmeans_clustering(
    df: pd.DataFrame, n_clusters: int = 5
) -> pd.DataFrame:
    """
    Perform K-Means clustering on normalized RFM features.
    This is an alternative/optional segmentation method.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: Recency, Frequency, Monetary
    n_clusters : int
        Number of clusters to create.

    Returns
    -------
    pd.DataFrame
        Original df with added columns: Cluster, Cluster_Segment
    """
    df = df.copy()

    # Select and normalize features
    features = df[["Recency", "Frequency", "Monetary"]].copy()
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    # Perform K-Means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    df["Cluster"] = kmeans.fit_predict(features_scaled)

    # Label clusters based on their characteristics
    cluster_centers = scaler.inverse_transform(kmeans.cluster_centers_)
    cluster_labels = {}

    for i in range(n_clusters):
        r, f, m = cluster_centers[i]
        # Determine label based on relative values
        if m >= cluster_centers[:, 2].mean() and f >= cluster_centers[:, 1].mean():
            cluster_labels[i] = "High Value"
        elif r <= cluster_centers[:, 0].mean() and m > cluster_centers[:, 2].mean():
            cluster_labels[i] = "At Risk - High Value"
        elif r <= cluster_centers[:, 0].mean():
            cluster_labels[i] = "At Risk"
        elif f >= cluster_centers[:, 1].mean():
            cluster_labels[i] = "Frequent but Low Spend"
        else:
            cluster_labels[i] = "Low Engagement"

    df["Cluster_Segment"] = df["Cluster"].map(cluster_labels)

    return df


def find_optimal_k(df: pd.DataFrame, max_k: int = 10) -> dict:
    """
    Find the optimal number of clusters using the Elbow method and Silhouette score.

    Parameters
    ----------
    df : pd.DataFrame
        Customer-level data with Recency, Frequency, Monetary columns.
    max_k : int
        Maximum number of clusters to evaluate.

    Returns
    -------
    dict
        Contains inertia and silhouette scores for each k value.
    """
    from sklearn.preprocessing import StandardScaler

    features = df[["Recency", "Frequency", "Monetary"]].copy()
    scaler = StandardScaler()
    features_scaled = scaler.fit_transform(features)

    results = {"k": [], "inertia": [], "silhouette": []}

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_scaled)

        results["k"].append(k)
        results["inertia"].append(kmeans.inertia_)

        sil = silhouette_score(features_scaled, labels)
        results["silhouette"].append(round(sil, 4))

    return results


def get_segment_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Create a summary table of all segments with key metrics.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns: Segment, Recency, Frequency, Monetary

    Returns
    -------
    pd.DataFrame
        Segment-level summary with metrics and recommendations.
    """
    summary = (
        df.groupby("Segment")
        .agg(
            Customer_Count=("CustomerID", "count"),
            Avg_Recency_Days=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
            Avg_Monetary=("Monetary", "mean"),
            Total_Revenue=("Monetary", "sum"),
            Pct_of_Customers=("CustomerID", lambda x: round(len(x) / len(df) * 100, 1)),
            Pct_of_Revenue=("Monetary", lambda x: round(x.sum() / df["Monetary"].sum() * 100, 1)),
        )
        .round(2)
        .reset_index()
        .sort_values("Customer_Count", ascending=False)
    )

    # Add segment-specific business recommendations
    recommendations = {
        "Champions": "🎖️ Reward with exclusive perks, loyalty programs, and VIP treatment. Ask for referrals.",
        "Loyal Customers": "💎 Upsell premium products. Send personalized offers and early access to sales.",
        "Potential Loyalists": "📈 Nurture with engagement campaigns. Offer cross-sell suggestions.",
        "Big Spenders": "💰 Provide concierge service. Offer bulk discounts and exclusive previews.",
        "New Customers": "🌟 Onboard with welcome series. Offer first-purchase discount to drive repeat buys.",
        "At Risk - Champions": "⚠️ Re-engage immediately! Send a personal note from management with a special offer.",
        "At Risk": "📧 Send win-back email campaign with time-limited discount. Offer loyalty points boost.",
        "Hibernating": "💤 Reactivation campaign: 'We miss you' email with strong incentive (40%+ off).",
        "Need Attention": "🔔 Offer personalized recommendations. Send reminder about abandoned cart items.",
        "Lost": "🔄 Last-resort re-engagement: big discount or survey to understand why they left.",
        "Low Engagement": "📬 Campaign to increase engagement: newsletters, tips, and small incentives.",
        "Others": "📊 Further analyze this group to identify hidden patterns and tailor approach.",
        "High Value": "🏆 Prioritize relationship management. Offer exclusive partnerships.",
        "Frequent but Low Spend": "🛒 Bundle products to increase basket size. Offer free shipping thresholds.",
    }

    summary["Recommendation"] = summary["Segment"].map(recommendations).fillna(
        "📊 Analyze segment behavior to determine best approach."
    )

    return summary
