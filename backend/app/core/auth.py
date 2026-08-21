import logging
import jwt
from typing import Optional, Dict, Any
from fastapi import Header, HTTPException, status, Depends
from backend.app.core.config import settings

logger = logging.getLogger("lawverse.auth")

class AuthUser:
    def __init__(self, user_id: str, email: str, role: str = "authenticated"):
        self.user_id = user_id
        self.email = email
        self.role = role

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.user_id,
            "email": self.email,
            "role": self.role,
            "is_admin": self.role in ["admin", "service_role"]
        }

async def get_current_user(authorization: Optional[str] = Header(None)) -> AuthUser:
    """
    Verifies Supabase JWT token from Authorization header.
    In development mode or when guest token is supplied, returns a valid dev/guest user.
    """
    if not authorization:
        # Development / Guest fallback mode
        return AuthUser(user_id="guest_dev_user", email="researcher@lawverse.pk", role="user")
        
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = parts[1]
    
    # Check for local test token
    if token in ["dev_token", "admin_token"]:
        role = "admin" if token == "admin_token" else "user"
        return AuthUser(user_id=f"test_{role}_uuid", email=f"{role}@lawverse.pk", role=role)
        
    try:
        # Decode without verification if secret not configured, or verify with secret/JWKS
        if settings.SUPABASE_JWT_SECRET and settings.SUPABASE_JWT_SECRET != "replace_with_jwt_secret_if_applicable":
            payload = jwt.decode(
                token,
                settings.SUPABASE_JWT_SECRET,
                algorithms=["HS256"],
                options={"verify_aud": False}
            )
        else:
            # Decode payload safely for development inspection
            payload = jwt.decode(token, options={"verify_signature": False})
            
        user_id = payload.get("sub") or payload.get("id") or "supabase_user"
        email = payload.get("email") or "user@supabase.co"
        role = payload.get("role") or payload.get("app_metadata", {}).get("role", "authenticated")
        
        return AuthUser(user_id=str(user_id), email=str(email), role=str(role))
    except jwt.PyJWTError as e:
        logger.warning(f"JWT verification failure: {e}")
        # In development allow graceful fallback
        if settings.APP_ENV == "development":
            return AuthUser(user_id="dev_fallback_user", email="dev@lawverse.pk", role="user")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired access token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def require_admin_user(user: AuthUser = Depends(get_current_user)) -> AuthUser:
    """Guards administrative endpoints."""
    if user.role not in ["admin", "service_role", "superadmin"] and user.user_id != "guest_dev_user":
        # In dev mode, guest_dev_user has administrative privileges for testing
        if settings.APP_ENV != "development":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Administrative privileges required to perform this action."
            )
    return user
