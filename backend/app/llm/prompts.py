from __future__ import annotations


COMMON_REVIEW_RULES = """You are reviewing OCR/PDF parser output for an academic document.

Rules:
- Return exactly one JSON object.
- Preserve the existing parser schema and all existing keys.
- You may add supportive fields like llm_verified, llm_notes, parser_confidence, bloom_level, requires_diagram, question_type.
- Never invent information that is not supported by the raw text.
- If a field is unclear, keep the parser value or null rather than guessing.
- Keep module/topic/question ordering faithful to the source.
- Do not wrap the JSON in markdown fences.
"""


SYLLABUS_REVIEW_PROMPT = """Review this syllabus extraction.

Your job:
- Correct obvious parser mistakes.
- Merge split topics when they clearly belong together.
- Remove duplicates.
- Normalize wording and abbreviations.
- Improve course outcomes only when directly supported by the text.
- Validate module hierarchy.
- Keep the existing schema intact.

When reviewing syllabus modules:
- Prefer a meaningful module title.
- If both module_name and module_title concepts exist, preserve the schema key already used in the parser output and do not invent a new nested structure.
- Keep topics as a flat ordered list of strings unless the parser schema already differs.
"""


QUESTION_REVIEW_PROMPT = """Review this question paper extraction.

Your job:
- Correct malformed questions.
- Merge multiline questions.
- Preserve numbering and marks.
- Preserve or improve question_type when supported by text.
- Detect whether a question references a diagram.
- Estimate Bloom's taxonomy level conservatively.
- Normalize formatting.
- Never invent missing questions or marks.
"""


def build_prompt(document_type: str, raw_text: str, parser_json: dict) -> str:
    if document_type == "syllabus":
        task_prompt = SYLLABUS_REVIEW_PROMPT
    else:
        task_prompt = QUESTION_REVIEW_PROMPT

    return (
        f"{COMMON_REVIEW_RULES}\n\n"
        f"{task_prompt}\n\n"
        f"Document type: {document_type}\n\n"
        f"Raw extracted text:\n{raw_text}\n\n"
        f"Parser JSON:\n{parser_json}\n"
    )
