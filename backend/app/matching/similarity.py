import re
from rapidfuzz import fuzz

def normalize_text(text: str) -> str:
    """Normalize text for matching by lowercasing and stripping."""
    return text.lower().strip()

def extract_keywords(text1: str, text2: str) -> list[str]:
    """Simple keyword extraction: intersection of words excluding stop words."""
    words1 = set(re.findall(r'\b\w+\b', text1.lower()))
    words2 = set(re.findall(r'\b\w+\b', text2.lower()))
    
    stop_words = {"the", "a", "an", "of", "and", "in", "to", "for", "on", "with"}
    intersection = words1.intersection(words2) - stop_words
    return list(intersection)

def exact_match(norm_q: str, norm_t: str) -> bool:
    """Check for exact string match."""
    return norm_q == norm_t

def partial_match(norm_q: str, norm_t: str) -> bool:
    """Check for partial substring match with minimum length constraints."""
    if len(norm_q) > 3 and len(norm_t) > 3:
        return norm_q in norm_t or norm_t in norm_q
    return False

def fuzzy_match_score(norm_q: str, norm_t: str) -> float:
    """Calculate fuzzy match score using RapidFuzz."""
    return fuzz.token_sort_ratio(norm_q, norm_t)
