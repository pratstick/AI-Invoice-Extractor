"""Streamlit entrypoint for AI Invoice Extractor."""

import hashlib
import json

import streamlit as st

from src.ai_client import get_gemini_response, load_api_key
from src.config import MAX_FILE_SIZE_MB, PROMPT_TEMPLATES, SUPPORTED_TYPES
from src.extractors import extract_text_from_image, extract_text_from_pdf, parse_invoice_fields
from src.ui import (
    build_gemini_csv,
    extract_json_from_response,
    show_download_buttons,
    show_extracted_text,
    show_invoice_table,
    show_json_table,
    sidebar_settings,
)

st.set_page_config(page_title="Invoice Lens", page_icon="🧾", layout="wide")

st.markdown(
    """
    <style>
      .block-container { max-width: 1200px; padding-top: 2.5rem; padding-bottom: 3rem; }
      [data-testid="stMetric"] { background: #f6f8fc; border: 1px solid #e6eaf2;
        border-radius: 12px; padding: .8rem 1rem; }
      [data-testid="stDownloadButton"] button { width: 100%; }
      .hero { font-size: 2.65rem; font-weight: 750; letter-spacing: -.045em; margin: 0; }
      .eyebrow { color: #52647a; font-size: 1.05rem; margin: .35rem 0 1.75rem; }
    </style>
    <p class="hero">Invoice Lens <span style="font-size:1.8rem">🧾</span></p>
    <p class="eyebrow">Turn PDFs and scans into structured, exportable invoice data.</p>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Extraction settings")
    st.caption("Your document is processed only when you choose to analyze it.")

prompt_type, uploaded_file = sidebar_settings()
api_key = load_api_key()
input_prompt = PROMPT_TEMPLATES[prompt_type]

if not api_key:
    st.sidebar.warning("Add `GOOGLE_API_KEY` to `.env` to enable AI extraction.")


def reset_results_for(file_id: str) -> None:
    """Discard results belonging to a previously uploaded file."""
    if st.session_state.get("file_id") != file_id:
        for key in ("extracted_text", "extracted_pages", "fields", "gemini_result", "gemini_raw"):
            st.session_state.pop(key, None)
        st.session_state["file_id"] = file_id


if not uploaded_file:
    st.info("Upload an invoice from the sidebar to begin. PDFs, JPG, and PNG files are supported.")
    st.stop()

if uploaded_file.type not in SUPPORTED_TYPES:
    st.error("Unsupported file type. Please upload a PDF, JPG, or PNG invoice.")
    st.stop()
if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
    st.error(f"This file is over the {MAX_FILE_SIZE_MB} MB limit. Please choose a smaller file.")
    st.stop()

file_bytes = uploaded_file.getvalue()
file_id = hashlib.sha256(file_bytes).hexdigest()
reset_results_for(file_id)

top_left, top_right = st.columns([3, 1])
with top_left:
    st.subheader(uploaded_file.name, divider="gray")
    st.caption(f"{SUPPORTED_TYPES[uploaded_file.type]} · {uploaded_file.size / 1024 / 1024:.2f} MB")
with top_right:
    analyze_clicked = st.button(
        "Analyze with Gemini", type="primary", use_container_width=True, disabled=not api_key
    )

if "extracted_text" not in st.session_state:
    with st.status("Reading document", expanded=False) as status:
        try:
            texts = (
                extract_text_from_pdf(file_bytes)
                if uploaded_file.type == "application/pdf"
                else extract_text_from_image(file_bytes)
            )
        except Exception as exc:
            status.update(label="Could not read document", state="error")
            st.error(f"We couldn't extract text from this file. Check the format and try again.\n\n{exc}")
            st.stop()
        extracted_text = "\n".join(texts).strip()
        if not extracted_text:
            status.update(label="No readable text found", state="error")
            st.warning("No text was found. Try a higher-quality scan or a text-based PDF.")
            st.stop()
        status.update(label="Document ready", state="complete", expanded=False)
    st.session_state["extracted_text"] = extracted_text
    st.session_state["extracted_pages"] = texts
    st.session_state["fields"] = parse_invoice_fields(extracted_text)

fields = st.session_state["fields"]
metrics = st.columns(3)
metrics[0].metric("Pages / images", len(extract_text_from_pdf(file_bytes)) if uploaded_file.type == "application/pdf" else 1)
metrics[1].metric("Invoice number", fields["Invoice Number"].replace("Invoice", "").strip() or "Not detected")
metrics[2].metric("Total", fields["Total Amount"].replace("Total", "").strip(" :-") or "Not detected")

preview_tab, ai_tab = st.tabs(["Document preview", "AI extraction"])
with preview_tab:
    show_extracted_text(st.session_state.get("extracted_pages", [st.session_state["extracted_text"]]))
    show_invoice_table(fields)
    show_download_buttons(fields)

if analyze_clicked:
    with st.spinner("Gemini is structuring your invoice…"):
        try:
            response = get_gemini_response(api_key, st.session_state["extracted_text"], input_prompt)
            st.session_state["gemini_result"] = json.loads(extract_json_from_response(response))
            st.session_state.pop("gemini_raw", None)
        except json.JSONDecodeError:
            st.session_state["gemini_result"] = None
            st.session_state["gemini_raw"] = response
        except Exception as exc:
            st.error(f"Gemini could not analyze this invoice. Please try again.\n\n{exc}")

with ai_tab:
    if st.session_state.get("gemini_result") is not None:
        result = st.session_state["gemini_result"]
        show_json_table(result)
        csv_data = build_gemini_csv(result)
        json_data = json.dumps(result, indent=2, ensure_ascii=False)
        col1, col2 = st.columns(2)
        col1.download_button("Download AI CSV", csv_data, "invoice_ai.csv", "text/csv", use_container_width=True)
        col2.download_button("Download AI JSON", json_data, "invoice_ai.json", "application/json", use_container_width=True)
    elif "gemini_raw" in st.session_state:
        st.warning("The model returned an unexpected format. Raw response is available below.")
        st.code(st.session_state["gemini_raw"], language="json")
    else:
        st.info("Choose “Analyze with Gemini” to extract line items and detailed invoice fields.")

st.caption("AI results can be inaccurate—confirm totals and payment details before using them operationally.")
