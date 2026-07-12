from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Any, Dict
from sqlalchemy.orm import Session
from app.services.matching_service import perform_matching
from app.database import crud, schemas, models
from app.database.database import get_db
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class MatchRequest(BaseModel):
    syllabus_id: Optional[int] = None
    question_paper_id: Optional[int] = None
    
    # Fallback/Legacy for raw passing
    syllabus_file: Optional[str] = None
    questions_file: Optional[str] = None
    syllabus_data: Optional[Dict[str, Any]] = None
    questions_data: Optional[Dict[str, Any]] = None

@router.post("/match")
async def match_questions(req: MatchRequest, db: Session = Depends(get_db)):
    syllabus_json = req.syllabus_data
    qp_json = req.questions_data
    
    db_syllabus = None
    db_qp = None

    if req.syllabus_id:
        db_syllabus = db.query(models.Syllabus).filter(models.Syllabus.id == req.syllabus_id).first()
        if not db_syllabus:
            raise HTTPException(404, "Syllabus not found")
        syllabus_json = db_syllabus.json_data

    if req.question_paper_id:
        db_qp = db.query(models.QuestionPaper).filter(models.QuestionPaper.id == req.question_paper_id).first()
        if not db_qp:
            raise HTTPException(404, "Question paper not found")
        qp_json = db_qp.json_data

    # Perform matching
    result = perform_matching(
        syllabus_data=syllabus_json,
        questions_data=qp_json,
        syllabus_file=req.syllabus_file if not db_syllabus else None,
        questions_file=req.questions_file if not db_qp else None
    )

    # If this match was based on database objects, save the result
    if db_syllabus and db_qp:
        match_schema = schemas.MatchResultCreate(
            syllabus_id=db_syllabus.id,
            question_paper_id=db_qp.id,
            result_json=result
        )
        crud.create_match_result(db, match_schema)
        
    return result
