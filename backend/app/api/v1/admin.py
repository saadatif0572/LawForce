import os
import shutil
import hashlib
from typing import Optional, List, Dict, Any
from pathlib import Path
from datetime import datetime, timezone
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, status, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from backend.app.core.auth import require_admin_user, AuthUser
from backend.app.core.config import settings
from backend.app.db.session import get_db
from backend.app.db.models import DocumentRegistry, DocumentVersion, IngestionJob, UserFeedback, AuditEvent
from backend.app.services.ingestion.ingestion_pipeline import IngestionPipeline

router = APIRouter(prefix="/admin", tags=["Admin & Corpus Management"])

@router.get("/corpus/stats")
def get_corpus_statistics(
    admin_user: AuthUser = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    total_docs = db.query(DocumentRegistry).count()
    
    # Jurisdiction breakdown
    jur_counts = db.query(
        DocumentRegistry.jurisdiction, func.count(DocumentRegistry.id)
    ).group_by(DocumentRegistry.jurisdiction).all()
    
    # Province breakdown
    prov_counts = db.query(
        DocumentRegistry.province, func.count(DocumentRegistry.id)
    ).filter(DocumentRegistry.province.isnot(None)).group_by(DocumentRegistry.province).all()
    
    # Type breakdown
    type_counts = db.query(
        DocumentRegistry.document_type, func.count(DocumentRegistry.id)
    ).group_by(DocumentRegistry.document_type).all()
    
    # Status breakdown
    status_counts = db.query(
        DocumentRegistry.legal_status, func.count(DocumentRegistry.id)
    ).group_by(DocumentRegistry.legal_status).all()

    # Feedback statistics
    pos_feedback = db.query(UserFeedback).filter(UserFeedback.rating == 1).count()
    neg_feedback = db.query(UserFeedback).filter(UserFeedback.rating == -1).count()

    return {
        "total_documents": total_docs,
        "mandatory_target": 500,
        "coverage_percentage": round((total_docs / 500.0) * 100, 1) if total_docs else 0,
        "jurisdictions": {k: v for k, v in jur_counts},
        "provinces": {k: v for k, v in prov_counts},
        "document_types": {k: v for k, v in type_counts},
        "legal_status": {k: v for k, v in status_counts},
        "feedback": {
            "positive": pos_feedback,
            "negative": neg_feedback,
            "satisfaction_rate": round((pos_feedback / (pos_feedback + neg_feedback)) * 100, 1) if (pos_feedback + neg_feedback) > 0 else 100.0
        },
        "last_updated": datetime.now(timezone.utc).isoformat()
    }

@router.get("/ingestion/jobs")
def list_ingestion_jobs(
    admin_user: AuthUser = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    jobs = db.query(IngestionJob).order_by(IngestionJob.started_at.desc()).limit(20).all()
    return [
        {
            "id": j.id,
            "job_type": j.job_type,
            "status": j.status,
            "total_documents": j.total_documents,
            "processed_documents": j.processed_documents,
            "total_chunks": j.total_chunks,
            "error_message": j.error_message,
            "started_at": j.started_at.isoformat() if j.started_at else None,
            "completed_at": j.completed_at.isoformat() if j.completed_at else None
        }
        for j in jobs
    ]

@router.post("/ingestion/run")
def trigger_ingestion_job(
    background_tasks: BackgroundTasks,
    admin_user: AuthUser = Depends(require_admin_user)
):
    pipeline = IngestionPipeline()
    background_tasks.add_task(pipeline.run_full_ingestion)
    return {
        "status": "triggered",
        "message": "Full 500-PDF corpus ingestion pipeline has been queued in background."
    }

@router.post("/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    canonical_title: str = Form(...),
    document_type: str = Form("act"),
    jurisdiction: str = Form("federal"),
    province: Optional[str] = Form(None),
    authority: str = Form("Parliament of Pakistan"),
    subject_categories: str = Form("administrative"),
    official_source_url: str = Form("https://pakistancode.gov.pk"),
    admin_user: AuthUser = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only official PDF documents are supported.")
        
    doc_id = Path(file.filename).stem.lower().replace(" ", "_")
    target_path = Path(settings.DATA_RAW_DIR) / f"{doc_id}.pdf"
    
    # Save file and calculate SHA256
    sha = hashlib.sha256()
    with open(target_path, "wb") as buffer:
        while chunk := await file.read(8192):
            buffer.write(chunk)
            sha.update(chunk)
            
    sha256_hash = sha.hexdigest()
    
    # Register in DB
    existing = db.query(DocumentRegistry).filter_by(id=doc_id).first()
    if not existing:
        doc = DocumentRegistry(
            id=doc_id,
            canonical_title=canonical_title,
            short_title=canonical_title,
            document_type=document_type,
            jurisdiction=jurisdiction,
            province=province,
            authority=authority,
            subject_categories=subject_categories,
            official_source_url=official_source_url,
            local_file_path=f"data/raw/{doc_id}.pdf",
            content_sha256=sha256_hash,
            mime_type="application/pdf",
            legal_status="in_force",
            verification_status="verified",
            is_official_pdf=True
        )
        db.add(doc)
    else:
        existing.canonical_title = canonical_title
        existing.content_sha256 = sha256_hash
        
    db.commit()
    
    return {
        "status": "success",
        "document_id": doc_id,
        "sha256": sha256_hash,
        "message": f"Successfully registered and saved {file.filename}"
    }

@router.delete("/documents/{document_id}")
def delete_document(
    document_id: str,
    admin_user: AuthUser = Depends(require_admin_user),
    db: Session = Depends(get_db)
):
    doc = db.query(DocumentRegistry).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    db.delete(doc)
    db.commit()
    return {"status": "deleted", "document_id": document_id}
