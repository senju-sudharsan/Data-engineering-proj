# Power BI Analytical Specifications & Architecture Guide

This document defines the data model, DAX measures, report page layouts, interactive features, and SCD visualization architecture for the **Kanini Data Engineering PoC — Power BI Analytical Suite**.

---

## 1. Power BI Data Model & Star Schema Relationships

Power BI connects directly to the PostgreSQL `gold` schema (via tables `gold.dim_*`, `gold.fact_sales` or views `gold.vw_powerbi_*`).

```
                    ┌─────────────────────────┐
                    │      gold.dim_date      │
                    │   (date_key [PK] INT)   │
                    └────────────┬────────────┘
                                 │ 1
                                 │
                                 │ *
┌─────────────────────────┐      │      ┌─────────────────────────┐
│   gold.dim_customer     │      │      │    gold.dim_product     │
│ (customer_key [PK] BIG) ├──1───┼───1──┤ (product_key [PK] BIG)  │
└─────────────────────────┘      │      └─────────────────────────┘
                                 │
                                 │
                        ┌────────┴────────┐
                        │ gold.fact_sales │
                        │ (sales_key [PK])│
                        └────────┬────────┘
                                 │
                                 │ *
┌─────────────────────────┐      │      ┌─────────────────────────┐
│     gold.dim_seller     ├──1───┼───1──┤    gold.dim_payment     │
│  (seller_key [PK] BIG)  │      │      │  (payment_key [PK] BIG) │
└─────────────────────────┘      │      └─────────────────────────┘
```

### Table Relationships Configuration

| From Table (Fact) | Foreign Key | To Table (Dimension) | Primary Key | Cardinality | Cross Filter Direction |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `fact_sales` | `date_key` | `dim_date` | `date_key` | Many to One (*:1) | Single |
| `fact_sales` | `customer_key` | `dim_customer` | `customer_key` | Many to One (*:1) | Single |
| `fact_sales` | `product_key` | `dim_product` | `product_key` | Many to One (*:1) | Single |
| `fact_sales` | `seller_key` | `dim_seller` | `seller_key` | Many to One (*:1) | Single |
| `fact_sales` | `payment_key` | `dim_payment` | `payment_key` | Many to One (*:1) | Single |

---

## 2. Complete DAX Measure Library

Create a dedicated measure table in Power BI (e.g. `_Measures`) or place measures in `fact_sales`.

### 2.1 Core Sales Measures

```dax
// 1. Total Sales Revenue
Total Sales = 
SUM(fact_sales[price])

// 2. Total Orders (Distinct)
Total Orders = 
DISTINCTCOUNT(fact_sales[order_id])

// 3. Units / Items Sold
Units Sold = 
COUNTROWS(fact_sales)

// 4. Total Freight
Total Freight = 
SUM(fact_sales[freight_value])

// 5. Total Gross Merchandise Value (GMV)
Total GMV = 
[Total Sales] + [Total Freight]

// 6. Average Order Value (AOV)
Average Order Value = 
DIVIDE([Total Sales], [Total Orders], 0)

// 7. Average Items Per Order
Avg Items Per Order = 
DIVIDE([Units Sold], [Total Orders], 0)
```

---

### 2.2 Estimated Profit Measures (Proxy Metric)

> [!NOTE]
> **Proxy Profit Assumption**: The Olist e-commerce dataset records customer sale prices and delivery freight values without supplier procurement cost (COGS).
> To enable robust enterprise profit analytics, **Estimated Profit** is modeled using standard e-commerce margin assumptions:
> - `Estimated Product Cost` = `Price * 70%` (assumes 30% baseline gross product margin)
> - `Estimated Freight Handling Cost` = `Freight Value * 15%`
> - `Estimated Profit` = `(Price * 30%) - (Freight Value * 15%)`
> All visuals and reports clearly label this measure as **Estimated Profit**.

```dax
// 8. Total Estimated Cost
Total Estimated Cost = 
SUM(fact_sales[estimated_cost])

// 9. Total Estimated Profit
Total Estimated Profit = 
SUM(fact_sales[estimated_profit])

// 10. Estimated Profit Margin %
Estimated Profit Margin % = 
DIVIDE([Total Estimated Profit], [Total Sales], 0)

// 11. Estimated Profit per Order
Estimated Profit per Order = 
DIVIDE([Total Estimated Profit], [Total Orders], 0)
```

---

### 2.3 Time Intelligence & Forecasting Measures

```dax
// 12. Sales Previous Month (PM)
Sales PM = 
CALCULATE(
    [Total Sales],
    PREVIOUSMONTH(dim_date[full_date])
)

// 13. Sales Month-over-Month Growth (MoM %)
Sales MoM Growth % = 
DIVIDE([Total Sales] - [Sales PM], [Sales PM], 0)

// 14. Sales Year-over-Year (YoY)
Sales YoY = 
CALCULATE(
    [Total Sales],
    SAMEPERIODLASTYEAR(dim_date[full_date])
)

// 15. Sales YoY Growth %
Sales YoY Growth % = 
DIVIDE([Total Sales] - [Sales YoY], [Sales YoY], 0)
```

---

### 2.4 Alert & Dynamic Indicator Measures

```dax
// 16. Profit Margin Alert Flag (Target >= 25%)
Margin Alert Flag = 
IF([Estimated Profit Margin %] >= 0.25, "Healthy", "Low Margin Warning")

// 17. Margin Alert Color (For conditional formatting)
Margin Alert Color = 
IF([Estimated Profit Margin %] >= 0.25, "#10B981", "#EF4444") // Emerald Green vs Crimson Red

// 18. Sales Target Alert Flag (Monthly Target = R$ 500,000)
Sales Target Variance % = 
DIVIDE([Total Sales] - 500000, 500000, 0)

// 19. Sales Target Alert Color
Sales Alert Color = 
IF([Total Sales] >= 500000, "#10B981", "#F59E0B") // Green if on target, Amber if below
```

---

## 3. Power BI Interactive Requirements & Mapping

| Requirement | Power BI Implementation | Location in Report |
| :--- | :--- | :--- |
| **1. Header** | Branded enterprise banner component with dynamic report title and refresh date | All Pages (Page 1, 2, 3) |
| **2. Hyperlink** | Action button linking to GitHub Repository / Project Documentation | Page 1 Header |
| **3. 5 Charts Total** | Line, Bar, Pie, Area/Treemap, and Map/Column visual suite | Across Pages 1, 2, 3 |
| **4. Line Chart** | Monthly Sales & Estimated Profit Trend over Time | Page 1 & Page 2 |
| **5. Bar Chart** | Top 10 Product Categories by Sales / Estimated Profit | Page 1 & Page 2 |
| **6. Pie / Donut Chart** | Sales Distribution by Payment Type (`dim_payment[payment_method]`) | Page 1 |
| **7. Prompt / Q&A** | Native Power BI Q&A Natural Language visual | Page 3 (Forecast) |
| **8. Slicer** | Category Name / Order Status single & multi-select slicer | Page 1 |
| **9. Synced Slicer** | Date Range / Year Slicer synchronized across Sales & Profit | Page 1 & Page 2 |
| **10. 3 Drill Operations** | 1. Date (`Year -> Quarter -> Month -> Day`)<br>2. Product (`Category -> Product ID`)<br>3. Geography (`State -> City`) | Page 1 (Date, Product)<br>Page 2 (Geography) |
| **11. 2 Alert Mechanisms** | 1. Margin Alert Color indicator on category bar chart<br>2. Dynamic KPI Variance Warning Card | Page 2 (Profit Page) |
| **12. 2 Page Navigations** | 1. Sales → Profit Navigation Button<br>2. Profit → Forecast Navigation Button | Page 1 & Page 2 |

---

## 4. Proposed Power BI Page Architecture

### Page 1 — Sales Overview
- **Header Banner**: Title: *"Kanini Enterprise E-Commerce Analytics — Sales Performance"* + Hyperlink button: *"Project Repository / Data Catalog"*
- **Synced Slicer**: `dim_date[year]` (Synced with Page 2)
- **Category Slicer**: `dim_product[category_name]`
- **KPI Summary Cards**:
  - `[Total Sales]` (e.g. R$ 13.59M)
  - `[Total Orders]` (e.g. 98.7K)
  - `[Average Order Value]` (e.g. R$ 137.76)
  - `[Units Sold]` (e.g. 112.6K)
- **Chart 1 (Line Chart)**: *Monthly Sales Revenue Trend*
  - X-Axis: Date Hierarchy (`Year -> Quarter -> Month -> Day`) *(Drill Operation 1)*
  - Y-Axis: `[Total Sales]`
- **Chart 2 (Bar Chart)**: *Sales Revenue by Product Category (Top 10)*
  - Y-Axis: `dim_product[category_name]` (`Category -> Product ID`) *(Drill Operation 2)*
  - X-Axis: `[Total Sales]`
- **Chart 3 (Pie / Donut Chart)**: *Sales by Payment Method*
  - Legend: `dim_payment[payment_method]`
  - Values: `[Total Sales]`
- **Navigation Button**: *"Navigate to Profit Analysis →"*

---

### Page 2 — Profit Analysis
- **Header Banner**: Title: *"Kanini Enterprise E-Commerce Analytics — Estimated Profitability"*
- **Synced Slicer**: `dim_date[year]` (Synced with Page 1)
- **KPI Summary Cards**:
  - `[Total Estimated Profit]` (e.g. R$ 3.74M)
  - `[Estimated Profit Margin %]` (e.g. 27.51%)
  - `[Total Estimated Cost]` (e.g. R$ 9.85M)
  - **Alert Card (Alert Mechanism 1)**: Visual alert badge displaying `[Margin Alert Flag]` formatted with `[Margin Alert Color]`
- **Chart 4 (Line / Area Chart)**: *Monthly Sales vs Estimated Profit & Cost Trend*
  - X-Axis: `dim_date[year_month]`
  - Y-Axis: `[Total Sales]`, `[Total Estimated Profit]`, `[Total Estimated Cost]`
- **Chart 5 (Bar Chart with Conditional Alert)**: *Estimated Profit by Category* *(Alert Mechanism 2)*
  - Bars conditionally formatted using `[Margin Alert Color]` (Red if margin < 25%, Green if >= 25%)
- **Geographic Visual (Bar / Map Chart)**: *Estimated Profit by Seller State & City*
  - Hierarchy: `dim_seller[seller_state] -> dim_seller[seller_city]` *(Drill Operation 3)*
  - Values: `[Total Estimated Profit]`
- **Navigation Buttons**: *"← Back to Sales"* | *"Navigate to Forecast →"*

---

### Page 3 — Forecast
- **Header Banner**: Title: *"Kanini Enterprise E-Commerce Analytics — Predictive Sales Forecasting"*
- **Forecast Visual (Line Chart with Built-in Power BI Forecast Analytics)**:
  - Source: `dim_date[full_date]` or `vw_powerbi_forecast_source[sales_month]`
  - Values: `[Total Sales]`
  - Analytics Pane: **Forecast enabled** (Forecast length: 6 months, Confidence interval: 95%, Seasonality: 12 points)
- **Secondary Forecast Visual (Column / Area)**: *Historical vs Forecasted Monthly Order Volume*
- **Prompt / Q&A Visual**: Embedded natural language query box allowing users to ask questions like:
  - *"total sales by state in 2018"*
  - *"top 5 products by estimated profit"*
  - *"average order value by payment method"*
- **Navigation Button**: *"← Back to Profit Analysis"*

---

## 5. SCD Type 1 vs Type 2 Visualizer (Technical / Demo Page)

Connects to `gold.vw_powerbi_scd_customer_history` and `gold.vw_powerbi_scd_type1_vs_type2`.

### Visual Components:
1. **Customer Selector Slicer**: `scd[customer_id]` (Default: `00012a2ce6f8dcda20d059ce98491703`)
2. **Comparison Cards**:
   - **SCD Type 1 Strategy**:
     - *Behavior*: "Overwrite Current Record"
     - *Retained History*: "NO (0 historical versions preserved)"
     - *Current City*: `[scd1_current_city]`
   - **SCD Type 2 Strategy**:
     - *Behavior*: "Expire Prior Record & Insert New Version"
     - *Retained History*: "YES (Full audit trail preserved)"
     - *Total Versions*: `[scd2_total_versions]`
3. **SCD Version History Table Visual**:
   - Columns: `version_number`, `customer_city`, `customer_state`, `effective_start_date`, `effective_end_date`, `version_status`, `days_in_effect`
   - Shows chronological progression from baseline version to simulated update versions.
