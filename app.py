from dotenv import load_dotenv
import os
from PIL import Image
import streamlit as st
import google.generativeai as genai
import fitz  # PyMuPDF
import pytesseract  # OCR library for text extraction from images
import io

# Load environment variables
load_dotenv()
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the API
genai.configure(api_key=api_key)
model = genai.GenerativeModel('gemini-1.5-flash')

def extract_text_from_pdf(pdf_file):
    """Extract text from a PDF file."""
    try:
        pdf_document = fitz.open(stream=pdf_file.read(), filetype="pdf")
        text = ""
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
        if not text.strip():
            return "The PDF contains no extractable text."
        return text
    except Exception as e:
        return f"An error occurred while extracting text from PDF: {str(e)}"

def extract_text_from_image(image_file):
    """Extract text from an image file using OCR."""
    try:
        image = Image.open(image_file)
        text = pytesseract.image_to_string(image)
        if not text.strip():
            return "The image contains no extractable text."
        return text
    except Exception as e:
        return f"An error occurred while extracting text from image: {str(e)}"

def get_gemini_response(input_text, prompt):
    try:
        # Construct the parts list
        parts = []
        
        if prompt:
            parts.append({"text": prompt})
        if input_text:
            parts.append({"text": input_text})

        # API expects a dictionary with a "parts" key
        response = model.generate_content({"parts": parts})
        return response.text
    except Exception as e:
        return f"An error occurred: {str(e)}"

# Initialize Streamlit app
st.set_page_config(page_title="AI Invoice Extractor")

st.header("AI Invoice Extractor")

# Revised prompt
input_prompt = """
You are an expert in analyzing invoices. Please analyze the uploaded invoice (image or PDF) and provide answers to the following questions:

1. What is the total amount due on this invoice?
2. What is the invoice number and the date of issuance?
3. Who is the issuing company, and what are their contact details?
4. What are the details of the items or services billed, including quantities and unit prices?
5. Are there any payment terms or due dates mentioned?

Respond clearly and directly to each question. If any information is not present or cannot be determined, please state so.
"""

input_text = st.text_input("Input Prompt:", key="input", value="Please analyze the provided invoice.")
uploaded_file = st.file_uploader("Choose an image or PDF of the invoice....", type=["jpg", "jpeg", "png", "pdf"])

if uploaded_file:
    if uploaded_file.type == "application/pdf":
        # Extract text from PDF
        text_from_pdf = extract_text_from_pdf(uploaded_file)
        st.text_area("Extracted Text from PDF:", value=text_from_pdf, height=300)
    else:
        # Extract text from image
        text_from_image = extract_text_from_image(uploaded_file)
        st.text_area("Extracted Text from Image:", value=text_from_image, height=300)

if st.button("Tell me about my invoice"):
    if uploaded_file and input_text:
        if uploaded_file.type == "application/pdf":
            # Send the extracted text from PDF
            response = get_gemini_response(text_from_pdf, input_prompt)
        else:
            # Send the extracted text from image
            response = get_gemini_response(text_from_image, input_prompt)
        st.subheader("The response is: ")
        st.write(response)
    else:
        st.error("Please upload an image or PDF and provide an input prompt.")
