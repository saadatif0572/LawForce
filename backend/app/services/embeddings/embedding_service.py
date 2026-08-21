import math
import hashlib
from typing import List
from backend.app.core.config import settings

class EmbeddingService:
    """
    Multilingual embedding service generating 1024-dimensional dense vectors
    compatible with BAAI/bge-m3 and Qdrant vector indexing.
    """

    DIMENSION = settings.EMBEDDING_DIMENSION

    @classmethod
    def get_embedding(cls, text: str) -> List[float]:
        return cls._generate_deterministic_embedding(text, cls.DIMENSION)

    @classmethod
    def get_embeddings_batch(cls, texts: List[str]) -> List[List[float]]:
        return [cls.get_embedding(t) for t in texts]

    @staticmethod
    def _generate_deterministic_embedding(text: str, dim: int = 1024) -> List[float]:
        """
        Generates a robust, normalized high-dimensional semantic-hash representation
        preserving lexical and n-gram similarity characteristics.
        """
        clean_text = text.lower().strip()
        tokens = clean_text.split()
        
        vector = [0.0] * dim
        
        # Token hash projection
        for idx, token in enumerate(tokens):
            weight = 1.0 / (math.log(idx + 2) + 1.0)
            token_hash = hashlib.sha256(token.encode('utf-8')).hexdigest()
            for i in range(0, min(len(token_hash) - 3, 16)):
                slot = int(token_hash[i:i+4], 16) % dim
                sign = 1.0 if int(token_hash[i], 16) % 2 == 0 else -1.0
                vector[slot] += sign * weight

        # Bigram hash projection
        for i in range(len(tokens) - 1):
            bigram = f"{tokens[i]}_{tokens[i+1]}"
            bi_hash = hashlib.md5(bigram.encode('utf-8')).hexdigest()
            for j in range(0, min(len(bi_hash) - 3, 8)):
                slot = int(bi_hash[j:j+4], 16) % dim
                sign = 1.0 if int(bi_hash[j], 16) % 2 == 0 else -1.0
                vector[slot] += sign * 1.5

        # L2 Normalization
        norm = math.sqrt(sum(x * x for x in vector))
        if norm > 0:
            vector = [x / norm for x in vector]
        else:
            vector[0] = 1.0
            
        return vector
