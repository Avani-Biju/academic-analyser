import re
import logging
from app.parsers.config import FIELD_PATTERNS, MODULE_HEADERS, STOP_SECTIONS, MODULE_NOISE_WORDS
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

# Dynamically build regex patterns from configuration
MODULE_REGEX = r"(?i)^(" + "|".join(MODULE_HEADERS) + r")\s*[-–]?\s*([IVX]+|\d+)"
STOP_REGEX = r"(?i)^(" + "|".join(STOP_SECTIONS) + r")"

# ==========================================
# COURSE OUTCOMES
# ==========================================
def extract_course_outcomes(lines: list[str]) -> list[str]:
    """
    Extracts course outcomes until it hits a stop boundary.
    """
    cos = []
    in_co_section = False
    
    for line in lines:
        if re.match(r"(?i)^Course\s*Outcomes?(?:\s*\(COs\))?$", line):
            in_co_section = True
            continue
            
        if re.search(MODULE_REGEX, line) or re.search(STOP_REGEX, line):
            in_co_section = False
            
        if in_co_section:
            if re.match(r"(?i)^CO\d+", line) or len(line) > 5:
                cos.append(line)
            
    return cos

# ==========================================
# MODULE STATE MACHINE
# ==========================================
def extract_modules(lines: list[str]) -> list[dict]:
    """
    Extracts module hierarchies using a finite state machine.
    """
    modules = []
    current_module = None
    in_module = False
    expecting_title = False
    
    for line in lines:
        module_match = re.search(MODULE_REGEX, line)
        if module_match:
            if current_module:
                modules.append(current_module)
                
            current_module = {
                "module_number": module_match.group(2),
                "module_title": None,
                "hours": None,
                "course_outcomes": [],
                "topics": []
            }
            in_module = True
            expecting_title = True
            continue
            
        if re.search(STOP_REGEX, line):
            in_module = False
            continue
            
        if in_module and current_module:
            if expecting_title:
                if line.lower() in MODULE_NOISE_WORDS:
                    continue
                current_module["module_title"] = line
                expecting_title = False
                continue
                
            hours_match = re.search(r"(?i)(\d+)\s*Hours?", line)
            if hours_match and not current_module["hours"]:
                current_module["hours"] = int(hours_match.group(1))
                if len(line) < 15:
                    continue
                    
            co_match = re.findall(r"(?i)CO\d+", line)
            if co_match:
                for co in co_match:
                    if co.upper() not in current_module["course_outcomes"]:
                        current_module["course_outcomes"].append(co.upper())
                if len(line.replace(",", "").replace(" ", "")) <= sum(len(c) for c in co_match):
                    continue
                    
            if re.match(r"^\d+$", line):
                continue
                
            current_module["topics"].append(line)
            
    if current_module:
        modules.append(current_module)
        
    return modules

# ==========================================
# ORCHESTRATOR
# ==========================================
def parse_syllabus(text: str) -> dict:
    """
    Coordinates the syllabus parsing pipeline: Normalization -> Extraction -> Generic Output.
    """
    logger.info("\n--- Starting Generic Syllabus Parsing ---")
    
    clean_lines = normalize_text(text)
    missing_fields = []
    
    course_code = extract_field("course_code", clean_lines, missing_fields, FIELD_PATTERNS)
    course_name = extract_field("course_name", clean_lines, missing_fields, FIELD_PATTERNS)
    semester = extract_field("semester", clean_lines, missing_fields, FIELD_PATTERNS)
    scheme = extract_field("scheme", clean_lines, missing_fields, FIELD_PATTERNS)
    credits = extract_field("credits", clean_lines, missing_fields, FIELD_PATTERNS)
    
    course_outcomes = extract_course_outcomes(clean_lines)
    modules = extract_modules(clean_lines)
    
    if modules:
        topic_count = sum(len(m["topics"]) for m in modules)
        logger.info(f"Total Topics Extracted: {topic_count}")
        
    if missing_fields:
        logger.warning(f"Missing Fields Detected: {', '.join(missing_fields)}")
        
    logger.info("--- Syllabus Parsing Complete ---\n")
    
    return {
        "document_type": "syllabus",
        "is_partial": len(missing_fields) > 0,
        "course_code": course_code,
        "course_name": course_name,
        "semester": semester,
        "scheme": scheme,
        "credits": credits,
        "course_outcomes": course_outcomes,
        "modules": modules,
        "missing_fields": missing_fields
    }
