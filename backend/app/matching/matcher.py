import re
from app.matching.similarity import normalize_text, extract_keywords, exact_match, partial_match, fuzzy_match_score
from app.matching.confidence import calculate_confidence

QUESTION_VERBS = [
    "explain", "define", "describe", "discuss", "compare", "draw",
    "what is", "what are", "state", "list", "outline", "illustrate",
    "derive", "evaluate", "write", "find", "calculate"
]

def parse_question(original_text: str) -> dict:
    """Extracts question verbs, preserving original text and generating normalized version."""
    original_text = original_text.strip()
    lower_text = original_text.lower()
    
    question_type = "None"
    norm_text = lower_text
    
    for verb in QUESTION_VERBS:
        if lower_text.startswith(verb):
            question_type = verb.capitalize()
            # Remove verb from the beginning
            norm_text = lower_text[len(verb):].strip()
            # Remove leading stop words if any
            norm_text = re.sub(r'^(the|a|an|of|for|on)\s+', '', norm_text)
            break
            
    return {
        "original": original_text,
        "normalized": norm_text,
        "type": question_type
    }

def match_question(question_text: str, structured_topics: list[dict]) -> dict:
    """
    structured_topics format: [{"module": "Module 1", "topic": "Rank of Matrix"}, ...]
    Returns dict with match details.
    """
    parsed = parse_question(question_text)
    norm_q = parsed["normalized"]
    
    best_match = None
    best_module = None
    best_confidence = 0.0
    final_match_type = "none"
    best_keywords = []

    for item in structured_topics:
        module_name = item.get("module")
        topic = item.get("topic")
        
        norm_t = normalize_text(topic)
        
        # 1. Similarity checks
        is_exact = exact_match(norm_q, norm_t)
        is_partial = partial_match(norm_q, norm_t)
        fuzz_score = fuzzy_match_score(norm_q, norm_t)
        
        # 2. Confidence & Match Type
        confidence, match_type = calculate_confidence(norm_q, norm_t, is_exact, is_partial, fuzz_score)
        
        if confidence > best_confidence:
            best_confidence = confidence
            best_match = topic
            best_module = module_name
            final_match_type = match_type
            best_keywords = extract_keywords(norm_q, norm_t)
            
            # If exact match, we can short-circuit
            if confidence == 1.00:
                break
            
    return {
        "question": parsed,
        "matched_module": best_module,
        "matched_topic": best_match,
        "confidence": best_confidence,
        "match_type": final_match_type,
        "matched_keywords": best_keywords
    }
