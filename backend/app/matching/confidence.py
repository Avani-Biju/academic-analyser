def map_fuzz_score(score: float) -> float:
    """
    RapidFuzz returns 0-100. 
    Map scores >60 to a 0.50 - 0.80 confidence range.
    """
    if score < 60:
        return 0.0
    # 60 -> 0.50, 100 -> 0.80
    return round(0.50 + ((score - 60) / 40.0) * 0.30, 2)

def calculate_confidence(norm_q: str, norm_t: str, exact: bool, partial: bool, fuzzy_score: float) -> tuple[float, str]:
    """
    Determine the confidence score and match type based on match results.
    Returns (confidence, match_type).
    """
    if exact:
        return 1.00, "exact"
        
    if partial:
        return 0.85, "partial"
        
    fuzz_conf = map_fuzz_score(fuzzy_score)
    if fuzz_conf >= 0.50:
        return fuzz_conf, "fuzzy"
        
    return 0.0, "none"
