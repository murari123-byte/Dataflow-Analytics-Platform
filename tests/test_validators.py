
import pandas as pd
import pytest

from src.validation.customer_validator import validate_customers
from src.validation.order_validator import validate_orders


VALID_CUSTOMER = {
    "customer_id": "CUST001",
    "customer_name": "Test Customer",
    "email": "test@example.com",
    "city": "Hyderabad",
    "state": "Telangana",
    "country": "India",
    "customer_segment": "Regular",
}


VALID_ORDER = {
    "order_id": "ORD001",
    "order_line_id": "LINE001",
    "customer_id": "CUST001",
    "product_id": "P004",
    "product_name": "Office Chair",
    "category": "Furniture",
    "order_date": "2026-03-17",
    "quantity": 2,
    "unit_price": 1000.00,
    "order_status": "COMPLETED",
}


@pytest.fixture
def valid_customer_df():
    return pd.DataFrame([VALID_CUSTOMER])


@pytest.fixture
def valid_order_df():
    return pd.DataFrame([VALID_ORDER])


@pytest.fixture
def valid_customer_ids():
    return {"CUST001"}


# ---------------- CUSTOMER VALIDATION TESTS ----------------


def test_valid_customer(valid_customer_df):
    valid, rejected = validate_customers(valid_customer_df)

    assert len(valid) == 1
    assert len(rejected) == 0


def test_missing_customer_name():
    customer = VALID_CUSTOMER.copy()
    customer["customer_name"] = None

    valid, rejected = validate_customers(
        pd.DataFrame([customer])
    )

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "Missing customer_name" in rejected.iloc[0]["rejection_reason"]


def test_blank_customer_id():
    customer = VALID_CUSTOMER.copy()
    customer["customer_id"] = " "

    valid, rejected = validate_customers(
        pd.DataFrame([customer])
    )

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "Missing customer_id" in rejected.iloc[0]["rejection_reason"]


def test_duplicate_customer_ids():
    customers = pd.DataFrame([
        VALID_CUSTOMER,
        VALID_CUSTOMER,
    ])

    valid, rejected = validate_customers(customers)

    assert len(valid) == 0
    assert len(rejected) == 2
    assert all(
        "Duplicate customer_id" in reason
        for reason in rejected["rejection_reason"]
    )


def test_empty_customer_dataframe():
    customers = pd.DataFrame(columns=[
        "customer_id",
        "customer_name",
    ])

    valid, rejected = validate_customers(customers)

    assert len(valid) == 0
    assert len(rejected) == 0


def test_missing_customer_column():
    customers = pd.DataFrame({
        "customer_id": ["CUST001"]
    })

    with pytest.raises(ValueError, match="missing columns"):
        validate_customers(customers)


# ---------------- ORDER VALIDATION TESTS ----------------


def test_valid_order(valid_order_df, valid_customer_ids):
    valid, rejected = validate_orders(
        valid_order_df,
        valid_customer_ids,
    )

    assert len(valid) == 1
    assert len(rejected) == 0
    assert valid.iloc[0]["total_amount"] == 2000.00


def test_missing_order_id(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "order_id"] = None

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert len(rejected) == 1
    assert "Missing order_id" in rejected.iloc[0]["rejection_reason"]


def test_duplicate_order_line_ids(valid_customer_ids):
    orders = pd.DataFrame([
        VALID_ORDER,
        VALID_ORDER,
    ])

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert len(rejected) == 2
    assert all(
        "Duplicate order_line_id" in reason
        for reason in rejected["rejection_reason"]
    )


def test_unknown_customer_reference(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "customer_id"] = "UNKNOWN_CUSTOMER"

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Unknown customer_id" in rejected.iloc[0]["rejection_reason"]


def test_unknown_product_reference(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "product_id"] = "P999"

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Unknown product_id" in rejected.iloc[0]["rejection_reason"]


@pytest.mark.parametrize("quantity", [0, -1, -10])
def test_invalid_quantity(valid_order_df, valid_customer_ids, quantity):
    orders = valid_order_df.copy()
    orders.loc[0, "quantity"] = quantity

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Invalid quantity" in rejected.iloc[0]["rejection_reason"]



def test_fractional_quantity_rejected(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()

    # Convert quantity column to float before assigning a fraction.
    orders["quantity"] = orders["quantity"].astype(float)
    orders.loc[0, "quantity"] = 1.5

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Invalid quantity" in rejected.iloc[0]["rejection_reason"]


def test_negative_unit_price(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "unit_price"] = -100

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Invalid unit_price" in rejected.iloc[0]["rejection_reason"]


def test_zero_unit_price_is_valid(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "unit_price"] = 0

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 1
    assert len(rejected) == 0
    assert valid.iloc[0]["total_amount"] == 0


def test_invalid_order_date(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "order_date"] = "not-a-date"

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Invalid order_date" in rejected.iloc[0]["rejection_reason"]


def test_invalid_order_status(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "order_status"] = "REFUNDED"

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert "Invalid order_status" in rejected.iloc[0]["rejection_reason"]


def test_empty_order_dataframe(valid_customer_ids):
    orders = pd.DataFrame(columns=[
        "order_id",
        "order_line_id",
        "customer_id",
        "product_id",
        "order_date",
        "quantity",
        "unit_price",
        "order_status",
    ])

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert len(rejected) == 0


def test_missing_order_column(valid_customer_ids):
    orders = pd.DataFrame({
        "order_id": ["ORD001"]
    })

    with pytest.raises(ValueError, match="missing columns"):
        validate_orders(orders, valid_customer_ids)


def test_multiple_validation_errors(valid_order_df, valid_customer_ids):
    orders = valid_order_df.copy()
    orders.loc[0, "quantity"] = 0
    orders.loc[0, "unit_price"] = -100
    orders.loc[0, "order_status"] = "INVALID"

    valid, rejected = validate_orders(
        orders,
        valid_customer_ids,
    )

    assert len(valid) == 0
    assert len(rejected) == 1

    reason = rejected.iloc[0]["rejection_reason"]

    assert "Invalid quantity" in reason
    assert "Invalid unit_price" in reason
    assert "Invalid order_status" in reason
