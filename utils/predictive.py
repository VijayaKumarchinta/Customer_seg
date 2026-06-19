"""
Predictive Analytics — CLV prediction (Linear Regression) and Churn probability (Logistic Regression).
Provides forward-looking customer value and risk scores.
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, roc_auc_score, roc_curve


def engineer_features(customer_df: pd.DataFrame, clean_df: pd.DataFrame) -> pd.DataFrame:
    """
    Engineer additional features for predictive modeling beyond base RFM.

    Parameters
    ----------
    customer_df : pd.DataFrame
        Customer-level data with Recency, Frequency, Monetary, FirstPurchase, LastPurchase.
    clean_df : pd.DataFrame
        Transaction-level data with InvoiceDate, TotalPrice, CustomerID.

    Returns
    -------
    pd.DataFrame
        Customer-level data with added features:
        TenureDays, AvgOrderValue, PurchaseRegularity, RecencyToTenure, MonthRecency
    """
    df = customer_df.copy()

    # Tenure: how long the customer has been active (days between first and last purchase)
    df["TenureDays"] = (df["LastPurchase"] - df["FirstPurchase"]).dt.days
    df["TenureDays"] = df["TenureDays"].clip(lower=1)  # avoid division by zero

    # Average order value
    df["AvgOrderValue"] = (df["Monetary"] / df["Frequency"]).round(2)

    # Purchase regularity: how often they buy (days between purchases)
    df["PurchaseRegularity"] = (df["TenureDays"] / df["Frequency"]).round(1)

    # Recency relative to tenure — high ratio means recently acquired but already dormant
    df["RecencyToTenure"] = (df["Recency"] / (df["TenureDays"] + df["Recency"])).round(3)

    # Month of last purchase (seasonal effects)
    df["LastPurchaseMonth"] = df["LastPurchase"].dt.month

    # Revenue per day of tenure (spend velocity)
    df["DailyValue"] = (df["Monetary"] / df["TenureDays"]).round(4)

    # Remove infinities and NaNs
    df = df.replace([np.inf, -np.inf], np.nan)
    df = df.dropna(subset=["TenureDays", "AvgOrderValue", "PurchaseRegularity", "DailyValue"])

    return df


def compute_clv(
    customer_df: pd.DataFrame,
    clean_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Predict Customer Lifetime Value (CLV) using Linear Regression.

    Uses engineered features (EXCLUDING Monetary derivatives to avoid data leakage)
    to predict the total monetary value a customer is expected to generate.

    IMPORTANT: The feature set deliberately excludes:
      - Monetary itself (would create identity leakage — feature = target)
      - DailyValue (Monetary / TenureDays — mathematical derivative of target)
      - AvgOrderValue (Monetary / Frequency — another derivative of target)

    Parameters
    ----------
    customer_df : pd.DataFrame
        Customer-level data with RFM and time features.
    clean_df : pd.DataFrame
        Transaction data for feature engineering.

    Returns
    -------
    pd.DataFrame
        Original df with added columns:
        Predicted_CLV, CLV_Lower_Bound, CLV_Upper_Bound, is_high_clv,
        plus model_metrics dict (for storing in session state by caller).
    """
    df = engineer_features(customer_df, clean_df)

    # Define features — ONLY non-leaking features (no Monetary or its derivatives)
    feature_cols = [
        "Recency", "Frequency",
        "TenureDays", "PurchaseRegularity",
        "RecencyToTenure", "LastPurchaseMonth",
    ]
    available = [c for c in feature_cols if c in df.columns]
    X = df[available].copy()
    y = df["Monetary"].values  # Target: total observed spend

    # Train/test split for evaluation
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Scale features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train linear regression
    lr = LinearRegression()
    lr.fit(X_train_scaled, y_train)

    # Evaluate
    y_pred_test = lr.predict(X_test_scaled)
    r2 = r2_score(y_test, y_pred_test)
    mae = mean_absolute_error(y_test, y_pred_test)

    print(f"[CLV] Model -- R-squared: {r2:.3f}, MAE: GBP{mae:.2f}")
    print(f"   Features (no leakage): {available}")

    # Predict on ALL customers
    X_all_scaled = scaler.transform(X[available])
    predictions = lr.predict(X_all_scaled)
    predictions = np.maximum(predictions, 0)  # No negative CLV

    # Calculate prediction intervals using residual std
    residuals = y_test - y_pred_test
    residual_std = np.std(residuals)

    # Build model metadata (caller is responsible for storing in session state)
    model_metrics = {
        "r2": round(r2, 3),
        "mae": round(mae, 2),
        "residual_std": round(residual_std, 2),
        "feature_names": available,
        "coefficients": dict(zip(available, [round(c, 4) for c in lr.coef_])),
        "intercept": round(lr.intercept_, 2),
    }

    # Map predictions back to the original customer_df (including filtered-out rows)
    pred_dict = dict(zip(df["CustomerID"], predictions))

    result = customer_df.copy()
    result["Predicted_CLV"] = result["CustomerID"].map(pred_dict).fillna(result["Monetary"])
    result["CLV_Lower_Bound"] = np.maximum(result["Predicted_CLV"] - 1.96 * residual_std, 0)
    result["CLV_Upper_Bound"] = result["Predicted_CLV"] + 1.96 * residual_std
    result["is_high_clv"] = result["Predicted_CLV"] >= result["Predicted_CLV"].median()

    # Attach metadata as an attribute so app.py can store it in session state
    result.attrs["model_metrics"] = model_metrics
    result.attrs["clv_scaler"] = scaler
    result.attrs["clv_model"] = lr

    return result


def compute_churn_probability(
    customer_df: pd.DataFrame,
    clean_df: pd.DataFrame,
    recency_threshold_days: int = 180,
) -> pd.DataFrame:
    """
    Predict churn probability using Logistic Regression.

    A customer is labeled as "churned" if their recency exceeds the threshold.
    The model learns patterns that lead to churn and outputs a probability [0, 1].

    Parameters
    ----------
    customer_df : pd.DataFrame
        Customer-level data with RFM and time features.
    clean_df : pd.DataFrame
        Transaction data for feature engineering.
    recency_threshold_days : int
        Days since last purchase beyond which a customer is considered churned.

    Returns
    -------
    pd.DataFrame
        Original df with added columns:
        Churn_Probability, Churn_Risk_Level, is_churned (label)
    """
    df = engineer_features(customer_df, clean_df)
    original_ids = customer_df["CustomerID"].values

    # Define churned label: recency > threshold
    df["is_churned"] = (df["Recency"] > recency_threshold_days).astype(int)

    churn_rate = df["is_churned"].mean()
    print(f"[CHURN] Churn rate (recency > {recency_threshold_days}d): {churn_rate:.1%}")

    # If class imbalance is extreme, adjust threshold
    if churn_rate < 0.05:
        # Use a lower threshold to get enough churned samples
        alt_threshold = int(df["Recency"].quantile(0.75))
        df["is_churned"] = (df["Recency"] > alt_threshold).astype(int)
        churn_rate = df["is_churned"].mean()
        recency_threshold_days = alt_threshold
        print(f"   Adjusted threshold to {alt_threshold}d (churn rate: {churn_rate:.1%})")

    # Define features
    feature_cols = [
        "Recency", "Frequency", "Monetary",
        "TenureDays", "AvgOrderValue", "PurchaseRegularity",
        "RecencyToTenure", "DailyValue", "LastPurchaseMonth",
    ]
    available = [c for c in feature_cols if c in df.columns]
    X = df[available].copy()
    y = df["is_churned"].values

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # Scale
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # Train logistic regression
    # Handle class imbalance with class_weight
    lr = LogisticRegression(class_weight="balanced", random_state=42, max_iter=1000)
    lr.fit(X_train_scaled, y_train)

    # Evaluate
    y_proba = lr.predict_proba(X_test_scaled)[:, 1]
    auc = roc_auc_score(y_test, y_proba)
    accuracy = lr.score(X_test_scaled, y_test)

    print(f"[CHURN] Model -- AUC: {auc:.3f}, Accuracy: {accuracy:.2%}")
    print(f"   Features: {available}")

    # Predict probabilities for ALL customers
    X_all_scaled = scaler.transform(X[available])
    churn_probs = lr.predict_proba(X_all_scaled)[:, 1]

    # Map back to original customer_df
    prob_dict = dict(zip(df["CustomerID"], churn_probs))

    result = customer_df.copy()
    result["Churn_Probability"] = result["CustomerID"].map(prob_dict).fillna(0.5)

    # Assign risk levels
    conditions = [
        result["Churn_Probability"] < 0.3,
        result["Churn_Probability"] < 0.5,
        result["Churn_Probability"] < 0.7,
        result["Churn_Probability"] >= 0.7,
    ]
    labels = ["Low Risk", "Medium Risk", "High Risk", "Critical"]
    result["Churn_Risk_Level"] = np.select(conditions, labels, default="Unknown")

    result["is_churned_label"] = result["CustomerID"].map(
        dict(zip(df["CustomerID"], df["is_churned"]))
    ).fillna(0).astype(int)

    # Get ROC curve data for dashboard
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    roc_data = pd.DataFrame({"fpr": fpr, "tpr": tpr})

    # Attach model metadata as attributes (caller stores in session state)
    result.attrs["churn_model_metrics"] = {
        "auc": round(auc, 3),
        "accuracy": round(accuracy, 3),
        "churn_threshold": recency_threshold_days,
        "churn_rate": round(churn_rate, 3),
        "feature_names": available,
        "coefficients": dict(zip(available, [round(c, 4) for c in lr.coef_[0]])),
    }
    result.attrs["churn_roc_data"] = roc_data
    result.attrs["churn_scaler"] = scaler
    result.attrs["churn_model"] = lr

    return result


def compute_mom_metrics(clean_df: pd.DataFrame) -> dict:
    """
    Compute month-over-month comparison metrics for KPIs.

    Parameters
    ----------
    clean_df : pd.DataFrame
        Cleaned transaction data with InvoiceDate and TotalPrice.

    Returns
    -------
    dict
        MoM metrics with current/previous values and deltas.
    """
    df = clean_df.copy()
    df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

    # Monthly aggregation
    monthly = (
        df.groupby("Month")
        .agg(
            Revenue=("TotalPrice", "sum"),
            Orders=("InvoiceNo", "nunique"),
            Customers=("CustomerID", "nunique"),
            AvgOrderValue=("TotalPrice", "mean"),
        )
        .reset_index()
        .sort_values("Month")
    )

    # Get last two months
    if len(monthly) < 2:
        return {
            "current_month": None,
            "prev_month": None,
            "revenue_delta": None,
            "orders_delta": None,
            "customers_delta": None,
            "aov_delta": None,
            "monthly_data": monthly,
        }

    current = monthly.iloc[-1]
    previous = monthly.iloc[-2]

    def pct_delta(curr, prev):
        if prev == 0:
            return None
        return round((curr - prev) / prev * 100, 1)

    return {
        "current_month": current["Month"],
        "prev_month": previous["Month"],
        "current_revenue": round(current["Revenue"], 2),
        "prev_revenue": round(previous["Revenue"], 2),
        "revenue_delta": pct_delta(current["Revenue"], previous["Revenue"]),
        "current_orders": int(current["Orders"]),
        "prev_orders": int(previous["Orders"]),
        "orders_delta": pct_delta(current["Orders"], previous["Orders"]),
        "current_customers": int(current["Customers"]),
        "prev_customers": int(previous["Customers"]),
        "customers_delta": pct_delta(current["Customers"], previous["Customers"]),
        "current_aov": round(current["AvgOrderValue"], 2),
        "prev_aov": round(previous["AvgOrderValue"], 2),
        "aov_delta": pct_delta(current["AvgOrderValue"], previous["AvgOrderValue"]),
        "monthly_data": monthly,
    }


def get_top_clv_customers(customer_df: pd.DataFrame, top_n: int = 10) -> pd.DataFrame:
    """
    Get top customers by predicted CLV with their key metrics.
    """
    if "Predicted_CLV" not in customer_df.columns:
        return pd.DataFrame()

    top = (
        customer_df.nlargest(top_n, "Predicted_CLV")[
            ["CustomerID", "Predicted_CLV", "Monetary", "Frequency",
             "Recency", "Segment", "Churn_Probability"]
            if "Churn_Probability" in customer_df.columns
            else ["CustomerID", "Predicted_CLV", "Monetary", "Frequency", "Recency", "Segment"]
        ]
        .reset_index(drop=True)
    )
    top.index = top.index + 1  # Rank starting at 1
    top.index.name = "Rank"
    return top


def get_churn_risk_summary(customer_df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate churn risk levels into a summary table.
    """
    if "Churn_Risk_Level" not in customer_df.columns:
        return pd.DataFrame()

    summary = (
        customer_df.groupby("Churn_Risk_Level")
        .agg(
            Customer_Count=("CustomerID", "count"),
            Avg_CLV=("Predicted_CLV", "mean") if "Predicted_CLV" in customer_df.columns else ("Monetary", "mean"),
            Avg_Recency=("Recency", "mean"),
            Avg_Frequency=("Frequency", "mean"),
        )
        .round(2)
        .reset_index()
        .sort_values("Customer_Count", ascending=False)
    )
    return summary
