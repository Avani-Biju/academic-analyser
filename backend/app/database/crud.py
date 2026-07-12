from sqlalchemy.orm import Session
from app.database import models, schemas

def get_course_by_code(db: Session, course_code: str):
    return db.query(models.Course).filter(models.Course.course_code == course_code).first()

def get_course_by_id(db: Session, course_id: int):
    return db.query(models.Course).filter(models.Course.id == course_id).first()

def get_all_courses(db: Session):
    return db.query(models.Course).all()

def create_course(db: Session, course: schemas.CourseCreate):
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course

def update_course(db: Session, db_course: models.Course, course_data: dict):
    for key, value in course_data.items():
        if value is not None:
            setattr(db_course, key, value)
    db.commit()
    db.refresh(db_course)
    return db_course

def create_syllabus(db: Session, syllabus: schemas.SyllabusCreate):
    db_syllabus = models.Syllabus(**syllabus.model_dump())
    db.add(db_syllabus)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus

def get_syllabus_by_course(db: Session, course_id: int):
    return db.query(models.Syllabus).filter(models.Syllabus.course_id == course_id).first()

def update_syllabus(db: Session, db_syllabus: models.Syllabus, json_data: dict):
    db_syllabus.json_data = json_data
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus

def update_syllabus_record(db: Session, db_syllabus: models.Syllabus, syllabus_data: dict):
    for key, value in syllabus_data.items():
        if value is not None:
            setattr(db_syllabus, key, value)
    db.commit()
    db.refresh(db_syllabus)
    return db_syllabus

def create_question_paper(db: Session, paper: schemas.QuestionPaperCreate):
    db_paper = models.QuestionPaper(**paper.model_dump())
    db.add(db_paper)
    db.commit()
    db.refresh(db_paper)
    return db_paper

def get_question_papers_by_course(db: Session, course_id: int):
    return db.query(models.QuestionPaper).filter(models.QuestionPaper.course_id == course_id).all()

def create_match_result(db: Session, match_result: schemas.MatchResultCreate):
    db_match = models.MatchResult(**match_result.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match

def get_match_results_by_course(db: Session, course_id: int):
    # Join across syllabus and question papers to get matches for this course
    syllabi_ids = [s.id for s in db.query(models.Syllabus.id).filter(models.Syllabus.course_id == course_id).all()]
    if not syllabi_ids:
        return []
    return db.query(models.MatchResult).filter(models.MatchResult.syllabus_id.in_(syllabi_ids)).all()
