from app.parsers.syllabus_parser import parse_syllabus

# 1. Saintgits Format (Complex, flattened tables, multi-line metadata)
FORMAT_SAINTGITS = """
Course Code
24BST1101
Course Name
Linear Algebra and Calculus
Semester
S1
Credits
4
Scheme
2024

Course Outcomes (COs)
After the successful completion of the course the students will be able to:
CO1 Determine the rank of a matrix
CO2 Apply fundamental principles

Module I
COs
Hrs.
Module Title
System of Linear Equations
System of linear equations - Solution by Gauss elimination
1
8

Module II
Hrs.
Module Title
Eigen Values
Eigen values and vectors
2
7

END SEMESTER EXAMINATION
Details here...
"""

# 2. KTU Format (Watermarks, repetitive headers, missing 'scheme')
FORMAT_KTU = """
KTUNOTES.IN
Downloaded from www.ktunotes.in
Subject Code: CST202
Subject Title: Computer Organization and Architecture
Semester: 4
Course Credit: 4

Course Outcomes
CO1: Explain the structure of a computer.
CO2: Discuss the arithmetic operations.

Module 1
Basic Structure of computers
Functional units, Basic operational concepts
9 Hours

Page 3
3 | Page

Module 2
Arithmetic
Addition and subtraction
8 Hours

TEXT BOOKS
1. Hamacher
"""

# 3. Minimal Manually Typed Format (Missing multiple fields, alternative module headers)
FORMAT_MINIMAL = """
Course Code: CS101
Title: Intro to CS

Unit 1
Programming Basics
Variables, Loops
10 Hours

Unit 2
Functions
Scope, Recursion
5 Hours

QUESTION PAPER PATTERN
Do not extract this.
"""

def test_parse_saintgits():
    """Test handling of multi-line values and flattened table noise in Saintgits format."""
    data = parse_syllabus(FORMAT_SAINTGITS)
    
    assert data["document_type"] == "syllabus"
    assert data["is_partial"] == False
    assert len(data["missing_fields"]) == 0
    
    assert data["course_code"] == "24BST1101"
    assert data["course_name"] == "Linear Algebra and Calculus"
    assert data["semester"] == "S1"
    assert data["credits"] == 4
    assert data["scheme"] == "2024"
    
    assert len(data["course_outcomes"]) == 3 # Intro text + 2 COs
    
    assert len(data["modules"]) == 2
    
    m1 = data["modules"][0]
    assert m1["module_number"] == "I"
    assert m1["module_title"] == "System of Linear Equations" # Noise skipped
    assert m1["hours"] is None
    assert "System of linear equations - Solution by Gauss elimination" in m1["topics"]
    assert "1" not in m1["topics"] # Numeric noise ignored
    
    m2 = data["modules"][1]
    assert m2["module_number"] == "II"
    assert m2["module_title"] == "Eigen Values"
    assert m2["hours"] is None # '7' is unlabelled numeric row, so it's ignored
    assert "Details here..." not in m2["topics"] # Stopped at END SEMESTER EXAMINATION

def test_parse_ktu():
    """Test handling of watermarks, PDF artifacts, and missing fields in KTU format."""
    data = parse_syllabus(FORMAT_KTU)
    
    # Scheme is missing in this syllabus
    assert data["is_partial"] == True
    assert "scheme" in data["missing_fields"]
    assert data["scheme"] is None
    
    assert data["course_code"] == "CST202"
    assert data["course_name"] == "Computer Organization and Architecture"
    assert data["semester"] == "4"
    assert data["credits"] == 4
    
    assert len(data["modules"]) == 2
    
    m1 = data["modules"][0]
    assert m1["module_number"] == "1"
    assert m1["hours"] == 9
    
    m2 = data["modules"][1]
    assert m2["module_number"] == "2"
    assert m2["hours"] == 8
    
    # Verify watermarks were scrubbed from topics
    topics_string = " ".join(m1["topics"] + m2["topics"])
    assert "KTUNOTES.IN" not in topics_string
    assert "Downloaded from" not in topics_string
    assert "Page 3" not in topics_string
    assert "3 | Page" not in topics_string
    
    # Verify STOP boundary
    assert "Hamacher" not in topics_string

def test_parse_minimal():
    """Test extremely basic format with missing fields and alternative headers."""
    data = parse_syllabus(FORMAT_MINIMAL)
    
    assert data["is_partial"] == True
    assert "semester" in data["missing_fields"]
    assert "scheme" in data["missing_fields"]
    assert "credits" in data["missing_fields"]
    
    assert data["course_code"] == "CS101"
    assert data["course_name"] == "Intro to CS"
    
    assert len(data["modules"]) == 2
    assert data["modules"][0]["module_number"] == "1"
    assert data["modules"][0]["module_title"] == "Programming Basics"
    
    assert data["modules"][1]["module_number"] == "2"
    assert data["modules"][1]["module_title"] == "Functions"
    
    # Verify STOP boundary
    assert "Do not extract this." not in " ".join(data["modules"][1]["topics"])
