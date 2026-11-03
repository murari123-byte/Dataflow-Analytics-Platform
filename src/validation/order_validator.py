
import pandas as pd


REQUIRED_COLUMNS = [
    "order_id",
    "order_line_id",
    "customer_id",
    "product_id",
    "order_date",
    "quantity",
    "unit_price",
    "order_status",
]

VALID_STATUSES = {
    "COMPLETED",
    "PENDING",
    "CANCELLED",
}

VALID_PRODUCTS = {
    "P001", "P002", "P003", "P004", "P005",
    "P006", "P007", "P008", "P009", "P010",
}


def validate_orders(dataframe, valid_customer_ids):
    """Validate orders and separate valid and rejected records."""

    df = dataframe.copy()

    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Order data is missing columns: {missing_columns}"
        )

    reasons = pd.Series("", index=df.index, dtype="object")

    # Required field validation.
    for column in REQUIRED_COLUMNS:
        invalid = (
            df[column].isna()
            | df[column].astype("string").str.strip().eq("")
        )

        reasons.loc[invalid] += f"Missing {column}; "

    # Duplicate order line validation.
    duplicate_lines = (
        df["order_line_id"].notna()
        & df["order_line_id"].duplicated(keep=False)
    )

    reasons.loc[duplicate_lines] += "Duplicate order_line_id; "

    # Customer reference validation.
    unknown_customers = (
        df["customer_id"].notna()
        & ~df["customer_id"].isin(valid_customer_ids)
    )

    reasons.loc[unknown_customers] += "Unknown customer_id; "

    # Product reference validation.
    unknown_products = (
        df["product_id"].notna()
        & ~df["product_id"].isin(VALID_PRODUCTS)
    )

    reasons.loc[unknown_products] += "Unknown product_id; "

    # Numeric validation.
    df["quantity"] = pd.to_numeric(
        df["quantity"], errors="coerce"
    )

    df["unit_price"] = pd.to_numeric(
        df["unit_price"], errors="coerce"
    )

    invalid_quantity = (
        df["quantity"].isna()
        | (df["quantity"] <= 0)
        | (df["quantity"] % 1 != 0)
    )

    reasons.loc[invalid_quantity] += "Invalid quantity; "

    invalid_price = (
        df["unit_price"].isna()
        | (df["unit_price"] < 0)
    )

    reasons.loc[invalid_price] += "Invalid unit_price; "

    # Date validation.
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )

    invalid_date = df["order_date"].isna()

    reasons.loc[invalid_date] += "Invalid order_date; "

    # Order status validation.
    invalid_status = ~df["order_status"].isin(VALID_STATUSES)

    reasons.loc[invalid_status] += "Invalid order_status; "

    # Calculate total amount.
    df["total_amount"] = (
        df["quantity"] * df["unit_price"]
    ).round(2)

    # Separate valid and rejected records.
    valid_mask = reasons.eq("")

    valid_records = df.loc[valid_mask].copy()
    rejected_records = df.loc[~valid_mask].copy()

    rejected_records["rejection_reason"] = (
        reasons.loc[~valid_mask].str.rstrip("; ")
    )

    print("Order validation completed.")
    print(f"Total records: {len(df):,}")
    print(f"Valid records: {len(valid_records):,}")
    print(f"Rejected records: {len(rejected_records):,}")

    return valid_records, rejected_records


if __name__ == "__main__":
    from src.ingestion.customer_loader import load_customers
    from src.ingestion.order_loader import load_orders
    from src.validation.customer_validator import validate_customers

    customers = load_customers()
    valid_customers, rejected_customers = validate_customers(
        customers
    )

    orders = load_orders()

    valid_customer_ids = set(
        valid_customers["customer_id"]
    )

    valid_orders, rejected_orders = validate_orders(
        orders,
        valid_customer_ids,
    )

    print("\nCustomer rejection count:", len(rejected_customers))
    print("Order rejection count:", len(rejected_orders))
