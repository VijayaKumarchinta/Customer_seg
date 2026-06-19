"""
PDF Report Generator — Creates professional multi-page PDF reports using ReportLab.
Generates executive summaries, segment breakdowns, KPI tables, and business recommendations.
"""

import io
from datetime import datetime

import pandas as pd
import numpy as np
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm, cm
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
    PageBreak,
    Image,
    KeepTogether,
)


# ---- Colour palette ----
PRIMARY = colors.HexColor("#FF4B4B")
DARK = colors.HexColor("#0F172A")
MEDIUM = colors.HexColor("#475569")
LIGHT = colors.HexColor("#F1F5F9")
WHITE = colors.white
GREEN = colors.HexColor("#166534")
RED = colors.HexColor("#991B1B")
ORANGE = colors.HexColor("#D97706")
TABLE_HEADER_BG = colors.HexColor("#FF4B4B")
TABLE_ALT_ROW = colors.HexColor("#F8FAFC")


def _build_styles():
    """Build and return a dictionary of paragraph styles for the report."""
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        fontSize=26,
        leading=32,
        textColor=PRIMARY,
        spaceAfter=6,
        alignment=TA_CENTER,
    )

    subtitle_style = ParagraphStyle(
        "ReportSubtitle",
        parent=styles["Normal"],
        fontSize=13,
        leading=18,
        textColor=MEDIUM,
        spaceAfter=20,
        alignment=TA_CENTER,
    )

    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontSize=18,
        leading=24,
        textColor=DARK,
        spaceBefore=16,
        spaceAfter=8,
        borderPadding=(0, 0, 4, 0),
    )

    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontSize=13,
        leading=17,
        textColor=PRIMARY,
        spaceBefore=12,
        spaceAfter=6,
    )

    body = ParagraphStyle(
        "Body",
        parent=styles["Normal"],
        fontSize=10,
        leading=14,
        textColor=MEDIUM,
        spaceAfter=6,
    )

    kpi_value = ParagraphStyle(
        "KPIValue",
        parent=styles["Normal"],
        fontSize=20,
        leading=24,
        textColor=DARK,
        alignment=TA_CENTER,
        spaceAfter=2,
    )

    kpi_label = ParagraphStyle(
        "KPILabel",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=MEDIUM,
        alignment=TA_CENTER,
        spaceAfter=8,
    )

    small = ParagraphStyle(
        "Small",
        parent=styles["Normal"],
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#94A3B8"),
        spaceAfter=4,
    )

    return {
        "title": title_style,
        "subtitle": subtitle_style,
        "h1": h1,
        "h2": h2,
        "body": body,
        "kpi_value": kpi_value,
        "kpi_label": kpi_label,
        "small": small,
    }


def _make_kpi_table(kpis: list[tuple[str, str]], styles: dict) -> Table:
    """
    Build a 4-column KPI summary table.

    Parameters
    ----------
    kpis : list of (label, value) tuples, up to 4.
    """
    data = []
    # Row 1: values
    row1 = []
    for label, value in kpis:
        row1.append(Paragraph(str(value), styles["kpi_value"]))
    data.append(row1)

    # Row 2: labels
    row2 = []
    for label, value in kpis:
        row2.append(Paragraph(label, styles["kpi_label"]))
    data.append(row2)

    tbl = Table(data, colWidths=[45 * mm] * len(kpis))
    tbl.setStyle(
        TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("BOX", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
            ("BACKGROUND", (0, 0), (-1, 0), LIGHT),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ])
    )
    return tbl


def _make_data_table(
    df: pd.DataFrame,
    col_widths: list | None = None,
    header_bg: colors.Color = TABLE_HEADER_BG,
) -> Table:
    """
    Convert a pandas DataFrame into a styled ReportLab Table.
    """
    # Header row
    headers = [Paragraph(str(c), ParagraphStyle(
        "TH", fontSize=9, leading=11, textColor=WHITE, fontName="Helvetica-Bold"
    )) for c in df.columns]

    # Data rows
    table_data = [headers]
    for _, row in df.iterrows():
        row_cells = []
        for val in row:
            text = str(val) if not pd.isna(val) else "-"
            row_cells.append(Paragraph(
                text,
                ParagraphStyle("TD", fontSize=8, leading=10, textColor=DARK)
            ))
        table_data.append(row_cells)

    col_count = len(df.columns)
    if col_widths is None:
        col_widths = [170 * mm / max(col_count, 1)] * col_count

    tbl = Table(table_data, colWidths=col_widths, repeatRows=1)

    # Alternating row colours
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#E2E8F0")),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
    ]

    # Alternate row colours
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            cmds.append(("BACKGROUND", (0, i), (-1, i), TABLE_ALT_ROW))

    tbl.setStyle(TableStyle(cmds))
    return tbl


def generate_report(
    customer_df: pd.DataFrame,
    segment_summary: pd.DataFrame,
    clean_df: pd.DataFrame,
    data_info: dict,
    mom_metrics: dict | None = None,
    churn_metrics: dict | None = None,
) -> bytes:
    """
    Generate a professional multi-page PDF report and return it as bytes.

    Parameters
    ----------
    customer_df : pd.DataFrame
        Customer-level data with RFM, segments, churn, CLV.
    segment_summary : pd.DataFrame
        Segment-level aggregated metrics.
    clean_df : pd.DataFrame
        Cleaned transaction data.
    data_info : dict
        Dataset metadata from get_data_info().
    mom_metrics : dict, optional
        Month-over-month metrics.
    churn_metrics : dict, optional
        Churn model metrics for the report.

    Returns
    -------
    bytes
        PDF as bytes ready for download.
    """
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
    )

    sty = _build_styles()
    story = []
    now_str = datetime.now().strftime("%B %d, %Y")
    total_customers = len(customer_df)
    total_revenue = customer_df["Monetary"].sum()
    avg_churn = customer_df["Churn_Probability"].mean() if "Churn_Probability" in customer_df.columns else None

    # ===== TITLE PAGE =====
    story.append(Spacer(1, 40 * mm))
    story.append(Paragraph("Customer Segmentation", sty["title"]))
    story.append(Paragraph("&amp; Analytics Report", sty["title"]))
    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph(
        f"Generated on {now_str} | UCI Online Retail II Dataset",
        sty["subtitle"],
    ))
    story.append(Spacer(1, 10 * mm))

    story.append(_make_kpi_table([
        ("Total Customers", f"{total_customers:,}"),
        ("Total Revenue", f"GBP{total_revenue:,.0f}"),
        (f"Avg Order Value", f"GBP{clean_df['TotalPrice'].mean():.2f}"),
        ("Segments Found", f"{segment_summary['Segment'].nunique()}"),
    ], sty))
    story.append(Spacer(1, 8 * mm))

    meta = data_info
    story.append(Paragraph(
        f"Data source: {meta.get('rows', 0):,} transactions from {meta.get('customers', 0):,} "
        f"customers across {meta.get('countries', 0)} countries. "
        f"Date range: {meta.get('date_range', ('N/A', 'N/A'))[0]} to {meta.get('date_range', ('N/A', 'N/A'))[1]}.",
        sty["small"],
    ))
    story.append(PageBreak())

    # ===== 1. EXECUTIVE SUMMARY =====
    story.append(Paragraph("1. Executive Summary", sty["h1"]))
    story.append(Spacer(1, 3 * mm))

    champions_count = segment_summary[segment_summary["Segment"] == "Champions"]["Customer_Count"].sum()
    at_risk_count = segment_summary[
        segment_summary["Segment"].isin(["At Risk", "At Risk - Champions"])
    ]["Customer_Count"].sum()

    story.append(Paragraph(
        f"This report presents a comprehensive customer segmentation analysis based on the "
        f"RFM (Recency, Frequency, Monetary) framework, supplemented by K-Means clustering "
        f"and predictive churn modeling. The analysis identifies {segment_summary['Segment'].nunique()} "
        f"distinct customer segments with tailored marketing strategies for each.",
        sty["body"],
    ))
    story.append(Spacer(1, 3 * mm))

    # Key findings
    story.append(Paragraph("<b>Key Findings:</b>", sty["body"]))
    findings = [
        f"The customer base of {total_customers:,} generated GBP{total_revenue:,.0f} in total revenue.",
        f"There are {int(champions_count):,} high-value 'Champion' customers who represent the top tier.",
        f"{int(at_risk_count):,} customers are currently at risk of churning and require immediate attention.",
    ]
    if avg_churn is not None:
        findings.append(
            f"The average predicted churn probability across all customers is {avg_churn:.1%}."
        )
    if mom_metrics and mom_metrics.get("revenue_delta") is not None:
        findings.append(
            f"Month-over-month revenue trend: {mom_metrics['revenue_delta']:+.1f}% "
            f"({mom_metrics['current_month']} vs {mom_metrics['prev_month']})."
        )

    for f_text in findings:
        story.append(Paragraph(f"&bull; {f_text}", sty["body"]))
    story.append(PageBreak())

    # ===== 2. SEGMENT OVERVIEW =====
    story.append(Paragraph("2. Segment Overview", sty["h1"]))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph(
        "Each customer is assigned to a behavioral segment based on their RFM scores. "
        "The table below shows the distribution and key metrics for each segment.",
        sty["body"],
    ))
    story.append(Spacer(1, 4 * mm))

    # Segment summary table
    seg_table = segment_summary[[
        "Segment", "Customer_Count", "Avg_Frequency", "Avg_Monetary",
        "Pct_of_Customers", "Pct_of_Revenue"
    ]].copy()
    seg_table.columns = ["Segment", "Customers", "Avg Orders", "Avg Spend (GBP)", "% Cust", "% Rev"]
    seg_table["Avg Orders"] = seg_table["Avg Orders"].round(1)
    seg_table["Avg Spend (GBP)"] = seg_table["Avg Spend (GBP)"].apply(lambda x: f"GBP{x:,.2f}")
    seg_table["% Cust"] = seg_table["% Cust"].apply(lambda x: f"{x}%")
    seg_table["% Rev"] = seg_table["% Rev"].apply(lambda x: f"{x}%")

    tbl = _make_data_table(seg_table)
    story.append(tbl)
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph(
        "<b>Revenue Concentration:</b> The top segments by revenue contribution should be "
        "prioritized for retention and upsell campaigns.",
        sty["body"],
    ))
    story.append(PageBreak())

    # ===== 3. CHURN RISK ANALYSIS =====
    if "Churn_Probability" in customer_df.columns and "Churn_Risk_Level" in customer_df.columns:
        story.append(Paragraph("3. Churn Risk Analysis", sty["h1"]))
        story.append(Spacer(1, 3 * mm))

        risk_summary = (
            customer_df.groupby("Churn_Risk_Level")
            .agg(
                Customers=("CustomerID", "count"),
                Avg_CLV=("Predicted_CLV", "mean") if "Predicted_CLV" in customer_df.columns else ("Monetary", "mean"),
                Avg_Recency=("Recency", "mean"),
            )
            .round(2)
            .reset_index()
        )
        risk_summary["Avg CLV (GBP)"] = risk_summary["Avg_CLV"].apply(lambda x: f"GBP{x:,.2f}")
        risk_summary["Avg Recency (days)"] = risk_summary["Avg_Recency"].round(0).astype(int)
        risk_display = risk_summary[["Churn_Risk_Level", "Customers", "Avg CLV (GBP)", "Avg Recency (days)"]]
        risk_display.columns = ["Risk Level", "Customers", "Avg CLV", "Avg Recency"]

        story.append(Paragraph(
            f"Churn probability was modeled using Logistic Regression on behavioral features. "
            f"Customers with a churn probability below 30% are considered low risk, "
            f"while those above 70% are critical.",
            sty["body"],
        ))
        story.append(Spacer(1, 4 * mm))

        tbl = _make_data_table(risk_display)
        story.append(tbl)
        story.append(PageBreak())

    # ===== 4. BUSINESS RECOMMENDATIONS =====
    story.append(Paragraph("4. Business Recommendations", sty["h1"]))
    story.append(Spacer(1, 3 * mm))

    # Priority score
    if "Priority_Score" in segment_summary.columns:
        story.append(Paragraph("<b>Priority Ranking (where to invest first):</b>", sty["body"]))
        story.append(Spacer(1, 2 * mm))

        priority = segment_summary.sort_values("Priority_Score", ascending=False)[
            ["Segment", "Customer_Count", "Pct_of_Revenue", "Priority_Score"]
        ].head(5)
        priority.columns = ["Segment", "Customers", "% Revenue", "Priority"]
        priority["% Revenue"] = priority["% Revenue"].apply(lambda x: f"{x}%")
        priority["Priority"] = priority["Priority"].round(2)

        tbl = _make_data_table(priority)
        story.append(tbl)
        story.append(Spacer(1, 6 * mm))

    # Campaign planner
    if "Recommendation" in segment_summary.columns:
        story.append(Paragraph("<b>Segment Strategies:</b>", sty["body"]))
        story.append(Spacer(1, 2 * mm))

        recs = segment_summary[["Segment", "Customer_Count", "Avg_Monetary", "Recommendation"]].copy()
        recs.columns = ["Segment", "Customers", "Avg Spend (GBP)", "Recommended Action"]
        recs["Avg Spend (GBP)"] = recs["Avg Spend (GBP)"].apply(lambda x: f"GBP{x:,.2f}")

        tbl = _make_data_table(recs)
        story.append(tbl)

    story.append(PageBreak())

    # ===== 5. MONTHLY PERFORMANCE =====
    if mom_metrics and mom_metrics.get("monthly_data") is not None:
        story.append(Paragraph("5. Monthly Performance Trends", sty["h1"]))
        story.append(Spacer(1, 3 * mm))

        monthly = mom_metrics["monthly_data"]
        if len(monthly) > 0:
            display = monthly.copy()
            display.columns = ["Month", "Revenue (GBP)", "Orders", "Customers", "AOV (GBP)"]
            display["Revenue (GBP)"] = display["Revenue (GBP)"].apply(lambda x: f"GBP{x:,.2f}")
            display["AOV (GBP)"] = display["AOV (GBP)"].apply(lambda x: f"GBP{x:,.2f}")

            tbl = _make_data_table(display)
            story.append(tbl)

        story.append(Spacer(1, 6 * mm))

        if mom_metrics.get("revenue_delta") is not None:
            story.append(Paragraph(
                f"<b>Month-over-Month:</b> Revenue {mom_metrics['revenue_delta']:+.1f}% | "
                f"Orders {mom_metrics['orders_delta']:+.1f}% | "
                f"Customers {mom_metrics['customers_delta']:+.1f}%",
                sty["body"],
            ))

        story.append(PageBreak())

    # ===== 6. DATA NOTES =====
    story.append(Paragraph("6. Data &amp; Methodology Notes", sty["h1"]))
    story.append(Spacer(1, 3 * mm))

    notes = [
        "<b>Data Source:</b> UCI Online Retail II dataset — real transaction records from a UK-based online gift retailer (December 2009 to December 2011).",
        "<b>Cleaning:</b> Removed cancelled transactions (InvoiceNo starting with 'C'), rows without CustomerID, negative quantities/prices, and outliers beyond the 99th percentile.",
        "<b>Segmentation:</b> RFM scores (1-5) calculated using quintile ranking in each dimension. Segments assigned using a rule-based framework of 10 behavioral categories.",
        "<b>Churn Model:</b> Logistic Regression with balanced class weights. Features include RFM metrics, customer tenure, average order value, and purchase regularity.",
        "<b>CLV Model:</b> Linear Regression on non-leaking features. Target is total observed monetary value.",
        "<b>Tools:</b> Python 3.11, scikit-learn, Pandas, Plotly (charts), ReportLab (PDF generation), Streamlit (dashboard).",
    ]
    for note in notes:
        story.append(Paragraph(f"&bull; {note}", sty["body"]))
        story.append(Spacer(1, 2 * mm))

    story.append(Spacer(1, 10 * mm))
    story.append(Paragraph(
        f"Report generated on {now_str} by the Customer Segmentation Dashboard.",
        sty["small"],
    ))

    # ===== BUILD PDF =====
    doc.build(story)
    pdf_bytes = buf.getvalue()
    buf.close()
    return pdf_bytes
