"""
Streamlit UI component helpers for the AI Invoice Extractor.
"""

import json
import re

import pandas as pd
import streamlit as st
from itables.streamlit import interactive_table as show_itable

from src.config import MAX_FILE_SIZE_MB, PROMPT_TEMPLATES
from src.extractors import flatten_json, to_csv

# Columns expected in line-item DataFrames
_LINE_ITEM_COLS = ["quantity", "unit_price", "total"]


def sidebar_settings() -> tuple[str, object]:
    """Render sidebar controls and return the selected prompt type and uploaded file."""
    st.sidebar.header("Settings")
    prompt_type = st.sidebar.selectbox("Prompt Template", list(PROMPT_TEMPLATES.keys()))
    uploaded_file = st.sidebar.file_uploader(
        "Upload Invoice (PDF, JPG, PNG)",
        type=["pdf", "jpg", "jpeg", "png"],
        label_visibility="collapsed",
    )
    if uploaded_file:
        if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
            st.sidebar.error(
                f"File too large! Please upload a file smaller than {MAX_FILE_SIZE_MB} MB."
            )
        else:
            st.sidebar.markdown(f"**File Name:** {uploaded_file.name}")
            st.sidebar.markdown(f"**File Size:** {uploaded_file.size / (1024 * 1024):.2f} MB")
    else:
        st.sidebar.info("Upload an invoice to get started.")
    return prompt_type, uploaded_file


def show_extracted_text(texts: list[str]) -> None:
    """Display the OCR-extracted text with optional page navigation."""
    st.subheader("Extracted Text")
    if len(texts) > 1:
        page = st.number_input("Page", min_value=1, max_value=len(texts), value=1)
        st.text_area("Text", value=texts[page - 1], height=200)
    else:
        st.text_area("Text", value=texts[0], height=200)


def show_invoice_table(fields: dict) -> None:
    """Display quick-parsed invoice fields as a static table."""
    st.subheader("Detected Invoice Fields")
    st.table([fields])


def show_download_buttons(fields: dict) -> None:
    """Render CSV and JSON download buttons for the given fields dict."""
    csv_data = to_csv(fields)
    json_data = json.dumps(fields, indent=2)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download as CSV", csv_data, file_name="invoice.csv", mime="text/csv"
        )
    with col2:
        st.download_button(
            "Download as JSON", json_data, file_name="invoice.json", mime="application/json"
        )


def _warn_if_line_items_incomplete(df: pd.DataFrame) -> None:
    """Show a warning if the expected line-item columns are mostly empty."""
    present = [c for c in _LINE_ITEM_COLS if c in df.columns]
    if not present:
        return
    subset = df[present]
    if (subset.isnull() | (subset == "")).all(axis=None):
        st.warning(
            "Most line items are missing 'quantity', 'unit_price', or 'total'. "
            "The extraction model may not be parsing these fields correctly. "
            "Check your prompt or invoice format."
        )


def _build_line_item_rows(invoice: dict) -> list[dict]:
    """Expand a single invoice dict into one row per line item."""
    base = {k: v for k, v in invoice.items() if k != "line_items"}
    line_items = invoice.get("line_items", [])
    if line_items:
        rows = []
        for item in line_items:
            row = base.copy()
            for k, v in item.items():
                row[f"line_{k}"] = v
            rows.append(row)
        return rows
    return [base]


def show_json_table(json_data) -> None:
    """
    Display Gemini-parsed invoice JSON as interactive tables.

    Handles both a single invoice dict and a list of invoice dicts.
    Line items are expanded into individual rows. Invoice-level fields
    are shown separately.
    """
    invoices: list[dict] = json_data if isinstance(json_data, list) else [json_data]

    # The "Line Items Only" prompt returns an array of items, not invoices.
    # Present that shape directly instead of treating each item as an invoice.
    if isinstance(json_data, list) and json_data and all(
        isinstance(item, dict) and "line_items" not in item
        and any(key in item for key in ("description", "quantity", "unit_price", "total"))
        for item in json_data
    ):
        st.markdown(
            "<div style='font-size:1.5rem;font-weight:700;color:#2d6cdf;"
            "margin-bottom:0.5em;'>Line Items</div>",
            unsafe_allow_html=True,
        )
        show_itable(pd.DataFrame(json_data), maxBytes=0)
        return

    # --- Line items table ---
    all_rows: list[dict] = []
    for invoice in invoices:
        all_rows.extend(_build_line_item_rows(invoice))

    has_line_items = any("line_items" in inv for inv in invoices)
    if has_line_items:
        st.markdown(
            "<div style='font-size:1.5rem;font-weight:700;color:#2d6cdf;"
            "margin-bottom:0.5em;'>Line Items</div>",
            unsafe_allow_html=True,
        )
        line_df = pd.DataFrame(all_rows)
        _warn_if_line_items_incomplete(line_df)
        show_itable(line_df, maxBytes=0, lengthMenu=[[10, 25, 50, 100, -1], [10, 25, 50, 100, "All"]])

    # --- Invoice fields table ---
    st.markdown(
        "<div style='font-size:1.3rem;font-weight:600;color:#2d6cdf;"
        "margin-bottom:0.3em;'>Invoice Fields</div>",
        unsafe_allow_html=True,
    )
    field_rows = []
    for invoice in invoices:
        data = {k: v for k, v in invoice.items() if k != "line_items"}
        field_rows.append(flatten_json(data))
    show_itable(pd.DataFrame(field_rows), maxBytes=0)


def build_gemini_csv(processed_json) -> str:
    """Build a flat CSV from a Gemini-parsed invoice JSON (dict or list)."""
    invoices = processed_json if isinstance(processed_json, list) else [processed_json]
    rows: list[dict] = []
    for invoice in invoices:
        rows.extend(_build_line_item_rows(invoice))
    return pd.DataFrame(rows).to_csv(index=False)


def extract_json_from_response(response_text: str) -> str:
    """
    Extract the first JSON object or array from a raw AI response string.

    Strips markdown code fences and any surrounding prose.
    """
    cleaned = re.sub(r"^\s*```(?:json)?\s*", "", response_text.strip(), flags=re.I)
    cleaned = re.sub(r"\s*```\s*$", "", cleaned)

    # A greedy regex breaks when prose contains braces or the response has more
    # than one JSON-looking fragment. The decoder reliably finds the first
    # complete JSON value instead.
    decoder = json.JSONDecoder()
    for match in re.finditer(r"[\[{]", cleaned):
        try:
            value, _ = decoder.raw_decode(cleaned[match.start() :])
        except json.JSONDecodeError:
            continue
        return json.dumps(value)
    return cleaned
