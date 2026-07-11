from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
from typing import Optional, Any, List, Dict
from app.services.matching_service import perform_matching
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

class MatchRequest(BaseModel):
    syllabus_file: Optional[str] = None
    questions_file: Optional[str] = None
    syllabus_data: Optional[Dict[str, Any]] = None
    questions_data: Optional[Dict[str, Any]] = None

@router.post("/match")
async def match_questions(req: MatchRequest):
    return perform_matching(
        syllabus_data=req.syllabus_data,
        questions_data=req.questions_data,
        syllabus_file=req.syllabus_file,
        questions_file=req.questions_file
    )
