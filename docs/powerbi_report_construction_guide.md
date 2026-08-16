# Power BI Report Construction & Visual Configuration Guide

This guide provides exact step-by-step instructions for building and configuring all 3 business pages, 1 technical SCD demo page, 5 primary charts, hierarchies, alerts, navigations, and Q&A prompt inside **Power BI Desktop**.

---

## 1. Global Setup: Theme & Format Settings

1. In **Power BI Desktop**, go to ribbon: **View** → **Themes** dropdown → **Browse for themes...**
2. Select [`docs/powerbi_theme.json`](./powerbi_theme.json).
3. Set Canvas size on all pages to **16:9** (1280 x 720 px or 1920 x 1080 px).

---

## 2. Hierarchies Setup (Model / Data Pane)

Create the **3 Drill Hierarchies** in the Data Pane:

### 1. Date Hierarchy (Drill Operation 1)
- In `dim_date`:
  - Right-click `year` → **Create hierarchy** → Name: `Date Hierarchy`
  - Right-click `quarter_name` → **Add to hierarchy** → `Date Hierarchy`
  - Right-click `month_name` → **Add to hierarchy** → `Date Hierarchy`
  - Right-click `day` → **Add to hierarchy** → `Date Hierarchy`

### 2. Product Hierarchy (Drill Operation 2)
- In `dim_product`:
  - Right-click `category_name` → **Create hierarchy** → Name: `Product Hierarchy`
  - Right-click `product_id` → **Add to hierarchy** → `Product Hierarchy`

### 3. Geography Hierarchy (Drill Operation 3)
- In `dim_seller`:
  - Right-click `seller_state` → **Create hierarchy** → Name: `Geography Hierarchy`
  - Right-click `seller_city` → **Add to hierarchy** → `Geography Hierarchy`

---

## 3. Page 1: Sales Performance

Rename Page 1 to **Sales**.

### Visual 1: Header Banner (Requirement 1 & Requirement 2)
- **Shape / Text Box**: Insert a rectangle at the top (`X: 0, Y: 0, Width: 1280, Height: 60`).
  - Background: Dark Slate (`#0F172A`).
  - Text: **"Kanini Enterprise Analytics — Sales Performance"** (White, Bold, 16 pt).
- **Hyperlink Button (Requirement 2)**:
  - Insert → **Buttons** → **Blank** (or Web Link icon) at top-right (`X: 1060, Y: 12, Width: 200, Height: 36`).
  - Button Text: `"GitHub Repository ↗"` (Color: White).
  - Action: Turn **ON** → Type: **Web URL** → Web URL: `https://github.com/senju-sudharsan/POC-kanini`

### Visual 2 & 3: Slicers (Requirement 8 & Requirement 9)
- **Synced Slicer (Requirement 9)**:
  - Visual: **Slicer**
  - Field: `dim_date[year]`
  - Format: Tile or Dropdown.
  - Sync Setting: Go to ribbon **View** → **Sync slicers** → Check **Sales** and **Profit** pages (both *Visible* and *Sync* checked).
- **Category Slicer (Requirement 8)**:
  - Visual: **Slicer**
  - Field: `dim_product[category_name]`
  - Format: Dropdown with Search enabled.

### Visual 4-7: KPI Summary Cards
- **Card 1**: Field = `[Total Sales]` (Display units: Millions, Currency: R$)
- **Card 2**: Field = `[Total Orders]` (Display units: Thousands)
- **Card 3**: Field = `[Average Order Value]` (Display units: Auto, Currency: R$)
- **Card 4**: Field = `[Units Sold]` (Display units: Thousands)

### Primary Chart 1: Monthly Sales Trend (Line Chart - Requirement 4 & 5)
- Visual: **Line chart**
- **X-axis**: Drag `Date Hierarchy` (`year` → `quarter_name` → `month_name` → `day`) → **(Drill Operation 1)**
- **Y-axis**: `[Total Sales]`
- Title: *"Monthly Sales Revenue Trend (Drillable by Year/Quarter/Month)"*
- Data labels: On (optional).

### Primary Chart 2: Top Product Categories (Bar Chart - Requirement 5)
- Visual: **Clustered Bar chart** (Horizontal)
- **Y-axis**: Drag `Product Hierarchy` (`category_name` → `product_id`) → **(Drill Operation 2)**
- **X-axis**: `[Total Sales]`
- Filters on this visual: `category_name` is Top 10 by `[Total Sales]`.
- Title: *"Top 10 Product Categories by Sales (Drill to Product Level)"*

### Primary Chart 3: Sales by Payment Method (Pie Chart - Requirement 5)
- Visual: **Pie chart** (or Donut chart)
- **Legend**: `dim_payment[payment_method]`
- **Values**: `[Total Sales]`
- Title: *"Sales Distribution by Payment Method"*

### Navigation Button (Requirement 12 - Nav 1)
- Insert → **Buttons** → **Navigator** (or Blank Button).
- Text: `"Go to Profit Analysis →"`
- Action: **ON** → Type: **Page navigation** → Destination: **Profit**.

---

## 4. Page 2: Profit Analysis

Create a new page and name it **Profit**.

### Visual 1: Header Banner (Requirement 1)
- Rectangle Header: **"Kanini Enterprise Analytics — Estimated Profitability"**

### Visual 2: Synced Slicer (Requirement 9)
- Synced `dim_date[year]` slicer (auto-synchronized with Page 1).

### Visual 3-5: Profit KPI Summary Cards & Alert Badge (Requirement 11 - Alert 1)
- **Card 1**: `[Total Estimated Profit]` (e.g. R$ 3.74M)
- **Card 2**: `[Estimated Profit Margin %]` (e.g. 27.51%)
- **Card 3**: `[Total Estimated Cost]` (e.g. R$ 9.85M)
- **Alert Badge Card (Alert Mechanism 1)**:
  - Visual: **Card**
  - Field: `[Margin Alert Flag]`
  - Format: Callout value text color → Conditional Formatting (`fx`) → **Format style**: Field value → Based on field: `[Margin Alert Color]` (Green `#10B981` if >= 25%, Red `#EF4444` if < 25%).

### Primary Chart 4: Sales vs Estimated Profit Trend (Line / Area - Requirement 5)
- Visual: **Line and Clustered Column chart** (or Line chart with 2 series)
- **X-axis**: `dim_date[year_month]`
- **Column values**: `[Total Sales]`
- **Line values**: `[Total Estimated Profit]`
- Title: *"Monthly Sales Revenue vs Estimated Profit Trend"*

### Primary Chart 5: Category Profitability with Alert Formatting (Bar Chart - Requirement 5 & 11 - Alert 2)
- Visual: **Clustered Bar chart**
- **Y-axis**: `dim_product[category_name]`
- **X-axis**: `[Total Estimated Profit]`
- **Bars Color Conditional Formatting (Alert Mechanism 2)**:
  - Go to **Format visual** → **Bars** → **Colors** → Click `fx` (Conditional formatting button).
  - Format style: **Field value** → What field should we base this on? → Select `[Margin Alert Color]`.
  - Result: Categories with margins under 25% are automatically highlighted in **Red**, while healthy categories show in **Green**.
- Title: *"Estimated Profit by Category (Alert: Red indicates Margin < 25%)"*

### Secondary Geo Visual: Profit by Seller Geography (Drill Operation 3)
- Visual: **Clustered Column chart** (or Azure Map)
- **X-axis**: Drag `Geography Hierarchy` (`seller_state` → `seller_city`) → **(Drill Operation 3)**
- **Y-axis**: `[Total Estimated Profit]`
- Title: *"Estimated Profit by Seller State & City (Drillable)"*

### Navigation Buttons (Requirement 12 - Nav 2)
- **Button 1**: Text: `"← Back to Sales"` → Action: Page navigation → Destination: **Sales**.
- **Button 2**: Text: `"Go to Forecast →"` → Action: Page navigation → Destination: **Forecast**.

---

## 5. Page 3: Predictive Forecasting & Q&A

Create a new page and name it **Forecast**.

### Visual 1: Header Banner (Requirement 1)
- Rectangle Header: **"Kanini Enterprise Analytics — Predictive Sales Forecasting"**

### Visual 2: Forecast Line Chart
- Visual: **Line chart**
- **X-axis**: `dim_date[full_date]` (continuous date) or `vw_powerbi_forecast_source[sales_month]`
- **Y-axis**: `[Total Sales]`
- **Enable Built-in Power BI Forecasting**:
  1. Select the Line chart visual.
  2. In the visual settings pane on the right, click the **Analytics** icon (magnifying glass with trendline).
  3. Expand **Forecast** → Click **+ Add**.
  4. Settings:
     - **Forecast length**: `6` Months (or `90` Days)
     - **Ignore last**: `0`
     - **Confidence interval**: `95%`
     - **Seasonality**: `12` (or Auto)
  5. Click **Apply**.
  6. Result: Power BI renders the projected future revenue trajectory bounded by upper and lower 95% confidence bands.
- Title: *"Historical Sales & 6-Month Predictive Forecast (95% Confidence Interval)"*

### Visual 3: Power BI Q&A / Prompt Visual (Requirement 6)
- In the Visualizations pane, click the **Q&A** icon (chat bubble).
- Place visual at bottom (`Width: 1240, Height: 240`).
- Title: *"Natural Language Analytics Prompt (Ask Questions About Your Data)"*
- Sample pre-configured suggestion chips:
  - *"top 5 product categories by total sales"*
  - *"total estimated profit by payment method"*
  - *"total sales by state in 2018"*

### Navigation Button
- Text: `"← Back to Profit Analysis"` → Action: Page navigation → Destination: **Profit**.

---

## 6. Technical Demo Page: SCD Type 1 vs Type 2 Visualizer

Create a technical demo page named **SCD Visualizer**.

### Visual 1: Customer Selector Slicer
- Visual: **Slicer**
- Field: `vw_powerbi_scd_customer_history[customer_id]`
- Default selection: `00012a2ce6f8dcda20d059ce98491703`

### Visual 2 & 3: Strategy Comparison Summary Cards
- **SCD Type 1 Card**:
  - Title: *"SCD Type 1 Strategy: Overwrite"*
  - Display: *"Current Location: [scd1_current_city], [scd1_current_state] | History: NO (Overwritten)"*
- **SCD Type 2 Card**:
  - Title: *"SCD Type 2 Strategy: Version History"*
  - Display: *"Total Versions: [scd2_total_versions] | Current Version: [scd2_current_version_number] | History: YES"*

### Visual 4: Customer Version Audit Table
- Visual: **Table**
- Fields from `vw_powerbi_scd_customer_history`:
  - `version_number` (Header: "Version")
  - `customer_city` (Header: "City")
  - `customer_state` (Header: "State")
  - `effective_start_date` (Header: "Effective Start")
  - `effective_end_date` (Header: "Effective End")
  - `version_status` (Header: "Status" - Active vs Expired)
  - `days_in_effect` (Header: "Days Active")
- Sort by: `version_number` ASC.

### Live Demonstration Runbook
1. View customer `00012a2ce6f8dcda20d059ce98491703` (shows 1 baseline row: `OSASCO, SP`).
2. Run simulation in terminal:
   ```bash
   python scripts/simulate_scd_change.py --city "SALVADOR" --state "BA" --apply-type 2
   ```
3. Click **Refresh** in Power BI Desktop.
4. Table immediately renders 2 version rows with expiration timestamp on Version 1 and active flag on Version 2.
5. Run reset in terminal:
   ```bash
   python scripts/simulate_scd_change.py --reset
   ```
6. Click **Refresh** in Power BI Desktop to return to baseline.
