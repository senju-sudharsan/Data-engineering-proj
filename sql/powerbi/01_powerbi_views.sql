-- =============================================================================
-- GOLD LAYER: POWER BI ANALYTICAL VIEWS
-- =============================================================================
-- Schema: gold
-- Purpose: Optimized SQL views specifically structured for Power BI Desktop
--          consumption, Star Schema modeling, and SCD visualization.
-- =============================================================================

-- -----------------------------------------------------------------------------
-- 1. FACT SALES VIEW (STAR SCHEMA CORE)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_powerbi_fact_sales AS
SELECT
    f.sales_key,
    f.order_id,
    f.order_item_id,
    f.customer_key,
    f.product_key,
    f.seller_key,
    f.date_key,
    f.payment_key,
    f.order_status,
    f.purchase_timestamp,
    f.shipping_limit_date,
    f.price AS sales_amount,
    f.freight_value,
    f.total_amount AS total_order_value,
    f.quantity,
    f.estimated_cost,
    f.estimated_profit,
    ROUND(
        CASE
            WHEN f.price > 0 THEN (f.estimated_profit / f.price) * 100
            ELSE 0
        END,
        2
    ) AS estimated_profit_margin_pct
FROM gold.fact_sales f;

-- -----------------------------------------------------------------------------
-- 2. DIMENSION VIEWS
-- -----------------------------------------------------------------------------

-- 2.1 DATE DIMENSION VIEW (With Sort-Order Keys for Power BI)
CREATE OR REPLACE VIEW gold.vw_powerbi_dim_date AS
SELECT
    d.date_key,
    d.full_date,
    d.year,
    d.quarter,
    d.quarter_name,
    d.month,
    d.month_name,
    d.month_short,
    d.day,
    d.day_of_week,
    d.day_name,
    d.is_weekend,
    d.year_month,
    d.year_quarter,
    -- Power BI Sort Keys
    (d.year * 100 + d.month) AS year_month_sort,
    (d.year * 10 + d.quarter) AS year_quarter_sort
FROM gold.dim_date d;

-- 2.2 CUSTOMER DIMENSION VIEW
CREATE OR REPLACE VIEW gold.vw_powerbi_dim_customer AS
SELECT
    c.customer_key,
    c.customer_id,
    c.customer_unique_id,
    c.customer_zip_code_prefix,
    c.customer_city,
    c.customer_state,
    -- Geographic hierarchy label
    c.customer_state || ' - ' || c.customer_city AS customer_state_city
FROM gold.dim_customer c;

-- 2.3 PRODUCT DIMENSION VIEW
CREATE OR REPLACE VIEW gold.vw_powerbi_dim_product AS
SELECT
    p.product_key,
    p.product_id,
    p.product_category_name AS category_portuguese,
    COALESCE(p.product_category_name_english, 'Uncategorized') AS category_name,
    p.product_photos_qty,
    p.product_weight_g,
    ROUND(p.product_weight_g / 1000.0, 2) AS product_weight_kg,
    p.product_length_cm,
    p.product_height_cm,
    p.product_width_cm,
    ROUND((p.product_length_cm * p.product_height_cm * p.product_width_cm) / 1000.0, 2) AS product_volume_liters
FROM gold.dim_product p;

-- 2.4 SELLER DIMENSION VIEW
CREATE OR REPLACE VIEW gold.vw_powerbi_dim_seller AS
SELECT
    s.seller_key,
    s.seller_id,
    s.seller_zip_code_prefix,
    s.seller_city,
    s.seller_state,
    s.seller_state || ' - ' || s.seller_city AS seller_state_city
FROM gold.dim_seller s;

-- 2.5 PAYMENT DIMENSION VIEW
CREATE OR REPLACE VIEW gold.vw_powerbi_dim_payment AS
SELECT
    pay.payment_key,
    INITCAP(REPLACE(pay.payment_type, '_', ' ')) AS payment_method,
    pay.payment_type,
    pay.payment_installments,
    pay.payment_installments_range
FROM gold.dim_payment pay;

-- -----------------------------------------------------------------------------
-- 3. FORECAST PREPARATION VIEW (Continuous Time Series Aggregate)
-- -----------------------------------------------------------------------------
CREATE OR REPLACE VIEW gold.vw_powerbi_forecast_source AS
SELECT
    DATE_TRUNC('month', f.purchase_timestamp)::DATE AS sales_month,
    TO_CHAR(f.purchase_timestamp, 'YYYY-MM') AS year_month,
    COUNT(DISTINCT f.order_id) AS monthly_orders,
    COUNT(*) AS monthly_units_sold,
    SUM(f.price) AS monthly_sales,
    SUM(f.freight_value) AS monthly_freight,
    SUM(f.estimated_profit) AS monthly_estimated_profit,
    ROUND(AVG(f.price), 2) AS monthly_avg_item_price
FROM gold.fact_sales f
GROUP BY DATE_TRUNC('month', f.purchase_timestamp), TO_CHAR(f.purchase_timestamp, 'YYYY-MM')
ORDER BY sales_month ASC;

-- -----------------------------------------------------------------------------
-- 4. SCD TYPE 1 & TYPE 2 ANALYTICAL VIEWS
-- -----------------------------------------------------------------------------

-- 4.1 Detailed Customer SCD Version History View
CREATE OR REPLACE VIEW gold.vw_powerbi_scd_customer_history AS
SELECT
    scd.customer_id,
    scd.version_number,
    scd.customer_city,
    scd.customer_state,
    scd.customer_state || ' - ' || scd.customer_city AS customer_location,
    scd.effective_start_date,
    scd.effective_end_date,
    scd.is_current,
    CASE
        WHEN scd.is_current THEN 'Active (Current)'
        ELSE 'Historical (Expired)'
    END AS version_status,
    CASE
        WHEN scd.effective_end_date IS NOT NULL THEN
            ROUND(EXTRACT(EPOCH FROM (scd.effective_end_date - scd.effective_start_date)) / 86400.0, 1)
        ELSE
            ROUND(EXTRACT(EPOCH FROM (CURRENT_TIMESTAMP - scd.effective_start_date)) / 86400.0, 1)
    END AS days_in_effect
FROM silver.customers_scd scd;

-- 4.2 SCD High-Level Governance Summary View
CREATE OR REPLACE VIEW gold.vw_powerbi_scd_summary AS
SELECT
    COUNT(*) AS total_scd_records,
    COUNT(*) FILTER (WHERE is_current) AS active_records,
    COUNT(*) FILTER (WHERE NOT is_current) AS historical_records,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT customer_id) FILTER (
        WHERE customer_id IN (
            SELECT customer_id
            FROM silver.customers_scd
            GROUP BY customer_id
            HAVING COUNT(*) > 1
        )
    ) AS multi_version_customers,
    MAX(created_at) AS last_scd_update
FROM silver.customers_scd;

-- 4.3 SCD Type 1 vs Type 2 Side-by-Side Analytical View
CREATE OR REPLACE VIEW gold.vw_powerbi_scd_type1_vs_type2 AS
WITH scd1_view AS (
    -- SCD Type 1 representation (overwritten current value only)
    SELECT
        customer_id,
        customer_city AS scd1_current_city,
        customer_state AS scd1_current_state,
        1 AS scd1_retained_versions,
        'No (Overwritten in Place)' AS scd1_history_preserved
    FROM silver.customers
),
scd2_metrics AS (
    -- SCD Type 2 representation (full version history)
    SELECT
        customer_id,
        COUNT(*) AS scd2_total_versions,
        COUNT(*) FILTER (WHERE NOT is_current) AS scd2_historical_versions,
        MAX(version_number) AS scd2_current_version_number,
        'Yes (Audit Trail Intact)' AS scd2_history_preserved
    FROM silver.customers_scd
    GROUP BY customer_id
)
SELECT
    s1.customer_id,
    s1.scd1_current_city,
    s1.scd1_current_state,
    s1.scd1_retained_versions,
    s1.scd1_history_preserved,
    s2.scd2_total_versions,
    s2.scd2_historical_versions,
    s2.scd2_current_version_number,
    s2.scd2_history_preserved
FROM scd1_view s1
JOIN scd2_metrics s2 ON s1.customer_id = s2.customer_id;
