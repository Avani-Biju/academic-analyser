import json
from pathlib import Path
from datetime import datetime, timezone
from app.parsers.syllabus_parser import parse_syllabus
from app.parsers.question_parser import parse_question_paper
import logging

logger = logging.getLogger(__name__)

# Resolve output directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_document(text: str, filename: str, doc_type: str = "syllabus") -> dict:
    """
    Routes the extracted text to the appropriate parser based on doc_type,
    injects generic document schema metadata, saves the output as JSON, 
    and returns the parsed dictionary.
    """
    logger.info(f"Routing document for parsing: {filename} (Type: {doc_type})")
    
    if doc_type == "syllabus":
        parsed_data = parse_syllabus(text)
    elif doc_type == "question_paper":
        parsed_data = parse_question_paper(text)
    else:
        raise ValueError(f"Unsupported document type: {doc_type}")
        
    # Inject common document schema metadata
    parsed_data["source_file"] = filename
    parsed_data["parsed_at"] = datetime.now(timezone.utc).isoformat()
        
    # Save the parsed data as JSON
    output_file_path = OUTPUT_DIR / Path(filename).with_suffix(".json").name
    logger.info(f"Saving parsed data to: {output_file_path}")
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(parsed_data, f, indent=4)
        
    return parsed_data
