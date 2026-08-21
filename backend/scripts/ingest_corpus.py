"""
LAWVERSE Corpus Ingestion CLI
Reads the 500-PDF manifest, parses sections, generates embeddings,
upserts into Qdrant collection, and syncs database registry.
"""

import sys
import logging
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.services.ingestion.ingestion_pipeline import IngestionPipeline

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

def main():
    print("=" * 70)
    print("LAWVERSE 500-PDF LEGAL CORPUS INGESTION")
    print("=" * 70)
    
    pipeline = IngestionPipeline()
    result = pipeline.run_full_ingestion()
    
    print("-" * 70)
    print("Ingestion Completed Successfully!")
    print(f"  - Job ID:              {result['job_id']}")
    print(f"  - Processed Documents: {result['processed_documents']}")
    print(f"  - Total Indexed Chunks: {result['total_chunks']}")
    print(f"  - Qdrant Collection:   {result['qdrant_collection']}")
    print("=" * 70)

if __name__ == "__main__":
    main()
