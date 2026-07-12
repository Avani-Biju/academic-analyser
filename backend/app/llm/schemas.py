from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field


DocumentType = Literal["syllabus", "question_paper"]


class GeminiConfig(BaseModel):
    api_key: str | None = None
    model: str = "gemini-2.5-flash"
    timeout_seconds: float = 30.0


class ReviewRequest(BaseModel):
    document_type: DocumentType
    raw_text: str
    parser_json: dict[str, Any]


class ReviewResult(BaseModel):
    data: dict[str, Any]
    used_llm: bool = False
    fallback_reason: str | None = None


class GeminiResponsePart(BaseModel):
    text: str | None = None


class GeminiResponseContent(BaseModel):
    parts: list[GeminiResponsePart] = Field(default_factory=list)


class GeminiCandidate(BaseModel):
    content: GeminiResponseContent | None = None


class GeminiGenerateContentResponse(BaseModel):
    candidates: list[GeminiCandidate] = Field(default_factory=list)
