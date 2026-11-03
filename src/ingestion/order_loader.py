
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ORDER_FILE = PROJECT_ROOT / "data" / "raw" / "orders.csv"


def load_orders():
    """Read order CSV data into a Pandas DataFrame."""

    if not ORDER_FILE.exists():
        raise FileNotFoundError(
            f"Order file not found: {ORDER_FILE}"
        )

    dataframe = pd.read_csv(ORDER_FILE)

    print("Order ingestion completed.")
    print(f"Total order records: {len(dataframe):,}")

    return dataframe


if __name__ == "__main__":
    orders_df = load_orders()
    print(orders_df.head())
    print("\nColumns:")
    print(orders_df.columns.tolist())
