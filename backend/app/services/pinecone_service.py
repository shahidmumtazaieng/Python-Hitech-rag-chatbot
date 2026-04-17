"""Pinecone Vector Store Service."""
import uuid
from typing import List, Dict, Any, Optional
from pinecone import Pinecone, ServerlessSpec

from app.config import get_settings
from app.services.embedding_service import get_embedding_service


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
        
        # Initialize Pinecone client
        self.pc = Pinecone(api_key=self.settings.PINECONE_API_KEY)
        
        # Check if index exists, create if not
        index_name = self.settings.PINECONE_INDEX_NAME
        existing_indexes = [idx.name for idx in self.pc.list_indexes()]
        
        if index_name not in existing_indexes:
            print(f"Creating Pinecone index: {index_name}")
            self.pc.create_index(
                name=index_name,
                dimension=self.settings.PINECONE_DIMENSION,
                metric="cosine",
                spec=ServerlessSpec(
                    cloud="aws",
                    region="us-east-1"
                )
            )
            print(f"Index {index_name} created successfully")
        
        # Connect to index
        self.index = self.pc.Index(index_name)
        self._initialized = True
        print(f"Connected to Pinecone index: {index_name}")
    
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
        include_metadata: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Perform similarity search.
        
        Args:
            query: Query text
            top_k: Number of results to return
            filter_dict: Optional metadata filter
            include_metadata: Whether to include metadata in results
            
        Returns:
            List of matching documents with scores
        """
        self.ensure_initialized()
        
        # Generate query embedding
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
