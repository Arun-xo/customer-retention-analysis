import pandas as pd
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

customers = pd.read_csv(DATA_DIR / "customers.csv")
orders = pd.read_csv(DATA_DIR / "orders.csv")
order_items = pd.read_csv(DATA_DIR / "order_items.csv")
products = pd.read_csv(DATA_DIR / "products.csv")


print("customers:", customers.shape)
print('orders:', orders.shape)
print('order_items:', order_items.shape)
print('products:', products.shape)

# check null values

print("\n--- missing values : customers---")
print(customers.isnull().sum())

print('\n--- missing values: orders---')
print(orders.isnull().sum())

print("\n--- missing values: order_items---")
print(order_items.isnull().sum())

print("\n--- missing_values: products---")
print(products.isnull().sum())

# Check duplicate rows
print("\n--- DUPLICATE ROWS ---")
print("Customers:", customers.duplicated().sum())
print("Orders:", orders.duplicated().sum())
print("Products:", products.duplicated().sum())
print("Order Items:", order_items.duplicated().sum())

print('\n --- orders data type ---')
print(orders.dtypes)

orders['order_date']= pd.to_datetime(orders['order_date'])

print(orders['order_date'].dtype)

print('first_order:', orders["order_date"].min())
print('last_order:', orders["order_date"].max())


# key business metrics

total_orders = orders['order_id'].nunique()
total_customers = customers['customer_id'].nunique()
total_revenue = orders['total_amount'].sum()
avg_order_value = orders['total_amount'].mean()

print('\n -- Key Business Metrics--')
print('Total_orders:', total_orders)
print('Total_customers:', total_customers)
print('Total_revenue:', round(total_revenue,2))
print('Average_order_value:', round(avg_order_value,2))

# Monthly revenue analysis

orders["order_month"] = orders["order_date"].dt.to_period("M")

monthly_revenue = (
    orders.groupby("order_month")["total_amount"]
    .sum()
    .reset_index()
)

monthly_revenue["order_month"] = (
    monthly_revenue["order_month"].astype(str)
)

print("\n--- MONTHLY REVENUE ---")
print(monthly_revenue.to_string(index=False))
      
      
# Month-over-month revenue growth

monthly_revenue["previous_month_revenue"] = (
    monthly_revenue["total_amount"].shift(1)
)

monthly_revenue["mom_growth_pct"] = (
    (
        monthly_revenue["total_amount"]
        - monthly_revenue["previous_month_revenue"]
    )
    / monthly_revenue["previous_month_revenue"]
) * 100

monthly_revenue["mom_growth_pct"] = (
    monthly_revenue["mom_growth_pct"].round(2)
)

print("\n--- MONTH-OVER-MONTH REVENUE GROWTH ---")
print(monthly_revenue.to_string(index=False))

import matplotlib.pyplot as plt

# Monthly revenue trend chart
plt.figure(figsize=(12, 6))

plt.plot(
    monthly_revenue["order_month"],
    monthly_revenue["total_amount"],
    marker="o"
)

plt.title("Monthly Revenue Trend")
plt.xlabel("Month")
plt.ylabel("Revenue")
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

# Save chart for portfolio
CHART_DIR = PROJECT_DIR / "screenshots"
CHART_DIR.mkdir(exist_ok=True)

plt.savefig(CHART_DIR / "monthly_revenue_trend.png", dpi=300)

#plt.show()

# Customer purchase frequency

customer_orders = (
    orders.groupby("customer_id")["order_id"]
    .nunique()
    .reset_index(name="total_orders")
)

repeat_customers = customer_orders[
    customer_orders["total_orders"] > 1
]

one_time_customers = customer_orders[
    customer_orders["total_orders"] == 1
]

total_customers = len(customer_orders)
repeat_count = len(repeat_customers)
one_time_count = len(one_time_customers)

repeat_rate = repeat_count / total_customers * 100

print("\n--- CUSTOMER RETENTION OVERVIEW ---")
print("Total Customers:", total_customers)
print("Repeat Customers:", repeat_count)
print("One-Time Customers:", one_time_count)
print("Repeat Customer Rate:", round(repeat_rate, 2), "%")

# Step 1: Find each customer's first purchase date
first_purchase = (
    orders.groupby("customer_id")["order_date"]
    .min()
    .reset_index()
)

first_purchase = first_purchase.rename(
    columns={"order_date": "first_purchase_date"}
)

# Step 2: Assign each customer to a cohort month
first_purchase["cohort_month"] = (
    first_purchase["first_purchase_date"]
    .dt.to_period("M")
)

print("\n--- CUSTOMER COHORTS ---")
print(first_purchase.head(10))

# Find the month each customer placed an order
orders["order_month"] = orders["order_date"].dt.to_period("M")

cohort_data = orders.merge(
    first_purchase[["customer_id", "cohort_month"]],
    on="customer_id",
    how="left"
)

print("\n--- COHORT ACTIVITY ---")
print(
    cohort_data[
        ["customer_id", "order_month", "cohort_month"]
    ].head(10)
)


# Calculate months since each customer's first-purchase cohort

cohort_data["cohort_index"] = (
    (cohort_data["order_month"].dt.year
     - cohort_data["cohort_month"].dt.year) * 12
    + (cohort_data["order_month"].dt.month
       - cohort_data["cohort_month"].dt.month)
)

# Count distinct customers in each cohort and activity month
cohort_counts = (
    cohort_data.groupby(
        ["cohort_month", "cohort_index"]
    )["customer_id"]
    .nunique()
    .reset_index(name="customers")
)

# Count customers in each original cohort
cohort_sizes = (
    cohort_counts[cohort_counts["cohort_index"] == 0]
    [["cohort_month", "customers"]]
    .rename(columns={"customers": "cohort_size"})
)

# Calculate retention percentage
cohort_counts = cohort_counts.merge(
    cohort_sizes,
    on="cohort_month",
    how="left"
)

cohort_counts["retention_rate"] = (
    cohort_counts["customers"]
    / cohort_counts["cohort_size"] * 100
).round(2)

print("\n--- COHORT RETENTION RESULTS ---")
print(cohort_counts.head(20).to_string(index=False))


# Customer churn analysis

analysis_date = pd.Timestamp("2025-12-31")
churn_days = 90

# Find each customer's most recent purchase
last_purchase = (
    orders.groupby("customer_id")["order_date"]
    .max()
    .reset_index(name="last_purchase_date")
)

# Find each customer's first purchase
customer_purchase_dates = last_purchase.merge(
    first_purchase[["customer_id", "first_purchase_date"]],
    on="customer_id",
    how="left"
)

# Calculate days since the last purchase
customer_purchase_dates["days_since_purchase"] = (
    analysis_date - customer_purchase_dates["last_purchase_date"]
).dt.days

# Include only customers with at least 90 days of observation
eligible_customers = customer_purchase_dates[
    customer_purchase_dates["first_purchase_date"]
    <= analysis_date - pd.Timedelta(days=churn_days)
].copy()

# Classify customers
eligible_customers["status"] = eligible_customers[
    "days_since_purchase"
].apply(
    lambda days: "Churned" if days >= churn_days else "Active"
)

# Summarize churn
churn_summary = eligible_customers["status"].value_counts()

total_eligible = len(eligible_customers)
churned_count = (eligible_customers["status"] == "Churned").sum()
active_count = (eligible_customers["status"] == "Active").sum()

churn_rate = churned_count / total_eligible * 100

print("\n--- CUSTOMER CHURN ANALYSIS ---")
print("Eligible Customers:", total_eligible)
print("Churned Customers:", churned_count)
print("Active Customers:", active_count)
print("Churn Rate:", round(churn_rate, 2), "%")

# RFM analysis: calculate customer-level metrics

analysis_date = pd.Timestamp("2025-12-31")

rfm = (
    orders.groupby("customer_id")
    .agg(
        last_purchase=("order_date", "max"),
        frequency=("order_id", "nunique"),
        monetary=("total_amount", "sum")
    )
    .reset_index()
)

rfm["recency"] = (
    analysis_date - rfm["last_purchase"]
).dt.days

print("\n--- RFM CUSTOMER METRICS ---")
print(rfm.head(10).to_string(index=False))

# Assign RFM scores from 1 to 5

rfm["R_score"] = pd.qcut(
    rfm["recency"].rank(method="first"),
    5,
    labels=[5, 4, 3, 2, 1]
).astype(int)

rfm["F_score"] = pd.qcut(
    rfm["frequency"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

rfm["M_score"] = pd.qcut(
    rfm["monetary"].rank(method="first"),
    5,
    labels=[1, 2, 3, 4, 5]
).astype(int)

# Combine the three scores
rfm["RFM_score"] = (
    rfm["R_score"]
    + rfm["F_score"]
    + rfm["M_score"]
)

print("\n--- RFM SCORES ---")
print(
    rfm[
        ["customer_id", "recency", "frequency", "monetary",
         "R_score", "F_score", "M_score", "RFM_score"]
    ].head(10).to_string(index=False)
)

# Assign customer segments

def assign_segment(score):
    if score >= 13:
        return "Champions"
    elif score >= 10:
        return "Loyal Customers"
    elif score >= 7:
        return "Potential/Average"
    elif score >= 5:
        return "At Risk"
    else:
        return "Lost"

rfm["segment"] = rfm["RFM_score"].apply(assign_segment)

segment_summary = (
    rfm.groupby("segment", observed=True)
    .agg(
        customers=("customer_id", "nunique"),
        revenue=("monetary", "sum")
    )
    .reset_index()
)

segment_summary["customer_percentage"] = (
    segment_summary["customers"] / len(rfm) * 100
).round(2)

print("\n--- CUSTOMER SEGMENT SUMMARY ---")
print(segment_summary.to_string(index=False))

# Export analysis results for Power BI

OUTPUT_DIR = PROJECT_DIR / "python" / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

monthly_revenue.to_csv(
    OUTPUT_DIR / "monthly_revenue.csv",
    index=False
)

rfm.to_csv(
    OUTPUT_DIR / "customer_rfm.csv",
    index=False
)

segment_summary.to_csv(
    OUTPUT_DIR / "customer_segments.csv",
    index=False
)

cohort_counts.to_csv(
    OUTPUT_DIR / "cohort_retention.csv",
    index=False
)

eligible_customers.to_csv(
    OUTPUT_DIR / "customer_churn.csv",
    index=False
)

print("\nAnalysis CSV files exported to:", OUTPUT_DIR)

# Create KPI summary for Power BI

kpi_summary = pd.DataFrame({
    "Metric": [
        "Total Revenue",
        "Total Orders",
        "Purchasing Customers",
        "Average Order Value"
    ],
    "Value": [
        orders["total_amount"].sum(),
        orders["order_id"].nunique(),
        orders["customer_id"].nunique(),
        orders["total_amount"].mean()
    ]
})

kpi_summary.to_csv(
    OUTPUT_DIR / "kpi_summary.csv",
    index=False
)

print("\n--- KPI SUMMARY ---")
print(kpi_summary.to_string(index=False))