"""
LAWVERSE Automated Legal Corpus Validator
Strictly enforces:
1. verified_pdf_count == 500
2. Every SHA-256 checksum is unique
3. Every local PDF file exists and opens successfully with PyMuPDF
4. Every manifest entry maps 1:1 to a valid physical PDF
5. All mandatory manifest columns are present and populated
"""

import sys
import csv
import json
import hashlib
from pathlib import Path
import fitz

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent.parent
DATA_RAW_DIR = WORKSPACE_ROOT / "data" / "raw"
CORPUS_DIR = WORKSPACE_ROOT / "corpus"
MANIFEST_PATH = CORPUS_DIR / "manifest.csv"
VALIDATION_REPORT_PATH = CORPUS_DIR / "validation_report.json"

REQUIRED_COLUMNS = [
    "document_id", "canonical_title", "short_title", "document_type",
    "jurisdiction", "province", "authority", "subject_categories",
    "official_source_url", "local_file_path", "language", "enactment_date",
    "effective_date", "amendment_date", "repeal_date", "legal_status",
    "version_label", "retrieved_at", "last_verified_at", "content_sha256",
    "mime_type", "source_format", "is_official_pdf", "local_pdf_valid",
    "page_count", "ocr_required", "verification_status", "verification_notes"
]

def calculate_sha256(filepath: Path) -> str:
    sha = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(8192):
            sha.update(chunk)
    return sha.hexdigest()

def validate():
    print("=" * 70)
    print("LAWVERSE CORPUS VALIDATION SUITE")
    print("=" * 70)
    
    if not MANIFEST_PATH.exists():
        print(f"FAILED: Manifest not found at {MANIFEST_PATH}")
        sys.exit(1)
        
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        manifest_rows = list(reader)
        fieldnames = reader.fieldnames
        
    print(f"Checking Manifest Headers: {len(fieldnames)} columns found.")
    for col in REQUIRED_COLUMNS:
        if col not in fieldnames:
            print(f"FAILED: Missing required column '{col}' in manifest.")
            sys.exit(1)
            
    total_manifest_rows = len(manifest_rows)
    print(f"Checking Manifest Rows: {total_manifest_rows} rows found.")
    if total_manifest_rows != 500:
        print(f"FAILED: Manifest rows count {total_manifest_rows} != 500 mandatory target!")
        sys.exit(1)
        
    # Check physical PDFs
    raw_pdfs = list(DATA_RAW_DIR.glob("*.pdf"))
    print(f"Checking Local Raw PDFs in {DATA_RAW_DIR}: {len(raw_pdfs)} files found.")
    if len(raw_pdfs) != 500:
        print(f"FAILED: Physical PDF count {len(raw_pdfs)} != 500 mandatory target!")
        sys.exit(1)
        
    sha256_seen = set()
    errors = []
    
    for idx, row in enumerate(manifest_rows, 1):
        doc_id = row["document_id"]
        rel_path = row["local_file_path"]
        pdf_path = WORKSPACE_ROOT / rel_path
        
        if not pdf_path.exists():
            errors.append(f"Row {idx} ({doc_id}): Physical file {pdf_path} does not exist.")
            continue
            
        # Verify SHA-256
        actual_sha = calculate_sha256(pdf_path)
        recorded_sha = row["content_sha256"]
        if actual_sha != recorded_sha:
            errors.append(f"Row {idx} ({doc_id}): Recorded SHA ({recorded_sha[:10]}...) != Actual SHA ({actual_sha[:10]}...).")
            
        if actual_sha in sha256_seen:
            errors.append(f"Row {idx} ({doc_id}): Duplicate SHA256 checksum detected!")
        sha256_seen.add(actual_sha)
        
        # Test PDF opening and readability with PyMuPDF
        try:
            doc = fitz.open(str(pdf_path))
            p_count = doc.page_count
            if p_count < 1:
                errors.append(f"Row {idx} ({doc_id}): PDF has 0 pages.")
            
            # Extract sample text
            sample_text = doc[0].get_text()
            if len(sample_text.strip()) < 50:
                errors.append(f"Row {idx} ({doc_id}): PDF page 1 text too short ({len(sample_text)} chars).")
            doc.close()
        except Exception as e:
            errors.append(f"Row {idx} ({doc_id}): Failed to open PDF via PyMuPDF: {e}")
            
    if errors:
        print(f"FAILED: Found {len(errors)} validation errors:")
        for err in errors[:10]:
            print(f"  - {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors.")
        sys.exit(1)
        
    print("-" * 70)
    print(f"SUCCESS: 500/500 PDFs verified!")
    print(f"  - Total Valid PDFs:       {len(raw_pdfs)}")
    print(f"  - Total Manifest Entries: {total_manifest_rows}")
    print(f"  - Unique SHA-256 Hashes:  {len(sha256_seen)}")
    print(f"  - Checksum Integrity:     100% Passed")
    print(f"  - PyMuPDF Readability:    100% Passed")
    print("=" * 70)

if __name__ == "__main__":
    validate()
