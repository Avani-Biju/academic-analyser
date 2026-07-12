from app.llm.review_service import review_document


def test_review_document_falls_back_without_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")

    parser_json = {
        "document_type": "syllabus",
        "course_code": "CST202",
        "course_name": "Computer Organisation",
        "modules": [{"module_name": "Module 1", "topics": ["CPU Basics"]}],
    }

    result = review_document("syllabus", "raw text", parser_json)

    assert result.used_llm is False
    assert result.data["course_code"] == "CST202"
    assert result.data["llm_verified"] is False
    assert result.fallback_reason == "missing_api_key"


def test_review_document_normalizes_syllabus_module_title(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeClient:
        def is_available(self):
            return True

        def generate_json(self, prompt: str):
            return {
                "modules": [
                    {
                        "module_title": "Functional Units",
                        "topics": ["Registers", "ALU"]
                    }
                ],
                "llm_notes": "Normalized title"
            }

    monkeypatch.setattr("app.llm.review_service.GeminiClient", lambda: FakeClient())

    parser_json = {
        "document_type": "syllabus",
        "course_code": "CST202",
        "course_name": "Computer Organisation",
        "modules": [{"module_name": "Module 1", "topics": ["Registers"]}],
    }

    result = review_document("syllabus", "raw text", parser_json)

    assert result.used_llm is True
    assert result.data["modules"][0]["module_name"] == "Functional Units"
    assert result.data["llm_verified"] is True


def test_review_document_normalizes_question_review(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    class FakeClient:
        def is_available(self):
            return True

        def generate_json(self, prompt: str):
            return {
                "questions": [
                    {
                        "question_number": "1",
                        "question": "Explain the ALU.",
                        "question_type": "Explain",
                        "bloom_level": "Understand",
                        "requires_diagram": 0,
                    }
                ]
            }

    monkeypatch.setattr("app.llm.review_service.GeminiClient", lambda: FakeClient())

    parser_json = {
        "document_type": "question_paper",
        "questions": [
            {"question_number": "1", "question": " Explain the ALU. "}
        ],
    }

    result = review_document("question_paper", "raw text", parser_json)

    assert result.used_llm is True
    assert result.data["questions"][0]["question"] == "Explain the ALU."
    assert result.data["questions"][0]["requires_diagram"] is False
