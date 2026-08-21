import pytest
from backend.app.services.generation.groq_generator import GroqGenerator

def test_groq_generator_grounding():
    generator = GroqGenerator()
    
    mock_chunks = [
        {
            "payload": {
                "document_id": "pakistan_penal_code_1860",
                "canonical_title": "Pakistan Penal Code, 1860",
                "section_number": "302",
                "section_heading": "Punishment of Qatl-e-Amd",
                "jurisdiction": "federal",
                "legal_status": "in_force",
                "source_url": "https://pakistancode.gov.pk/302",
                "page_start": 145,
                "text": "Whoever commits qatl-e-amd shall be punished with death or imprisonment for life as ta'zir."
            },
            "relevance_score": 0.95
        }
    ]
    
    res = generator.generate_response(
        question="What is the punishment under Section 302 PPC?",
        retrieved_chunks=mock_chunks,
        language="en"
    )
    
    assert res["confidence"] == "high"
    assert len(res["sources"]) == 1
    assert "Pakistan Penal Code" in res["sources"][0]["title"]
    assert "Section 302" in res["sources"][0]["article_or_section"]
    assert "disclaimer" in res
    assert "General legal information only" in res["disclaimer"]

def test_insufficient_evidence_refusal():
    generator = GroqGenerator()
    res = generator.generate_response(
        question="Alien immigration code on Mars",
        retrieved_chunks=[],
        language="en"
    )
    assert res["confidence"] == "ungrounded"
    assert res["needs_clarification"] is True
    assert "does not contain sufficient" in res["answer_markdown"].lower()
