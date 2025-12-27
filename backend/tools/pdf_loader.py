# pdf_loader.py

import fitz  # PyMuPDF

def load_pdf_text(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)
