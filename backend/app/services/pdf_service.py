import fitz  # PyMuPDF
from pathlib import Path

def extract_text_from_pdf(file_path: Path) -> dict:
    """
    Extracts all text page-by-page from a PDF file.
    Returns:
        dict: {
            "text": str (all extracted text joined by newlines),
            "pages": int (total page count),
            "text_length": int (total character length)
        }
    """
    doc = fitz.open(file_path)
    text_content = []
    
    for page in doc:
        text_content.append(page.get_text())
        
    full_text = "\n".join(text_content)
    
    return {
        "text": full_text,
        "pages": len(doc),
        "text_length": len(full_text)
    }
