"""
Google Gemini AI client integration using the google-genai SDK.
"""

import os
import logging

import streamlit as st
from dotenv import load_dotenv
from google import genai

logger = logging.getLogger(__name__)


def load_api_key() -> str | None:
    """Load the Google API key from environment variables or .env file."""
    load_dotenv()
    return os.getenv("GOOGLE_API_KEY")


@st.cache_resource
def get_gemini_client(api_key: str) -> genai.Client:
    """Create and cache a Gemini AI client for the lifetime of the app."""
    return genai.Client(api_key=api_key)


def get_gemini_response(api_key: str, input_text: str, prompt: str) -> str:
    """
    Send the extracted invoice text and prompt to Gemini and return the response.

    Returns the model's text response, or an error message string on failure.
    """
    client = get_gemini_client(api_key)
    contents = f"{prompt}\n\n{input_text}" if input_text else prompt
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=contents,
        )
        return response.text
    except Exception as exc:
        logger.error("Gemini API error: %s", exc)
        raise
