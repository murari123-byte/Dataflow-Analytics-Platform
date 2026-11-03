
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDER_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"

EXPECTED_COLUMNS = [
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


def load_orders():
    """Read order CSV data into a Pandas DataFrame."""

    if not ORDER_FILE.exists():
        raise FileNotFoundError(
            f"Order file not found: {ORDER_FILE}"
        )

    try:
        dataframe = pd.read_csv(ORDER_FILE)
    except pd.errors.EmptyDataError as error:
        raise ValueError(
            "Order CSV is empty and does not contain column headers."
        ) from error
    except pd.errors.ParserError as error:
        raise ValueError(
            f"Invalid order CSV file: {error}"
        ) from error

    if dataframe.empty and len(dataframe.columns) == 0:
        dataframe = pd.DataFrame(columns=EXPECTED_COLUMNS)

    print("Order ingestion completed.")
    print(f"Total order records: {len(dataframe):,}")

    return dataframe


if __name__ == "__main__":
    orders_df = load_orders()
    print(orders_df.head())
    print("\nColumns:")
    print(orders_df.columns.tolist())
