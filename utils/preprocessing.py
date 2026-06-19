"""
Data Preprocessing — Cleans the raw Online Retail II dataset.
Handles missing values, cancellations, outliers, and feature engineering.
"""

import pandas as pd
import numpy as np


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw transaction data:
    - Remove rows without CustomerID
    - Remove cancelled transactions (InvoiceNo starting with 'C')
    - Remove rows with negative or zero Quantity
    - Remove rows with negative or zero UnitPrice
    - Remove rows where Description is null

    Parameters
    ----------
    df : pd.DataFrame
        Raw transaction data.

    Returns
    -------
    pd.DataFrame
        Cleaned transaction data.
    """
    initial_count = len(df)
    df = df.copy()

    # ── Build a single composite filter mask (avoids multiple df copies) ──
    # Column names are already normalized by data_loader.py before caching to parquet
    mask = pd.Series(True, index=df.index)

    if "CustomerID" in df.columns:
        mask &= df["CustomerID"].notna()
    else:
        # No CustomerID column at all — return empty with expected columns
        return df.head(0)

    if "InvoiceNo" in df.columns:
        mask &= ~df["InvoiceNo"].astype(str).str.startswith("C", na=False)

    if "Quantity" in df.columns:
        mask &= df["Quantity"] > 0

    if "UnitPrice" in df.columns:
        mask &= df["UnitPrice"] > 0

    if "Description" in df.columns:
        mask &= df["Description"].notna()

    # Apply the composite mask once
    df = df.loc[mask].copy()

    # ── Type conversions ──
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])
    df["InvoiceNo"] = df["InvoiceNo"].astype(str)
    df["StockCode"] = df["StockCode"].astype(str)
    df["Description"] = df["Description"].astype(str)

    # ── Create total spend column ──
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    # ── Remove outliers using quantiles (single-pass quantile computation) ──
    q_qty = df["Quantity"].quantile(0.99)
    p_price = df["UnitPrice"].quantile(0.99)
    df = df[(df["Quantity"] <= q_qty) & (df["UnitPrice"] <= p_price)]

    removed = initial_count - len(df)
    print(f"[CLEAN] Cleaned data: removed {removed:,} rows ({removed/initial_count:.1%})")
    print(f"   Remaining: {len(df):,} transactions")
    print(f"   Unique customers: {df['CustomerID'].nunique():,}")
    print(f"   Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")

    return df


def create_customer_summary(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate transaction data to customer-level summary.
    This is the input for RFM analysis.

    Parameters
    ----------
    df : pd.DataFrame
        Cleaned transaction data.

    Returns
    -------
    pd.DataFrame
        Customer-level summary with columns:
        CustomerID, Monetary, Frequency, Recency, FirstPurchase, LastPurchase
    """
    snapshot_date = df["InvoiceDate"].max() + pd.Timedelta(days=1)

    customer_summary = (
        df.groupby("CustomerID", sort=False)
        .agg(
            Monetary=("TotalPrice", "sum"),
            Frequency=("InvoiceNo", "nunique"),
            Recency=("InvoiceDate", lambda x: (snapshot_date - x.max()).days),
            FirstPurchase=("InvoiceDate", "min"),
            LastPurchase=("InvoiceDate", "max"),
        )
        .reset_index()
    )

    # Monetary in pounds
    customer_summary["Monetary"] = customer_summary["Monetary"].round(2)

    print(f"[SUMMARY] Customer summary created: {len(customer_summary):,} customers")

    return customer_summary



