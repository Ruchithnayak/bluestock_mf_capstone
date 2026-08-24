-- Bluestock Data Analytics Task: Customer, Revenue, and Product Performance Analysis

-- 1. Total Revenue and Order Count by Customer
SELECT 
    c.customer_id,
    c.customer_name,
    COUNT(o.order_id) AS total_orders,
    SUM(o.total_amount) AS total_spent
FROM customers c
JOIN orders o ON c.customer_id = o.customer_id
GROUP BY c.customer_id, c.customer_name
ORDER BY total_spent DESC;

-- 2. Top-Performing Products by Sales Volume and Revenue
SELECT 
    p.product_id,
    p.product_name,
    SUM(oi.quantity) AS total_units_sold,
    SUM(oi.quantity * oi.unit_price) AS gross_revenue
FROM products p
JOIN order_items oi ON p.product_id = oi.product_id
GROUP BY p.product_id, p.product_name
HAVING total_units_sold > 50
ORDER BY gross_revenue DESC;

-- 3. Monthly Sales Trend Analysis (Window Function)
SELECT 
    DATE_TRUNC('month', order_date) AS sales_month,
    SUM(total_amount) AS monthly_revenue,
    AVG(SUM(total_amount)) OVER (
        ORDER BY DATE_TRUNC('month', order_date) 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) AS 3_month_moving_avg
FROM orders
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY sales_month ASC;