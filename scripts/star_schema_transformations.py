"""Transform Silver layer into Gold Dimensional Star Schema (OLAP).

Tables Created & Loaded:
- gold.dim_date
- gold.dim_customer
- gold.dim_product
- gold.dim_seller
- gold.dim_payment
- gold.fact_sales
"""

from __future__ import annotations

import os
from pathlib import Path
from utils.db import get_connection

SQL_FILE = Path(__file__).resolve().parent.parent / "sql" / "gold" / "04_star_schema.sql"


def run_star_schema_etl() -> dict[str, int]:
    """Executes the Star Schema DDL and population script, returning table row counts."""
    print("Starting Gold Dimensional Star Schema transformation...")
    
    if not SQL_FILE.exists():
        raise FileNotFoundError(f"Star schema SQL file not found: {SQL_FILE}")

    with open(SQL_FILE, "r", encoding="utf-8") as f:
        sql_script = f.read()

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            print("Executing DDL and data load from 04_star_schema.sql...")
            cur.execute(sql_script)
            conn.commit()

            # Collect metrics and validation
            counts: dict[str, int] = {}
            tables = [
                "gold.dim_date",
                "gold.dim_customer",
                "gold.dim_product",
                "gold.dim_seller",
                "gold.dim_payment",
                "gold.fact_sales",
            ]
            for table in tables:
                cur.execute(f"SELECT COUNT(*) FROM {table};")
                counts[table] = cur.fetchone()[0]

            # Foreign Key / Referential Integrity Checks
            cur.execute("""
                SELECT
                    (SELECT COUNT(*) FROM gold.fact_sales f LEFT JOIN gold.dim_customer c ON f.customer_key = c.customer_key WHERE c.customer_key IS NULL) AS orphan_customer,
                    (SELECT COUNT(*) FROM gold.fact_sales f LEFT JOIN gold.dim_product p ON f.product_key = p.product_key WHERE p.product_key IS NULL) AS orphan_product,
                    (SELECT COUNT(*) FROM gold.fact_sales f LEFT JOIN gold.dim_seller s ON f.seller_key = s.seller_key WHERE s.seller_key IS NULL) AS orphan_seller,
                    (SELECT COUNT(*) FROM gold.fact_sales f LEFT JOIN gold.dim_date d ON f.date_key = d.date_key WHERE d.date_key IS NULL) AS orphan_date,
                    (SELECT COUNT(*) FROM gold.fact_sales f LEFT JOIN gold.dim_payment pay ON f.payment_key = pay.payment_key WHERE pay.payment_key IS NULL) AS orphan_payment;
            """)
            orphan_results = cur.fetchone()
            counts["orphan_records"] = sum(orphan_results)

        return counts
    finally:
        conn.close()


def main():
    counts = run_star_schema_etl()
    print("\n--- Star Schema Load Summary ---")
    for tbl, count in counts.items():
        print(f"  {tbl}: {count:,}")
    
    if counts.get("orphan_records", 0) == 0:
        print("\n[SUCCESS] All foreign keys and referential integrity constraints validated with 0 orphan records.")
    else:
        print(f"\n[WARNING] Found {counts.get('orphan_records')} orphan records in fact_sales.")


if __name__ == "__main__":
    main()
