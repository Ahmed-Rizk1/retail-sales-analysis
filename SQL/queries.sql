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
