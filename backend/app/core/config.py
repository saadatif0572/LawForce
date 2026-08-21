import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "LawForce"
    APP_ENV: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    FRONTEND_ORIGIN: str = "http://localhost:5173"
    
    # Supabase Configuration
    SUPABASE_URL: str = "https://your-project.supabase.co"
    SUPABASE_JWKS_URL: str = "https://your-project.supabase.co/auth/v1/.well-known/jwks.json"
    SUPABASE_JWT_SECRET: str = "replace_with_jwt_secret_if_applicable"
    
    # Database
    DATABASE_URL: str = "sqlite:///./lawverse.db"
    
    # Qdrant Vector Store
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str = ""
    QDRANT_COLLECTION: str = "lawverse_legal_documents"
    
    # Groq API Configuration
    GROQ_API_KEY: str = "replace_with_new_key"
    GROQ_MODEL: str = "llama-3.3-70b-versatile"
    
    # Embedding Model Configuration
    EMBEDDING_MODEL: str = "BAAI/bge-m3"
    EMBEDDING_DIMENSION: int = 1024
    
    # Corpus Paths
    DATA_RAW_DIR: str = "./data/raw"
    CORPUS_MANIFEST_PATH: str = "./corpus/manifest.csv"
    
    # Minimum Relevance Threshold for RAG Evidence
    MIN_RELEVANCE_THRESHOLD: float = 0.35
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent.parent / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
