import sys
import logging
from pathlib import Path
from qdrant_client import QdrantClient
from backend.app.core.config import settings

logger = logging.getLogger("lawverse.qdrant_factory")

def get_qdrant_client() -> QdrantClient:
    """
    Returns a process-wide shared singleton QdrantClient instance
    to prevent local disk lock conflicts.
    """
    if hasattr(sys, "_lawverse_qdrant_client") and sys._lawverse_qdrant_client is not None:
        return sys._lawverse_qdrant_client

    workspace_root = Path(__file__).resolve().parents[3]
    storage_path = workspace_root / "data" / "qdrant_storage"
    storage_path.mkdir(parents=True, exist_ok=True)

    if settings.QDRANT_URL and settings.QDRANT_URL.strip():
        try:
            client = QdrantClient(
                url=settings.QDRANT_URL.strip(),
                api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                timeout=2.0
            )
            client.get_collections()
            sys._lawverse_qdrant_client = client
            return sys._lawverse_qdrant_client
        except Exception as e:
            logger.info(f"Qdrant server at {settings.QDRANT_URL} unavailable, falling back to local disk storage.")

    # Local disk mode - persistent across all tests in process
    client = QdrantClient(path=str(storage_path))
    sys._lawverse_qdrant_client = client
    return sys._lawverse_qdrant_client
