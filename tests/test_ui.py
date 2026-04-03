import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
from src.ui import extract_json_from_response, build_gemini_csv


def test_extract_json_from_plain_json():
    raw = '{"invoice_number": "INV-001", "total_amount": "100.00"}'
    result = extract_json_from_response(raw)
    parsed = json.loads(result)
    assert parsed["invoice_number"] == "INV-001"


def test_extract_json_strips_markdown_fences():
    raw = "```json\n{\"total_amount\": \"50.00\"}\n```"
    result = extract_json_from_response(raw)
    parsed = json.loads(result)
    assert parsed["total_amount"] == "50.00"


def test_extract_json_with_surrounding_prose():
    raw = 'Here is the extracted data:\n{"invoice_number": "42"}\nEnd.'
    result = extract_json_from_response(raw)
    parsed = json.loads(result)
    assert parsed["invoice_number"] == "42"


def test_extract_json_array():
    raw = '[{"description": "Widget", "quantity": "2"}]'
    result = extract_json_from_response(raw)
    parsed = json.loads(result)
    assert isinstance(parsed, list)
    assert parsed[0]["description"] == "Widget"


def test_build_gemini_csv_single_invoice_no_line_items():
    data = {"invoice_number": "INV-001", "total_amount": "200.00"}
    csv_out = build_gemini_csv(data)
    assert "invoice_number" in csv_out
    assert "INV-001" in csv_out


def test_build_gemini_csv_with_line_items():
    data = {
        "invoice_number": "INV-002",
        "line_items": [
            {"description": "Widget", "quantity": "2", "unit_price": "10.00", "total": "20.00"},
            {"description": "Gadget", "quantity": "1", "unit_price": "30.00", "total": "30.00"},
        ],
    }
    csv_out = build_gemini_csv(data)
    assert "line_description" in csv_out
    assert "Widget" in csv_out
    assert "Gadget" in csv_out


def test_build_gemini_csv_list_of_invoices():
    data = [
        {"invoice_number": "INV-003", "total_amount": "100.00"},
        {"invoice_number": "INV-004", "total_amount": "200.00"},
    ]
    csv_out = build_gemini_csv(data)
    assert "INV-003" in csv_out
    assert "INV-004" in csv_out
