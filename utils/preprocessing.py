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
    df = df.copy()

    initial_count = len(df)

    # Remove rows without CustomerID
    df = df.dropna(subset=["CustomerID"])
    df["CustomerID"] = df["CustomerID"].astype(int).astype(str)

    # Remove cancelled transactions
    df = df[~df["InvoiceNo"].astype(str).str.startswith("C", na=False)]

    # Remove rows with invalid quantities and prices
    df = df[(df["Quantity"] > 0) & (df["UnitPrice"] > 0)]

    # Remove rows without description
    df = df.dropna(subset=["Description"])

    # Remove outliers: Quantity above 99th percentile (bulk orders)
    q99 = df["Quantity"].quantile(0.99)
    df = df[df["Quantity"] <= q99]

    # Remove outliers: UnitPrice above 99th percentile
    p99 = df["UnitPrice"].quantile(0.99)
    df = df[df["UnitPrice"] <= p99]

    # Ensure InvoiceDate is datetime
    df["InvoiceDate"] = pd.to_datetime(df["InvoiceDate"])

    # Create a total spend column
    df["TotalPrice"] = df["Quantity"] * df["UnitPrice"]

    # --- Ensure all ID/object columns are string for pyarrow compatibility ---
    # The ucimlrepo may return InvoiceNo as 'Invoice' with mixed types.
    # PyArrow serialization (used by Streamlit's @st.cache_data) requires consistent types.
    
    # Find and convert any invoice-related column
    invoice_col = None
    for col in df.columns:
        if "invoice" in col.lower():
            invoice_col = col
            break
    if invoice_col:
        df[invoice_col] = df[invoice_col].astype(str)
        # Rename to InvoiceNo if it's named differently (e.g., just 'Invoice')
        if invoice_col != "InvoiceNo":
            df.rename(columns={invoice_col: "InvoiceNo"}, inplace=True)

    # Ensure StockCode is string
    if "StockCode" in df.columns:
        df["StockCode"] = df["StockCode"].astype(str)

    # Ensure Description is string
    if "Description" in df.columns:
        df["Description"] = df["Description"].astype(str)

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
        df.groupby("CustomerID")
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



