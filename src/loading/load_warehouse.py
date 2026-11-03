
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from src.ingestion.customer_loader import load_customers
from src.ingestion.order_loader import load_orders
from src.validation.customer_validator import validate_customers
from src.validation.order_validator import validate_orders
from src.loading.database import engine


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def insert_in_batches(connection, sql, records, batch_size=5000):
    """Insert records in smaller batches."""

    total_affected = 0

    for start in range(0, len(records), batch_size):
        batch = records[start:start + batch_size]
        result = connection.execute(text(sql), batch)
        total_affected += max(result.rowcount, 0)

    return total_affected


def create_pipeline_run():
    """Create a monitoring record before pipeline execution."""

    sql = """
        INSERT INTO pipeline_runs (
            run_status,
            start_time,
            source_records,
            valid_records,
            rejected_records,
            inserted_records
        )
        VALUES (
            'RUNNING',
            CURRENT_TIMESTAMP,
            0,
            0,
            0,
            0
        )
        RETURNING run_id
    """

    with engine.begin() as connection:
        return connection.execute(text(sql)).scalar_one()


def update_pipeline_run(
    run_id,
    status,
    source_count,
    valid_count,
    rejected_count,
    inserted_count,
    error_message=None,
):
    """Update pipeline status and processing counts."""

    sql = """
        UPDATE pipeline_runs
        SET
            run_status = :status,
            end_time = CURRENT_TIMESTAMP,
            source_records = :source_count,
            valid_records = :valid_count,
            rejected_records = :rejected_count,
            inserted_records = :inserted_count,
            error_message = :error_message
        WHERE run_id = :run_id
    """

    with engine.begin() as connection:
        connection.execute(
            text(sql),
            {
                "run_id": run_id,
                "status": status,
                "source_count": source_count,
                "valid_count": valid_count,
                "rejected_count": rejected_count,
                "inserted_count": inserted_count,
                "error_message": error_message,
            },
        )


def clean_record(record):
    """Convert Pandas missing values into JSON-compatible values."""

    cleaned = {}

    for key, value in record.items():
        if pd.isna(value):
            cleaned[key] = None
        elif hasattr(value, "item"):
            cleaned[key] = value.item()
        else:
            cleaned[key] = value

    return cleaned


def save_rejected_records(
    connection,
    rejected_dataframe,
    source_file,
    record_id_column,
    run_id,
):
    """Save invalid source records and their rejection reasons."""

    if rejected_dataframe.empty:
        return 0

    sql = """
        INSERT INTO rejected_records (
            run_id,
            source_file,
            source_record_id,
            raw_record,
            rejection_reason
        )
        VALUES (
            :run_id,
            :source_file,
            :source_record_id,
            CAST(:raw_record AS JSONB),
            :rejection_reason
        )
    """

    records = []

    for row in rejected_dataframe.to_dict(orient="records"):
        cleaned_record = clean_record(row)

        record_id = cleaned_record.get(record_id_column)
        rejection_reason = cleaned_record.get(
            "rejection_reason",
            "Unknown validation error",
        )

        # Keep the original source fields in the stored record.
        cleaned_record.pop("rejection_reason", None)

        records.append({
            "run_id": run_id,
            "source_file": source_file,
            "source_record_id": (
                str(record_id) if record_id is not None else None
            ),
            "raw_record": json.dumps(
                cleaned_record,
                default=str,
                allow_nan=False,
            ),
            "rejection_reason": str(rejection_reason),
        })

    return insert_in_batches(connection, sql, records)


def load_customer_dimension(connection, customers):
    """Insert or update customer dimension records."""

    if customers.empty:
        return 0

    sql = """
        INSERT INTO dim_customer (
            customer_id,
            customer_name,
            email,
            city,
            state,
            country,
            customer_segment
        )
        VALUES (
            :customer_id,
            :customer_name,
            :email,
            :city,
            :state,
            :country,
            :customer_segment
        )
        ON CONFLICT (customer_id)
        DO UPDATE SET
            customer_name = EXCLUDED.customer_name,
            email = EXCLUDED.email,
            city = EXCLUDED.city,
            state = EXCLUDED.state,
            country = EXCLUDED.country,
            customer_segment = EXCLUDED.customer_segment,
            updated_at = CURRENT_TIMESTAMP
    """

    records = customers.to_dict(orient="records")
    return insert_in_batches(connection, sql, records)


def load_product_dimension(connection, orders):
    """Create unique product records from order source data."""

    if orders.empty:
        return 0

    products = (
        orders[["product_id", "product_name", "category"]]
        .drop_duplicates(subset=["product_id"])
    )

    sql = """
        INSERT INTO dim_product (
            product_id,
            product_name,
            category
        )
        VALUES (
            :product_id,
            :product_name,
            :category
        )
        ON CONFLICT (product_id)
        DO UPDATE SET
            product_name = EXCLUDED.product_name,
            category = EXCLUDED.category,
            updated_at = CURRENT_TIMESTAMP
    """

    records = products.to_dict(orient="records")
    return insert_in_batches(connection, sql, records)


def load_date_dimension(connection, orders):
    """Generate and insert unique calendar dates."""

    if orders.empty:
        return 0

    order_dates = pd.to_datetime(
        orders["order_date"]
    ).dt.date

    unique_dates = sorted(set(order_dates))
    records = []

    for current_date in unique_dates:
        records.append({
            "date_key": int(current_date.strftime("%Y%m%d")),
            "full_date": current_date,
            "year": current_date.year,
            "quarter": (current_date.month - 1) // 3 + 1,
            "month": current_date.month,
            "month_name": current_date.strftime("%B"),
            "day": current_date.day,
            "day_of_week": current_date.strftime("%A"),
        })

    sql = """
        INSERT INTO dim_date (
            date_key,
            full_date,
            year,
            quarter,
            month,
            month_name,
            day,
            day_of_week
        )
        VALUES (
            :date_key,
            :full_date,
            :year,
            :quarter,
            :month,
            :month_name,
            :day,
            :day_of_week
        )
        ON CONFLICT (date_key) DO NOTHING
    """

    return insert_in_batches(connection, sql, records)


def load_sales_fact(connection, orders):
    """Map dimension keys and load sales transactions."""

    if orders.empty:
        return 0

    customer_rows = connection.execute(
        text("SELECT customer_id, customer_key FROM dim_customer")
    ).mappings().all()

    product_rows = connection.execute(
        text("SELECT product_id, product_key FROM dim_product")
    ).mappings().all()

    date_rows = connection.execute(
        text("SELECT full_date, date_key FROM dim_date")
    ).mappings().all()

    customer_map = {
        row["customer_id"]: row["customer_key"]
        for row in customer_rows
    }

    product_map = {
        row["product_id"]: row["product_key"]
        for row in product_rows
    }

    date_map = {
        row["full_date"]: row["date_key"]
        for row in date_rows
    }

    records = []

    for row in orders.to_dict(orient="records"):
        order_date = pd.Timestamp(row["order_date"]).date()

        quantity = int(row["quantity"])
        unit_price = Decimal(str(row["unit_price"])).quantize(
            Decimal("0.01"),
            rounding=ROUND_HALF_UP,
        )

        total_amount = (
            unit_price * quantity
        ).quantize(Decimal("0.01"))

        records.append({
            "order_id": row["order_id"],
            "order_line_id": row["order_line_id"],
            "customer_key": customer_map[row["customer_id"]],
            "product_key": product_map[row["product_id"]],
            "date_key": date_map[order_date],
            "quantity": quantity,
            "unit_price": unit_price,
            "total_amount": total_amount,
            "order_status": row["order_status"],
            "source_file": "orders.csv",
        })

    sql = """
        INSERT INTO fact_sales (
            order_id,
            order_line_id,
            customer_key,
            product_key,
            date_key,
            quantity,
            unit_price,
            total_amount,
            order_status,
            source_file
        )
        VALUES (
            :order_id,
            :order_line_id,
            :customer_key,
            :product_key,
            :date_key,
            :quantity,
            :unit_price,
            :total_amount,
            :order_status,
            :source_file
        )
        ON CONFLICT (order_line_id) DO NOTHING
    """

    return insert_in_batches(connection, sql, records)


def main():
    print("\nStarting DataFlow warehouse loading...\n")

    run_id = create_pipeline_run()
    print(f"Pipeline run started. Run ID: {run_id}")

    customers = pd.DataFrame()
    orders = pd.DataFrame()
    valid_customers = pd.DataFrame()
    valid_orders = pd.DataFrame()
    rejected_customers = pd.DataFrame()
    rejected_orders = pd.DataFrame()

    customer_count = 0
    product_count = 0
    date_count = 0
    sales_count = 0

    try:
        # Step 1: Ingest source data.
        customers = load_customers()
        orders = load_orders()

        # Step 2: Validate source data.
        valid_customers, rejected_customers = validate_customers(
            customers
        )

        valid_customer_ids = set(
            valid_customers["customer_id"]
        )

        valid_orders, rejected_orders = validate_orders(
            orders,
            valid_customer_ids,
        )

        source_count = len(customers) + len(orders)
        valid_count = len(valid_customers) + len(valid_orders)
        rejected_count = (
            len(rejected_customers) + len(rejected_orders)
        )

        print("\nValidation summary:")
        print(f"Source records: {source_count:,}")
        print(f"Valid records: {valid_count:,}")
        print(f"Rejected records: {rejected_count:,}")

        # Step 3: Persist rejected records separately.
        # This transaction commits even if warehouse loading fails.
        with engine.begin() as connection:
            customer_reject_count = save_rejected_records(
                connection,
                rejected_customers,
                "customers.json",
                "customer_id",
                run_id,
            )

            order_reject_count = save_rejected_records(
                connection,
                rejected_orders,
                "orders.csv",
                "order_line_id",
                run_id,
            )

        print(
            f"\nRejected customer records saved: "
            f"{customer_reject_count:,}"
        )
        print(
            f"Rejected order records saved: "
            f"{order_reject_count:,}"
        )

        # Step 4: Load valid data into the warehouse.
        # All warehouse changes happen in one transaction.
        with engine.begin() as connection:
            customer_count = load_customer_dimension(
                connection, valid_customers
            )

            product_count = load_product_dimension(
                connection, valid_orders
            )

            date_count = load_date_dimension(
                connection, valid_orders
            )

            sales_count = load_sales_fact(
                connection, valid_orders
            )

        # Step 5: Mark the run as successful.
        update_pipeline_run(
            run_id=run_id,
            status="SUCCESS",
            source_count=source_count,
            valid_count=valid_count,
            rejected_count=rejected_count,
            inserted_count=sales_count,
        )

        print("\nWarehouse loading completed successfully!")
        print(f"Customer rows inserted/updated: {customer_count:,}")
        print(f"Product rows inserted/updated: {product_count:,}")
        print(f"Date rows inserted: {date_count:,}")
        print(f"Sales rows newly inserted: {sales_count:,}")
        print(f"Rejected records saved: {rejected_count:,}")
        print(f"Pipeline run ID: {run_id}")
        print("\nDatabase transaction committed.")

    except Exception as error:
        source_count = len(customers) + len(orders)
        valid_count = len(valid_customers) + len(valid_orders)
        rejected_count = (
            len(rejected_customers) + len(rejected_orders)
        )

        try:
            update_pipeline_run(
                run_id=run_id,
                status="FAILED",
                source_count=source_count,
                valid_count=valid_count,
                rejected_count=rejected_count,
                inserted_count=0,
                error_message=str(error)[:4000],
            )
        except Exception as monitoring_error:
            print(
                "Could not update pipeline failure status: "
                f"{monitoring_error}"
            )

        print(f"\nPipeline failed: {error}")
        raise


if __name__ == "__main__":
    try:
        main()
    finally:
        engine.dispose()
