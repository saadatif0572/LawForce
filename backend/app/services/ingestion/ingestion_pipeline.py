import csv
import uuid
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from backend.app.core.config import settings
from backend.app.db.session import SessionLocal, init_db
from backend.app.db.models import DocumentRegistry, DocumentVersion, IngestionJob, AuditEvent
from backend.app.services.extraction.pdf_extractor import PDFExtractor
from backend.app.services.chunking.legal_chunker import LegalChunker
from backend.app.services.embeddings.embedding_service import EmbeddingService

logger = logging.getLogger("lawverse.ingestion")

class IngestionPipeline:
    """
    Idempotent Legal Ingestion Pipeline for the 500-PDF Pakistani Legal Corpus.
    Extracts text, builds structured legal chunks, generates embeddings,
    indexes into Qdrant vector database, and records state in PostgreSQL/SQLite.
    """

    def __init__(self):
        self.workspace_root = Path(__file__).resolve().parents[4]
        self.manifest_path = self.workspace_root / "corpus" / "manifest.csv"
        self.data_raw_dir = self.workspace_root / "data" / "raw"
        self.collection_name = settings.QDRANT_COLLECTION
        
        # Connect to Qdrant using singleton factory
        from backend.app.core.qdrant_client_factory import get_qdrant_client
        self.qdrant = get_qdrant_client()

    def run_full_ingestion(self, max_docs: Optional[int] = None) -> Dict[str, Any]:
        """Runs the complete end-to-end ingestion pipeline."""
        init_db()
        db = SessionLocal()
        
        # Create Ingestion Job Record
        job_id = str(uuid.uuid4())
        job = IngestionJob(
            id=job_id,
            job_type="full_corpus",
            status="running",
            started_at=datetime.now(timezone.utc)
        )
        db.add(job)
        db.commit()

        try:
            # 1. Initialize Qdrant Collection & Payload Indexes
            self._setup_qdrant_collection()
            
            # 2. Read Manifest
            if not self.manifest_path.exists():
                raise FileNotFoundError(f"Manifest not found at {self.manifest_path}")
                
            with open(self.manifest_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                manifest_rows = list(reader)
                
            total_manifest_docs = len(manifest_rows)
            job.total_documents = total_manifest_docs
            db.commit()
            
            docs_to_process = manifest_rows[:max_docs] if max_docs else manifest_rows
            
            total_chunks_indexed = 0
            processed_docs = 0
            
            # Batch upsert points
            points_batch = []
            
            for idx, row in enumerate(docs_to_process, 1):
                doc_id = row["document_id"]
                pdf_path = self.workspace_root / row["local_file_path"]
                
                if not pdf_path.exists():
                    logger.error(f"Missing PDF for {doc_id} at {pdf_path}")
                    continue
                    
                # 3. Extract text page-by-page
                pages_data = PDFExtractor.extract_pages(pdf_path)
                
                # 4. Legal-aware chunking
                chunks = LegalChunker.chunk_document(row, pages_data)
                
                # 5. Generate embeddings and create Qdrant Points
                for c in chunks:
                    vector = EmbeddingService.get_embedding(c["text"])
                    # Use deterministic integer/uuid point ID from chunk_id
                    point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, c["chunk_id"]))
                    
                    points_batch.append(
                        qmodels.PointStruct(
                            id=point_id,
                            vector=vector,
                            payload=c
                        )
                    )
                    
                total_chunks_indexed += len(chunks)
                processed_docs += 1
                
                # 6. Record/Update in PostgreSQL / DB
                self._upsert_document_registry(db, row)
                
                # Batch upsert into Qdrant every 50 chunks or at end
                if len(points_batch) >= 100:
                    self.qdrant.upsert(
                        collection_name=self.collection_name,
                        points=points_batch
                    )
                    points_batch = []
                    
                if idx % 50 == 0 or idx == len(docs_to_process):
                    logger.info(f"Ingested {idx}/{len(docs_to_process)} documents ({total_chunks_indexed} chunks)")
                    job.processed_documents = processed_docs
                    job.total_chunks = total_chunks_indexed
                    db.commit()

            # Flush remaining points
            if points_batch:
                self.qdrant.upsert(
                    collection_name=self.collection_name,
                    points=points_batch
                )

            job.status = "completed"
            job.processed_documents = processed_docs
            job.total_chunks = total_chunks_indexed
            job.completed_at = datetime.now(timezone.utc)
            
            # Audit log
            audit = AuditEvent(
                event_type="ingestion_run",
                details={
                    "job_id": job_id,
                    "processed_documents": processed_docs,
                    "total_chunks": total_chunks_indexed
                }
            )
            db.add(audit)
            db.commit()
            
            return {
                "job_id": job_id,
                "status": "completed",
                "processed_documents": processed_docs,
                "total_chunks": total_chunks_indexed,
                "qdrant_collection": self.collection_name
            }
            
        except Exception as e:
            logger.error(f"Ingestion failed: {e}")
            job.status = "failed"
            job.error_message = str(e)
            job.completed_at = datetime.now(timezone.utc)
            db.commit()
            raise
        finally:
            db.close()

    def _setup_qdrant_collection(self):
        """Creates collection and payload indexes for metadata filtering."""
        collections = [c.name for c in self.qdrant.get_collections().collections]
        if self.collection_name not in collections:
            logger.info(f"Creating Qdrant collection: {self.collection_name}")
            self.qdrant.create_collection(
                collection_name=self.collection_name,
                vectors_config=qmodels.VectorParams(
                    size=settings.EMBEDDING_DIMENSION,
                    distance=qmodels.Distance.COSINE
                )
            )
            
        # Create payload indexes for fast filtering
        index_fields = [
            "jurisdiction", "province", "document_type", "legal_status",
            "language", "document_id", "section_number", "article_number", "canonical_title"
        ]
        for field in index_fields:
            try:
                self.qdrant.create_payload_index(
                    collection_name=self.collection_name,
                    field_name=field,
                    field_schema=qmodels.PayloadSchemaType.KEYWORD
                )
            except Exception:
                pass

    def _upsert_document_registry(self, db, row: Dict[str, Any]):
        doc_id = row["document_id"]
        existing = db.query(DocumentRegistry).filter_by(id=doc_id).first()
        
        if not existing:
            doc = DocumentRegistry(
                id=doc_id,
                canonical_title=row["canonical_title"],
                short_title=row.get("short_title"),
                document_type=row["document_type"],
                jurisdiction=row["jurisdiction"],
                province=row.get("province") if row.get("province") else None,
                authority=row["authority"],
                subject_categories=row.get("subject_categories"),
                official_source_url=row["official_source_url"],
                local_file_path=row["local_file_path"],
                language=row.get("language", "en"),
                enactment_date=row.get("enactment_date"),
                effective_date=row.get("effective_date"),
                amendment_date=row.get("amendment_date"),
                repeal_date=row.get("repeal_date"),
                legal_status=row.get("legal_status", "in_force"),
                version_label=row.get("version_label", "verified-2026"),
                content_sha256=row["content_sha256"],
                mime_type=row.get("mime_type", "application/pdf"),
                page_count=int(row.get("page_count", 1)),
                is_official_pdf=row.get("is_official_pdf", "True").lower() == "true",
                verification_status=row.get("verification_status", "verified"),
                verification_notes=row.get("verification_notes")
            )
            db.add(doc)
            # Add initial version
            ver = DocumentVersion(
                document_id=doc_id,
                version_label=row.get("version_label", "verified-2026"),
                content_sha256=row["content_sha256"],
                legal_status=row.get("legal_status", "in_force"),
                change_summary="Initial verified corpus ingestion"
            )
            db.add(ver)
        else:
            # Update existing
            existing.canonical_title = row["canonical_title"]
            existing.legal_status = row.get("legal_status", "in_force")
            existing.content_sha256 = row["content_sha256"]
            existing.last_verified_at = datetime.now(timezone.utc)
            
        db.commit()
