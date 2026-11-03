
import argparse
import csv
import json
import random
from datetime import date, timedelta
from pathlib import Path


# Project directories
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"

# Fixed seed makes generated data reproducible
RANDOM_SEED = 42

# Sample product catalogue
PRODUCTS = [
    ("P001", "Laptop", "Electronics"),
    ("P002", "Mobile Phone", "Electronics"),
    ("P003", "Headphones", "Electronics"),
    ("P004", "Office Chair", "Furniture"),
    ("P005", "Desk", "Furniture"),
    ("P006", "Notebook", "Stationery"),
    ("P007", "Pen Set", "Stationery"),
    ("P008", "Water Bottle", "Accessories"),
    ("P009", "Backpack", "Accessories"),
    ("P010", "Smart Watch", "Electronics"),
]

CITIES = [
    ("Hyderabad", "Telangana"),
    ("Bengaluru", "Karnataka"),
    ("Chennai", "Tamil Nadu"),
    ("Mumbai", "Maharashtra"),
    ("Pune", "Maharashtra"),
    ("Delhi", "Delhi"),
    ("Kochi", "Kerala"),
    ("Visakhapatnam", "Andhra Pradesh"),
]

SEGMENTS = ["Retail", "Corporate", "Small Business"]

ORDER_STATUSES = ["COMPLETED", "PENDING", "CANCELLED"]


def generate_customers(customer_count, rng):
    """Generate synthetic customer records."""

    customers = []

    for number in range(1, customer_count + 1):
        city, state = rng.choice(CITIES)

        customer = {
            "customer_id": f"CUST{number:06d}",
            "customer_name": f"Customer {number}",
            "email": f"customer{number}@example.com",
            "city": city,
            "state": state,
            "country": "India",
            "customer_segment": rng.choice(SEGMENTS),
        }

        customers.append(customer)

    return customers


def generate_orders(order_count, customers, rng):
    """Generate synthetic order-line records."""

    orders = []

    start_date = date(2025, 1, 1)
    end_date = date(2026, 10, 31)
    total_days = (end_date - start_date).days

    for number in range(1, order_count + 1):
        customer = rng.choice(customers)
        product = rng.choice(PRODUCTS)

        order_date = start_date + timedelta(
            days=rng.randint(0, total_days)
        )

        quantity = rng.randint(1, 5)
        unit_price = round(rng.uniform(100, 50000), 2)

        order = {
            "order_id": f"ORD{number:08d}",
            "order_line_id": f"LINE{number:08d}",
            "customer_id": customer["customer_id"],
            "product_id": product[0],
            "product_name": product[1],
            "category": product[2],
            "order_date": order_date.isoformat(),
            "quantity": quantity,
            "unit_price": unit_price,
            "order_status": rng.choice(ORDER_STATUSES),
        }

        orders.append(order)

    return orders


def save_customers(customers):
    """Save customer records as JSON."""

    output_file = RAW_DATA_DIR / "customers.json"

    with output_file.open("w", encoding="utf-8") as file:
        json.dump(customers, file, indent=4)

    print(f"Customer data saved: {output_file}")
    print(f"Customer records: {len(customers):,}")


def save_orders(orders):
    """Save order records as CSV."""

    output_file = RAW_DATA_DIR / "orders.csv"

    fieldnames = [
        "order_id",
        "order_line_id",
        "customer_id",
        "product_id",
        "product_name",
        "category",
        "order_date",
        "quantity",
        "unit_price",
        "order_status",
    ]

    with output_file.open(
        "w", newline="", encoding="utf-8"
    ) as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(orders)

    print(f"Order data saved: {output_file}")
    print(f"Order records: {len(orders):,}")


def main():
    parser = argparse.ArgumentParser(
        description="Generate synthetic sales data."
    )

    parser.add_argument(
        "--customers",
        type=int,
        default=10000,
        help="Number of customers to generate.",
    )

    parser.add_argument(
        "--orders",
        type=int,
        default=100000,
        help="Number of order lines to generate.",
    )

    args = parser.parse_args()

    if args.customers <= 0 or args.orders <= 0:
        parser.error("Customer and order counts must be positive.")

    rng = random.Random(RANDOM_SEED)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)

    print("Generating synthetic sales data...")

    customers = generate_customers(args.customers, rng)
    orders = generate_orders(args.orders, customers, rng)

    save_customers(customers)
    save_orders(orders)

    print("\nData generation completed successfully!")


if __name__ == "__main__":
    main()
