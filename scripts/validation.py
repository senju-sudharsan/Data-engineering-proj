from utils.db import get_connection

VALIDATIONS = [

    ("Silver Customers",
     "SELECT COUNT(*) FROM silver.customers"),

    ("Silver Orders",
     "SELECT COUNT(*) FROM silver.orders"),

    ("Silver Products",
     "SELECT COUNT(*) FROM silver.products"),

    ("Silver Sellers",
     "SELECT COUNT(*) FROM silver.sellers"),

    ("Silver Payments",
     "SELECT COUNT(*) FROM silver.payments"),

    ("Silver Order Fact",
     "SELECT COUNT(*) FROM silver.order_fact"),

    ("Gold Sales Summary",
     "SELECT COUNT(*) FROM gold.sales_summary"),

    ("Gold Product Performance",
     "SELECT COUNT(*) FROM gold.product_performance"),

    ("Gold Seller Performance",
     "SELECT COUNT(*) FROM gold.seller_performance"),

    ("Silver Customers SCD",
     "SELECT COUNT(*) FROM silver.customers_scd"),

    ("Gold Dim Date",
     "SELECT COUNT(*) FROM gold.dim_date"),

    ("Gold Dim Customer",
     "SELECT COUNT(*) FROM gold.dim_customer"),

    ("Gold Dim Product",
     "SELECT COUNT(*) FROM gold.dim_product"),

    ("Gold Dim Seller",
     "SELECT COUNT(*) FROM gold.dim_seller"),

    ("Gold Dim Payment",
     "SELECT COUNT(*) FROM gold.dim_payment"),

    ("Gold Fact Sales",
     "SELECT COUNT(*) FROM gold.fact_sales")
]


def main():

    conn = get_connection()
    cur = conn.cursor()

    print("\n===== VALIDATION REPORT =====\n")

    for name, sql in VALIDATIONS:

        cur.execute(sql)

        count = cur.fetchone()[0]

        print(f"{name}: {count}")

    cur.close()
    conn.close()

    print("\nValidation Completed")


if __name__ == "__main__":
    main()
