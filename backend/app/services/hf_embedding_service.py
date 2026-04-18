"""Hugging Face API Embedding Service for fast query-time embeddings."""
import os
import requests
import numpy as np
from typing import List, Dict, Any, Optional
from functools import lru_cache

from app.config import get_settings


class HuggingFaceEmbeddingService:
    """Service for generating embeddings using Hugging Face Inference API.
    
    Uses BGE-M3 via Hugging Face API for query-time embeddings,
    avoiding the need to load the heavy model locally.
    """
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(HuggingFaceEmbeddingService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.settings = get_settings()
        # Use BGE-M3 API (1024-dim) - matches your Pinecone index
        self.api_url = "https://api-inference.huggingface.co/pipeline/feature-extraction/BAAI/bge-m3"
        self.api_key = os.getenv("HF_API_TOKEN", "")
        self.dimension = 1024  # BGE-M3 dimension - MUST match Pinecone index
        self._local_fallback = None
        
        # Initialize local fallback - USE BGE-Small if possible, otherwise all-MiniLM
        self._init_local_fallback()
    
    def _init_local_fallback(self):
        """Initialize lightweight local model as fallback."""
        try:
            from sentence_transformers import SentenceTransformer
            # Note: all-MiniLM-L6-v2 is 384-dim, which WON'T match 1024-dim Pinecone index
            # This is only for offline testing - HF API should always be used
            print("Loading local fallback model (all-MiniLM-L6-v2, 384-dim)...")
            self._local_fallback = SentenceTransformer('all-MiniLM-L6-v2', device='cpu')
            print("⚠️ Local fallback loaded (384-dim) - won't match Pinecone 1024-dim index")
        except Exception as e:
            print(f"Local fallback not available: {e}")
            self._local_fallback = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get API headers."""
        headers = {
            "Content-Type": "application/json",
        }
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers
    
    def embed_query(self, text: str) -> List[float]:
        """
        Generate embedding for a single query using Hugging Face API.
        Falls back to local model if API fails.
        
        Args:
            text: Query text to embed
            
        Returns:
            List of float values (1024 dimensions for BGE-M3)
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Try Hugging Face API first
        if self.api_key:
            try:
                return self._embed_via_api([text])[0]
            except Exception as e:
                print(f"HF API failed, using local fallback: {e}")
        
        # Fallback to local model
        if self._local_fallback:
            embedding = self._local_fallback.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        
        raise RuntimeError("No embedding method available. Set HF_API_TOKEN or ensure local model is loaded.")
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple documents.
        Note: For ingestion, use local BGE-M3. This is for query-time only.
        
        Args:
            texts: List of document texts
            
        Returns:
            List of embedding vectors
        """
        if not texts:
            return []
        
        # Filter empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            return []
        
        # Try Hugging Face API first
        if self.api_key:
            try:
                return self._embed_via_api(valid_texts)
            except Exception as e:
                print(f"HF API failed for batch, using local fallback: {e}")
        
        # Fallback to local model
        if self._local_fallback:
            embeddings = self._local_fallback.encode(valid_texts, convert_to_numpy=True, batch_size=8)
            return [emb.tolist() for emb in embeddings]
        
        raise RuntimeError("No embedding method available.")
    
    def _embed_via_api(self, texts: List[str]) -> List[List[float]]:
        """
        Call Hugging Face Inference API for embeddings.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        # BGE-M3 works best with instruction prefix for queries
        # But for general use, we'll send as-is
        payload = {
            "inputs": texts,
            "options": {
                "wait_for_model": True,  # Wait if model is loading
                "use_cache": True
            }
        }
        
        response = requests.post(
            self.api_url,
            headers=self._get_headers(),
            json=payload,
            timeout=30  # HF API can be slow on first call
        )
        
        if response.status_code != 200:
            raise RuntimeError(f"HF API error {response.status_code}: {response.text}")
        
        embeddings = response.json()
        
        # Handle different response formats
        if isinstance(embeddings, list) and len(embeddings) > 0:
            if isinstance(embeddings[0], list):
                return embeddings
            elif isinstance(embeddings[0], float):
                # Single embedding returned directly
                return [embeddings]
        
        raise RuntimeError(f"Unexpected HF API response format: {type(embeddings)}")
    
    def embed_query_with_instruction(self, text: str, task: str = "search") -> List[float]:
        """
        Generate embedding with BGE-M3 instruction prefix for better retrieval.
        
        Args:
            text: Query text
            task: Task type - 'search', 'qa', 'clustering', etc.
            
        Returns:
            Embedding vector
        """
        # BGE-M3 instruction templates
        instructions = {
            "search": "Represent this sentence for searching relevant passages: ",
            "qa": "Represent this question for retrieving supporting documents: ",
            "clustering": "Represent this sentence for clustering: ",
            "classification": "Represent this sentence for classification: ",
        }
        
        instruction = instructions.get(task, instructions["search"])
        prompted_text = f"{instruction}{text}"
        
        return self.embed_query(prompted_text)
    
    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """Compute cosine similarity between two embeddings."""
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)
        
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(np.dot(vec1, vec2) / (norm1 * norm2))
    
    @property
    def is_api_available(self) -> bool:
        """Check if HF API is configured and available."""
        if not self.api_key:
            return False
        
        try:
            # Quick test with empty call
            response = requests.post(
                self.api_url,
                headers=self._get_headers(),
                json={"inputs": ["test"]},
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status."""
        return {
            "service": "HuggingFaceEmbeddingService",
            "api_configured": bool(self.api_key),
            "api_available": self.is_api_available,
            "local_fallback_available": self._local_fallback is not None,
            "dimension": self.dimension,
            "model": "BAAI/bge-m3 (via HF API)",
            "fallback_model": "all-MiniLM-L6-v2 (local)" if self._local_fallback else None
        }


# Global instance
_hf_embedding_service = None


def get_hf_embedding_service() -> HuggingFaceEmbeddingService:
    """Get the Hugging Face embedding service instance."""
    global _hf_embedding_service
    if _hf_embedding_service is None:
        _hf_embedding_service = HuggingFaceEmbeddingService()
    return _hf_embedding_service


# Convenience function for RAG pipeline
def embed_query_fast(text: str) -> List[float]:
    """Fast query embedding using HF API."""
    service = get_hf_embedding_service()
    return service.embed_query_with_instruction(text, task="search")
