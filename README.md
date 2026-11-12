# 📊 Retail Sales Intelligence — End-to-End Data Analysis

<div align="center">

![Python](https://img.shields.io/badge/Python-3.11-blue?logo=python&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-2.2-150458?logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-5.22-3F4F75?logo=plotly&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35-FF4B4B?logo=streamlit&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?logo=mysql&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

**A complete data analysis pipeline — from raw Excel to interactive dashboard.**

[🚀 Live Dashboard](#-live-dashboard) · [📁 Project Structure](#-project-structure) · [🔧 Setup](#-setup) · [📈 Key Findings](#-key-findings)

</div>

---

## 🎯 Project Overview

This project walks through a full data analysis lifecycle on the **AdventureWorks Internet Sales** dataset (2010–2014) — a realistic retail dataset covering bicycle sales across multiple countries, products, and customer segments.

### What this project demonstrates

| Skill | Tool |
|---|---|
| Data ingestion & schema design | Python · SQLAlchemy · MySQL |
| Data cleaning & transformation | Pandas · SQL |
| Exploratory data analysis (EDA) | Pandas · Matplotlib · Seaborn |
| Interactive visualisation | Plotly · Streamlit |
| Business intelligence dashboard | Power BI · Streamlit Cloud |
| End-to-end pipeline automation | Python scripts |

---

## 🚀 Live Dashboard

> **Deployed on Streamlit Cloud — no installation required.**

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://retail-sales-analysis-mvp.streamlit.app/)

---

## 🗂️ Dataset

| Property | Value |
|---|---|
| Source | AdventureWorks (Microsoft) |
| Period | December 2010 – January 2014 |
| Rows | ~60,000 transactions |
| Tables | 7 (facts + 6 dimensions) |
| Key columns | SalesAmount, ProductCategory, Geography, Customer demographics |

**Schema (Star Schema)**

```
fact_InternetSales
    ├── dim_Customer          (demographics, income, commute)
    ├── dim_Product           (name, cost, colour)
    │     ├── dim_ProductSubcategory
    │     └── dim_ProductCategory
    ├── dim_SalesTerritory    (country, region)
    └── dim_Currency
```

---

## 📁 Project Structure

```
retail-sales-analysis/
│
├── Data/
│   ├── salesdata.xlsx            # Raw source data (7 sheets)
│   └── df.csv                    # Cleaned, analysis-ready export
│
├── Scripts/
│   ├── End-to-End.ipynb          # Full EDA notebook (20+ analyses)
│   └── export_to_sql.py          # Loads Excel sheets → MySQL tables
│
├── SQL/
│   ├── queries.sql               # All SQL queries (setup → analysis)
│   └── clean_sales_data_table.sql # Cleaned table SQL dump
│
├── PowerBI/
│   └── sales-retail-dashboard.pbix  # Power BI dashboard file
│
├── app.py                        # Streamlit interactive dashboard
├── requirements.txt
├── .env.example                  # Environment variable template
└── README.md
```

---

## 🔧 Setup

### 1 — Clone the repository

```bash
git clone https://github.com/ahmedrizkgawish/retail-sales-analysis.git
cd retail-sales-analysis
```

### 2 — Install dependencies

```bash
pip install -r requirements.txt
```

### 3 — Configure environment

```bash
cp .env.example .env
# Edit .env and fill in your MySQL credentials
```

### 4 — Seed the database

```bash
# Start MySQL, then create the database:
mysql -u root -p -e "CREATE DATABASE sales_database;"

# Load the Excel sheets into MySQL tables:
python Scripts/export_to_sql.py
```

### 5 — Run the Streamlit dashboard locally

```bash
streamlit run app.py
```

### 6 — Open the Jupyter Notebook

```bash
jupyter notebook Scripts/End-to-End.ipynb
```

---

## 📈 Key Findings

> Figures are drawn from the full 2010–2013 dataset (60,398 transactions, $29.4 M revenue).

### 1. Revenue Performance
- **\$29.4 M total revenue** across 60,398 transactions over 4 years; average order value \$486.
- **Q4 is consistently the strongest quarter** in every year — peak in December, driven by seasonal purchasing cycles.
- **2013 was the highest revenue year**, with YoY growth accelerating from ~18% (2011→2012) to ~38% (2012→2013).

### 2. Product Mix
- **Bikes dominate at 96% of revenue** (\$28.3 M); Accessories and Clothing combined contribute just 4%.
- Within Bikes: **Road Bikes are the top subcategory** (\$14.5 M), followed by Mountain Bikes (\$9.9 M), then Touring Bikes.
- **Mountain Bikes grew 37,249%** in revenue from 2010 to 2013 — the fastest-growing subcategory by relative growth.
- **Accessories carry the highest profit margins** despite low absolute revenue — a key insight for pricing strategy.
- Products with no colour attribute (labelled "Unknown") cluster exclusively in the Accessories category, consistent with the AdventureWorks schema.

### 3. Customer Demographics
- **Age 25–54** generates ~87% of total revenue — the primary target segment for marketing spend.
- **Gender split is nearly equal**: Female \$14.8 M (50.4%) vs Male \$14.5 M (49.6%) — indicating broad product appeal with no strong gender skew.
- **Customers commuting 2–5 miles have the highest average transaction value** — likely correlating with recreational cyclists vs. commuters.
- Married customers account for a slightly higher share of revenue than single customers across all product categories.

### 4. Geographic Performance
- **United States is the largest market** (~\$9.4 M), followed by **Australia** (~\$9.1 M) and **Canada** (~\$1.9 M).
- **Australia punches above its weight**: similar revenue to the US despite being a smaller population — indicates high per-customer spend.
- Pacific and North America regions show the strongest YoY growth trajectory, suggesting expanding market penetration.

### 5. Profitability
- Overall portfolio profit margin: **~41%** (total profit / total revenue).
- Accessories deliver the highest per-unit margins; Bikes deliver the highest absolute profit dollars.
- No negative-margin products detected in the cleaned dataset — StandardCost is always below SalesAmount.

---

## 📊 Power BI Dashboard

![Power BI Dashboard Preview](PowerBI/dashboard_preview.jpg)

The `.pbix` file in `/PowerBI` contains a fully interactive dashboard connected to the cleaned dataset, featuring:

- **Month-wise Sales Bar Chart** — seasonal patterns at a glance
- **Product Category Pie Chart** — Bikes / Clothing / Accessories / Components breakdown
- **Sales Trend Lines** — YoY growth with dynamic time filters
- **Customer Demographics Panel** — gender, income bracket, commute distance cross-filters

> **Don't have Power BI Desktop?** Use the [live Streamlit dashboard](https://retail-sales-analysis-mvp.streamlit.app/) for identical insights in your browser.

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Data Storage | MySQL 8.0 (star schema) |
| Data Processing | Python 3.11 · Pandas · NumPy |
| SQL Analysis | MySQL Workbench |
| Visualisation | Matplotlib · Seaborn · Plotly |
| Dashboard | Streamlit · Power BI |
| Notebook | Jupyter Lab |

---

## 🔮 Future Enhancements

- [ ] **Forecasting** — ARIMA / Prophet model for 2014 revenue predictions
- [ ] **Customer segmentation** — K-Means clustering on demographics + purchase behaviour
- [ ] **Real-time ingestion** — Kafka or Airflow pipeline replacing the manual Excel load
- [ ] **Unit tests** — pytest suite for the cleaning scripts

---

## 👤 Author

**Ahmed Rizk Gawish**

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-0A66C2?logo=linkedin)](https://www.linkedin.com/in/ahmedrizkgawish/)
[![GitHub](https://img.shields.io/badge/GitHub-Profile-181717?logo=github)](https://github.com/Ahmed-Rizk1)

---

## 📄 License

This project is licensed under the **MIT License** — feel free to use it as a portfolio reference.

The underlying dataset (AdventureWorks) is provided by Microsoft under their sample data license.
