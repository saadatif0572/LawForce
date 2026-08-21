import pytest
from backend.app.services.retrieval.hybrid_retriever import HybridRetriever

def test_hybrid_retrieval_query_parsing():
    retriever = HybridRetriever()
    
    # Section query
    info_sec = retriever.parse_legal_query("What does Section 302 of PPC state?")
    assert info_sec["exact_section"] == "302"
    assert info_sec["language"] == "en"
    
    # Urdu query
    info_ur = retriever.parse_legal_query("آئین کا آرٹیکل 199 کیا کہتا ہے؟")
    assert info_ur["language"] == "ur"
    assert info_ur["exact_section"] == "199"
    
    # Province query
    info_prov = retriever.parse_legal_query("Punjab consumer court rules")
    assert info_prov["detected_province"] == "punjab"

def test_hybrid_retrieval_execution():
    retriever = HybridRetriever()
    results = retriever.search("Section 498 CrPC bail before arrest", top_k=5)
    assert len(results) > 0
    assert "payload" in results[0]
    assert "relevance_score" in results[0]
