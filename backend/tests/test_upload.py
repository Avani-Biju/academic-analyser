import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app

client = TestClient(app)

# Resolve directories relative to this test file
BASE_DIR = Path(__file__).resolve().parent.parent
TEST_VALID_PDF = BASE_DIR / "app" / "uploads" / "Project_Overview.pdf"
TEST_INVALID_PDF = BASE_DIR / "dummy.pdf"
EXTRACTED_DIR = BASE_DIR / "app" / "extracted"

def test_upload_valid_pdf():
    # Verify the valid PDF exists
    assert TEST_VALID_PDF.exists(), f"Test PDF not found at {TEST_VALID_PDF}"

    with open(TEST_VALID_PDF, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("Project_Overview.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "Project_Overview.pdf"
    assert data["pages"] == 13
    assert data["text_length"] > 0
    assert data["message"] == "Text extracted and parsed successfully"

    # Verify that the extracted .txt file was created
    extracted_file = EXTRACTED_DIR / "Project_Overview.txt"
    assert extracted_file.exists()
    
    # Read text to ensure it has content
    with open(extracted_file, "r", encoding="utf-8") as f:
        extracted_text = f.read()
    assert len(extracted_text) == data["text_length"]

    # Clean up the extracted text file
    if extracted_file.exists():
        extracted_file.unlink()

def test_upload_invalid_pdf():
    # Verify invalid PDF file exists
    assert TEST_INVALID_PDF.exists(), f"Dummy PDF not found at {TEST_INVALID_PDF}"

    with open(TEST_INVALID_PDF, "rb") as f:
        response = client.post(
            "/upload",
            files={"file": ("dummy.pdf", f, "application/pdf")}
        )

    assert response.status_code == 400
    data = response.json()
    assert "Failed to parse PDF" in data["detail"]

def test_upload_non_pdf_file():
    # Try uploading a plain text file or non-PDF file
    response = client.post(
        "/upload",
        files={"file": ("test.txt", b"This is some plain text content.", "text/plain")}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Uploaded file is not a PDF"
