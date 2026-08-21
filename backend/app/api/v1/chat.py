import time
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from backend.app.core.auth import get_current_user, AuthUser
from backend.app.db.session import get_db
from backend.app.db.models import ChatSession, ChatMessage, AnswerSource, RetrievalEvent
from backend.app.services.retrieval.hybrid_retriever import HybridRetriever
from backend.app.services.generation.groq_generator import GroqGenerator

router = APIRouter(prefix="/chat", tags=["Legal Chat & RAG QA"])

_retriever = None
_generator = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever

def get_generator():
    global _generator
    if _generator is None:
        _generator = GroqGenerator()
    return _generator

class QueryRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=2000, description="Legal question in plain English or Urdu")
    chat_id: Optional[str] = Field(None, description="Existing chat session UUID")
    jurisdiction: Optional[str] = Field("all", description="Jurisdiction filter (federal, punjab, sindh, kp, balochistan, all)")
    province: Optional[str] = Field(None, description="Specific province filter")
    language: Optional[str] = Field("en", description="Language preference (en or ur)")

class SourceCitation(BaseModel):
    document_id: str
    title: str
    article_or_section: Optional[str] = None
    section_heading: Optional[str] = None
    jurisdiction: str
    province: Optional[str] = None
    legal_status: str
    page: Optional[int] = 1
    source_url: str
    relevance_score: float

class QueryResponse(BaseModel):
    chat_id: str
    message_id: str
    answer_markdown: str
    language: str
    confidence: str
    needs_clarification: bool
    disclaimer: str
    sources: List[SourceCitation]

@router.post("/query", response_model=QueryResponse)
def execute_query(
    req: QueryRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    start_time = time.time()
    retriever = get_retriever()
    generator = get_generator()
    
    # 1. Resolve or Create Chat Session
    if req.chat_id:
        session = db.query(ChatSession).filter_by(id=req.chat_id).first()
        if not session:
            session = ChatSession(
                id=req.chat_id,
                title=req.query[:60],
                language=req.language,
                jurisdiction_filter=req.jurisdiction
            )
            db.add(session)
            db.commit()
    else:
        session = ChatSession(
            title=req.query[:60],
            language=req.language,
            jurisdiction_filter=req.jurisdiction
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        
    # 2. Record User Message
    user_msg = ChatMessage(
        session_id=session.id,
        role="user",
        content=req.query
    )
    db.add(user_msg)
    db.commit()

    # 3. Hybrid Retrieval
    retrieved_chunks = retriever.search(
        query=req.query,
        jurisdiction_filter=req.jurisdiction if req.jurisdiction != "all" else None,
        province_filter=req.province,
        top_k=8
    )

    # 4. Generate Grounded Response via Groq
    gen_result = generator.generate_response(
        question=req.query,
        retrieved_chunks=retrieved_chunks,
        language=req.language
    )

    # 5. Save Assistant Message and Sources
    assistant_msg = ChatMessage(
        session_id=session.id,
        role="assistant",
        content=gen_result["answer_markdown"],
        confidence=gen_result["confidence"],
        needs_clarification=gen_result["needs_clarification"],
        disclaimer=gen_result["disclaimer"]
    )
    db.add(assistant_msg)
    db.commit()
    db.refresh(assistant_msg)

    # Save Sources
    for s in gen_result["sources"]:
        src_row = AnswerSource(
            message_id=assistant_msg.id,
            document_id=s["document_id"],
            title=s["title"],
            article_or_section=s.get("article_or_section"),
            jurisdiction=s["jurisdiction"],
            legal_status=s.get("legal_status", "in_force"),
            page=s.get("page", 1),
            source_url=s["source_url"],
            relevance_score=s.get("relevance_score", 0.0)
        )
        db.add(src_row)
        
    # Record Retrieval Event Telemetry
    elapsed_ms = (time.time() - start_time) * 1000.0
    telemetry = RetrievalEvent(
        query_text=req.query,
        language_detected=req.language,
        jurisdiction_filter=req.jurisdiction,
        fused_results_count=len(retrieved_chunks),
        top_score=retrieved_chunks[0]["relevance_score"] if retrieved_chunks else 0.0,
        execution_time_ms=elapsed_ms
    )
    db.add(telemetry)
    db.commit()

    return {
        "chat_id": session.id,
        "message_id": assistant_msg.id,
        "answer_markdown": gen_result["answer_markdown"],
        "language": gen_result["language"],
        "confidence": gen_result["confidence"],
        "needs_clarification": gen_result["needs_clarification"],
        "disclaimer": gen_result["disclaimer"],
        "sources": gen_result["sources"]
    }

@router.post("/query/stream")
async def execute_query_stream(
    req: QueryRequest,
    user: AuthUser = Depends(get_current_user)
):
    """Streams token-by-token answer via Server-Sent Events (SSE)."""
    retriever = get_retriever()
    generator = get_generator()
    
    retrieved_chunks = retriever.search(
        query=req.query,
        jurisdiction_filter=req.jurisdiction if req.jurisdiction != "all" else None,
        province_filter=req.province,
        top_k=8
    )

    async def sse_event_generator():
        async for chunk in generator.generate_stream(
            question=req.query,
            retrieved_chunks=retrieved_chunks,
            language=req.language
        ):
            yield chunk

    return StreamingResponse(
        sse_event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
