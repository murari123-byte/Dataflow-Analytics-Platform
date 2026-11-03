
-- 1. Monthly sales performance
SELECT
    d.year,
    d.month,
    d.month_name,
    COUNT(f.order_line_id) AS total_order_lines,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.total_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_date d ON f.date_key = d.date_key
GROUP BY d.year, d.month, d.month_name
ORDER BY d.year, d.month;


-- 2. Revenue by product category
SELECT
    p.category,
    COUNT(f.order_line_id) AS total_order_lines,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.total_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p ON f.product_key = p.product_key
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 3. Top 10 customers by revenue
SELECT
    c.customer_id,
    c.customer_name,
    c.city,
    COUNT(f.order_line_id) AS total_order_lines,
    ROUND(SUM(f.total_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_id, c.customer_name, c.city
ORDER BY total_revenue DESC
LIMIT 10;


-- 4. Sales by customer segment
SELECT
    c.customer_segment,
    COUNT(f.order_line_id) AS total_order_lines,
    COUNT(DISTINCT c.customer_id) AS total_customers,
    ROUND(SUM(f.total_amount), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c ON f.customer_key = c.customer_key
GROUP BY c.customer_segment
ORDER BY total_revenue DESC;


-- 5. Order status distribution
SELECT
    order_status,
    COUNT(*) AS total_order_lines,
    ROUND(SUM(total_amount), 2) AS total_amount
FROM fact_sales
GROUP BY order_status
ORDER BY total_order_lines DESC;


-- 6. Overall sales summary
SELECT
    COUNT(*) AS total_order_lines,
    SUM(quantity) AS total_units_sold,
    ROUND(SUM(total_amount), 2) AS total_revenue,
    ROUND(AVG(total_amount), 2) AS average_line_value
FROM fact_sales;


-- 7. Completed sales revenue only
SELECT
    COUNT(*) AS completed_order_lines,
    SUM(quantity) AS completed_units,
    ROUND(SUM(total_amount), 2) AS completed_revenue
FROM fact_sales
WHERE order_status = 'COMPLETED';