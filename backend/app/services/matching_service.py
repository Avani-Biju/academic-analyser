import json
from pathlib import Path
from fastapi import HTTPException
from app.matching.matcher import match_question

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"

def load_json_file(filename: str) -> dict:
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(404, f"File {filename} not found")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def extract_structured_topics(syllabus: dict) -> list[dict]:
    """Returns a list of dicts: [{'module': 'M1', 'topic': 'topic text'}, ...]"""
    structured_topics = []
    modules = syllabus.get("modules", [])
    for idx, module in enumerate(modules):
        module_title = module.get("module_title")
        module_num = module.get("module_number")
        mod_name = module_title if module_title else f"Module {module_num if module_num else idx+1}"
        
        for topic in module.get("topics", []):
            structured_topics.append({
                "module": mod_name,
                "topic": topic
            })
    return structured_topics

def perform_matching(syllabus_data: dict = None, questions_data: dict = None,
                     syllabus_file: str = None, questions_file: str = None) -> dict:
                         
    # 1. Resolve syllabus
    if syllabus_data:
        syllabus = syllabus_data
    elif syllabus_file:
        syllabus = load_json_file(syllabus_file)
    else:
        raise HTTPException(400, "Provide syllabus_file or syllabus_data")
        
    # 2. Resolve questions
    if questions_data:
        questions = questions_data
    elif questions_file:
        questions = load_json_file(questions_file)
    else:
        raise HTTPException(400, "Provide questions_file or questions_data")
        
    structured_topics = extract_structured_topics(syllabus)
    questions_list = questions.get("questions", [])
    
    if not structured_topics:
        raise HTTPException(400, "No topics found in the syllabus data")
        
    if not questions_list:
        raise HTTPException(400, "No questions found in the questions data")
        
    results = []
    for q_obj in questions_list:
        question_text = q_obj.get("question", "")
        if not question_text:
            continue
            
        match_result = match_question(question_text, structured_topics)
        
        enriched_question = {**q_obj}
        enriched_question["match"] = match_result
        
        results.append(enriched_question)
        
    return {
        "status": "success",
        "total_questions": len(results),
        "results": results
    }
