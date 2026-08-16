# Power BI Desktop Connection & Setup Quickstart

This guide explains how to connect **Power BI Desktop** directly to the PostgreSQL Star Schema and build the analytical reports.

---

## 1. Prerequisites & Database Connection Details

Ensure your PostgreSQL container is running on Docker:
- **Server**: `localhost:5433` (or `127.0.0.1:5433`)
- **Database**: `de_poc`
- **Authentication**: Database (PostgreSQL)
- **User**: `postgres`
- **Password**: `postgres`

> [!TIP]
> If Power BI Desktop prompts for Npgsql .NET connector, select standard PostgreSQL database connector or specify server `localhost:5433`.

---

## 2. Step-by-Step Connection Instructions in Power BI Desktop

### Step 1: Get Data
1. Open **Power BI Desktop**.
2. Click **Get Data** → Select **PostgreSQL database** → Click **Connect**.
3. In the dialog:
   - **Server**: `localhost:5433`
   - **Database**: `de_poc`
   - **Data Connectivity mode**: Select **Import** (Recommended for fast in-memory DAX & forecasting) or **DirectQuery**.
4. Enter credentials:
   - **User name**: `postgres`
   - **Password**: `postgres`

---

### Step 2: Select Views / Tables
In the **Navigator** window, expand the `gold` schema and select the following views (or underlying tables):
- `gold.vw_powerbi_fact_sales` (rename in Power BI to `fact_sales`)
- `gold.vw_powerbi_dim_date` (rename to `dim_date`)
- `gold.vw_powerbi_dim_customer` (rename to `dim_customer`)
- `gold.vw_powerbi_dim_product` (rename to `dim_product`)
- `gold.vw_powerbi_dim_seller` (rename to `dim_seller`)
- `gold.vw_powerbi_dim_payment` (rename to `dim_payment`)
- `gold.vw_powerbi_scd_customer_history` (rename to `scd_customer_history`)
- `gold.vw_powerbi_scd_type1_vs_type2` (rename to `scd_type1_vs_type2`)
- `gold.vw_powerbi_forecast_source` (rename to `forecast_source`)

Click **Load**.

---

### Step 3: Verify Relationships in Model View
Navigate to the **Model View** (left sidebar icon) and verify the 1-to-Many relationships:
1. `dim_date[date_key]` → `fact_sales[date_key]` (1:*)
2. `dim_customer[customer_key]` → `fact_sales[customer_key]` (1:*)
3. `dim_product[product_key]` → `fact_sales[product_key]` (1:*)
4. `dim_seller[seller_key]` → `fact_sales[seller_key]` (1:*)
5. `dim_payment[payment_key]` → `fact_sales[payment_key]` (1:*)

---

### Step 4: Create Hierarchies
1. **Date Hierarchy** (in `dim_date`):
   - Right-click `year` → **Create hierarchy** → Name: `Date Hierarchy`.
   - Right-click `quarter_name` → **Add to hierarchy**.
   - Right-click `month_name` → **Add to hierarchy**.
   - Right-click `day` → **Add to hierarchy**.
2. **Product Hierarchy** (in `dim_product`):
   - Right-click `category_name` → **Create hierarchy** → Name: `Product Hierarchy`.
   - Right-click `product_id` → **Add to hierarchy**.
3. **Geography Hierarchy** (in `dim_seller` or `dim_customer`):
   - Right-click `seller_state` → **Create hierarchy** → Name: `Geography Hierarchy`.
   - Right-click `seller_city` → **Add to hierarchy**.

---

### Step 5: Add DAX Measures
Click **New Measure** on the Home ribbon and paste the measures defined in [`docs/powerbi_analytical_specifications.md`](./powerbi_analytical_specifications.md).

Quick essential snippets:
```dax
Total Sales = SUM(fact_sales[sales_amount])
Total Orders = DISTINCTCOUNT(fact_sales[order_id])
Average Order Value = DIVIDE([Total Sales], [Total Orders], 0)
Units Sold = COUNTROWS(fact_sales)
Total Estimated Profit = SUM(fact_sales[estimated_profit])
Estimated Profit Margin % = DIVIDE([Total Estimated Profit], [Total Sales], 0)
```

---

## 3. Demonstrating SCD Live in Power BI Desktop

1. On the **SCD Comparison Visualizer** page in Power BI, select Customer `00012a2ce6f8dcda20d059ce98491703`.
2. Observe the baseline version in the table (Version 1, `OSASCO`, `SP`).
3. Open a terminal and run the simulation change:
   ```bash
   python scripts/simulate_scd_change.py --city "SALVADOR" --state "BA" --apply-type 2
   ```
4. In Power BI Desktop, click the **Refresh** button on the Home ribbon.
5. Observe the instant live update:
   - Version 1 now shows `Historical (Expired)` with an effective end date.
   - Version 2 appears as `Active (Current)` with `SALVADOR`, `BA`.
6. To reset back to baseline:
   ```bash
   python scripts/simulate_scd_change.py --reset
   ```
   and click **Refresh** in Power BI Desktop.
