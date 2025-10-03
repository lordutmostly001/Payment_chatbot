"""
Embedding service for generating vector representations of documents
"""
from typing import List, Dict
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
import numpy as np
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add parent directory to path to import config
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import settings


class EmbeddingService:
    """Service for generating and managing document embeddings"""
    
    def __init__(self):
        """Initialize the embedding service"""
        self.model_name = getattr(settings, 'EMBEDDING_MODEL', 'sentence-transformers/all-MiniLM-L6-v2')
        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self.embedding_dimension = self.model.get_sentence_embedding_dimension()
        
        # Initialize text splitter for chunking documents
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            length_function=len,
        )
        
        logger.info(f"Embedding service initialized. Dimension: {self.embedding_dimension}")
    
    def embed_query(self, query: str) -> List[float]:
        """Generate embedding for a single query"""
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        embedding = self.model.encode(query, convert_to_numpy=True)
        return embedding.tolist()
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple documents"""
        if not texts:
            raise ValueError("Text list cannot be empty")
        
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("No valid texts to embed")
        
        embeddings = self.model.encode(valid_texts, convert_to_numpy=True)
        return embeddings.tolist()
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Compute cosine similarity between two texts
        """
        emb1 = np.array(self.embed_query(text1))
        emb2 = np.array(self.embed_query(text2))
        
        # Cosine similarity
        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity)



    def split_text(self, text: str) -> list:
        """Split text into chunks for embedding"""
        return self.text_splitter.split_text(text)

# Singleton instance

    def split_text(self, text: str) -> list:
        """Split text into chunks for embedding"""
        return self.text_splitter.split_text(text)

_embedding_service = None

def get_embedding_service() -> EmbeddingService:
    """Get or create the embedding service singleton"""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service


# Legacy support - for backward compatibility
embedding_service = get_embedding_service()
