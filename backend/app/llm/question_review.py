from __future__ import annotations

from copy import deepcopy


def normalize_question_review(parser_json: dict, reviewed_json: dict) -> dict:
    base = deepcopy(parser_json)
    base.update(reviewed_json or {})

    questions = base.get("questions")
    if isinstance(questions, list):
        normalized_questions = []
        for question in questions:
            if not isinstance(question, dict):
                continue

            normalized = dict(question)
            if "question" in normalized and normalized["question"] is not None:
                normalized["question"] = str(normalized["question"]).strip()
            if "question_type" in normalized and normalized["question_type"] is not None:
                normalized["question_type"] = str(normalized["question_type"]).strip()
            if "bloom_level" in normalized and normalized["bloom_level"] is not None:
                normalized["bloom_level"] = str(normalized["bloom_level"]).strip()
            if "requires_diagram" in normalized:
                normalized["requires_diagram"] = bool(normalized["requires_diagram"])

            normalized_questions.append(normalized)
        base["questions"] = normalized_questions

    base["llm_verified"] = bool(reviewed_json)
    return base
