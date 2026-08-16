"""Controlled and reversible SCD change simulation tool.

This script simulates customer attribute changes in the Silver layer (silver.customers)
and applies the actual SCD Type 1 or SCD Type 2 logic from scripts/scd.py.
It provides a 100% reversible --reset flag to restore the demo customer baseline without
modifying original CSV source data.

Usage examples:
    # 1. Reset demo customer to clean baseline
    python simulate_scd_change.py --reset

    # 2. Show current state of demo customer
    python simulate_scd_change.py --status

    # 3. Simulate change and apply SCD Type 1 (overwrite in place)
    python simulate_scd_change.py --city "CURITIBA" --state "PR" --apply-type 1

    # 4. Simulate change and apply SCD Type 2 (version history preserved)
    python simulate_scd_change.py --city "SALVADOR" --state "BA" --apply-type 2
"""

from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

# Add scripts directory to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from utils.db import get_connection
from scd import run_scd_type_1, run_scd_type_2

DEFAULT_DEMO_CUSTOMER_ID = "00012a2ce6f8dcda20d059ce98491703"
DEFAULT_BASELINE_CITY = "OSASCO"
DEFAULT_BASELINE_STATE = "SP"


def get_customer_state(customer_id: str) -> dict:
    """Retrieves customer record from silver.customers and all versions from silver.customers_scd."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT customer_id, customer_city, customer_state FROM silver.customers WHERE customer_id = %s;",
                (customer_id,)
            )
            silver_row = cur.fetchone()

            cur.execute(
                """
                SELECT
                    customer_id,
                    customer_city,
                    customer_state,
                    effective_start_date,
                    effective_end_date,
                    is_current,
                    version_number
                FROM silver.customers_scd
                WHERE customer_id = %s
                ORDER BY version_number ASC;
                """,
                (customer_id,)
            )
            scd_rows = cur.fetchall()

        return {
            "customer_id": customer_id,
            "silver_record": silver_row,
            "scd_versions": scd_rows,
        }
    finally:
        conn.close()


def print_customer_scd_table(customer_id: str) -> None:
    """Prints a formatted ASCII table of the customer's current SCD versions."""
    state = get_customer_state(customer_id)
    silver_rec = state["silver_record"]
    scd_rows = state["scd_versions"]

    print("\n" + "=" * 90)
    print(f" CUSTOMER SCD STATUS: {customer_id}")
    print("=" * 90)
    if silver_rec:
        print(f"Current Silver Location: City='{silver_rec[1]}', State='{silver_rec[2]}'")
    else:
        print("Customer not found in silver.customers!")

    print("\nSCD Versions in silver.customers_scd:")
    print("-" * 90)
    header = f"{'Ver':<5} | {'City':<18} | {'State':<6} | {'Effective Start':<20} | {'Effective End':<20} | {'Current':<7}"
    print(header)
    print("-" * 90)

    if not scd_rows:
        print("  (No SCD records found)")
    else:
        for r in scd_rows:
            ver = r[6]
            city = r[1] or ""
            st = r[2] or ""
            start = r[3].strftime("%Y-%m-%d %H:%M:%S") if r[3] else "NULL"
            end = r[4].strftime("%Y-%m-%d %H:%M:%S") if r[4] else "NULL (Active)"
            curr = "TRUE" if r[5] else "FALSE"
            print(f"{ver:<5} | {city:<18} | {st:<6} | {start:<20} | {end:<20} | {curr:<7}")

    print("-" * 90 + "\n")


def update_silver_customer(customer_id: str, new_city: str, new_state: str) -> None:
    """Updates the customer's location in silver.customers to simulate source change."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                UPDATE silver.customers
                SET customer_city = %s,
                    customer_state = %s
                WHERE customer_id = %s;
                """,
                (new_city.upper(), new_state.upper(), customer_id)
            )
            conn.commit()
            print(f"[STAGE] Updated silver.customers: customer_id={customer_id} -> City='{new_city.upper()}', State='{new_state.upper()}'")
    finally:
        conn.close()


def reset_customer_baseline(customer_id: str = DEFAULT_DEMO_CUSTOMER_ID) -> None:
    """Restores the customer in silver.customers and silver.customers_scd to original baseline."""
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Reset silver.customers
            cur.execute(
                """
                UPDATE silver.customers
                SET customer_city = %s,
                    customer_state = %s
                WHERE customer_id = %s;
                """,
                (DEFAULT_BASELINE_CITY, DEFAULT_BASELINE_STATE, customer_id)
            )

            # 2. Reset silver.customers_scd to single clean version 1
            cur.execute(
                "DELETE FROM silver.customers_scd WHERE customer_id = %s;",
                (customer_id,)
            )

            cur.execute(
                """
                INSERT INTO silver.customers_scd (
                    customer_id,
                    customer_city,
                    customer_state,
                    effective_start_date,
                    effective_end_date,
                    is_current,
                    version_number
                )
                VALUES (%s, %s, %s, '2016-01-01 00:00:00'::TIMESTAMP, NULL, TRUE, 1);
                """,
                (customer_id, DEFAULT_BASELINE_CITY, DEFAULT_BASELINE_STATE)
            )
            conn.commit()
            print(f"[RESET] Demo customer {customer_id} restored to Baseline (Version 1, City='{DEFAULT_BASELINE_CITY}', State='{DEFAULT_BASELINE_STATE}').")
    finally:
        conn.close()

    print_customer_scd_table(customer_id)


def main():
    parser = argparse.ArgumentParser(description="Simulate customer SCD changes and execute SCD 1 or SCD 2.")
    parser.add_argument("--customer-id", default=DEFAULT_DEMO_CUSTOMER_ID, help="Customer ID to target (default: demo customer).")
    parser.add_argument("--city", help="New city name to apply.")
    parser.add_argument("--state", help="New state abbreviation to apply.")
    parser.add_argument("--apply-type", choices=("1", "2"), help="Automatically invoke SCD Type 1 or Type 2 after staging.")
    parser.add_argument("--status", action="store_true", help="Print current SCD status for the customer.")
    parser.add_argument("--reset", action="store_true", help="Reset demo customer back to clean Version 1 baseline.")

    args = parser.parse_args()

    if args.reset:
        reset_customer_baseline(args.customer_id)
        return

    if args.status:
        print_customer_scd_table(args.customer_id)
        return

    if args.city or args.state:
        city = args.city or "CURITIBA"
        state = args.state or "PR"

        print(f"Simulating attribute change for customer {args.customer_id}...")
        update_silver_customer(args.customer_id, city, state)

        if args.apply_type == "1":
            print("[EXECUTE] Running actual SCD Type 1 logic from scripts/scd.py...")
            updated, inserted = run_scd_type_1()
            print(f"[RESULT] SCD Type 1 completed: {updated} current rows overwritten, {inserted} inserted.")
        elif args.apply_type == "2":
            print("[EXECUTE] Running actual SCD Type 2 logic from scripts/scd.py...")
            versioned, inserted = run_scd_type_2()
            print(f"[RESULT] SCD Type 2 completed: {versioned} versions created, {inserted} inserted.")
        else:
            print("[INFO] Change staged in silver.customers. Run 'python scd.py --type 1' or '--type 2' to apply.")

        print_customer_scd_table(args.customer_id)
    else:
        # Default behavior when no action arguments given: show status
        print_customer_scd_table(args.customer_id)


if __name__ == "__main__":
    main()
