"""
Knowledge Base Module
High-level interface for document processing and storage
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
from langchain.schema import Document

from document_processor import pdf_processor, classifier, entity_extractor
from .embedding_service import embedding_service
from .vector_search import vector_search

logger = logging.getLogger(__name__)


class KnowledgeBase:
    """
    High-level knowledge base that orchestrates document processing and storage
    """
    
    def __init__(self):
        self.vector_search = vector_search
        self.pdf_processor = pdf_processor
        self.classifier = classifier
        self.entity_extractor = entity_extractor
        self.embedding_service = embedding_service
    
    def process_and_index_document(
        self,
        file_path: Path,
        namespace: str = ""
    ) -> Dict:
        """
        Complete pipeline: Read PDF -> Classify -> Extract entities -> Embed -> Store
        
        Args:
            file_path: Path to PDF file
            namespace: Optional namespace for organizing documents
            
        Returns:
            Processing results dictionary
        """
        try:
            logger.info(f"Processing document: {file_path.name}")
            
            # Step 1: Extract text from PDF
            document = self.pdf_processor.process_pdf(file_path)
            logger.info(f"Extracted {len(document.page_content)} characters")
            
            # Step 2: Classify document
            classification = self.classifier.classify_document(document.page_content)
            logger.info(f"Classified as: {classification['doc_type']} ({classification['confidence']:.2%})")
            
            # Step 3: Extract entities
            entities = self.entity_extractor.extract_entities(document.page_content)
            logger.info(f"Extracted entities: {list(entities.keys())}")
            
            # Step 4: Add classification and entities to metadata
            document.metadata.update({
                'doc_type': classification['doc_type'],
                'confidence': classification['confidence'],
                'stakeholder_relevance': classification['stakeholder_relevance'],
                'entities': entities
            })
            
            # Step 5: Split into chunks for better retrieval
            chunks = self.embedding_service.split_text(document.page_content)
            logger.info(f"Split into {len(chunks)} chunks")
            
            # Create Document objects for each chunk
            chunk_docs = []
            for i, chunk in enumerate(chunks):
                chunk_doc = Document(
                    page_content=chunk,
                    metadata={
                        **document.metadata,
                        'chunk_index': i,
                        'total_chunks': len(chunks)
                    }
                )
                chunk_docs.append(chunk_doc)
            
            # Step 6: Index in vector database
            result = self.vector_search.add_documents(
                documents=chunk_docs,
                namespace=namespace
            )
            
            logger.info(f"Successfully indexed {result['documents_added']} chunks")
            
            return {
                'success': True,
                'filename': file_path.name,
                'doc_type': classification['doc_type'],
                'confidence': classification['confidence'],
                'chunks_created': len(chunks),
                'chunks_indexed': result['documents_added'],
                'entities': {k: len(v) for k, v in entities.items() if v}
            }
            
        except Exception as e:
            logger.error(f"Error processing {file_path.name}: {str(e)}")
            return {
                'success': False,
                'filename': file_path.name,
                'error': str(e)
            }
    
    def process_directory(
        self,
        directory_path: Path,
        namespace: str = "",
        recursive: bool = True
    ) -> List[Dict]:
        """
        Process all PDFs in a directory
        
        Args:
            directory_path: Directory containing PDFs
            namespace: Optional namespace
            recursive: Search subdirectories
            
        Returns:
            List of processing results
        """
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return []
        
        # Find all PDFs
        if recursive:
            pdf_files = list(directory_path.rglob("*.pdf"))
        else:
            pdf_files = list(directory_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files to process")
        
        results = []
        for pdf_path in pdf_files:
            result = self.process_and_index_document(pdf_path, namespace)
            results.append(result)
        
        # Summary
        successful = sum(1 for r in results if r['success'])
        logger.info(f"Processed {successful}/{len(results)} documents successfully")
        
        return results
    
    def query(
        self,
        question: str,
        stakeholder: Optional[str] = None,
        top_k: int = 3,
        namespace: str = ""
    ) -> List[Dict]:
        """
        Query the knowledge base
        
        Args:
            question: User's question
            stakeholder: Optional stakeholder filter
            top_k: Number of results
            namespace: Optional namespace
            
        Returns:
            List of relevant document chunks
        """
        if stakeholder:
            results = self.vector_search.search_by_stakeholder(
                query=question,
                stakeholder=stakeholder,
                top_k=top_k,
                namespace=namespace
            )
        else:
            results = self.vector_search.search(
                query=question,
                top_k=top_k,
                namespace=namespace
            )
        
        return results
    
    def get_stats(self) -> Dict:
        """Get knowledge base statistics"""
        return self.vector_search.get_stats()


# Singleton instance
knowledge_base = KnowledgeBase()
