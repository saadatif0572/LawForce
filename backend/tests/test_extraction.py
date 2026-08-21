import pytest
from pathlib import Path
from backend.app.services.extraction.pdf_extractor import PDFExtractor

def test_pdf_extraction_page_count():
    workspace_root = Path(__file__).resolve().parents[2]
    sample_pdf = workspace_root / "data" / "raw" / "pakistan_penal_code_1860.pdf"
    
    assert sample_pdf.exists(), f"Sample PDF must exist at {sample_pdf}"
    
    pages = PDFExtractor.extract_pages(sample_pdf)
    assert len(pages) >= 1
    assert "page_number" in pages[0]
    assert "text" in pages[0]
    assert len(pages[0]["text"]) > 20
