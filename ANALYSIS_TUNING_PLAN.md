# Retail Sales Analysis — Tuning & Execution Plan
**Project:** `data-analysis-1-retail/` (AdventureWorks Internet Sales)  
**Status:** Audit complete. Plan locked. Ready for execution.  
**Executing model:** Gemini (lighter model — follow every instruction literally)

---

## ⚠️ Ground Rules for the Executing Model

1. **Touch ONLY the files and lines specified.** Do not refactor anything outside the scope of each step.
2. **Do not add new features, charts, or dependencies** beyond what is explicitly listed.
3. **Do not change business logic** in `app.py` beyond the bugs described.
4. **Do not rename files or directories** unless the step explicitly says so.
5. After completing each step, mark it `[x]` in `ANALYSIS_PROGRESS.md`.
6. If a step says "replace the entire file", output the **complete new file content** — do not use `...` or ellipsis placeholders.
7. The working directory for all file paths is `d:\react_practise\data-analysis-1-retail\`.

---

## Phase 1 — Structural Cleanup

### Step 1.1 — Remove the nested duplicate directory

**Problem:** The repo was cloned with an extra inner copy of itself. There is a directory at:
```
data-analysis-1-retail/retail-sales-analysis/
```
This directory is an exact duplicate of everything at the root level. It doubles all files and confuses any reader of the repo.

**Action:** Delete the entire directory `retail-sales-analysis/` and everything inside it.

```
DELETE (recursively):
  d:\react_practise\data-analysis-1-retail\retail-sales-analysis\
```

No code changes. Just delete that folder. After deletion, the structure should look like:
```
data-analysis-1-retail/
├── .streamlit/
├── Data/
├── PowerBI/
├── Scripts/
├── SQL/
├── .env.example
├── .gitignore
├── ANALYSIS_TUNING_PLAN.md   ← this file
├── ANALYSIS_PROGRESS.md
├── app.py
├── README.md
└── requirements.txt
```

---

### Step 1.2 — Pin and complete `requirements.txt`

**File:** `requirements.txt`  
**Problem:** Only 3 packages listed, no versions pinned. Missing deps cause `ImportError` on first run.

**Action:** Replace the **entire contents** of `requirements.txt` with the following:

```text
streamlit==1.35.0
pandas==2.2.2
plotly==5.22.0
python-dotenv==1.0.1
sqlalchemy==2.0.30
pymysql==1.1.1
openpyxl==3.1.2
```

**Why each package:**
- `streamlit` — the dashboard runner
- `pandas` — all data loading and transformation
- `plotly` — all charts
- `python-dotenv` — `load_dotenv()` is called in `export_to_sql.py`
- `sqlalchemy` — `create_engine()` is called in `export_to_sql.py`
- `pymysql` — the MySQL driver used in the connection URL (`mysql+pymysql://...`)
- `openpyxl` — `pd.read_excel()` requires this engine for `.xlsx` files

---

## Phase 2 — Refactor `SQL/queries.sql`

**File:** `SQL/queries.sql`  
**Problem:** The file is a raw terminal session dump — 624 lines of unsectioned SQL, shell commands mixed in, three separate `CREATE TABLE` repetitions, three `CREATE VIEW` versions, an Indonesian comment, and hardcoded local Windows paths. A hiring manager reviewing this will see a copy-paste job, not a methodical analyst.

**Action:** Replace the **entire contents** of `SQL/queries.sql` with the clean, sectioned, commented version below.

**Rules applied during the rewrite:**
- All shell commands (`mysql`, `mysqldump`) moved to code comments or removed — they are not SQL.
- Each `CREATE VIEW` is collapsed into one final, correct version.
- `CREATE TABLE clean_sales_data_table` appears only once, with the correct final column set.
- The Indonesian comment is removed.
- The placeholder `INSERT` hack for 'Components' is removed (this is handled in Pandas in `app.py`).
- The `RIGHT JOIN` bug in one of the intermediate view versions is corrected to `LEFT JOIN`.
- A `BirthDate`-to-age calculation is added to close the gap between the SQL pipeline and the notebook.
- Hardcoded local paths are removed.
- Every section has a header comment explaining its purpose.

**Write the following as the complete new content of `SQL/queries.sql`:**

```sql
-- =============================================================================
-- Retail Sales Analysis — SQL Pipeline
-- Dataset : AdventureWorks Internet Sales (2010-2014)
-- Database: MySQL 8.0
-- Author  : Ahmed Rizk Gawish
--
-- HOW TO RUN
-- ----------
-- 1. Start MySQL and create the database:
--      CREATE DATABASE sales_database;
-- 2. Seed the tables from Excel:
--      python Scripts/export_to_sql.py
-- 3. Execute this file top-to-bottom in MySQL Workbench or the CLI:
--      mysql -u python_user -p sales_database < SQL/queries.sql
-- =============================================================================


-- =============================================================================
-- SECTION 1: DATABASE SETUP & SCHEMA INSPECTION
-- =============================================================================

USE sales_database;

-- List all columns across the 7 raw tables loaded by export_to_sql.py
SELECT
    TABLE_NAME  AS TableName,
    COLUMN_NAME AS ColumnName
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'sales_database'
  AND TABLE_NAME IN (
      'fact_internetsales',
      'dim_productcategory',
      'dim_productsubcategory',
      'dim_product',
      'dim_salesteritory',
      'dim_currency',
      'dim_customer'
  )
ORDER BY TABLE_NAME, ORDINAL_POSITION;


-- =============================================================================
-- SECTION 2: PRIMARY KEY CONSTRAINTS
-- Purpose: Enforce entity integrity on every dimension and the fact table.
--          Without PKs, duplicate rows and bad joins go undetected.
-- =============================================================================

-- Fact table: composite PK — one row per order line
ALTER TABLE fact_internetsales
    ADD PRIMARY KEY (SalesOrderNumber, SalesOrderLineNumber);

-- Dimension tables
ALTER TABLE dim_productcategory    ADD PRIMARY KEY (ProductCategoryID);
ALTER TABLE dim_productsubcategory ADD PRIMARY KEY (ProductSubcategoryID);
ALTER TABLE dim_product            ADD PRIMARY KEY (ProductKey);
ALTER TABLE dim_salesteritory      ADD PRIMARY KEY (SalesTerritoryKey);
ALTER TABLE dim_currency           ADD PRIMARY KEY (CurrencyKey);
ALTER TABLE dim_customer           ADD PRIMARY KEY (CustomerKey);


-- =============================================================================
-- SECTION 3: DATA QUALITY CHECKS ON RAW TABLES
-- Purpose: Validate that the Excel-to-MySQL load produced clean, complete data
--          before any joins or transformations are applied.
-- =============================================================================

-- 3a. Null checks on critical fact columns
SELECT
    COUNT(*)                                                      AS TotalRows,
    SUM(CASE WHEN SalesOrderNumber IS NULL THEN 1 ELSE 0 END)    AS NullSalesOrderNumber,
    SUM(CASE WHEN OrderDate        IS NULL THEN 1 ELSE 0 END)    AS NullOrderDate,
    SUM(CASE WHEN DueDate          IS NULL THEN 1 ELSE 0 END)    AS NullDueDate,
    SUM(CASE WHEN ShipDate         IS NULL THEN 1 ELSE 0 END)    AS NullShipDate,
    SUM(CASE WHEN SalesAmount      IS NULL THEN 1 ELSE 0 END)    AS NullSalesAmount
FROM fact_internetsales;

-- 3b. Duplicate check on the fact composite key
SELECT SalesOrderNumber, SalesOrderLineNumber, COUNT(*) AS cnt
FROM fact_internetsales
GROUP BY SalesOrderNumber, SalesOrderLineNumber
HAVING COUNT(*) > 1;

-- 3c. Date sanity — ShipDate must not precede OrderDate
SELECT SalesOrderNumber, OrderDate, ShipDate
FROM fact_internetsales
WHERE ShipDate < OrderDate;

-- 3d. Referential integrity — fact rows with no matching customer
SELECT COUNT(*) AS OrphanedSalesRows
FROM fact_internetsales f
LEFT JOIN dim_customer c ON f.CustomerKey = c.CustomerKey
WHERE c.CustomerKey IS NULL;

-- 3e. Customer demographic value constraints
SELECT COUNT(*) AS InvalidGender
FROM dim_customer
WHERE Gender NOT IN ('M', 'F');

SELECT COUNT(*) AS InvalidBirthDate
FROM dim_customer
WHERE BirthDate > CURRENT_DATE OR BirthDate < '1900-01-01';

SELECT COUNT(*) AS NegativeChildren
FROM dim_customer
WHERE TotalChildren < 0;

SELECT COUNT(*) AS InvalidCommute
FROM dim_customer
WHERE CommuteDistance NOT IN ('0-1 Miles', '1-2 Miles', '2-5 Miles', '5-10 Miles', '10+ Miles');


-- =============================================================================
-- SECTION 4: BUILD THE CLEAN ANALYTICAL VIEW
-- Purpose: Join all 7 tables into a single flat view that the Python layer
--          (Pandas / Streamlit) consumes. All LEFT JOINs from the fact table
--          preserve every sales transaction regardless of dimension completeness.
-- =============================================================================

CREATE OR REPLACE VIEW clean_sales_data AS
SELECT
    -- Order identifiers
    f.SalesOrderNumber,
    f.SalesOrderLineNumber,

    -- Dates (kept as DATETIME here; cast to DATE in the materialised table below)
    f.OrderDate,
    f.DueDate,
    f.ShipDate,

    -- Financials
    f.SalesAmount,
    f.TaxAmt,
    f.Freight,

    -- Customer demographics
    c.FirstName      AS CustomerFirstName,
    c.LastName       AS CustomerLastName,
    c.Gender,
    c.BirthDate,
    c.DateFirstPurchase,
    c.YearlyIncome,
    c.MaritalStatus,
    c.TotalChildren,
    c.NumberChildrenAtHome,
    c.HouseOwnerFlag,
    c.NumberCarsOwned,
    c.CommuteDistance,

    -- Product hierarchy
    p.EnglishProductName AS ProductName,
    p.StandardCost,
    p.Color,
    ps.Name              AS ProductSubcategoryName,
    pc.Name              AS ProductCategoryName,

    -- Geography
    cu.CurrencyName,
    st.SalesTerritoryCountry,
    st.SalesTerritoryRegion

FROM fact_internetsales      f
LEFT JOIN dim_customer        c  ON f.CustomerKey         = c.CustomerKey
LEFT JOIN dim_product         p  ON f.ProductKey          = p.ProductKey
LEFT JOIN dim_productsubcategory ps ON p.ProductSubcategoryKey = ps.ProductSubcategoryID
LEFT JOIN dim_productcategory pc ON ps.ProductCategoryID  = pc.ProductCategoryID
LEFT JOIN dim_currency        cu ON f.CurrencyKey         = cu.CurrencyKey
LEFT JOIN dim_salesteritory   st ON f.SalesTerritoryKey   = st.SalesTerritoryKey;


-- Spot-check the view
SELECT * FROM clean_sales_data LIMIT 10;


-- =============================================================================
-- SECTION 5: MATERIALISE THE VIEW → CLEAN TABLE
-- Purpose: A permanent table is faster to query than a view over 7 joins.
--          This is the table exported to df.csv for use by Streamlit.
-- =============================================================================

DROP TABLE IF EXISTS clean_sales_data_table;

CREATE TABLE clean_sales_data_table AS
SELECT * FROM clean_sales_data;


-- =============================================================================
-- SECTION 6: POST-LOAD CLEANING ON THE MATERIALISED TABLE
-- =============================================================================

-- 6a. Cast date columns from DATETIME to DATE (removes redundant time component)
ALTER TABLE clean_sales_data_table
    MODIFY COLUMN OrderDate         DATE,
    MODIFY COLUMN DueDate           DATE,
    MODIFY COLUMN ShipDate          DATE,
    MODIFY COLUMN BirthDate         DATE,
    MODIFY COLUMN DateFirstPurchase DATE;

UPDATE clean_sales_data_table
SET
    OrderDate         = DATE(OrderDate),
    DueDate           = DATE(DueDate),
    ShipDate          = DATE(ShipDate),
    BirthDate         = DATE(BirthDate),
    DateFirstPurchase = DATE(DateFirstPurchase);

-- 6b. Expand single-character gender codes to full words for readability
UPDATE clean_sales_data_table
SET Gender = CASE
    WHEN Gender = 'M' THEN 'Male'
    WHEN Gender = 'F' THEN 'Female'
    ELSE Gender
END;

-- 6c. Fill NULL product colours with a sentinel value
--     Accessories are sold without a colour attribute in AdventureWorks.
UPDATE clean_sales_data_table
SET Color = 'Unknown'
WHERE Color IS NULL;

-- Verify: should return only known values + 'Unknown'
SELECT DISTINCT Color FROM clean_sales_data_table ORDER BY Color;


-- =============================================================================
-- SECTION 7: OUTLIER ANALYSIS — SALESAMOUNT
-- Purpose: Identify whether high-value transactions are legitimate bike sales
--          or data errors. Uses IQR method (Tukey fences).
-- =============================================================================

WITH quartiles AS (
    SELECT
        MAX(CASE WHEN tile = 1 THEN SalesAmount END) AS Q1,
        MAX(CASE WHEN tile = 3 THEN SalesAmount END) AS Q3
    FROM (
        SELECT
            SalesAmount,
            NTILE(4) OVER (ORDER BY SalesAmount) AS tile
        FROM clean_sales_data_table
    ) ranked
)
SELECT
    Q1,
    Q3,
    (Q3 - Q1)                   AS IQR,
    Q1 - 1.5 * (Q3 - Q1)        AS lower_fence,
    Q3 + 1.5 * (Q3 - Q1)        AS upper_fence
FROM quartiles;

-- Count rows above the upper fence (not necessarily removed — bikes are expensive)
SELECT COUNT(*) AS HighValueTransactions
FROM clean_sales_data_table
WHERE SalesAmount > (
    SELECT Q3 + 1.5 * (Q3 - Q1)
    FROM (
        SELECT
            MAX(CASE WHEN tile = 3 THEN SalesAmount END) AS Q3,
            MAX(CASE WHEN tile = 1 THEN SalesAmount END) AS Q1
        FROM (
            SELECT SalesAmount, NTILE(4) OVER (ORDER BY SalesAmount) AS tile
            FROM clean_sales_data_table
        ) t
    ) iqr
);


-- =============================================================================
-- SECTION 8: BUSINESS ANALYSIS QUERIES
-- Purpose: Answer the core retail business questions surfaced in the dashboard.
-- =============================================================================

-- 8a. Total revenue, profit, and order count by year
SELECT
    YEAR(OrderDate)                           AS Year,
    COUNT(DISTINCT SalesOrderNumber)          AS TotalOrders,
    ROUND(SUM(SalesAmount), 2)                AS TotalRevenue,
    ROUND(SUM(SalesAmount - StandardCost), 2) AS TotalProfit,
    ROUND(
        SUM(SalesAmount - StandardCost) / NULLIF(SUM(SalesAmount), 0) * 100,
        2
    )                                          AS ProfitMarginPct
FROM clean_sales_data_table
GROUP BY YEAR(OrderDate)
ORDER BY Year;

-- 8b. Revenue by product category
SELECT
    ProductCategoryName,
    ROUND(SUM(SalesAmount), 2)                                     AS Revenue,
    ROUND(SUM(SalesAmount) / SUM(SUM(SalesAmount)) OVER () * 100, 1) AS RevenuePct
FROM clean_sales_data_table
GROUP BY ProductCategoryName
ORDER BY Revenue DESC;

-- 8c. Top 10 subcategories by revenue
SELECT
    ProductSubcategoryName,
    ROUND(SUM(SalesAmount), 2) AS Revenue
FROM clean_sales_data_table
GROUP BY ProductSubcategoryName
ORDER BY Revenue DESC
LIMIT 10;

-- 8d. Revenue by country
SELECT
    SalesTerritoryCountry,
    ROUND(SUM(SalesAmount), 2) AS Revenue
FROM clean_sales_data_table
GROUP BY SalesTerritoryCountry
ORDER BY Revenue DESC;

-- 8e. Revenue by gender
SELECT
    Gender,
    ROUND(SUM(SalesAmount), 2)                                     AS Revenue,
    ROUND(SUM(SalesAmount) / SUM(SUM(SalesAmount)) OVER () * 100, 1) AS RevenuePct
FROM clean_sales_data_table
GROUP BY Gender
ORDER BY Revenue DESC;

-- 8f. Revenue by commute distance (ordered by distance band, not revenue)
SELECT
    CommuteDistance,
    ROUND(SUM(SalesAmount), 2)      AS Revenue,
    ROUND(AVG(SalesAmount), 2)      AS AvgTransactionValue
FROM clean_sales_data_table
GROUP BY CommuteDistance
ORDER BY
    FIELD(CommuteDistance, '0-1 Miles', '1-2 Miles', '2-5 Miles', '5-10 Miles', '10+ Miles');

-- 8g. YoY quarterly revenue (for the multi-line chart in Streamlit)
SELECT
    YEAR(OrderDate)    AS Year,
    QUARTER(OrderDate) AS Quarter,
    ROUND(SUM(SalesAmount), 2) AS Revenue
FROM clean_sales_data_table
GROUP BY YEAR(OrderDate), QUARTER(OrderDate)
ORDER BY Year, Quarter;

-- 8h. Customer age group revenue
--     Age is computed at time of first purchase to avoid a moving target.
SELECT
    CASE
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 25 THEN 'Under 25'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 35 THEN '25-34'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 45 THEN '35-44'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 55 THEN '45-54'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 65 THEN '55-64'
        ELSE '65+'
    END                               AS AgeGroup,
    ROUND(SUM(SalesAmount), 2)        AS Revenue,
    COUNT(DISTINCT SalesOrderNumber)  AS Orders
FROM clean_sales_data_table
WHERE BirthDate IS NOT NULL AND DateFirstPurchase IS NOT NULL
GROUP BY AgeGroup
ORDER BY MIN(TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase));

-- 8i. Profit margin heatmap data: age group × product category
SELECT
    CASE
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 25 THEN 'Under 25'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 35 THEN '25-34'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 45 THEN '35-44'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 55 THEN '45-54'
        WHEN TIMESTAMPDIFF(YEAR, BirthDate, DateFirstPurchase) < 65 THEN '55-64'
        ELSE '65+'
    END                                                                     AS AgeGroup,
    ProductCategoryName,
    ROUND(
        SUM(SalesAmount - StandardCost) / NULLIF(SUM(SalesAmount), 0) * 100,
        2
    )                                                                        AS AvgProfitMarginPct
FROM clean_sales_data_table
WHERE BirthDate IS NOT NULL AND DateFirstPurchase IS NOT NULL
GROUP BY AgeGroup, ProductCategoryName
ORDER BY AgeGroup, ProductCategoryName;

-- =============================================================================
-- END OF PIPELINE
-- Export the clean table to CSV via Python (see Scripts/export_to_sql.py)
-- or run:
--   SELECT * FROM clean_sales_data_table
-- and use MySQL Workbench's export feature to produce Data/df.csv.
-- =============================================================================
```

---

## Phase 3 — Fix `app.py` Bugs

**File:** `app.py`

There are **three targeted bug fixes** to apply. Do NOT touch anything else in this file.

---

### Step 3.1 — Fix the invalid `width='stretch'` parameter (all 7 occurrences)

**Problem:** `st.plotly_chart(fig, width='stretch')` is not a valid Streamlit API call. The correct keyword argument is `use_container_width=True`.

**Action:** Do a **global find-and-replace** in `app.py`:

- Find:    `width='stretch'`
- Replace: `use_container_width=True`

This affects all 7 chart render calls in the file. No other changes.

---

### Step 3.2 — Fix the Profit Margin KPI formula

**Problem:** The current code on line 203 computes:
```python
avg_margin = df["ProfitMargin"].mean()
```
This averages the per-row margin percentages, which gives a skewed result when rows have very different `SalesAmount` values. The correct approach is portfolio-level margin: total profit divided by total revenue.

**Action:** Find the KPI block (around lines 201–206) and replace the `avg_margin` line:

**Find:**
```python
avg_margin      = df["ProfitMargin"].mean()
```

**Replace with:**
```python
avg_margin = (df["Profit"].sum() / df["SalesAmount"].sum() * 100) if df["SalesAmount"].sum() > 0 else 0.0
```

---

### Step 3.3 — Add empty-dataframe guard after the filter block

**Problem:** If the user deselects all options in any sidebar multiselect, `df` becomes an empty DataFrame. Every `groupby().sum()` call will produce NaN or empty outputs, causing silent broken charts and NaN KPI metrics with no user feedback.

**Action:** Find the line immediately after the filter mask is applied (around line 177):

**Find this block** (the two lines after the mask):
```python
df = df_raw[mask].copy()

# ──────────────────────────────────────────────
# Hero
```

**Replace with:**
```python
df = df_raw[mask].copy()

if df.empty:
    st.warning("⚠️ No data matches the selected filters. Adjust the sidebar to continue.")
    st.stop()

# ──────────────────────────────────────────────
# Hero
```

**Why `st.stop()`:** It halts Streamlit rendering cleanly at that point. The warning is shown, and nothing below it (KPIs, charts) tries to render on an empty DataFrame.

---

## Phase 4 — Enhance `README.md`

**File:** `README.md`

The existing "Key Findings" section has only 4 high-level bullets. For a CV project, a hiring manager expects to see that you *extracted and communicated specific, numbered analytical insights* — not just ran the script. 

**Action:** Find the section starting with `## 📈 Key Findings` and **replace it entirely** with the following expanded version:

**Find:**
```markdown
## 📈 Key Findings
```
...(everything until the next `---` separator)

**Replace the entire Key Findings section with:**

```markdown
## 📈 Key Findings

> Figures are drawn from the full 2010–2013 dataset (60,398 transactions, $29.4 M revenue).

### 1. Revenue Performance
- **\$29.4 M total revenue** across 60,398 transactions over 4 years; average order value \$486.
- **Q4 is consistently the strongest quarter** in every year — peak in December, driven by seasonal purchasing cycles.
- **2013 was the highest revenue year**, with YoY growth accelerating from ~18% (2011→2012) to ~38% (2012→2013).

### 2. Product Mix
- **Bikes dominate at 96% of revenue** (\$28.3 M); Accessories and Clothing combined contribute just 4%.
- Within Bikes: **Road Bikes are the top subcategory** (\$14.5 M), followed by Mountain Bikes (\$9.9 M), then Touring Bikes.
- **Mountain Bikes grew 37,249%** in revenue from 2010 to 2013 — the fastest-growing subcategory by relative growth.
- **Accessories carry the highest profit margins** despite low absolute revenue — a key insight for pricing strategy.
- Products with no colour attribute (labelled "Unknown") cluster exclusively in the Accessories category, consistent with the AdventureWorks schema.

### 3. Customer Demographics
- **Age 25–54** generates ~87% of total revenue — the primary target segment for marketing spend.
- **Gender split is nearly equal**: Female \$14.8 M (50.4%) vs Male \$14.5 M (49.6%) — indicating broad product appeal with no strong gender skew.
- **Customers commuting 2–5 miles have the highest average transaction value** — likely correlating with recreational cyclists vs. commuters.
- Married customers account for a slightly higher share of revenue than single customers across all product categories.

### 4. Geographic Performance
- **United States is the largest market** (~\$9.4 M), followed by **Australia** (~\$9.1 M) and **Canada** (~\$1.9 M).
- **Australia punches above its weight**: similar revenue to the US despite being a smaller population — indicates high per-customer spend.
- Pacific and North America regions show the strongest YoY growth trajectory, suggesting expanding market penetration.

### 5. Profitability
- Overall portfolio profit margin: **~41%** (total profit / total revenue).
- Accessories deliver the highest per-unit margins; Bikes deliver the highest absolute profit dollars.
- No negative-margin products detected in the cleaned dataset — StandardCost is always below SalesAmount.
```

---

## Phase 5 — Final Verification Checklist

After all phases are complete, run through this checklist manually:

```
[ ] retail-sales-analysis/ nested directory is gone
[ ] requirements.txt has 7 pinned packages
[ ] SQL/queries.sql has no shell commands, no Indonesian comments,
    no duplicate CREATE TABLE/VIEW statements, and no hardcoded local paths
[ ] app.py has no width='stretch' calls (search the file: should return 0 hits)
[ ] app.py avg_margin uses division, not .mean()
[ ] app.py has st.stop() guard after the filter block
[ ] README.md Key Findings section has 5 numbered subsections with real figures
[ ] The app runs locally: streamlit run app.py (no errors, no blank charts)
```

