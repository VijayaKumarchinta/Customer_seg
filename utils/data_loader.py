"""
Data Loader — Downloads and caches the UCI Online Retail II dataset.
Provides a clean DataFrame ready for preprocessing.
"""

import os
import warnings
from pathlib import Path

import pandas as pd

warnings.filterwarnings("ignore")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
CACHE_PATH = DATA_DIR / "online_retail_II.parquet"


def _download_via_ucimlrepo() -> pd.DataFrame:
    """Download the dataset using the ucimlrepo library."""
    from ucimlrepo import fetch_ucirepo

    print("[DOWNLOAD] Downloading Online Retail II dataset from UCI Repository...")
    online_retail = fetch_ucirepo(id=502)
    df = online_retail.data.original
    return df


def _download_via_direct_xlsx() -> pd.DataFrame:
    """
    Fallback: download the xlsx file from the UCI mirror via its zip.
    This is used if ucimlrepo is not available.
    """
    import io
    import zipfile
    import requests

    url = "https://archive.ics.uci.edu/static/public/502/online+retail+ii.zip"
    zip_path = DATA_DIR / "online_retail_ii.zip"

    print("[DOWNLOAD] Downloading Online Retail II dataset (direct xlsx)...")
    os.makedirs(DATA_DIR, exist_ok=True)

    response = requests.get(url, timeout=120)
    with open(zip_path, "wb") as f:
        f.write(response.content)

    # Extract the xlsx from the zip archive
    with zipfile.ZipFile(zip_path, "r") as z:
        xlsx_files = [f for f in z.namelist() if f.endswith(".xlsx")]
        if not xlsx_files:
            raise FileNotFoundError("No xlsx file found in the downloaded zip.")
        # Read the first xlsx file found
        with z.open(xlsx_files[0]) as xlsx_file:
            df = pd.read_excel(io.BytesIO(xlsx_file.read()), engine="openpyxl")

    # Clean up zip
    if zip_path.exists():
        zip_path.unlink()

    return df


def load_data(force_refresh: bool = False) -> pd.DataFrame:
    """
    Load the Online Retail II dataset.
    Uses a cached Parquet file for speed after the first download.

    Parameters
    ----------
    force_refresh : bool
        If True, re-download even if cache exists.

    Returns
    -------
    pd.DataFrame
        Raw transaction data with columns:
        InvoiceNo, StockCode, Description, Quantity, InvoiceDate,
        UnitPrice, CustomerID, Country
    """
    # Return cached data if available
    if CACHE_PATH.exists() and not force_refresh:
        print("[CACHE] Loading cached dataset...")
        return pd.read_parquet(CACHE_PATH)

    # Download the dataset
    os.makedirs(DATA_DIR, exist_ok=True)

    try:
        df = _download_via_ucimlrepo()
    except Exception as e:
        print(f"[ERROR] ucimlrepo failed ({e}), trying direct download...")
        try:
            df = _download_via_direct_xlsx()
        except Exception as e2:
            raise RuntimeError(
                f"Could not download the dataset. "
                f"Please download manually from:\n"
                f"https://archive.ics.uci.edu/dataset/502/online+retail+ii\n"
                f"and save the xlsx file to {DATA_DIR}\n\n"
                f"Errors: {e}, {e2}"
            )

    # ---- Normalize column names for consistency ----
    # The ucimlrepo may return column names different from what our code expects.
    # E.g., 'Price' instead of 'UnitPrice', 'Customer ID' instead of 'CustomerID',
    # and 'Invoice' instead of 'InvoiceNo'.
    rename_map = {}
    for col in df.columns:
        col_lower = col.lower().strip()
        if col_lower == "invoice" and col != "InvoiceNo":
            rename_map[col] = "InvoiceNo"
        elif col_lower == "price" and col != "UnitPrice":
            rename_map[col] = "UnitPrice"
        elif col_lower in ("customer id", "customerid", "customer_id") and col != "CustomerID":
            rename_map[col] = "CustomerID"
    if rename_map:
        df.rename(columns=rename_map, inplace=True)
        print(f"[INFO] Renamed columns: {rename_map}")

    # ---- Standardize types for pyarrow compatibility ----
    # Convert ALL object-type columns to string. PyArrow can't handle mixed-type
    # object columns (e.g., Description containing both text and integers).
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(str)

    # Cache as Parquet for faster future loads
    print("[CACHE] Caching dataset to Parquet...")
    df.to_parquet(CACHE_PATH, index=False)

    print(f"[OK] Loaded {len(df):,} transactions")
    return df


def get_data_info(df: pd.DataFrame) -> dict:
    """Return basic info about the dataset."""
    return {
        "rows": len(df),
        "columns": list(df.columns),
        "date_range": (
            df["InvoiceDate"].min().strftime("%Y-%m-%d"),
            df["InvoiceDate"].max().strftime("%Y-%m-%d"),
        ),
        "customers": df["CustomerID"].nunique(),
        "countries": df["Country"].nunique(),
        "products": df["StockCode"].nunique(),
        "memory_mb": round(df.memory_usage(deep=True).sum() / 1e6, 2),
    }


if __name__ == "__main__":
    df = load_data()
    info = get_data_info(df)
    for k, v in info.items():
        print(f"  {k}: {v}")
