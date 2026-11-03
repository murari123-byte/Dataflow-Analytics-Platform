
-- 1. Latest pipeline execution summary
SELECT
    run_id,
    run_status,
    source_records,
    valid_records,
    rejected_records,
    inserted_records,
    source_records - valid_records - rejected_records
        AS reconciliation_difference,
    start_time,
    end_time
FROM pipeline_runs
ORDER BY run_id DESC
LIMIT 5;


-- 2. Check duplicate sales order-line IDs
SELECT
    order_line_id,
    COUNT(*) AS duplicate_count
FROM fact_sales
GROUP BY order_line_id
HAVING COUNT(*) > 1;


-- 3. Check invalid sales amounts
SELECT
    COUNT(*) AS invalid_amount_count
FROM fact_sales
WHERE total_amount <> quantity * unit_price;


-- 4. Check missing dimension references
SELECT
    COUNT(*) AS orphaned_sales_count
FROM fact_sales f
LEFT JOIN dim_customer c
    ON f.customer_key = c.customer_key
LEFT JOIN dim_product p
    ON f.product_key = p.product_key
LEFT JOIN dim_date d
    ON f.date_key = d.date_key
WHERE
    c.customer_key IS NULL
    OR p.product_key IS NULL
    OR d.date_key IS NULL;


-- 5. Compare warehouse record counts
SELECT 'Customers' AS table_name, COUNT(*) AS total_records
FROM dim_customer

UNION ALL

SELECT 'Products', COUNT(*)
FROM dim_product

UNION ALL

SELECT 'Dates', COUNT(*)
FROM dim_date

UNION ALL

SELECT 'Sales', COUNT(*)
FROM fact_sales

UNION ALL

SELECT 'Rejected Records', COUNT(*)
FROM rejected_records;


-- 6. Compare rejected record counts against pipeline monitoring
SELECT
    p.run_id,
    p.rejected_records AS reported_rejections,
    COUNT(r.rejection_id) AS stored_rejections
FROM pipeline_runs p
LEFT JOIN rejected_records r
    ON p.run_id = r.run_id
GROUP BY p.run_id, p.rejected_records
ORDER BY p.run_id DESC;
