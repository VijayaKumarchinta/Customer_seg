"""
CI Pipeline Smoke Test — Loads data, runs RFM segmentation, trains ML models.
Run locally:  python ci/pipeline_smoke_test.py
Run in CI:    python ci/pipeline_smoke_test.py
"""

import os
import sys


def main():
    # Ensure we're in the project root and it's on sys.path
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(project_root)
    sys.path.insert(0, project_root)

    from utils.data_loader import load_data
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

    print("1/6 Loading data...")
    raw = load_data()
    print(f"   {len(raw):,} transactions")

    print("2/6 Cleaning data...")
    clean = clean_data(raw)
    print(f"   {len(clean):,} transactions")

    print("3/6 Creating customer summary...")
    customers = create_customer_summary(clean)
    print(f"   {len(customers):,} customers")

    print("4/6 Computing RFM scores and segments...")
    customers = calculate_rfm_scores(customers)
    customers = label_segments_rfm(customers)
    summary = get_segment_summary(customers)
    print(f"   {summary['Segment'].nunique()} segments")

    print("5/6 Training ML models...")
    clv = compute_clv(customers, clean)
    churn = compute_churn_probability(customers, clean)
    clv_r2 = clv.attrs["model_metrics"]["r2"]
    churn_auc = churn.attrs["churn_model_metrics"]["auc"]
    print(f"   CLV R²={clv_r2:.4f}, Churn AUC={churn_auc:.4f}")

    print("6/6 Computing MoM metrics...")
    mom = compute_mom_metrics(clean)
    print(f"   {len(mom['monthly_data'])} months")

    print()
    print("=" * 55)
    print("  [PASS] ALL PIPELINE STEPS PASSED")
    print(f"     Transactions: {len(raw):,} -> Cleaned: {len(clean):,}")
    print(f"     Customers:    {len(customers):,}")
    print(f"     Segments:     {summary['Segment'].nunique()}")
    print(f"     CLV R-squared:       {clv_r2:.4f}")
    print(f"     Churn AUC:    {churn_auc:.4f}")
    print("=" * 55)


if __name__ == "__main__":
    main()
