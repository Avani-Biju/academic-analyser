from __future__ import annotations

from copy import deepcopy


def normalize_syllabus_review(parser_json: dict, reviewed_json: dict) -> dict:
    base = deepcopy(parser_json)
    base.update(reviewed_json or {})

    modules = base.get("modules")
    if isinstance(modules, list):
        normalized_modules = []
        for index, module in enumerate(modules, start=1):
            if not isinstance(module, dict):
                continue

            normalized = dict(module)
            module_title = (
                normalized.get("module_name")
                or normalized.get("module_title")
                or f"Module {index}"
            )
            normalized["module_name"] = module_title

            topics = normalized.get("topics")
            if not isinstance(topics, list):
                normalized["topics"] = []
            else:
                normalized["topics"] = [str(topic).strip() for topic in topics if str(topic).strip()]

            normalized_modules.append(normalized)
        base["modules"] = normalized_modules

    outcomes = base.get("course_outcomes")
    if isinstance(outcomes, list):
        base["course_outcomes"] = [str(item).strip() for item in outcomes if str(item).strip()]

    base["llm_verified"] = bool(reviewed_json)
    return base
