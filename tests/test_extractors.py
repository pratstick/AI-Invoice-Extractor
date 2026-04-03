import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.extractors import parse_invoice_fields, flatten_json, to_csv


def test_parse_invoice_fields_all_present():
    sample = "Invoice #12345\nDate: 01/01/2024\nTotal: $123.45\nFrom: ACME Corp"
    fields = parse_invoice_fields(sample)
    assert fields["Invoice Number"] == "Invoice #12345"
    assert fields["Date"] == "Date: 01/01/2024"
    assert fields["Total Amount"] == "Total: $123.45"
    assert fields["Vendor"] == "From: ACME Corp"


def test_parse_invoice_fields_missing_returns_empty_string():
    fields = parse_invoice_fields("No relevant content here.")
    assert fields["Invoice Number"] == ""
    assert fields["Total Amount"] == ""
    assert fields["Date"] == ""
    assert fields["Vendor"] == ""


def test_parse_invoice_fields_empty_string():
    fields = parse_invoice_fields("")
    assert all(v == "" for v in fields.values())


def test_flatten_json_flat_dict():
    result = flatten_json({"a": 1, "b": 2})
    assert result == {"a": 1, "b": 2}


def test_flatten_json_nested_dict():
    result = flatten_json({"vendor": {"name": "ACME", "address": "123 St"}})
    assert result == {"vendor.name": "ACME", "vendor.address": "123 St"}


def test_flatten_json_list():
    result = flatten_json([{"qty": 1}, {"qty": 2}])
    assert result == {"0.qty": 1, "1.qty": 2}


def test_flatten_json_mixed():
    result = flatten_json({"items": [{"desc": "Widget", "price": "10.00"}]})
    assert result["items.0.desc"] == "Widget"
    assert result["items.0.price"] == "10.00"


def test_to_csv_contains_headers_and_values():
    csv_str = to_csv({"Invoice Number": "INV-001", "Total Amount": "$50.00"})
    assert "Invoice Number" in csv_str
    assert "INV-001" in csv_str
    assert "Total Amount" in csv_str
    assert "$50.00" in csv_str
