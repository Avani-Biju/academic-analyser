import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database.database import Base
from app.database import models, schemas, crud

# Use in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def db():
    # Create the tables
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Drop the tables after the test
        Base.metadata.drop_all(bind=engine)

def test_create_and_retrieve_course(db):
    course_in = schemas.CourseCreate(
        course_code="CS101",
        course_name="Intro to CS",
        semester="1",
        scheme="2020",
        credits="4"
    )
    course = crud.create_course(db, course_in)
    
    assert course.id is not None
    assert course.course_code == "CS101"
    
    fetched = crud.get_course_by_code(db, "CS101")
    assert fetched.id == course.id

def test_workflow_course_syllabus_question_paper_match(db):
    # 1. Create Course
    course_in = schemas.CourseCreate(course_code="CS102")
    course = crud.create_course(db, course_in)
    
    # 2. Create Syllabus
    syl_in = schemas.SyllabusCreate(
        course_id=course.id,
        source_file="syllabus.pdf",
        json_data={"modules": []}
    )
    syllabus = crud.create_syllabus(db, syl_in)
    assert syllabus.id is not None
    
    # 3. Create Question Paper
    qp_in = schemas.QuestionPaperCreate(
        course_id=course.id,
        source_file="qp.pdf",
        json_data={"questions": []}
    )
    qp = crud.create_question_paper(db, qp_in)
    assert qp.id is not None
    
    # 4. Create Match Result
    match_in = schemas.MatchResultCreate(
        syllabus_id=syllabus.id,
        question_paper_id=qp.id,
        result_json={"status": "success", "results": []}
    )
    match = crud.create_match_result(db, match_in)
    assert match.id is not None
    
    # 5. Fetch matches for course
    course_matches = crud.get_match_results_by_course(db, course.id)
    assert len(course_matches) == 1
    assert course_matches[0].id == match.id
