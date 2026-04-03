"""
AI Invoice Extractor — main Streamlit entrypoint.

All business logic lives in the src/ package:
  src/config.py       - constants & prompt templates
  src/extractors.py   - PDF/image text extraction
  src/ai_client.py    - Google Gemini integration
  src/ui.py           - Streamlit UI components
"""

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

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Invoice Extractor",
    page_icon="🧾",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
<style>
.big-title {
    font-size: 2.5rem;
    font-weight: 700;
    color: #2d6cdf;
    margin-bottom: 0.2em;
}
.subtext {
    font-size: 1.1rem;
    color: #444;
    margin-bottom: 1.5em;
}
.stButton>button {
    background-color: #2d6cdf;
    color: white;
    font-weight: 600;
    border-radius: 6px;
    padding: 0.5em 1.5em;
    margin-top: 0.5em;
}
.stDownloadButton>button {
    background-color: #e0e7ff;
    color: #2d6cdf;
    font-weight: 600;
    border-radius: 6px;
    margin-right: 0.5em;
}
.stTable, .stDataFrame, .itables-container {
    background: #f8fafc;
    border-radius: 8px;
    padding: 1em;
    margin-bottom: 1.5em;
}
</style>
<div class="big-title">🧾 AI Invoice Extractor</div>
<div class="subtext">
  Extract invoice data from PDFs and images using AI.
  Enjoy interactive tables and easy downloads!
</div>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown(
        """
<div style='font-size:1.2rem;font-weight:600;color:#2d6cdf;'>Quick Start</div>
<ol style='margin-top:0.5em;'>
  <li>Upload an invoice (PDF or image).</li>
  <li>Select the extraction prompt.</li>
  <li>Click <b>Analyze Invoice</b>.</li>
</ol>
<hr style='margin:0.7em 0;'>
<div style='color:#444;'>
<b>About:</b> This app uses Google Gemini AI to extract invoice data and display it
in interactive tables. Download your results as CSV or JSON.
</div>
""",
        unsafe_allow_html=True,
    )

prompt_type, uploaded_file = sidebar_settings()
input_prompt = PROMPT_TEMPLATES[prompt_type]
api_key = load_api_key()

# ---------------------------------------------------------------------------
# File upload & OCR extraction
# ---------------------------------------------------------------------------
if uploaded_file:
    if uploaded_file.type not in SUPPORTED_TYPES:
        st.error("Unsupported file type. Please upload a PDF or image (JPG, PNG).")
        st.stop()

    if uploaded_file.size > MAX_FILE_SIZE_MB * 1024 * 1024:
        st.error(
            f"File too large! Max size is {MAX_FILE_SIZE_MB} MB. Please upload a smaller file."
        )
        st.stop()

    file_type = uploaded_file.type
    st.info(f"Detected file type: {SUPPORTED_TYPES.get(file_type, 'Unknown')}")

    with st.spinner("Extracting text from your invoice. Please wait..."):
        try:
            file_bytes = uploaded_file.read()
            if file_type == "application/pdf":
                texts = extract_text_from_pdf(file_bytes)
            else:
                texts = extract_text_from_image(file_bytes)
        except Exception as exc:
            st.error(
                "Sorry, we couldn't extract text from your file. "
                f"Please check the file format or try another file.\nError: {exc}"
            )
            st.stop()

    if not texts or all(not t.strip() for t in texts):
        st.warning(
            "No text could be extracted from your file. "
            "Please check the file quality or try another document."
        )
        st.stop()

    show_extracted_text(texts)
    fields = parse_invoice_fields(" ".join(texts))
    show_invoice_table(fields)
    show_download_buttons(fields)
    st.session_state["extracted_text"] = " ".join(texts)
    st.session_state["fields"] = fields

# ---------------------------------------------------------------------------
# Gemini AI analysis
# ---------------------------------------------------------------------------
if st.button("Analyze Invoice", disabled=not (uploaded_file and api_key)):
    if not api_key:
        st.error("API key required. Please set your Google API key in the .env file.")
    elif not uploaded_file:
        st.error("Please upload an invoice file to analyze.")
    else:
        with st.spinner("Analyzing your invoice with Gemini AI. This may take a few seconds..."):
            try:
                response = get_gemini_response(
                    api_key,
                    st.session_state.get("extracted_text", ""),
                    input_prompt,
                )
            except Exception as exc:
                st.error(
                    "Sorry, there was an error communicating with the AI model. "
                    f"Please try again later.\nError: {exc}"
                )
                st.stop()

        try:
            cleaned_response = extract_json_from_response(response)
            processed_json = json.loads(cleaned_response)
            st.session_state["gemini_result"] = processed_json
            st.session_state.pop("gemini_raw", None)
        except Exception:
            st.session_state["gemini_result"] = None
            st.session_state["gemini_raw"] = response
            st.error(
                "The AI response could not be parsed as valid JSON. "
                "Please check the raw output below or try a different prompt."
            )

# ---------------------------------------------------------------------------
# Display latest Gemini result
# ---------------------------------------------------------------------------
if st.session_state.get("gemini_result") is not None:
    processed_json = st.session_state["gemini_result"]
    show_json_table(processed_json)

    csv_data = build_gemini_csv(processed_json)
    json_data = json.dumps(processed_json, indent=2)
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            "Download as CSV", csv_data, file_name="invoice_gemini.csv", mime="text/csv"
        )
    with col2:
        st.download_button(
            "Download as JSON", json_data, file_name="invoice_gemini.json", mime="application/json"
        )
elif (
    "gemini_result" in st.session_state
    and st.session_state["gemini_result"] is None
    and "gemini_raw" in st.session_state
):
    st.info("Gemini output is not valid JSON. See raw output below for debugging.")
    st.code(st.session_state["gemini_raw"], language="json")

# ---------------------------------------------------------------------------
# Footer
# ---------------------------------------------------------------------------
st.markdown(
    """
<hr style='margin-top:2em;'>
<div style='text-align:center;font-size:1rem;color:#888;'>
  View source or contribute on
  <a href='https://github.com/pratstick/AI-Invoice-Extractor'
     target='_blank' style='color:#2d6cdf;text-decoration:underline;'>GitHub</a>.<br>
  <span style='font-size:0.95rem;color:#aaa;'>
    Powered by <span style='color:#4285F4;font-weight:600;'>Google Gemini</span>
  </span>
</div>
""",
    unsafe_allow_html=True,
)
