
import pandas as pd


REQUIRED_COLUMNS = [
    "customer_id",
    "customer_name",
]


def validate_customers(dataframe):
    """Validate customer records and separate rejected records."""

    df = dataframe.copy()

    # Check that all expected columns exist.
    missing_columns = [
        column for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Customer data is missing columns: {missing_columns}"
        )

    # Store rejection reasons for every record.
    reasons = pd.Series("", index=df.index, dtype="object")

    # Required field validation.
    for column in REQUIRED_COLUMNS:
        invalid = (
            df[column].isna()
            | df[column].astype("string").str.strip().eq("")
        )

        reasons.loc[invalid] += f"Missing {column}; "

    # Duplicate customer ID validation.
    duplicate_ids = (
        df["customer_id"].notna()
        & df["customer_id"].duplicated(keep=False)
    )

    reasons.loc[duplicate_ids] += "Duplicate customer_id; "

    # Separate valid and rejected records.
    valid_mask = reasons.eq("")

    valid_records = df.loc[valid_mask].copy()
    rejected_records = df.loc[~valid_mask].copy()

    rejected_records["rejection_reason"] = (
        reasons.loc[~valid_mask].str.rstrip("; ")
    )

    print("Customer validation completed.")
    print(f"Total records: {len(df):,}")
    print(f"Valid records: {len(valid_records):,}")
    print(f"Rejected records: {len(rejected_records):,}")

    return valid_records, rejected_records


if __name__ == "__main__":
    from src.ingestion.customer_loader import load_customers

    customers = load_customers()
    valid, rejected = validate_customers(customers)

    print("\nValid customer sample:")
    print(valid.head())

    print("\nRejected customer sample:")
    print(rejected.head())
