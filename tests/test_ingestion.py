
import json

import pytest

from src.ingestion import customer_loader, order_loader


def test_empty_customer_json(monkeypatch, tmp_path):
    file_path = tmp_path / "customers.json"
    file_path.write_text("[]", encoding="utf-8")

    monkeypatch.setattr(customer_loader, "CUSTOMER_FILE", file_path)

    result = customer_loader.load_customers()

    assert result.empty
    assert "customer_id" in result.columns
    assert "customer_name" in result.columns


def test_malformed_customer_json(monkeypatch, tmp_path):
    file_path = tmp_path / "customers.json"
    file_path.write_text("{invalid json}", encoding="utf-8")

    monkeypatch.setattr(customer_loader, "CUSTOMER_FILE", file_path)

    with pytest.raises(ValueError, match="Invalid customer JSON"):
        customer_loader.load_customers()


def test_customer_json_wrong_structure(monkeypatch, tmp_path):
    file_path = tmp_path / "customers.json"
    file_path.write_text(
        json.dumps({"customer_id": "C001"}),
        encoding="utf-8"
    )

    monkeypatch.setattr(customer_loader, "CUSTOMER_FILE", file_path)

    with pytest.raises(ValueError, match="must contain a list"):
        customer_loader.load_customers()


def test_missing_customer_file(monkeypatch, tmp_path):
    file_path = tmp_path / "missing_customers.json"

    monkeypatch.setattr(customer_loader, "CUSTOMER_FILE", file_path)

    with pytest.raises(FileNotFoundError):
        customer_loader.load_customers()


def test_empty_order_csv_with_headers(monkeypatch, tmp_path):
    file_path = tmp_path / "orders.csv"
    file_path.write_text(
        "order_id,order_line_id,customer_id,product_id,"
        "product_name,category,order_date,quantity,"
        "unit_price,order_status\n",
        encoding="utf-8"
    )

    monkeypatch.setattr(order_loader, "ORDER_FILE", file_path)

    result = order_loader.load_orders()

    assert result.empty
    assert "order_id" in result.columns
    assert "order_line_id" in result.columns


def test_completely_empty_order_csv(monkeypatch, tmp_path):
    file_path = tmp_path / "orders.csv"
    file_path.write_text("", encoding="utf-8")

    monkeypatch.setattr(order_loader, "ORDER_FILE", file_path)

    with pytest.raises(ValueError, match="CSV is empty"):
        order_loader.load_orders()


def test_missing_order_file(monkeypatch, tmp_path):
    file_path = tmp_path / "missing_orders.csv"

    monkeypatch.setattr(order_loader, "ORDER_FILE", file_path)

    with pytest.raises(FileNotFoundError):
        order_loader.load_orders()
