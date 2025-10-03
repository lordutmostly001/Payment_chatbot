"""
Vector Database Package
Handles embeddings, vector search, and knowledge base operations
"""

from .embedding_service import embedding_service, EmbeddingService
from .vector_search import vector_search, VectorSearch
from .knowledge_base import knowledge_base, KnowledgeBase

__all__ = [
    'embedding_service',
    'EmbeddingService',
    'vector_search',
    'VectorSearch',
    'knowledge_base',
    'KnowledgeBase',
]
