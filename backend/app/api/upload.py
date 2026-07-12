from enum import Enum
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends
import shutil
import logging
from pathlib import Path
from sqlalchemy.orm import Session

from app.services.pdf_service import extract_text_from_pdf
from app.services.parser_service import parse_document
from app.database import crud, schemas, models
from app.database.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
UPLOAD_DIR.mkdir(exist_ok=True)

EXTRACTED_DIR = BASE_DIR / "extracted"
EXTRACTED_DIR.mkdir(exist_ok=True)

class DocumentType(str, Enum):
    syllabus = "syllabus"
    question_paper = "question_paper"

@router.post("/upload")
async def upload_pdf(
    file: UploadFile = File(...),
    doc_type: DocumentType = Form(...),
    db: Session = Depends(get_db)
):
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
        extraction_result = extract_text_from_pdf(file_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to parse PDF: {str(e)}")

    try:
        extracted_file_path = EXTRACTED_DIR / Path(file.filename).with_suffix(".txt")
        with open(extracted_file_path, "w", encoding="utf-8") as f:
            f.write(extraction_result["text"])
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save extracted text: {str(e)}")

    try:
        parsed_data = parse_document(extraction_result["text"], file.filename, doc_type.value)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse {doc_type.value}: {str(e)}")

    course_code = parsed_data.get("course_code")
    if not course_code:
        raise HTTPException(status_code=400, detail="Failed to extract course code from document")

    # DB Logic
    db_course = crud.get_course_by_code(db, course_code)

    if doc_type == DocumentType.syllabus:
        # Create or update course
        if not db_course:
            course_schema = schemas.CourseCreate(
                course_code=str(course_code),
                course_name=str(parsed_data.get("course_name") or "") or None,
                semester=str(parsed_data.get("semester") or "") or None,
                scheme=str(parsed_data.get("scheme") or "") or None,
                credits=str(parsed_data.get("credits") or "") or None,
            )
            db_course = crud.create_course(db, course_schema)
        else:
            # Update missing fields if possible, cast to str defensively
            crud.update_course(db, db_course, {
                "course_name": str(parsed_data.get("course_name") or "") or db_course.course_name,
                "semester": str(parsed_data.get("semester") or "") or db_course.semester,
                "scheme": str(parsed_data.get("scheme") or "") or db_course.scheme,
                "credits": str(parsed_data.get("credits") or "") or db_course.credits,
            })
            
        # Check if syllabus already exists
        existing_syllabus = crud.get_syllabus_by_course(db, db_course.id)
        if existing_syllabus:
            crud.update_syllabus(db, existing_syllabus, parsed_data)
        else:
            syllabus_schema = schemas.SyllabusCreate(
                course_id=db_course.id,
                source_file=file.filename,
                json_data=parsed_data
            )
            crud.create_syllabus(db, syllabus_schema)
            
    elif doc_type == DocumentType.question_paper:
        # Require existing syllabus
        if not db_course:
            raise HTTPException(status_code=400, detail="No syllabus found for this course. Please upload the syllabus before uploading question papers.")
            
        existing_syllabus = crud.get_syllabus_by_course(db, db_course.id)
        if not existing_syllabus:
            raise HTTPException(status_code=400, detail="No syllabus found for this course. Please upload the syllabus before uploading question papers.")
            
        # Create question paper
        qp_schema = schemas.QuestionPaperCreate(
            course_id=db_course.id,
            exam=str(parsed_data.get("exam") or "") or None,
            month=str(parsed_data.get("month") or "") or None,
            year=str(parsed_data.get("year") or "") or None,
            duration=str(parsed_data.get("duration") or "") or None,
            maximum_marks=str(parsed_data.get("maximum_marks") or "") or None,
            source_file=file.filename,
            json_data=parsed_data
        )
        crud.create_question_paper(db, qp_schema)

    return {
        "filename": file.filename,
        "message": f"Text extracted, parsed, and saved as {doc_type.value} successfully",
        "course_code": course_code,
        "course_id": db_course.id if db_course else None,
        "syllabus_id": existing_syllabus.id if doc_type == DocumentType.syllabus and existing_syllabus else (
            crud.get_syllabus_by_course(db, db_course.id).id if doc_type == DocumentType.syllabus and db_course else None
        ),
        "parsed_data": parsed_data
    }
