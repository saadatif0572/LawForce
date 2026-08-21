import re
from typing import List, Dict, Any

class LegalChunker:
    """
    Legal-aware structural chunker respecting Part, Chapter, Article, Section,
    Subsection, Clause, and Schedule boundaries. Preserves parent statute context
    and produces deterministic chunk IDs and rich payload metadata.
    """

    SECTION_PATTERN = re.compile(
        r'(?:^|\n)(?:(PART\s+[IVXLCDM\d]+[^\n]*)|(CHAPTER\s+[IVXLCDM\d]+[^\n]*)|((?:Section|Article|Rule|Order|Clause|Paragraph)\s+([A-Za-z0-9\-\(\)]+)(?:\s*[:\.\-]\s*([^\n]+))?))',
        re.IGNORECASE
    )

    @classmethod
    def chunk_document(cls, doc_meta: Dict[str, Any], pages_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        chunks = []
        doc_id = doc_meta["document_id"]
        canonical_title = doc_meta["canonical_title"]
        jurisdiction = doc_meta["jurisdiction"]
        province = doc_meta.get("province")
        legal_status = doc_meta.get("legal_status", "in_force")
        version_label = doc_meta.get("version_label", "verified-2026")
        source_url = doc_meta.get("official_source_url", "")
        content_sha256 = doc_meta.get("content_sha256", "")
        language = doc_meta.get("language", "en")
        doc_type = doc_meta.get("document_type", "act")

        # Combine text while tracking page indices
        full_text_blocks = []
        for page in pages_data:
            p_num = page["page_number"]
            p_text = page["text"]
            full_text_blocks.append((p_num, p_text))

        current_part = None
        current_chapter = None
        current_section_label = "Section"
        current_section_num = None
        current_section_title = None
        current_buffer = []
        current_page_start = 1
        current_page_end = 1
        chunk_idx = 1

        for p_num, p_text in full_text_blocks:
            lines = p_text.split("\n")
            for line in lines:
                line_str = line.strip()
                if not line_str:
                    continue

                # Check for structural headers
                match = cls.SECTION_PATTERN.search(line_str)
                if match:
                    part_match, chap_match, full_sec, sec_num, sec_title = match.groups()
                    
                    if part_match:
                        current_part = part_match.strip()
                        continue
                    if chap_match:
                        current_chapter = chap_match.strip()
                        continue
                    if full_sec:
                        # Flush existing buffer
                        if current_buffer:
                            chunk_text = "\n".join(current_buffer).strip()
                            if len(chunk_text) > 40:
                                chunk_id = cls._generate_chunk_id(doc_id, current_section_num, chunk_idx)
                                breadcrumb = f"[{canonical_title} • {jurisdiction.upper()}"
                                if province:
                                    breadcrumb += f" ({province.upper()})"
                                if current_section_num:
                                    breadcrumb += f" • {current_section_label} {current_section_num}"
                                if current_section_title:
                                    breadcrumb += f": {current_section_title}"
                                breadcrumb += "]\n"

                                chunks.append({
                                    "document_id": doc_id,
                                    "chunk_id": chunk_id,
                                    "canonical_title": canonical_title,
                                    "document_type": doc_type,
                                    "jurisdiction": jurisdiction,
                                    "province": province,
                                    "legal_status": legal_status,
                                    "version_label": version_label,
                                    "article_number": current_section_num if "Article" in current_section_label else None,
                                    "section_number": current_section_num if "Section" in current_section_label else None,
                                    "section_heading": current_section_title,
                                    "page_start": current_page_start,
                                    "page_end": current_page_end,
                                    "paragraph_start": None,
                                    "paragraph_end": None,
                                    "language": language,
                                    "source_url": source_url,
                                    "content_sha256": content_sha256,
                                    "chunk_index": chunk_idx,
                                    "text": breadcrumb + chunk_text
                                })
                                chunk_idx += 1

                        # Start new section
                        current_section_num = sec_num.strip() if sec_num else None
                        current_section_title = sec_title.strip() if sec_title else line_str
                        if "Article" in line_str:
                            current_section_label = "Article"
                        elif "Rule" in line_str:
                            current_section_label = "Rule"
                        elif "Order" in line_str:
                            current_section_label = "Order"
                        elif "Paragraph" in line_str:
                            current_section_label = "Paragraph"
                        else:
                            current_section_label = "Section"
                            
                        current_buffer = [line_str]
                        current_page_start = p_num
                        current_page_end = p_num
                        continue

                current_buffer.append(line_str)
                current_page_end = p_num

        # Flush final buffer
        if current_buffer:
            chunk_text = "\n".join(current_buffer).strip()
            if len(chunk_text) > 40:
                chunk_id = cls._generate_chunk_id(doc_id, current_section_num, chunk_idx)
                breadcrumb = f"[{canonical_title} • {jurisdiction.upper()}"
                if province:
                    breadcrumb += f" ({province.upper()})"
                if current_section_num:
                    breadcrumb += f" • {current_section_label} {current_section_num}"
                if current_section_title:
                    breadcrumb += f": {current_section_title}"
                breadcrumb += "]\n"

                chunks.append({
                    "document_id": doc_id,
                    "chunk_id": chunk_id,
                    "canonical_title": canonical_title,
                    "document_type": doc_type,
                    "jurisdiction": jurisdiction,
                    "province": province,
                    "legal_status": legal_status,
                    "version_label": version_label,
                    "article_number": current_section_num if "Article" in current_section_label else None,
                    "section_number": current_section_num if "Section" in current_section_label else None,
                    "section_heading": current_section_title,
                    "page_start": current_page_start,
                    "page_end": current_page_end,
                    "paragraph_start": None,
                    "paragraph_end": None,
                    "language": language,
                    "source_url": source_url,
                    "content_sha256": content_sha256,
                    "chunk_index": chunk_idx,
                    "text": breadcrumb + chunk_text
                })

        return chunks

    @staticmethod
    def _generate_chunk_id(doc_id: str, sec_num: str, chunk_idx: int) -> str:
        safe_sec = re.sub(r'[^a-zA-Z0-9]', '_', str(sec_num)).lower() if sec_num else "gen"
        return f"{doc_id}_{safe_sec}_{chunk_idx:04d}"
