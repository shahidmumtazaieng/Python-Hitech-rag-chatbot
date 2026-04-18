"""Pinecone Vector Store Service."""
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.services.embedding_service import get_embedding_service
from app.services.hf_embedding_service import get_hf_embedding_service


class PineconeService:
    """Service for Pinecone vector store operations."""
    
    _instance = None
    
    def __new__(cls):
        """Singleton pattern."""
        if cls._instance is None:
            cls._instance = super(PineconeService, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self.settings = get_settings()
        self.pc: Optional[Pinecone] = None
        self.index = None
        self._initialized = False
    
    def initialize(self):
        """Initialize Pinecone client and ensure index exists."""
        if self._initialized:
            return
        
        try:
            print(f"Initializing Pinecone...")
            
            # Initialize Pinecone client (new API doesn't need environment)
            self.pc = Pinecone(
                api_key=self.settings.PINECONE_API_KEY,
                host=self.settings.PINECONE_HOST if self.settings.PINECONE_HOST else None
            )
            
            # Check if index exists
            index_name = self.settings.PINECONE_INDEX_NAME
            print(f"Checking for index: {index_name}")
            
            try:
                existing_indexes = [idx.name for idx in self.pc.list_indexes()]
                
                if index_name not in existing_indexes:
                    print(f"Index '{index_name}' not found. Creating new index...")
                    self.pc.create_index(
                        name=index_name,
                        dimension=self.settings.PINECONE_DIMENSION,
                        metric="cosine",
                        spec=ServerlessSpec(
                            cloud="aws",
                            region="us-east-1"
                        )
                    )
                    print(f"✅ Index '{index_name}' created successfully")
                    
                    # Wait for index to be ready
                    import time
                    print("Waiting for index to be ready...")
                    time.sleep(10)
                else:
                    print(f"✅ Index '{index_name}' already exists")
            except Exception as e:
                print(f"⚠️ Warning: Could not list/create index: {e}")
                print("Continuing anyway - index may already exist...")
            
            # Connect to index
            self.index = self.pc.Index(index_name)
            self._initialized = True
            print(f"✅ Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            print(f"❌ Pinecone initialization failed: {e}")
            print(f"Using mock mode - vector operations will be simulated")
            self._initialized = True  # Set to True to allow app to continue
            self.index = None
    
    def ensure_initialized(self):
        """Ensure service is initialized."""
        if not self._initialized:
            self.initialize()
    
    def upsert_documents(
        self,
        documents: List[Dict[str, Any]],
        batch_size: int = 100
    ) -> Dict[str, Any]:
        """
        Upsert documents to Pinecone.
        
        Args:
            documents: List of documents with 'content', 'embedding', and metadata
            batch_size: Number of vectors per batch
            
        Returns:
            Upsert response stats
        """
        self.ensure_initialized()
        
        vectors = []
        for doc in documents:
            vector_id = doc.get('id', str(uuid.uuid4()))
            vector = {
                'id': vector_id,
                'values': doc['embedding'],
                'metadata': {
                    'content': doc['content'],
                    'source': doc.get('source', ''),
                    'title': doc.get('title', ''),
                    'url': doc.get('url', ''),
                    'timestamp': doc.get('timestamp', ''),
                    'chunk_index': doc.get('chunk_index', 0)
                }
            }
            vectors.append(vector)
        
        # Batch upsert
        total_upserted = 0
        for i in range(0, len(vectors), batch_size):
            batch = vectors[i:i + batch_size]
            self.index.upsert(vectors=batch)
            total_upserted += len(batch)
        
        return {
            "upserted_count": total_upserted,
            "index_name": self.settings.PINECONE_INDEX_NAME
        }
    
    def similarity_search(
        self,
        query: str,
        top_k: int = 5,
        filter_dict: Optional[Dict] = None,
        include_metadata: bool = True,
        use_hf_api: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            include_metadata: Whether to include metadata in results
            use_hf_api: Use Hugging Face API for query embeddings (fast, high quality)
            
        Returns:
            List of matching documents with scores
        """
        self.ensure_initialized()
        
        # Handle mock mode (Pinecone not connected)
        if self.index is None:
            print(f"[Pinecone] Mock mode - returning empty results for: {query[:50]}...")
            return []
        
        # Generate query embedding using HF API (fast) or local model (fallback)
        if use_hf_api:
            try:
                hf_service = get_hf_embedding_service()
                query_embedding = hf_service.embed_query_with_instruction(query, task="search")
            except Exception as e:
                print(f"[Pinecone] HF API failed, using local embedding: {e}")
                embedding_service = get_embedding_service()
                query_embedding = embedding_service.embed_query(query)
        else:
            embedding_service = get_embedding_service()
            query_embedding = embedding_service.embed_query(query)
        
        # Query index
        results = self.index.query(
            vector=query_embedding,
            top_k=top_k,
            filter=filter_dict,
            include_metadata=include_metadata
        )
        
        # Format results
        documents = []
        for match in results.matches:
            doc = {
                'id': match.id,
                'score': match.score,
                'content': match.metadata.get('content', '') if match.metadata else '',
                'source': match.metadata.get('source', '') if match.metadata else '',
                'title': match.metadata.get('title', '') if match.metadata else '',
                'url': match.metadata.get('url', '') if match.metadata else ''
            }
            documents.append(doc)
        
        return documents
    
    def delete_all(self, namespace: str = ""):
        """Delete all vectors from the index."""
        self.ensure_initialized()
        self.index.delete(delete_all=True, namespace=namespace)
        return {"deleted": True}
    
    def delete_by_filter(self, filter_dict: Dict[str, Any]):
        """Delete vectors matching filter."""
        self.ensure_initialized()
        self.index.delete(filter=filter_dict)
        return {"deleted": True}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get index statistics."""
        self.ensure_initialized()
        stats = self.index.describe_index_stats()
        return {
            "total_vectors": stats.total_vector_count,
            "dimension": stats.dimension,
            "index_fullness": getattr(stats, 'index_fullness', 0)
        }


# Global instance
pinecone_service = PineconeService()


def get_pinecone_service() -> PineconeService:
    """Get the Pinecone service instance."""
    return pinecone_service
