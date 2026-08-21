from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.db.models import DocumentRegistry

router = APIRouter(prefix="/sources", tags=["Corpus Sources Library"])

@router.get("")
def list_corpus_sources(
    jurisdiction: Optional[str] = Query(None, description="federal or provincial"),
    province: Optional[str] = Query(None, description="punjab, sindh, kp, balochistan"),
    document_type: Optional[str] = Query(None, description="act, ordinance, rules, constitution, judgment"),
    legal_status: Optional[str] = Query(None, description="in_force, amended, repealed"),
    search: Optional[str] = Query(None, description="Search term in title"),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db)
):
    query = db.query(DocumentRegistry)
    
    if jurisdiction and jurisdiction.lower() != "all":
        query = query.filter(DocumentRegistry.jurisdiction == jurisdiction.lower())
    if province:
        query = query.filter(DocumentRegistry.province == province.lower())
    if document_type:
        query = query.filter(DocumentRegistry.document_type == document_type.lower())
    if legal_status:
        query = query.filter(DocumentRegistry.legal_status == legal_status.lower())
    if search:
        query = query.filter(DocumentRegistry.canonical_title.ilike(f"%{search}%"))
        
    total_count = query.count()
    items = query.order_by(DocumentRegistry.canonical_title.asc()).offset((page - 1) * limit).limit(limit).all()
    
    results = [
        {
            "document_id": doc.id,
            "canonical_title": doc.canonical_title,
            "short_title": doc.short_title,
            "document_type": doc.document_type,
            "jurisdiction": doc.jurisdiction,
            "province": doc.province,
            "authority": doc.authority,
            "subject_categories": doc.subject_categories,
            "official_source_url": doc.official_source_url,
            "enactment_date": doc.enactment_date,
            "legal_status": doc.legal_status,
            "version_label": doc.version_label,
            "content_sha256": doc.content_sha256,
            "page_count": doc.page_count,
            "is_official_pdf": doc.is_official_pdf,
            "verification_status": doc.verification_status,
            "last_verified_at": doc.last_verified_at.isoformat() if doc.last_verified_at else None
        }
        for doc in items
    ]
    
    return {
        "total": total_count,
        "page": page,
        "limit": limit,
        "total_pages": (total_count + limit - 1) // limit,
        "sources": results
    }

@router.get("/{document_id}")
def get_source_details(
    document_id: str,
    db: Session = Depends(get_db)
):
    doc = db.query(DocumentRegistry).filter_by(id=document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found in corpus registry")
        
    versions_out = [
        {
            "version_label": v.version_label,
            "content_sha256": v.content_sha256,
            "legal_status": v.legal_status,
            "change_summary": v.change_summary,
            "created_at": v.created_at.isoformat()
        }
        for v in doc.versions
    ]
    
    return {
        "document_id": doc.id,
        "canonical_title": doc.canonical_title,
        "short_title": doc.short_title,
        "document_type": doc.document_type,
        "jurisdiction": doc.jurisdiction,
        "province": doc.province,
        "authority": doc.authority,
        "subject_categories": doc.subject_categories,
        "official_source_url": doc.official_source_url,
        "local_file_path": doc.local_file_path,
        "language": doc.language,
        "enactment_date": doc.enactment_date,
        "effective_date": doc.effective_date,
        "amendment_date": doc.amendment_date,
        "repeal_date": doc.repeal_date,
        "legal_status": doc.legal_status,
        "version_label": doc.version_label,
        "content_sha256": doc.content_sha256,
        "page_count": doc.page_count,
        "is_official_pdf": doc.is_official_pdf,
        "verification_status": doc.verification_status,
        "verification_notes": doc.verification_notes,
        "last_verified_at": doc.last_verified_at.isoformat() if doc.last_verified_at else None,
        "versions": versions_out
    }
