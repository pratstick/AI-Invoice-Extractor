# AI Invoice Extractor

A production-grade Streamlit web application that extracts structured data from invoice PDFs and images using Google Gemini AI and Tesseract OCR.

## Features

- **AI-Powered Extraction** — Uses Google Gemini 2.0 Flash (vision-capable) to parse invoice fields and line items into structured JSON.
- **OCR Preview** — Tesseract OCR extracts raw text from images and PDFs for a quick preview before AI analysis.
- **Multiple Prompt Templates** — Choose between General Invoice, Minimal, or Line Items Only extraction modes.
- **Interactive Tables** — Results are displayed in sortable, paginated tables powered by itables.
- **Export** — Download extracted data as CSV or JSON with a single click.
- **Robust Error Handling** — Friendly messages for API errors, malformed AI responses, unsupported files, and oversized uploads.

## Tech Stack

| Layer | Technology |
|---|---|
| UI | [Streamlit](https://streamlit.io) |
| AI | [Google Gemini 2.0 Flash](https://ai.google.dev) via `google-genai` SDK |
| OCR | [Tesseract](https://github.com/tesseract-ocr/tesseract) + [pytesseract](https://github.com/madmaze/pytesseract) |
| PDF parsing | [PyMuPDF (fitz)](https://pymupdf.readthedocs.io) |
| Tables | [itables](https://mwouts.github.io/itables) + [pandas](https://pandas.pydata.org) |

## Architecture

```
AI-Invoice-Extractor/
├── app.py                  # Thin Streamlit entrypoint
├── src/
│   ├── config.py           # Constants and prompt templates
│   ├── extractors.py       # PDF/image OCR text extraction
│   ├── ai_client.py        # Google Gemini client (cached)
│   └── ui.py               # Reusable Streamlit UI components
├── tests/
│   ├── test_extractors.py  # Unit tests for extractors & utilities
│   └── test_ui.py          # Unit tests for UI helpers
├── .env.example            # Environment variable template
├── packages.txt            # System-level apt packages (for Streamlit Cloud)
└── requirements.txt        # Python dependencies
```

## Setup

### Prerequisites

- Python 3.10+
- Tesseract OCR engine
- A [Google AI Studio API key](https://aistudio.google.com/app/apikey)

### Install Tesseract

| Platform | Command |
|---|---|
| Debian/Ubuntu | `sudo apt-get install tesseract-ocr` |
| macOS | `brew install tesseract` |
| Windows | [Download installer](https://github.com/tesseract-ocr/tesseract/releases) |

### Install & Run

```bash
# 1. Clone the repo
git clone https://github.com/pratstick/AI-Invoice-Extractor.git
cd AI-Invoice-Extractor

# 2. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your_key_here

# 5. Run the app
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501) in your browser.

## Usage

1. **Upload** a PDF or image (JPG/PNG) invoice using the sidebar.
2. **Select** an extraction prompt template.
3. **Click** "Analyze Invoice" to run Gemini AI extraction.
4. **Review** the interactive tables and download results as CSV or JSON.

## Environment Variables

| Variable | Description |
|---|---|
| `GOOGLE_API_KEY` | Your Google AI Studio API key |

## Testing

```bash
pytest tests/ -v
```

## Deployment

### Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io) → "New app".
3. Point it at `app.py`.
4. Add `GOOGLE_API_KEY` under **Settings → Secrets**.
5. Click **Deploy** — `packages.txt` ensures Tesseract is installed automatically.

### Docker

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y tesseract-ocr && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
docker build -t ai-invoice-extractor .
docker run -e GOOGLE_API_KEY=your_key -p 8501:8501 ai-invoice-extractor
```

## Contributing

Contributions are welcome! Fork the repository and submit a pull request. Ensure new code is tested and documented.

## License

MIT — see [LICENSE](LICENSE).
