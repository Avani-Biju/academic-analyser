import json
from pathlib import Path
from datetime import datetime, timezone
from copy import deepcopy
from app.parsers.syllabus_parser import parse_syllabus
from app.parsers.question_parser import parse_question_paper
from app.llm.review_service import review_document
import logging

logger = logging.getLogger(__name__)

# Resolve output directory relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "output"
OUTPUT_DIR.mkdir(exist_ok=True)

def parse_document(text: str, filename: str, doc_type: str = "syllabus") -> dict:
    """
    Routes the extracted text to the appropriate parser based on doc_type,
    injects generic document schema metadata, runs LLM review as a silent
    enhancement layer, saves the final JSON,
    and returns the parsed dictionary.
    """
    logger.info(f"Routing document for parsing: {filename} (Type: {doc_type})")
    
    if doc_type == "syllabus":
        parsed_data = parse_syllabus(text)
    elif doc_type == "question_paper":
        parsed_data = parse_question_paper(text)
    else:
        raise ValueError(f"Unsupported document type: {doc_type}")
        
    # Inject common document schema metadata before LLM review so the final
    # reviewed object preserves the existing schema and common fields.
    parsed_data["source_file"] = filename
    parsed_data["parsed_at"] = datetime.now(timezone.utc).isoformat()
    parsed_data["llm_verified"] = False

    review_result = review_document(doc_type, text, deepcopy(parsed_data))
    logger.info(
        "[LLM] Review result accepted: used_llm=%s fallback_reason=%s",
        review_result.used_llm,
        review_result.fallback_reason,
    )
    final_data = review_result.data
    final_data["source_file"] = filename
    final_data["parsed_at"] = parsed_data["parsed_at"]

    # Save the parsed data as JSON
    output_file_path = OUTPUT_DIR / Path(filename).with_suffix(".json").name
    logger.info(f"Saving parsed data to: {output_file_path}")
    
    with open(output_file_path, "w", encoding="utf-8") as f:
        json.dump(final_data, f, indent=4)
        
    return final_data
