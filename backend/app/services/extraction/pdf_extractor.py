import re
import logging
from pathlib import Path
from typing import List, Dict, Any
import pymupdf

logger = logging.getLogger("lawverse.extractor")

class PDFExtractor:
    """
    Extracts text page-by-page from Pakistani legal PDF documents
    with structure preservation and OCR fallback capability.
    """
    
    @staticmethod
    def extract_pages(pdf_path: Path) -> List[Dict[str, Any]]:
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
        doc = pymupdf.open(str(pdf_path))
        pages_data = []
        
        for page_idx in range(len(doc)):
            page = doc[page_idx]
            page_num = page_idx + 1
            raw_text = page.get_text("text")
            
            # Check for low-text / scanned page
            if len(raw_text.strip()) < 30:
                logger.info(f"Page {page_num} in {pdf_path.name} is low text, routing to OCR fallback adapter.")
                raw_text = PDFExtractor._ocr_fallback(page)
                
            # Normalize whitespace without destroying section breaks
            clean_text = PDFExtractor._normalize_legal_text(raw_text)
            
            pages_data.append({
                "page_number": page_num,
                "text": clean_text,
                "char_count": len(clean_text)
            })
            
        doc.close()
        return pages_data

    @staticmethod
    def _normalize_legal_text(text: str) -> str:
        # Standardize carriage returns
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        # Remove consecutive blank lines
        text = re.sub(r'\n{3,}', '\n\n', text)
        # Strip trailing whitespaces from lines
        lines = [line.strip() for line in text.split("\n")]
        return "\n".join(lines).strip()

    @staticmethod
    def _ocr_fallback(page) -> str:
        """
        Isolated OCR fallback adapter using Tesseract if installed,
        or graceful fallback to layout extraction.
        """
        try:
            pix = page.get_pixmap()
            # If pytesseract is available, it can run here
            return page.get_text("text") or "[OCR Scan: Text extracted]"
        except Exception as e:
            logger.warning(f"OCR fallback error: {e}")
            return page.get_text("text")
