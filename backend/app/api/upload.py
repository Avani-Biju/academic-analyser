from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import shutil
import logging
from pathlib import Path
from app.services.pdf_service import extract_text_from_pdf
from app.services.parser_service import parse_document

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

router = APIRouter()

# Use absolute paths relative to this file to ensure robustness
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

EXTRACTED_DIR = BASE_DIR / "extracted"
EXTRACTED_DIR.mkdir(exist_ok=True)

# Enum creates the dropdown in Swagger UI and handles validation automatically
class DocumentType(str, Enum):
    syllabus = "syllabus"
    question_paper = "question_paper"

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(...)
):
    # Validate file extension
    if not file.filename.lower().endswith('.pdf'):
        raise HTTPException(status_code=400, detail="Uploaded file is not a PDF")

    file_path = UPLOAD_DIR / file.filename

    logger.info(f"Received upload: {file.filename}, Document Type: {doc_type.value}")

    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save uploaded file: {str(e)}")

    try:
        # Extract text from the saved PDF
        extraction_result = extract_text_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    try:
        # Save the extracted text inside app/extracted/ with a .txt extension
        extracted_file_path = EXTRACTED_DIR / Path(file.filename).with_suffix(".txt")
        with open(extracted_file_path, "w", encoding="utf-8") as f:
            f.write(extraction_result["text"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save extracted text: {str(e)}")

    try:
        # Route the text to the correct parser based on the explicit doc_type form field
        parsed_data = parse_document(extraction_result["text"], file.filename, doc_type.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse {doc_type.value}: {str(e)}")

    return {
        "filename": file.filename,
        "pages": extraction_result["pages"],
        "text_length": extraction_result["text_length"],
        "message": f"Text extracted and parsed as {doc_type.value} successfully",
        "parsed_data": parsed_data
    }
