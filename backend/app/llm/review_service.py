from __future__ import annotations

import logging
from copy import deepcopy

from app.llm.client import GeminiClient
from app.llm.prompts import build_prompt
from app.llm.question_review import normalize_question_review
from app.llm.schemas import ReviewRequest, ReviewResult
from app.llm.syllabus_review import normalize_syllabus_review

logger = logging.getLogger(__name__)


def review_document(document_type: str, raw_text: str, parser_json: dict) -> ReviewResult:
    logger.info("[LLM] Review started")
    request = ReviewRequest(
        document_type=document_type,
        raw_text=raw_text,
        parser_json=deepcopy(parser_json),
    )
    client = GeminiClient()
    logger.info("[LLM] GEMINI_API_KEY loaded: %s", "yes" if client.is_available() else "no")

    if not client.is_available():
        logger.info("[LLM] Falling back to parser")
        fallback = deepcopy(parser_json)
        fallback["llm_verified"] = False
        return ReviewResult(data=fallback, used_llm=False, fallback_reason="missing_api_key")

    prompt = build_prompt(request.document_type, request.raw_text, request.parser_json)

    try:
        reviewed_json = client.generate_json(prompt)
        normalized = _normalize_review(request.document_type, request.parser_json, reviewed_json)
        logger.info("[LLM] Review completed")
        return ReviewResult(data=normalized, used_llm=True)
    except Exception as exc:
        logger.exception("[LLM] Falling back to parser: %s", exc)
        fallback = deepcopy(parser_json)
        fallback["llm_verified"] = False
        fallback["llm_notes"] = "LLM review unavailable; showing parser output."
        return ReviewResult(data=fallback, used_llm=False, fallback_reason=str(exc))


def _normalize_review(document_type: str, parser_json: dict, reviewed_json: dict) -> dict:
    if document_type == "syllabus":
        return normalize_syllabus_review(parser_json, reviewed_json)
    if document_type == "question_paper":
        return normalize_question_review(parser_json, reviewed_json)
    return deepcopy(parser_json)
