import pytest
from app.matching.matcher import match_question, parse_question

@pytest.fixture
def structured_topics():
    return [
        {"module": "Module 1", "topic": "Rank of Matrix"},
        {"module": "Module 1", "topic": "Gauss Elimination Method"},
        {"module": "Module 2", "topic": "Eigenvalues and Eigenvectors"},
        {"module": "Module 3", "topic": "Partial Differentiation"}
    ]

def test_parse_question():
    result = parse_question("Explain the Rank of Matrix")
    assert result["type"] == "Explain"
    assert result["original"] == "Explain the Rank of Matrix"
    assert result["normalized"] == "rank of matrix"

def test_exact_match(structured_topics):
    result = match_question("Define Rank of Matrix", structured_topics)
    assert result["confidence"] == 1.00
    assert result["match_type"] == "exact"
    assert result["matched_module"] == "Module 1"
    assert result["matched_topic"] == "Rank of Matrix"
    
def test_partial_match(structured_topics):
    # Topic is "Eigenvalues and Eigenvectors"
    # Question is "Find the Eigenvalues and Eigenvectors of the given matrix"
    result = match_question("Find the Eigenvalues and Eigenvectors of the given matrix", structured_topics)
    # partial match because 'eigenvalues and eigenvectors' is a substring of the normalized question
    assert result["confidence"] == 0.85
    assert result["match_type"] == "partial"
    assert result["matched_module"] == "Module 2"
    
def test_fuzzy_match(structured_topics):
    # Typo or slight variation: "Gaus elimination method"
    result = match_question("Describe Gaus Elimination method", structured_topics)
    assert result["match_type"] == "fuzzy"
    assert result["matched_topic"] == "Gauss Elimination Method"
    assert 0.50 <= result["confidence"] < 0.85
    
def test_no_match(structured_topics):
    result = match_question("Discuss Shakespeare's Hamlet", structured_topics)
    assert result["match_type"] == "none"
    assert result["confidence"] == 0.0
    assert result["matched_topic"] is None
