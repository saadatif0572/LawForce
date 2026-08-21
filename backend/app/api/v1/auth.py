from fastapi import APIRouter, Depends
from backend.app.core.auth import get_current_user, AuthUser
from backend.app.db.session import get_db
from backend.app.db.models import Profile
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth", tags=["Authentication & User"])

@router.get("/me")
def get_current_user_profile(
    user: AuthUser = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    profile = db.query(Profile).filter_by(supabase_uid=user.user_id).first()
    if not profile:
        profile = Profile(
            supabase_uid=user.user_id,
            email=user.email,
            full_name=user.email.split("@")[0].title(),
            role=user.role
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
    return {
        "id": profile.id,
        "supabase_uid": profile.supabase_uid,
        "email": profile.email,
        "full_name": profile.full_name,
        "role": profile.role,
        "created_at": profile.created_at.isoformat()
    }
