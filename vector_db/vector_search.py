"""
Vector Search Module
Handles vector similarity search using Pinecone
"""

import logging
import uuid  # Added this import
from typing import List, Dict, Optional
from pinecone import Pinecone, ServerlessSpec
from langchain.schema import Document
from config import settings
from .embedding_service import embedding_service

logger = logging.getLogger(__name__)


class VectorSearch:
    """Vector search using Pinecone for semantic document retrieval"""
    
    def __init__(self):
        """Initialize Pinecone connection"""
        self.pc = Pinecone(api_key=settings.PINECONE_API_KEY)
        self.index_name = settings.PINECONE_INDEX_NAME
        self.index = None
        self._initialize_index()
    
    def _initialize_index(self):
        """Initialize or connect to Pinecone index"""
        try:
            # Check if index exists
            existing_indexes = [index.name for index in self.pc.list_indexes()]
            
            if self.index_name not in existing_indexes:
                logger.info(f"Creating new Pinecone index: {self.index_name}")
                self.pc.create_index(
                    name=self.index_name,
                    dimension=384,  # all-MiniLM-L6-v2 dimension
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                logger.info("Index created successfully")
            
            # Connect to index
            self.index = self.pc.Index(self.index_name)
            logger.info(f"Connected to Pinecone index: {self.index_name}")
            
        except Exception as e:
            logger.error(f"Error initializing Pinecone index: {str(e)}")
            raise
    
    def add_documents(
        self,
        documents: List[Document],
        namespace: str = ""
    ) -> Dict:
        """
        Add documents to the vector index
        
        Args:
            documents: List of Document objects to index
            namespace: Optional namespace for organizing vectors
            
        Returns:
            Dictionary with indexing statistics
        """
        try:
            vectors = []
            
            for idx, doc in enumerate(documents):
                # Generate unique ID using UUID
                doc_id = str(uuid.uuid4())  # Changed this line
                
                # Generate embedding
                embedding = embedding_service.embed_query(doc.page_content)
                
                # Prepare metadata (Pinecone has size limits)
                metadata = {
                    'text': doc.page_content[:1000],  # Truncate for metadata
                    'source': doc.metadata.get('source', 'unknown'),
                    'doc_type': doc.metadata.get('doc_type', 'unknown'),
                }
                
                # Add stakeholder relevance if available
                if 'stakeholder_relevance' in doc.metadata:
                    metadata['stakeholders'] = ','.join(
                        doc.metadata['stakeholder_relevance']
                    )
                
                # Add entities if available
                if 'entities' in doc.metadata:
                    entities = doc.metadata['entities']
                    if 'amounts' in entities and entities['amounts']:
                        metadata['has_amounts'] = True
                    if 'dates' in entities and entities['dates']:
                        metadata['has_dates'] = True
                
                vectors.append({
                    'id': doc_id,
                    'values': embedding,
                    'metadata': metadata
                })
            
            # Upsert to Pinecone
            self.index.upsert(vectors=vectors, namespace=namespace)
            
            logger.info(f"Added {len(vectors)} documents to index")
            
            return {
                'success': True,
                'documents_added': len(vectors),
                'namespace': namespace
            }
            
        except Exception as e:
            logger.error(f"Error adding documents to index: {str(e)}")
            raise
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        namespace: str = "",
        filter_dict: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Search for similar documents
        
        Args:
            query: Search query text
            top_k: Number of results to return
            namespace: Namespace to search in
            filter_dict: Optional metadata filters
            
        Returns:
            List of matching documents with scores
        """
        try:
            # Generate query embedding
            query_embedding = embedding_service.embed_query(query)
            
            # Search Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=namespace,
                filter=filter_dict,
                include_metadata=True
            )
            
            # Format results
            formatted_results = []
            for match in results['matches']:
                formatted_results.append({
                    'id': match['id'],
                    'score': match['score'],
                    'text': match['metadata'].get('text', ''),
                    'source': match['metadata'].get('source', 'unknown'),
                    'doc_type': match['metadata'].get('doc_type', 'unknown'),
                    'metadata': match['metadata']
                })
            
            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error searching index: {str(e)}")
            raise
    
    def search_by_stakeholder(
        self,
        query: str,
        stakeholder: str,
        top_k: int = 5,
        namespace: str = ""
    ) -> List[Dict]:
        """Search for documents relevant to a specific stakeholder"""
        results = self.search(
            query=query,
            top_k=top_k * 2,  # Get more results to filter
            namespace=namespace
        )
        
        # Filter by stakeholder
        filtered_results = []
        for result in results:
            stakeholders = result['metadata'].get('stakeholders', '')
            if stakeholder in stakeholders or not stakeholders:
                filtered_results.append(result)
                if len(filtered_results) >= top_k:
                    break
        
        return filtered_results
    
    def get_stats(self) -> Dict:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'dimension': stats.dimension,
                'index_fullness': stats.index_fullness,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            logger.error(f"Error getting index stats: {str(e)}")
            return {}


# Singleton instance
vector_search = VectorSearch()