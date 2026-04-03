"""
Application configuration: constants, supported file types, and prompt templates.
"""

MAX_FILE_SIZE_MB = 10

SUPPORTED_TYPES: dict[str, str] = {
    "application/pdf": "PDF",
    "image/jpeg": "Image",
    "image/png": "Image",
    "image/jpg": "Image",
}

PROMPT_TEMPLATES: dict[str, str] = {
    "General Invoice": """
You are an expert invoice extraction assistant. Analyze the provided invoice (image or PDF) and extract the following fields. Output ONLY a valid JSON object, with no extra text, comments, explanations, markdown, or code blocks. Do NOT mention the word 'json' anywhere. The JSON should have the following structure:

{
  "total_amount": "",
  "invoice_number": "",
  "invoice_date": "",
  "vendor": {
    "name": "",
    "address": "",
    "contact": ""
  },
  "customer": {
    "name": "",
    "address": "",
    "contact": ""
  },
  "line_items": [
    {
      "description": "",
      "quantity": "",
      "unit_price": "",
      "total": ""
    }
  ],
  "payment_terms": "",
  "due_date": ""
}

For each line item, ensure that the fields 'description', 'quantity', 'unit_price', and 'total' are extracted as separate values. Do NOT combine multiple details (such as color, country, etc.) into the description field. If any of these fields are missing or not present in the invoice, use an empty string for that field. Do not add explanations. Do not include any text before or after the JSON. Do not use markdown or code blocks. Only output the JSON object, nothing else. Any deviation will break the downstream system.
""",
    "Minimal": """
Extract the following fields from this invoice and return ONLY a valid JSON object (no extra text, markdown, explanations, or code blocks). Do NOT mention the word 'json' anywhere:
{
  "total_amount": "",
  "invoice_number": "",
  "invoice_date": "",
  "vendor": ""
}
If a field is missing, leave it blank. Do not include any text before or after the JSON. Do not use markdown or code blocks. Only output the JSON object, nothing else. Any deviation will break the downstream system.
""",
    "Line Items Only": """
List all line items from this invoice in a JSON array. Output ONLY the JSON array, with no extra text, markdown, explanations, or code blocks. Do NOT mention the word 'json' anywhere. Each item should include:
{
  "description": "",
  "quantity": "",
  "unit_price": "",
  "total": ""
}
For each line item, ensure that the fields 'description', 'quantity', 'unit_price', and 'total' are extracted as separate values. Do NOT combine multiple details (such as color, country, etc.) into the description field. If any of these fields are missing or not present in the invoice, use an empty string for that field. Return only the JSON array. If no line items are found, return an empty array. Do not include any text before or after the JSON. Do not use markdown or code blocks. Only output the JSON array, nothing else. Any deviation will break the downstream system.
""",
}
