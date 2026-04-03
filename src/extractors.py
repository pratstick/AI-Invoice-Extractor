"""
Text extraction utilities for PDF and image invoice files.
"""

import io
import re
import csv

import fitz  # PyMuPDF
import pytesseract
import streamlit as st
from PIL import Image


@st.cache_data(show_spinner=False)
def extract_text_from_pdf(pdf_bytes: bytes, max_pages: int = 10) -> list[str]:
    """Extract text from a PDF file using PyMuPDF."""
    pdf_document = fitz.open(stream=pdf_bytes, filetype="pdf")
    texts: list[str] = []
    for page_num in range(min(len(pdf_document), max_pages)):
        page = pdf_document.load_page(page_num)
        texts.append(page.get_text())
    return texts


@st.cache_data(show_spinner=False)
def extract_text_from_image(image_bytes: bytes) -> list[str]:
    """Extract text from an image file using Tesseract OCR."""
    image = Image.open(io.BytesIO(image_bytes))
    text = pytesseract.image_to_string(image)
    return [text]


def parse_invoice_fields(text: str) -> dict[str, str]:
    """Parse basic invoice fields from text using regex (for quick preview)."""
    fields = {
        "Total Amount": re.search(r"(Total\s*[:\-]?\s*\$?\s*[\d,]+\.\d{2})", text, re.I),
        "Invoice Number": re.search(r"(Invoice\s*#?\s*[:\-]?\s*\w+)", text, re.I),
        "Date": re.search(r"(Date\s*[:\-]?\s*\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})", text, re.I),
        "Vendor": re.search(r"(From\s*[:\-]?\s*.+)", text, re.I),
    }
    return {k: (v.group(1) if v else "") for k, v in fields.items()}


def to_csv(data_dict: dict) -> str:
    """Convert a flat dictionary to a CSV string."""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=data_dict.keys())
    writer.writeheader()
    writer.writerow(data_dict)
    return output.getvalue()


def flatten_json(y, parent_key: str = "", sep: str = ".") -> dict:
    """Recursively flatten a nested JSON object for tabular display."""
    items: list = []
    if isinstance(y, list):
        for i, v in enumerate(y):
            new_key = f"{parent_key}{sep}{i}" if parent_key else str(i)
            items.extend(flatten_json(v, new_key, sep=sep).items())
    elif isinstance(y, dict):
        for k, v in y.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            items.extend(flatten_json(v, new_key, sep=sep).items())
    else:
        items.append((parent_key, y))
    return dict(items)
