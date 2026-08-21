from typing import Optional
from pydantic import BaseModel, Field
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.core.auth import get_current_user, AuthUser
from backend.app.db.session import get_db
from backend.app.db.models import UserFeedback, ChatMessage

router = APIRouter(prefix="/feedback", tags=["User Feedback"])

class FeedbackRequest(BaseModel):
    message_id: str
    rating: int = Field(..., ge=-1, le=1, description="1 for positive, -1 for negative")
    feedback_tag: Optional[str] = Field(None, description="inaccurate_citation, helpful, hallucination, etc.")
    comments: Optional[str] = Field(None, max_length=1000)

@router.post("")
def submit_feedback(
    req: FeedbackRequest,
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    msg = db.query(ChatMessage).filter_by(id=req.message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Referenced message not found")
        
    feedback = UserFeedback(
        message_id=req.message_id,
        rating=req.rating,
        feedback_tag=req.feedback_tag,
        comments=req.comments
    )
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return {
        "status": "success",
        "feedback_id": feedback.id,
        "message": "Thank you for your feedback. This helps improve LAWVERSE legal research precision."
    }
