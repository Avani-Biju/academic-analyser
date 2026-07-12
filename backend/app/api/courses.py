from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import crud, schemas
from app.database.database import get_db

router = APIRouter(prefix="/courses", tags=["courses"])

@router.get("", response_model=list[schemas.Course])
def list_courses(db: Session = Depends(get_db)):
    """List all available courses."""
    return crud.get_all_courses(db)

@router.get("/{course_id}", response_model=schemas.Course)
def get_course(course_id: int, db: Session = Depends(get_db)):
    """Get details of a specific course."""
    course = crud.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course

@router.patch("/{course_id}", response_model=schemas.Course)
def update_course(course_id: int, payload: schemas.CourseUpdate, db: Session = Depends(get_db)):
    """Update course metadata after syllabus review."""
    course = crud.get_course_by_id(db, course_id=course_id)
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    updated_fields = payload.model_dump(exclude_unset=True)
    if not updated_fields:
        return course

    next_code = updated_fields.get("course_code")
    if next_code and next_code != course.course_code:
        existing_course = crud.get_course_by_code(db, next_code)
        if existing_course and existing_course.id != course_id:
            raise HTTPException(status_code=400, detail="A course with this code already exists")

    return crud.update_course(db, course, updated_fields)

@router.get("/{course_id}/syllabus", response_model=schemas.Syllabus)
def get_course_syllabus(course_id: int, db: Session = Depends(get_db)):
    """Get the syllabus for a specific course."""
    syllabus = crud.get_syllabus_by_course(db, course_id=course_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found for this course")
    return syllabus

@router.patch("/{course_id}/syllabus", response_model=schemas.Syllabus)
def update_course_syllabus(course_id: int, payload: schemas.SyllabusUpdate, db: Session = Depends(get_db)):
    """Persist reviewed syllabus JSON for a course."""
    syllabus = crud.get_syllabus_by_course(db, course_id=course_id)
    if not syllabus:
        raise HTTPException(status_code=404, detail="Syllabus not found for this course")

    updated_fields = payload.model_dump(exclude_unset=True)
    return crud.update_syllabus_record(db, syllabus, updated_fields)

@router.get("/{course_id}/question-papers", response_model=list[schemas.QuestionPaper])
def get_course_question_papers(course_id: int, db: Session = Depends(get_db)):
    """Get all question papers for a specific course."""
    papers = crud.get_question_papers_by_course(db, course_id=course_id)
    return papers

@router.get("/{course_id}/matches", response_model=list[schemas.MatchResult])
def get_course_matches(course_id: int, db: Session = Depends(get_db)):
    """Get all match results for a specific course."""
    matches = crud.get_match_results_by_course(db, course_id=course_id)
    return matches
