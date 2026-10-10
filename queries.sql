SELECT 
    order_id,
    customer_id,
    order_date,
    ship_date,
    (ship_date - order_date) AS delivery_lead_time_days,
    sales,
    profit,
    ROUND((profit / NULLIF(sales, 0)) * 100, 2) AS profit_margin_pct
FROM superstore_orders
LIMIT 15;



WITH regional_subcat_sales AS (
    SELECT 
        region,
        sub_category,
        SUM(sales) AS total_regional_sales
    FROM superstore_orders
    GROUP BY region, sub_category
),
ranked_subcategories AS (
    SELECT 
        region,
        sub_category,
        total_regional_sales,
        RANK() OVER (PARTITION BY region ORDER BY total_regional_sales DESC) AS sales_rank
    FROM regional_subcat_sales
)
SELECT * 
FROM ranked_subcategories
WHERE sales_rank <= 3
ORDER BY region, sales_rank;


SELECT 
    order_date,
    region,
    sales,
    SUM(sales) OVER (
        PARTITION BY region 
        ORDER BY order_date, row_id
    ) AS running_total_sales
FROM superstore_orders
ORDER BY region, order_date;



SELECT 
    order_id,
    sub_category,
    product_name,
    profit,
    ROUND(AVG(profit) OVER (PARTITION BY sub_category), 2) AS avg_subcategory_profit,
    ROUND(profit - AVG(profit) OVER (PARTITION BY sub_category), 2) AS variance_from_avg
FROM superstore_orders
ORDER BY variance_from_avg ASC;
