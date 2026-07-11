import re
import logging
from app.parsers.config import FIELD_PATTERNS, QUESTION_METADATA, QUESTION_SECTION_HEADERS, QUESTION_STOP_SECTIONS
from app.parsers.parser_utils import normalize_text, extract_field

# ==========================================
# LOGGING SETUP
# ==========================================
logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# Dynamically build regex patterns
SECTION_REGEX = r"(?i)^(" + "|".join(QUESTION_SECTION_HEADERS) + r")\s*([A-Za-z0-9]+)"
STOP_REGEX = r"(?i)^(" + "|".join(QUESTION_STOP_SECTIONS) + r")"

# ==========================================
# HELPERS
# ==========================================
def classify_question_type(question_text: str) -> str:
    """
    Classifies the question to assist with future LLM/ML analytics (e.g. '70% of questions are Explain').
    """
    text_lower = question_text.lower()
    # Ordered by priority/complexity
    keywords = ["derive", "calculate", "design", "differentiate", "compare", "explain", "discuss", "draw", "define", "list", "state"]
    for word in keywords:
        # Check if the word is present as a whole word or prefix
        if re.search(r'\b' + word, text_lower):
            return word.capitalize()
    
    if "?" in text_lower or re.search(r'\bwhat|why|how|when|where\b', text_lower):
        return "Short Answer"
        
    return "Other"

def extract_marks(line: str) -> tuple[int | None, str]:
    """
    Extracts marks from a line like '(10)', '10 Marks', 'Marks: 10' and removes it from the text.
    """
    # 1. Matches (10) or [10]
    match = re.search(r"[\(\[](\d{1,2})[\)\]]", line)
    if match:
        return int(match.group(1)), line.replace(match.group(0), "").strip()
        
    # 2. Matches "Marks: 10" or "10 Marks"
    match = re.search(r"(?i)Marks?\s*[:\-]?\s*(\d{1,2})|(\d{1,2})\s*Marks?", line)
    if match:
        marks = match.group(1) if match.group(1) else match.group(2)
        return int(marks), line.replace(match.group(0), "").strip()
        
    return None, line

# ==========================================
# STATE MACHINE
# ==========================================
def extract_questions(lines: list[str]) -> list[dict]:
    """
    State machine that extracts questions, handling parts, OR logic, sub-questions, and marks.
    """
    questions = []
    current_part = None
    is_or = False
    
    current_q_num = None
    current_sub_q = None
    current_marks = None
    current_text = []
    
    def save_current_question():
        if current_text:
            q_text = " ".join(current_text).strip()
            q_type = classify_question_type(q_text)
            questions.append({
                "question_number": current_q_num,
                "part": current_part,
                "sub_question": current_sub_q,
                "marks": current_marks,
                "or_question": is_or,
                "question_type": q_type,
                "difficulty": None, # Placeholder for LLM phase
                "question": q_text
            })
            current_text.clear()
            
    for line in lines:
        # 1. Check for Stop Conditions
        if re.search(STOP_REGEX, line):
            # Instructions usually appear at the start or middle; we should skip them, not halt the entire parser.
            if re.search(r"(?i)instructions", line):
                continue
            if questions or current_q_num:
                save_current_question()
                break
            continue
            
        # 1.5 Prevent multiple papers from merging by stopping at a new exam header
        if re.search(r"(?i)^\s*(Sample Question Paper|End Semester Examination|Mid Semester Examination|Internal Assessment|Sample Test Paper)", line):
            if questions or current_q_num:
                save_current_question()
                break

        # 2. Check for Section/Part Header (e.g. "PART A")
        part_match = re.search(SECTION_REGEX, line)
        if part_match:
            save_current_question()
            current_part = part_match.group(2).upper()
            is_or = False # Reset OR logic on new part
            current_q_num = None
            current_sub_q = None
            current_marks = None
            continue
            
        # 3. Check for OR logic
        if re.match(r"(?i)^\s*OR\s*$", line):
            is_or = True
            continue
            
        # 4. Try to extract marks from the current line
        marks, line_without_marks = extract_marks(line)
        if marks and current_q_num:
            # If we found marks on this line, and we are currently tracking a question
            current_marks = marks
            
        if not line_without_marks:
            continue
            
        # 5. Check for Main Question Number
        q_match1 = re.match(r"^(?:Q(?:uestion)?|q(?:uestion)?)\.?\s*(\d{1,2})\s*(?:[.\)]|\(([a-z])\))?\s*(.*)", line_without_marks)
        # Uppercase letters only for main questions to prevent swallowing sub-questions like 'a)'
        q_match2 = re.match(r"^\s*([A-Z]|\d{1,2})\s*(?:[.\)]|\(([a-z])\))\s*(.*)", line_without_marks)
        q_match = q_match1 or q_match2
        if q_match:
            save_current_question()
            
            current_q_num = q_match.group(1)
            current_sub_q = q_match.group(2) if q_match.group(2) else None
            # Marks might have been found on this starting line
            current_marks = marks 
            
            content = q_match.group(3).strip()
            if content:
                current_text.append(content)
            continue
            
        # 6. Check for Sub-Question (e.g. "a.", "(a)", "a)", "ii)")
        sub_match = re.match(r"^\s*(?:([a-z]{1,4})\.|([a-z]{1,4})\)|\(([a-z]{1,4})\))\s*(.*)", line_without_marks)
        if sub_match and current_q_num:
            # Only trigger a sub-question if we already have a main question
            save_current_question()
            
            raw_sub = sub_match.group(1) or sub_match.group(2) or sub_match.group(3)
            current_sub_q = raw_sub
            current_marks = marks
            
            content = sub_match.group(4).strip()
            if content:
                current_text.append(content)
            continue
            
        # 7. Append normal text to the current question
        if current_q_num:
            current_text.append(line_without_marks)
            
    # Save the very last question
    save_current_question()
    
    return questions

# ==========================================
# ORCHESTRATOR
# ==========================================
def parse_question_paper(text: str) -> dict:
    """
    Coordinates the question paper parsing pipeline.
    """
    logger.info("\n--- Starting Generic Question Paper Parsing ---")
    
    clean_lines = normalize_text(text)
    missing_fields = []
    
    # We reuse FIELD_PATTERNS for standard course metadata
    course_code = extract_field("course_code", clean_lines, missing_fields, FIELD_PATTERNS)
    program_code = extract_field("program_code", clean_lines, [], FIELD_PATTERNS) # Don't flag as missing
    course_name = extract_field("course_name", clean_lines, missing_fields, FIELD_PATTERNS)
    semester = extract_field("semester", clean_lines, missing_fields, FIELD_PATTERNS)
    
    # Use QUESTION_METADATA for specific question paper metadata
    exam = extract_field("exam", clean_lines, missing_fields, QUESTION_METADATA)
    month = extract_field("month", clean_lines, missing_fields, QUESTION_METADATA)
    year = extract_field("year", clean_lines, missing_fields, QUESTION_METADATA)
    duration = extract_field("duration", clean_lines, missing_fields, QUESTION_METADATA)
    max_marks = extract_field("maximum_marks", clean_lines, missing_fields, QUESTION_METADATA)
    
    # Log findings
    logger.info(f"Course Code Found: {course_code}")
    if program_code:
        logger.info(f"Program Code Found: {program_code}")
    logger.info(f"Exam Found: {exam}")
    
    questions = extract_questions(clean_lines)
    logger.info(f"Questions Found: {len(questions)}")
    
    if missing_fields:
        logger.warning(f"Missing Metadata: {', '.join(missing_fields)}")
        
    logger.info("--- Question Paper Parsing Complete ---\n")
    
    return {
        "document_type": "question_paper",
        "is_partial": len(missing_fields) > 0,
        "course_code": course_code,
        "program_code": program_code,
        "course_name": course_name,
        "semester": semester,
        "exam": exam,
        "month": month,
        "year": year,
        "duration": duration,
        "maximum_marks": max_marks,
        "questions": questions,
        "missing_fields": missing_fields
    }
