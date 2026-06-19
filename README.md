<div align="center">

# 📊 Customer Segmentation & Reporting Dashboard

**RFM Analysis · K-Means Clustering · Interactive Visualizations**

[![CI](https://github.com/VijayaKumarchinta/Customer_seg/actions/workflows/ci.yml/badge.svg)](https://github.com/VijayaKumarchinta/Customer_seg/actions/workflows/ci.yml)
[![Streamlit](https://img.shields.io/badge/Built%20with-Streamline-red?logo=streamlit&logoColor=white)](https://streamlit.io)
[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Dataset](https://img.shields.io/badge/Dataset-UCI%20Online%20Retail%20II-orange)](https://archive.ics.uci.edu/dataset/502/online+retail+ii)

**Analyze 1M+ real transactions from a UK-based online retailer. Segment customers by behavioral patterns using RFM analysis and K-Means clustering, and get data-driven marketing recommendations — all in an interactive dashboard.**

[🚀 Live Demo](https://your-app.streamlit.app) · [📖 Dataset Details](https://archive.ics.uci.edu/dataset/502/online+retail+ii) · [🐛 Report Bug](https://github.com/your-username/customer-segmentation-dashboard/issues)

</div>

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Dataset](#-dataset)
- [Getting Started](#-getting-started)
- [Usage Guide](#-usage-guide)
- [Project Structure](#-project-structure)
- [Methodology](#-methodology)
- [Deployment](#-deployment)
- [Screenshots](#-screenshots)
- [Contributing](#-contributing)
- [License](#-license)
- [Contact](#-contact)

---

## 🎯 Overview

This project is an **end-to-end customer segmentation and analytics dashboard** that processes real transactional data to uncover behavioral customer segments and deliver actionable business insights.

### What It Does

1. **Loads & cleans** the UCI Online Retail II dataset — 1,067,371 real transactions
2. **Calculates RFM scores** (Recency, Frequency, Monetary) for every customer
3. **Assigns behavioral segments** using RFM-based rules — Champions, At Risk, Lost, etc.
4. **Performs K-Means clustering** as an alternative segmentation method
5. **Renders an interactive dashboard** with Plotly charts, cohort analysis, and business recommendations
6. **Exports** segment reports and customer-level data as CSV

### Who It's For

- **Data Analysts** looking to demonstrate RFM + K-Means on real data
- **Data Scientists** wanting a deployable Streamlit portfolio project
- **Marketers** who need actionable customer segment insights
- **Students** learning customer segmentation and data visualization

---

## ✨ Features

### 📊 Segment Overview
- **KPI Cards** — Total customers, average recency, frequency, monetary, and revenue
- **Donut Chart** — Customer distribution across segments
- **Revenue Bar Chart** — Revenue contribution per segment
- **Metric Comparison** — Selectable side-by-side segment metrics
- **Country Filter** — Filter all data by country (UK, Germany, France, etc.)

### 🔬 RFM Analysis
- **Interactive Scatter Plot** — Customizable X, Y, and bubble size axes; 1,500+ customers sampled
- **Radar Profiles** — Compare RFM score profiles across selected segments
- **Cohort Heatmap** — Monthly customer retention visualized as a heatmap
- **K-Means Explorer** — Adjust K (2-8), view cluster distribution, elbow curve, silhouette scores, and 3D scatter

### 🎯 Business Recommendations
- **Priority Scoring** — Segments ranked by revenue contribution, size, and urgency
- **Segment Deep Dive** — Select any segment to see its profile, top products, and recommended strategy
- **Campaign Planner** — Pre-built marketing campaigns per segment with channel, discount, and urgency
- **Executive Summary** — Quick action items for Champions, At Risk, Lost, and New customers
- **CSV Export** — Download full segment reports and customer-level labels

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Language** | [Python 3.11+](https://python.org) | Core programming |
| **Dashboard** | [Streamlit](https://streamlit.io) | Interactive web app framework |
| **Data Processing** | [Pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org) | Data manipulation and analysis |
| **Machine Learning** | [scikit-learn](https://scikit-learn.org) | K-Means clustering, standardization |
| **Visualization** | [Plotly](https://plotly.com/python/) | Interactive charts (scatter, bar, pie, heatmap, 3D, radar) |
| **Dataset Access** | [ucimlrepo](https://pypi.org/project/ucimlrepo/) | UCI repository dataset download |
| **Excel Support** | [openpyxl](https://openpyxl.readthedocs.io) | Excel file parsing |
| **Deployment** | [Streamlit Cloud](https://streamlit.io/cloud) | Free hosting with live URL |

---

## 📦 Dataset

### UCI Online Retail II

This project uses the **Online Retail II** dataset from the [UCI Machine Learning Repository](https://archive.ics.uci.edu/dataset/502/online+retail+ii).

| Property | Value |
|----------|-------|
| **Source** | UK-based online gift retailer |
| **Transactions** | 1,067,371 |
| **Customers** | ~5,000+ |
| **Products** | ~5,000+ |
| **Countries** | ~36 |
| **Date Range** | Dec 2009 – Dec 2011 |
| **Columns** | InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country |
| **License** | CC BY 4.0 (academic/citable) |

The dataset is automatically downloaded on first run via `ucimlrepo` and cached as a Parquet file for faster subsequent loads.

### Data Cleaning

The pipeline handles real-world data quality issues:

- ✅ Removes rows without CustomerID
- ✅ Removes cancelled transactions (InvoiceNo starting with 'C')
- ✅ Removes negative quantities and prices
- ✅ Removes null descriptions
- ✅ Caps outliers at the 99th percentile for Quantity and UnitPrice

---

## 🚀 Getting Started

### Prerequisites

- Python 3.11 or later
- pip (Python package manager)

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/your-username/customer-segmentation-dashboard.git
cd customer-segmentation-dashboard

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv

# On Windows:
venv\Scripts\activate

# On macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the dashboard
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`. On first launch, it will automatically download the dataset (∼30-60 seconds), clean it, compute RFM scores, and generate segments.

### Quick Start with Docker (Optional)

```bash
docker build -t customer-segmentation .
docker run -p 8501:8501 customer-segmentation
```

---

## 🎮 Usage Guide

### Navigation

The dashboard has a sidebar with global filters and a multi-page layout:

```
📊 Home                    → Overview, KPIs, segment quick table
📊 Segment Overview        → Donut chart, revenue bars, metric comparison
🔬 RFM Analysis            → Scatter plots, radar, cohort heatmap, K-Means
🎯 Business Recommendations → Priority scoring, strategy, campaign planner
```

### Sidebar Controls

| Control | Description |
|---------|-------------|
| **Country Filter** | Filter all data to a specific country |
| **K-Means K Slider** | Adjust number of clusters (2-8) for the K-Means explorer |

### Interacting with Charts

- **Hover** over any chart element for detailed tooltips
- **Click** legend items to toggle visibility
- **Drag** to zoom on scatter plots and heatmaps
- **Double-click** to reset zoom

### Exporting Data

Click the **"Download CSV"** buttons on any data table to export:
- Segment summary with metrics and recommendations
- Customer-level RFM scores and segment labels

---

## 📁 Project Structure

```
customer-segmentation-dashboard/
├── app.py                           # Main entry point — page config, data loading, sidebar
├── requirements.txt                 # Python dependencies
├── README.md                        # This file
├── utils/
│   ├── data_loader.py               # Dataset download, caching, metadata
│   ├── preprocessing.py             # Data cleaning and customer aggregation
│   └── segmentation.py              # RFM scoring, K-Means, segment labeling, summary
├── pages/
│   ├── 1_Segment_Overview.py        # Segment distribution, KPIs, revenue analysis
│   ├── 2_RFM_Analysis.py            # RFM scatter, radar, cohort heatmap, K-Means
│   └── 3_Business_Recommendations.py # Strategy, campaigns, export, executive summary
└── data/
    └── online_retail_II.parquet     # Cached dataset (auto-generated on first run)
```

---

## 🧪 Methodology

### RFM Segmentation

**RFM** is a behavior-based segmentation framework that scores every customer on three dimensions:

```
R — Recency:    Days since last purchase  (lower → better  → score 1-5)
F — Frequency:  Number of transactions    (higher → better → score 1-5)
M — Monetary:   Total spend in £          (higher → better → score 1-5)
```

Customers are assigned to segments based on their RFM score patterns:

| Segment | R Score | F Score | M Score | Strategy |
|---------|---------|---------|---------|----------|
| **Champions** | ≥4 | ≥4 | ≥4 | Reward with loyalty perks |
| **Loyal Customers** | ≥4 | ≥3 | ≥3 | Upsell premium products |
| **Potential Loyalists** | ≥3 | ≥3 | ≥3 | Nurture engagement |
| **Big Spenders** | ≥4 | ≤3 | ≥4 | Provide concierge service |
| **New Customers** | ≥4 | ≤2 | ≤2 | Onboard with welcome series |
| **At Risk - Champions** | ≤2 | ≥4 | ≥4 | Urgent re-engagement |
| **At Risk** | ≤2 | ≥3 | ≥3 | Win-back campaign |
| **Hibernating** | ≤2 | — | ≤2 | Reactivation offer |
| **Need Attention** | ≥3 | ≤2 | ≥3 | Personalized recommendations |
| **Lost** | ≤2 | ≤2 | ≤2 | Last-resort re-engagement |

### K-Means Clustering

As an alternative approach, the dashboard applies **K-Means clustering** to normalized RFM features. The optimal K can be determined using:

- **Elbow Method** — Plot of inertia vs. K to find the "bend" point
- **Silhouette Score** — Measure of cluster cohesion and separation (higher = better)

The 3D scatter plot in the K-Means tab visualizes clusters in Recency-Frequency-Monetary space.

### Cohort Retention Analysis

The cohort heatmap tracks customer retention over time by grouping customers by their first purchase month and measuring how many return in subsequent months. This reveals:
- Which acquisition cohorts are most loyal
- When customer drop-off typically occurs
- How retention trends change over time

---

## 🌐 Deployment

### Streamlit Cloud (Free)

1. Push the project to a **public GitHub repository**
2. Go to [streamlit.io/cloud](https://streamlit.io/cloud) and sign in with GitHub
3. Click **"New app"** → select your repository
4. Set:
   - **Branch:** `main`
   - **Main file:** `app.py`
5. Click **"Deploy"**

Your app will be live at `https://your-username-your-repo-name.streamlit.app` within minutes.

### Alternative Hosting

| Platform | Instructions |
|----------|-------------|
| [Hugging Face Spaces](https://huggingface.co/spaces) | Create a Space → Streamlit SDK → `git push` |
| [Railway](https://railway.app) | Connect GitHub repo → add build command: `pip install -r requirements.txt` → start: `streamlit run app.py` |
| [Google Cloud Run](https://cloud.google.com/run) | Containerize with Docker → deploy with `gcloud run deploy` |

---

## 📸 Screenshots

> ⚠️ *Add screenshots here after running the dashboard. Suggested images:*

| View | Description |
|------|-------------|
| `screenshots/home.png` | Home page with KPI cards and segment table |
| `screenshots/segment_overview.png` | Donut chart + revenue bars + metric comparison |
| `screenshots/rfm_scatter.png` | Interactive RFM scatter plot colored by segment |
| `screenshots/cohort_heatmap.png` | Monthly cohort retention heatmap |
| `screenshots/kmeans_3d.png` | 3D K-Means cluster visualization |
| `screenshots/recommendations.png` | Business recommendations with campaign planner |

---

## 🤝 Contributing

Contributions are welcome! Here's how to help:

1. **Fork** the repository
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Commit your changes**: `git commit -m 'Add amazing feature'`
4. **Push to the branch**: `git push origin feature/amazing-feature`
5. **Open a Pull Request**

### Ideas for Improvements

- [ ] Add **Customer Lifetime Value (CLV/LTV)** prediction using linear regression
- [ ] Add **churn probability** scoring with logistic regression
- [ ] Add **month-over-month comparison** with delta indicators on KPIs
- [ ] Add **PDF report generation** (with WeasyPrint or ReportLab)
- [ ] Add **database integration** (PostgreSQL/MySQL) for real-time data
- [ ] Add **user authentication** for multi-user access
- [ ] Add **automated email reports** for segment changes

---

## 📄 License

Distributed under the **MIT License**. See `LICENSE` for more information.

### Dataset Citation

If you use the UCI Online Retail II dataset, please cite:

```
Chen, D. (2015). Online Retail II [Dataset]. UCI Machine Learning Repository.
https://doi.org/10.24432/C5CG6D
```

---

## 📬 Contact

**Your Name** — [your.email@example.com](mailto:your.email@example.com)

**GitHub:** [https://github.com/your-username/customer-segmentation-dashboard](https://github.com/your-username/customer-segmentation-dashboard)

**Project Link:** [https://github.com/your-username/customer-segmentation-dashboard](https://github.com/your-username/customer-segmentation-dashboard)

---

<div align="center">

**⭐ If you found this project useful, give it a star on GitHub! ⭐**

</div>
