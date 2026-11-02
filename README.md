# Customer Retention Analysis

## Project Overview
An end-to-end data analytics project analyzing customer purchasing behavior, retention, churn, and customer segments using SQL, Python, and Power BI.

**Note:** This project uses synthetic data created for portfolio and learning purposes.

## Business Objectives
- Analyze revenue and order performance.
- Measure repeat purchasing behavior.
- Understand customer retention using cohort analysis.
- Identify customers inactive for 90 days.
- Segment customers using Recency, Frequency, and Monetary (RFM) analysis.

## Tools & Technologies
- **SQL / MySQL:** Data querying and business metrics
- **Python:** Pandas, NumPy, Matplotlib
- **Power BI:** KPI cards, trend charts, cohort matrix, and segmentation dashboard
- **Excel / CSV:** Dataset handling

## Dataset
The project includes synthetic customer, order, product, and order-item data covering January 2024 to December 2025.

## Key Findings
- **Total revenue:** 31.12 million
- **Total orders:** 12,302
- **Purchasing customers:** 5,000
- **Average order value:** 2,529.68
- **Repeat customers:** 48.1%
- **90-day churn rate:** 72.47% among customers eligible for the 90-day observation period

## Analysis Performed
1. Data validation and exploratory data analysis
2. Monthly revenue and business KPI analysis
3. Repeat customer analysis
4. Cohort retention analysis
5. 90-day customer churn analysis
6. RFM customer segmentation
7. Interactive Power BI dashboard development

## Repository Structure
- `data/` — Synthetic datasets
- `python/` — Python analysis script and output files
- `sql/` — SQL analysis queries
- `powerbi/` — Power BI dashboard
- `screenshots/` — Dashboard screenshots

## How to Use
1. Download the repository.
2. Import the CSV datasets into MySQL.
3. Run the SQL queries.
4. Run the Python analysis script after installing its required libraries.
5. Open the `.pbix` file in Power BI Desktop.

## Limitations
The data is synthetic and intended to demonstrate analytical methods. Product-level order items are not fully reconciled to order totals, so revenue analysis uses `orders.total_amount`.

## Conclusion
This project demonstrates an end-to-end workflow for analyzing customer behavior and presenting actionable business metrics using SQL, Python, and Power BI.
