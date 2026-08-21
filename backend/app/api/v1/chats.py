from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.auth import get_current_user, AuthUser
from backend.app.db.session import get_db
from backend.app.db.models import ChatSession, ChatMessage

router = APIRouter(prefix="/chats", tags=["Chat History Management"])

class ChatSessionSummary(BaseModel):
    id: str
    title: str
    language: str
    jurisdiction_filter: Optional[str] = None
    created_at: str
    message_count: int

@router.get("", response_model=List[ChatSessionSummary])
def list_user_chats(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    sessions = db.query(ChatSession).order_by(ChatSession.updated_at.desc()).limit(50).all()
    return [
        {
            "id": s.id,
            "title": s.title,
            "language": s.language,
            "jurisdiction_filter": s.jurisdiction_filter,
            "created_at": s.created_at.isoformat(),
            "message_count": len(s.messages)
        }
        for s in sessions
    ]

@router.get("/{chat_id}")
def get_chat_session_details(
    chat_id: str,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter_by(id=chat_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
        
    messages_out = []
    for msg in session.messages:
        sources_out = [
            {
                "document_id": src.document_id,
                "title": src.title,
                "article_or_section": src.article_or_section,
                "jurisdiction": src.jurisdiction,
                "legal_status": src.legal_status,
                "page": src.page,
                "source_url": src.source_url,
                "relevance_score": src.relevance_score
            }
            for src in msg.sources
        ]
        messages_out.append({
            "id": msg.id,
            "role": msg.role,
            "content": msg.content,
            "confidence": msg.confidence,
            "needs_clarification": msg.needs_clarification,
            "disclaimer": msg.disclaimer,
            "created_at": msg.created_at.isoformat(),
            "sources": sources_out
        })
        
    return {
        "id": session.id,
        "title": session.title,
        "language": session.language,
        "jurisdiction_filter": session.jurisdiction_filter,
        "created_at": session.created_at.isoformat(),
        "messages": messages_out
    }

@router.delete("/{chat_id}")
def delete_chat_session(
    chat_id: str,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    session = db.query(ChatSession).filter_by(id=chat_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Chat session not found")
    db.delete(session)
    db.commit()
    return {"status": "deleted", "chat_id": chat_id}
