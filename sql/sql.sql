use customer_retention;
SELECT
    COUNT(*) AS total_rows,
    SUM(customer_id IS NULL) AS missing_customer_id,
    SUM(signup_date IS NULL) AS missing_signup_date,
    SUM(country IS NULL) AS missing_country,
    SUM(channel IS NULL) AS missing_channel
FROM customers;

select count(*) as total_rows,
sum(order_id is null)as missing_order_id,
sum(customer_id is null)as missing_customer_id,
sum(order_date is null)as missing_order_date,
sum(quantity is null)as misiing_quantity,
sum(total_amount is null) as missing_amount
from orders;

select count(*)as occurences, customer_id
from customers 
group by customer_id
having count(*) >1;

select count(*)as occurences,
          order_id
from orders 
group by order_id
having count(*) >1;

select 
     min(total_amount)as min_total_amount,
     max(total_amount)as max_total_amount,
     avg(total_amount)as avg_total_amount
 from orders ;
 
 SELECT
    MIN(quantity) AS minimum_quantity,
    MAX(quantity) AS maximum_quantity,
    AVG(quantity) AS average_quantity
FROM orders;

SELECT
    MIN(order_date) AS first_order,
    MAX(order_date) AS last_order
FROM orders;

SELECT
    COUNT(*) AS total_orders,
    SUM(customer_id IS NULL) AS missing_customer_id,
    SUM(order_date IS NULL) AS missing_order_date,
    SUM(total_amount IS NULL) AS missing_amount,
    SUM(quantity IS NULL) AS missing_quantity,
    SUM(total_amount < 0) AS negative_orders,
    SUM(quantity <= 0) AS invalid_quantity,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT order_id) AS unique_orders
FROM orders;

select 
count(distinct customer_id)as customers,
count(distinct order_id)as orders,
sum(total_amount)as revenue,
avg(total_amount)as avg_order_value
from orders;


select 
customer_id,
count(distinct order_id)as order_count
from orders
group by customer_id
order by 2 desc;

select 
   customer_id,
   count(distinct order_id) order_count,
   case when count(distinct order_id) = 1 then 'One_time' else 'Repeat'
   end as customer_type
   from orders
   group by customer_id;
   
   select 
      customer_type,
      count(*)as customer_count
   from
       (
       select customer_id,
              count(distinct order_id)as order_count,
              case when count(distinct order_id) =1 then 'One_time' else 'Repeat' end as customer_type
		from orders 
        group by customer_id
       )as customer_summary
   group by customer_type;  
   
   
   
   select order_count,
          count(*)as customer_count
   from 
    (       
       select customer_id,
          count(distinct order_id)as order_count
        from orders
         group by customer_id
    )as customer_orders
    group by order_count
    order by order_count;
 
 
 select 
        round(count(distinct order_id)* 1.0 /
		count(distinct customer_id),2)as avg_orders_per_customer
 from orders;       
	
use customer_retention;
SELECT
    MAX(retention_rate) AS max_retention,
    MIN(retention_rate) AS min_retention
FROM
(
    WITH first_purchase AS
    (
        SELECT
            customer_id,
            MIN(order_date) AS first_order_date
        FROM orders
        GROUP BY customer_id
    ),

    customer_activity AS
    (
        SELECT
            o.customer_id,
            DATE_FORMAT(fp.first_order_date, '%Y-%m-01') AS cohort_month,
            TIMESTAMPDIFF(
                MONTH,
                DATE_FORMAT(fp.first_order_date, '%Y-%m-01'),
                DATE_FORMAT(o.order_date, '%Y-%m-01')
            ) AS month_number
        FROM orders o
        JOIN first_purchase fp
            ON o.customer_id = fp.customer_id
    ),

    cohort_counts AS
    (
        SELECT
            cohort_month,
            month_number,
            COUNT(DISTINCT customer_id) AS active_customers
        FROM customer_activity
        GROUP BY cohort_month, month_number
    ),

    cohort_size AS
    (
        SELECT
            cohort_month,
            COUNT(DISTINCT customer_id) AS cohort_customers
        FROM customer_activity
        WHERE month_number = 0
        GROUP BY cohort_month
    )

    SELECT
        cc.cohort_month,
        cc.month_number,
        ROUND(
            cc.active_customers * 100.0 / cs.cohort_customers,
            2
        ) AS retention_rate
    FROM cohort_counts cc
    JOIN cohort_size cs
        ON cc.cohort_month = cs.cohort_month
) AS retention_summary;

#churned customers

select customer_id ,
       max(order_date)as last_order_date,
       case when max(order_date) <= '2025-10-02'
            then 'Churned' else 'Active'
         end as customer_status
   from orders
   group by customer_id;
   
   SELECT
    COUNT(*) AS total_customers,

    SUM(
        CASE
            WHEN last_order_date <= '2025-10-02'
            THEN 1
            ELSE 0
        END
    ) AS churned_customers,

    SUM(
        CASE
            WHEN last_order_date > '2025-10-02'
            THEN 1
            ELSE 0
        END
    ) AS active_customers,

    ROUND(
        SUM(
            CASE
                WHEN last_order_date <= '2025-10-02'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS churn_rate

FROM
(
    SELECT
        customer_id,
        MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
) AS customer_last_order;

WITH customer_purchase_history AS
(
    SELECT
        customer_id,
        MIN(order_date) AS first_order_date,
        MAX(order_date) AS last_order_date
    FROM orders
    GROUP BY customer_id
)

SELECT
    COUNT(*) AS eligible_customers,

    SUM(
        CASE
            WHEN last_order_date <= '2025-10-02'
            THEN 1
            ELSE 0
        END
    ) AS churned_customers,

    SUM(
        CASE
            WHEN last_order_date > '2025-10-02'
            THEN 1
            ELSE 0
        END
    ) AS active_customers,

    ROUND(
        SUM(
            CASE
                WHEN last_order_date <= '2025-10-02'
                THEN 1
                ELSE 0
            END
        ) * 100.0 / COUNT(*),
        2
    ) AS churn_rate

FROM customer_purchase_history
WHERE first_order_date <= '2025-10-02';

#RFM Segmentation
use customer_retention;
WITH rfm_base AS
(
    SELECT
        customer_id,
        DATEDIFF('2025-12-31', MAX(order_date)) AS recency_days,
        COUNT(DISTINCT order_id) AS frequency,
        SUM(total_amount) AS monetary_value
    FROM orders
    GROUP BY customer_id
),

rfm_scores AS
(
    SELECT
        *,
        NTILE(5) OVER (ORDER BY recency_days DESC) AS recency_score,
        NTILE(5) OVER (ORDER BY frequency ASC) AS frequency_score,
        NTILE(5) OVER (ORDER BY monetary_value ASC) AS monetary_score
    FROM rfm_base
),

rfm_final AS
(
    SELECT
        *,
        recency_score + frequency_score + monetary_score AS rfm_score
    FROM rfm_scores
),

segments AS
(
    SELECT
        *,
        CASE
            WHEN rfm_score >= 13 THEN 'Champions'
            WHEN rfm_score >= 10 THEN 'Loyal Customers'
            WHEN rfm_score >= 7 THEN 'Potential / Average'
            WHEN rfm_score >= 5 THEN 'At Risk'
            ELSE 'Lost'
        END AS customer_segment
    FROM rfm_final
)

SELECT
    customer_segment,
    COUNT(*) AS customer_count,
    ROUND(
        COUNT(*) * 100.0 /
        (SELECT COUNT(*) FROM segments),
        2
    ) AS customer_percentage
FROM segments
GROUP BY customer_segment
ORDER BY customer_count DESC;