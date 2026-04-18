"""Embedding Service using sentence-transformers (all-MiniLM-L6-v2, 384-dim)."""
import numpy as np
from typing import List
from app.config import get_settings

EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 — must match PINECONE_DIMENSION in .env


class EmbeddingService:
    """Singleton service for generating embeddings."""

    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        self.settings = get_settings()
        # dimension is a class-level constant — never overwritten after init
        if not hasattr(self, '_initialized'):
            self._initialized = True
            self.dimension = EMBEDDING_DIMENSION
            if EmbeddingService._model is None:
                self._load_model()

    def _load_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            print("Loading embedding model (all-MiniLM-L6-v2, 384-dim)…")
            EmbeddingService._model = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            print("Embedding model loaded successfully.")
        except Exception as exc:
            print(f"WARNING: Could not load embedding model: {exc}")
            print("Falling back to deterministic mock embeddings (for testing only).")
            EmbeddingService._model = None

    @property
    def model(self):
        return EmbeddingService._model

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def embed_query(self, text: str) -> List[float]:
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        if self.model is None:
            return self._mock_embed(text)
        query_text = f"Represent this sentence for searching relevant passages: {text}"
        embedding = self.model.encode(query_text, convert_to_numpy=True)
        return embedding.tolist()

    def embed_documents(self, texts: List[str], batch_size: int = 8) -> List[List[float]]:
        valid = [t for t in texts if t and t.strip()]
        if not valid:
            return []
        if self.model is None:
            return [self._mock_embed(t) for t in valid]
        embeddings = self.model.encode(valid, convert_to_numpy=True, batch_size=batch_size)
        return [e.tolist() for e in embeddings]

    def embed_document_chunks(self, chunks: List[dict], batch_size: int = 8) -> List[dict]:
        if not chunks:
            return []
        texts = [c['content'] for c in chunks]
        embeddings = self.embed_documents(texts, batch_size)
        for chunk, emb in zip(chunks, embeddings):
            chunk['embedding'] = emb
        return chunks

    def compute_similarity(self, e1: List[float], e2: List[float]) -> float:
        v1, v2 = np.array(e1), np.array(e2)
        n1, n2 = np.linalg.norm(v1), np.linalg.norm(v2)
        if n1 == 0 or n2 == 0:
            return 0.0
        return float(np.dot(v1, v2) / (n1 * n2))

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _mock_embed(self, text: str) -> List[float]:
        import hashlib
        h = int(hashlib.md5(text.encode()).hexdigest(), 16)
        base = [(h >> i & 0xFF) / 255.0 for i in range(self.dimension)]
        # normalise so cosine similarity is meaningful
        norm = np.linalg.norm(base) or 1.0
        return [v / norm for v in base]


# Singleton
embedding_service = EmbeddingService()


def get_embedding_service() -> EmbeddingService:
    return embedding_service