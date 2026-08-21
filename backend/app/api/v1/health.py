from fastapi import APIRouter
from datetime import datetime, timezone
from backend.app.core.config import settings

router = APIRouter(tags=["Health & System"])

@router.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "LawForce Legal Assistant API",
        "environment": settings.APP_ENV,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@router.get("/readiness")
def readiness_check():
    return {
        "status": "ready",
        "groq_configured": bool(settings.GROQ_API_KEY and settings.GROQ_API_KEY != "replace_with_new_key"),
        "model": settings.GROQ_MODEL,
        "embedding_model": settings.EMBEDDING_MODEL,
        "qdrant_collection": settings.QDRANT_COLLECTION,
        "corpus_target": 500
    }
