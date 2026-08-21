import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from backend.app.db.session import Base

def utc_now():
    return datetime.now(timezone.utc)

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    supabase_uid = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=True)
    role = Column(String(64), default="user", nullable=False) # user, researcher, admin
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    chat_sessions = relationship("ChatSession", back_populates="user", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="user")


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True, nullable=False)
    description = Column(Text, nullable=True)
    permissions = Column(JSON, default=list)


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(64), ForeignKey("profiles.id", ondelete="CASCADE"), nullable=True)
    title = Column(String(255), default="New Legal Research Inquiry")
    language = Column(String(16), default="en") # en, ur
    jurisdiction_filter = Column(String(64), nullable=True) # federal, punjab, sindh, kp, balochistan, all
    created_at = Column(DateTime, default=utc_now)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)

    user = relationship("Profile", back_populates="chat_sessions")
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan", order_by="ChatMessage.created_at")


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(64), ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
    role = Column(String(32), nullable=False) # user, assistant, system
    content = Column(Text, nullable=False)
    confidence = Column(String(32), default="medium") # high, medium, low, ungrounded
    needs_clarification = Column(Boolean, default=False)
    disclaimer = Column(Text, default="General legal information only; not legal advice.")
    created_at = Column(DateTime, default=utc_now)

    session = relationship("ChatSession", back_populates="messages")
    sources = relationship("AnswerSource", back_populates="message", cascade="all, delete-orphan")
    feedback = relationship("UserFeedback", back_populates="message", cascade="all, delete-orphan")


class DocumentRegistry(Base):
    __tablename__ = "document_registry"

    id = Column(String(128), primary_key=True) # document_id
    canonical_title = Column(String(512), nullable=False, index=True)
    short_title = Column(String(255), nullable=True)
    document_type = Column(String(64), nullable=False, index=True) # act, ordinance, rules, constitution, judgment
    jurisdiction = Column(String(64), nullable=False, index=True) # federal, provincial
    province = Column(String(64), nullable=True, index=True) # punjab, sindh, kp, balochistan
    authority = Column(String(255), nullable=False)
    subject_categories = Column(String(512), index=True)
    official_source_url = Column(String(1024), nullable=False)
    local_file_path = Column(String(512), nullable=False)
    language = Column(String(16), default="en")
    enactment_date = Column(String(32), nullable=True)
    effective_date = Column(String(32), nullable=True)
    amendment_date = Column(String(32), nullable=True)
    repeal_date = Column(String(32), nullable=True)
    legal_status = Column(String(32), default="in_force", index=True) # in_force, amended, repealed, draft
    version_label = Column(String(64), default="verified-2026")
    content_sha256 = Column(String(64), unique=True, nullable=False)
    mime_type = Column(String(64), default="application/pdf")
    page_count = Column(Integer, default=1)
    is_official_pdf = Column(Boolean, default=True)
    verification_status = Column(String(32), default="verified")
    verification_notes = Column(Text, nullable=True)
    retrieved_at = Column(DateTime, default=utc_now)
    last_verified_at = Column(DateTime, default=utc_now)

    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")


class DocumentVersion(Base):
    __tablename__ = "document_versions"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    document_id = Column(String(128), ForeignKey("document_registry.id", ondelete="CASCADE"), nullable=False)
    version_label = Column(String(64), nullable=False)
    content_sha256 = Column(String(64), nullable=False)
    legal_status = Column(String(32), default="in_force")
    change_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    document = relationship("DocumentRegistry", back_populates="versions")


class IngestionJob(Base):
    __tablename__ = "ingestion_jobs"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    job_type = Column(String(64), default="full_corpus") # full_corpus, single_document, refresh
    status = Column(String(32), default="pending") # pending, running, completed, failed
    total_documents = Column(Integer, default=0)
    processed_documents = Column(Integer, default=0)
    total_chunks = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime, default=utc_now)
    completed_at = Column(DateTime, nullable=True)


class RetrievalEvent(Base):
    __tablename__ = "retrieval_events"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    query_text = Column(Text, nullable=False)
    language_detected = Column(String(16), default="en")
    jurisdiction_filter = Column(String(64), nullable=True)
    dense_results_count = Column(Integer, default=0)
    sparse_results_count = Column(Integer, default=0)
    fused_results_count = Column(Integer, default=0)
    top_score = Column(Float, default=0.0)
    execution_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime, default=utc_now)


class AnswerSource(Base):
    __tablename__ = "answer_sources"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(64), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    document_id = Column(String(128), nullable=False)
    title = Column(String(512), nullable=False)
    article_or_section = Column(String(255), nullable=True)
    jurisdiction = Column(String(64), nullable=False)
    legal_status = Column(String(32), default="in_force")
    page = Column(Integer, nullable=True)
    source_url = Column(String(1024), nullable=False)
    relevance_score = Column(Float, default=0.0)

    message = relationship("ChatMessage", back_populates="sources")


class UserFeedback(Base):
    __tablename__ = "user_feedback"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    message_id = Column(String(64), ForeignKey("chat_messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), ForeignKey("profiles.id", ondelete="SET NULL"), nullable=True)
    rating = Column(Integer, nullable=False) # 1 (up) or -1 (down)
    feedback_tag = Column(String(64), nullable=True) # inaccurate_citation, hallucination, wrong_jurisdiction, excellent
    comments = Column(Text, nullable=True)
    created_at = Column(DateTime, default=utc_now)

    message = relationship("ChatMessage", back_populates="feedback")
    user = relationship("Profile", back_populates="feedback")


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id = Column(String(64), primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String(64), nullable=False) # document_added, document_amended, ingestion_run, auth_login
    actor_id = Column(String(128), nullable=True)
    details = Column(JSON, default=dict)
    ip_address = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=utc_now)
