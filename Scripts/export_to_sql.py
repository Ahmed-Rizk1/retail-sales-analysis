"""
export_to_sql.py
----------------
Loads each sheet from salesdata.xlsx into a local MySQL database.
Run this once to seed the `sales_database` before opening the notebook.

Usage:
    python Scripts/export_to_sql.py

Prerequisites:
    - MySQL running locally with `sales_database` created.
    - A `.env` file at the project root containing DB credentials:
        DB_USER=python_user
        DB_PASSWORD=
        DB_HOST=localhost
        DB_NAME=sales_database
"""

from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

ROOT = Path(__file__).resolve().parent.parent
load_dotenv(ROOT / ".env")

DB_USER     = os.getenv("DB_USER", "python_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_NAME     = os.getenv("DB_NAME", "sales_database")

EXCEL_FILE = ROOT / "Data" / "salesdata.xlsx"

SHEETS = [
    "fact_InternetSales",
    "dim_ProductCategory",
    "dim_ProductSubcategory",
    "dim_Product",
    "dim_SalesTeritory",
    "dim_Currency",
    "dim_Customer",
]

# ---------------------------------------------------------------------------
# Database connection
# ---------------------------------------------------------------------------

connection_url = (
    f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}"
    "?charset=utf8mb4"
)

engine = create_engine(
    connection_url,
    pool_pre_ping=True,   # validate connections before use
    pool_recycle=1800,    # recycle connections every 30 minutes
)


def verify_connection() -> None:
    """Raise immediately if the database is not reachable."""
    with engine.connect() as conn:
        conn.execute(text("SELECT 1"))
    print(f"✅  Connected to MySQL: {DB_HOST}/{DB_NAME}")


# ---------------------------------------------------------------------------
# Load sheets → MySQL tables
# ---------------------------------------------------------------------------

def load_sheets() -> None:
    for sheet in SHEETS:
        table_name = sheet.lower()
        print(f"  Loading sheet '{sheet}' → table '{table_name}' ...", end=" ")
        df = pd.read_excel(EXCEL_FILE, sheet_name=sheet)
        df.to_sql(
            name=table_name,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=1000,
        )
        print(f"done  ({len(df):,} rows)")


def list_tables() -> None:
    with engine.connect() as conn:
        result = conn.execute(text("SHOW TABLES;"))
        tables = [row[0] for row in result]
    print(f"\n📋  Tables in `{DB_NAME}`: {tables}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    verify_connection()
    load_sheets()
    list_tables()
    print("\n✅  All sheets loaded successfully.")
