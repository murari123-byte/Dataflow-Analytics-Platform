
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMER_FILE = PROJECT_ROOT / "data" / "raw" / "customers.json"


def load_customers():
    """Read customer JSON data into a Pandas DataFrame."""

    if not CUSTOMER_FILE.exists():
        raise FileNotFoundError(
            f"Customer file not found: {CUSTOMER_FILE}"
        )

    with CUSTOMER_FILE.open("r", encoding="utf-8") as file:
        records = json.load(file)

    if not isinstance(records, list):
        raise ValueError("Customer JSON must contain a list of records.")

    dataframe = pd.DataFrame(records)

    print("Customer ingestion completed.")
    print(f"Total customer records: {len(dataframe):,}")

    return dataframe


if __name__ == "__main__":
    customers_df = load_customers()
    print(customers_df.head())
    print("\nColumns:")
    print(customers_df.columns.tolist())
