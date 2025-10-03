"""
PDF Processing Module
Handles PDF text extraction and preprocessing
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
from langchain.schema import Document

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF documents and extract text content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf']
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """
        Extract text content from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text as string
        """
        try:
            text_content = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                logger.info(f"Processing PDF: {pdf_path.name} ({num_pages} pages)")
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    
                    if text.strip():
                        text_content.append(text)
                
            full_text = "\n\n".join(text_content)
            logger.info(f"Extracted {len(full_text)} characters from {pdf_path.name}")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise
    
    def process_pdf(
        self, 
        pdf_path: Path,
        metadata: Optional[Dict] = None
    ) -> Document:
        """
        Process a PDF file and create a Document object
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata dictionary
            
        Returns:
            Document object with text and metadata
        """
        # Extract text
        text = self.extract_text_from_pdf(pdf_path)
        
        # Build metadata
        doc_metadata = {
            'source': str(pdf_path),
            'filename': pdf_path.name,
            'file_type': 'pdf',
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Create Document
        document = Document(
            page_content=text,
            metadata=doc_metadata
        )
        
        return document
    
    def process_directory(
        self, 
        directory_path: Path,
        recursive: bool = True
    ) -> List[Document]:
        """
        Process all PDF files in a directory
        
        Args:
            directory_path: Path to directory containing PDFs
            recursive: Whether to search subdirectories
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return documents
        
        # Find all PDFs
        if recursive:
            pdf_files = list(directory_path.rglob("*.pdf"))
        else:
            pdf_files = list(directory_path.glob("*.pdf"))
        
        logger.info(f"Found {len(pdf_files)} PDF files in {directory_path}")
        
        # Process each PDF
        for pdf_path in pdf_files:
            try:
                doc = self.process_pdf(pdf_path)
                documents.append(doc)
                logger.info(f"Successfully processed: {pdf_path.name}")
            except Exception as e:
                logger.error(f"Failed to process {pdf_path.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(documents)} out of {len(pdf_files)} PDFs")
        return documents


# Singleton instance
pdf_processor = PDFProcessor()
