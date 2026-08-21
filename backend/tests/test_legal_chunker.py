import pytest
from backend.app.services.chunking.legal_chunker import LegalChunker

def test_legal_chunker_structure_detection():
    doc_meta = {
        "document_id": "test_crpc_1898",
        "canonical_title": "Code of Criminal Procedure, 1898",
        "jurisdiction": "federal",
        "document_type": "act",
        "legal_status": "in_force",
        "official_source_url": "https://pakistancode.gov.pk/test",
        "content_sha256": "abcdef1234567890",
        "language": "en"
    }
    
    pages_data = [
        {
            "page_number": 1,
            "text": "Code of Criminal Procedure, 1898\n\nSection 154: Information in cognizable cases\nEvery information relating to the commission of a cognizable offence shall be reduced to writing.\n\nSection 497: When bail may be taken in case of non-bailable offence\nWhen any person accused of non-bailable offence is arrested, he may be released on bail."
        }
    ]
    
    chunks = LegalChunker.chunk_document(doc_meta, pages_data)
    assert len(chunks) >= 2
    
    sec_154_chunk = next((c for c in chunks if c["section_number"] == "154"), None)
    sec_497_chunk = next((c for c in chunks if c["section_number"] == "497"), None)
    
    assert sec_154_chunk is not None
    assert sec_497_chunk is not None
    assert "Section 154" in sec_154_chunk["text"]
    assert "Section 497" in sec_497_chunk["text"]
    assert sec_154_chunk["document_id"] == "test_crpc_1898"
