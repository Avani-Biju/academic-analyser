from pydantic import BaseModel, ConfigDict
from typing import Optional, Any, List
from datetime import datetime

class CourseBase(BaseModel):
    course_code: str
    course_name: Optional[str] = None
    semester: Optional[str] = None
    scheme: Optional[str] = None
    credits: Optional[str] = None

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    course_code: Optional[str] = None
    course_name: Optional[str] = None
    semester: Optional[str] = None
    scheme: Optional[str] = None
    credits: Optional[str] = None

class Course(CourseBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class SyllabusBase(BaseModel):
    course_id: int
    source_file: str
    json_data: Any

class SyllabusCreate(SyllabusBase):
    pass

class SyllabusUpdate(BaseModel):
    source_file: Optional[str] = None
    json_data: Any

class Syllabus(SyllabusBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class QuestionPaperBase(BaseModel):
    course_id: int
    exam: Optional[str] = None
    month: Optional[str] = None
    year: Optional[str] = None
    duration: Optional[str] = None
    maximum_marks: Optional[str] = None
    source_file: str
    json_data: Any

class QuestionPaperCreate(QuestionPaperBase):
    pass

class QuestionPaper(QuestionPaperBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class MatchResultBase(BaseModel):
    syllabus_id: int
    question_paper_id: int
    result_json: Any

class MatchResultCreate(MatchResultBase):
    pass

class MatchResult(MatchResultBase):
    id: int
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)
