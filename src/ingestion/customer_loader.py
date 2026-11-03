
import json
from pathlib import Path

import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parents[2]
CUSTOMER_FILE = PROJECT_ROOT / "data" / "raw" / "customers.json"

EXPECTED_COLUMNS = [
    "customer_id",
    "customer_name",
    "email",
    "city",
    "state",
    "country",
    "customer_segment",
]


def load_customers():
    """Read customer JSON data into a Pandas DataFrame."""

    if not CUSTOMER_FILE.exists():
        raise FileNotFoundError(
            f"Customer file not found: {CUSTOMER_FILE}"
        )

    try:
        with CUSTOMER_FILE.open("r", encoding="utf-8") as file:
            records = json.load(file)
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Invalid customer JSON file: {error}"
        ) from error

    if not isinstance(records, list):
        raise ValueError("Customer JSON must contain a list of records.")

    if not records:
        dataframe = pd.DataFrame(columns=EXPECTED_COLUMNS)
    else:
        dataframe = pd.DataFrame(records)

    print("Customer ingestion completed.")
    print(f"Total customer records: {len(dataframe):,}")

    return dataframe


if __name__ == "__main__":
    customers_df = load_customers()
    print(customers_df.head())
    print("\nColumns:")
    print(customers_df.columns.tolist())
