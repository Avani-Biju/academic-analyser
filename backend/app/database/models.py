from sqlalchemy import Column, Integer, String, JSON, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from app.database.database import Base

class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    course_code = Column(String, unique=True, index=True, nullable=False)
    course_name = Column(String, nullable=True)
    semester = Column(String, nullable=True)
    scheme = Column(String, nullable=True)
    credits = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    syllabus = relationship("Syllabus", back_populates="course", uselist=False)
    question_papers = relationship("QuestionPaper", back_populates="course")


class Syllabus(Base):
    __tablename__ = "syllabi"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False, unique=True)
    source_file = Column(String, nullable=False)
    json_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="syllabus")
    match_results = relationship("MatchResult", back_populates="syllabus")


class QuestionPaper(Base):
    __tablename__ = "question_papers"

    id = Column(Integer, primary_key=True, index=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    exam = Column(String, nullable=True)
    month = Column(String, nullable=True)
    year = Column(String, nullable=True)
    duration = Column(String, nullable=True)
    maximum_marks = Column(String, nullable=True)
    source_file = Column(String, nullable=False)
    json_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    course = relationship("Course", back_populates="question_papers")
    match_results = relationship("MatchResult", back_populates="question_paper")


class MatchResult(Base):
    __tablename__ = "match_results"

    id = Column(Integer, primary_key=True, index=True)
    syllabus_id = Column(Integer, ForeignKey("syllabi.id"), nullable=False)
    question_paper_id = Column(Integer, ForeignKey("question_papers.id"), nullable=False)
    result_json = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    syllabus = relationship("Syllabus", back_populates="match_results")
    question_paper = relationship("QuestionPaper", back_populates="match_results")

# Future expansion ready for StudentMarks 
# class StudentMarks(Base): ...
