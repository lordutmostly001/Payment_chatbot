"""
Multi-Format Document Processing Module
Handles PDF, JSON, and CSV text extraction and preprocessing
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional, Union
import PyPDF2
import json
import pandas as pd
from io import StringIO
from langchain.schema import Document

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Process PDF, JSON, and CSV documents and extract text content"""
    
    def __init__(self):
        self.supported_extensions = ['.pdf', '.json', '.csv']
    
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
    
    def extract_text_from_json(self, json_path: Path) -> str:
        """
        Extract text content from a JSON file
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Extracted text as string
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as file:
                data = json.load(file)
            
            logger.info(f"Processing JSON: {json_path.name}")
            
            # Detect JSON structure type
            json_type = self._detect_json_type(data)
            
            # Extract text based on type
            if json_type == "api_spec":
                text = self._process_api_spec(data)
            elif json_type == "config":
                text = self._process_config(data)
            elif json_type == "array":
                text = self._process_array(data)
            else:
                text = self._process_generic_json(data)
            
            logger.info(f"Extracted {len(text)} characters from {json_path.name}")
            return text
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in {json_path}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error processing JSON {json_path}: {str(e)}")
            raise
    
    def extract_text_from_csv(self, csv_path: Path) -> str:
        """
        Extract text content from a CSV file
        
        Args:
            csv_path: Path to the CSV file
            
        Returns:
            Extracted text as string
        """
        try:
            df = pd.read_csv(csv_path)
            logger.info(f"Processing CSV: {csv_path.name} ({len(df)} rows, {len(df.columns)} columns)")
            
            # Create summary
            text_parts = []
            
            # Add summary
            text_parts.append(f"CSV Data Summary:")
            text_parts.append(f"Total Rows: {len(df)}")
            text_parts.append(f"Total Columns: {len(df.columns)}")
            text_parts.append(f"Columns: {', '.join(df.columns)}\n")
            
            # Add column descriptions
            text_parts.append("Column Information:")
            for col in df.columns:
                unique_count = df[col].nunique()
                null_count = df[col].isnull().sum()
                text_parts.append(f"  - {col}: {unique_count} unique values, {null_count} nulls")
                
                # Add sample values for categorical columns
                if unique_count < 10 and df[col].dtype == 'object':
                    samples = df[col].dropna().unique()[:5]
                    text_parts.append(f"    Examples: {', '.join(str(x) for x in samples)}")
            
            text_parts.append("")
            
            # Add statistical summary for numeric columns
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 0:
                text_parts.append("Statistical Summary:")
                for col in numeric_cols:
                    text_parts.append(f"  {col}:")
                    text_parts.append(f"    Mean: {df[col].mean():.2f}")
                    text_parts.append(f"    Median: {df[col].median():.2f}")
                    text_parts.append(f"    Min: {df[col].min():.2f}")
                    text_parts.append(f"    Max: {df[col].max():.2f}")
                text_parts.append("")
            
            # Add sample rows
            text_parts.append("Sample Data (first 10 rows):")
            for idx, row in df.head(10).iterrows():
                row_text = " | ".join([f"{col}: {val}" for col, val in row.items() if pd.notna(val)])
                text_parts.append(f"Row {idx + 1}: {row_text}")
            
            full_text = "\n".join(text_parts)
            logger.info(f"Extracted {len(full_text)} characters from {csv_path.name}")
            
            return full_text
            
        except Exception as e:
            logger.error(f"Error processing CSV {csv_path}: {str(e)}")
            raise
    
    def _detect_json_type(self, data) -> str:
        """Detect the type of JSON structure"""
        if isinstance(data, dict):
            if any(key in data for key in ['openapi', 'swagger', 'paths', 'endpoints']):
                return "api_spec"
            elif any(key in data for key in ['config', 'settings', 'configuration']):
                return "config"
            else:
                return "object"
        elif isinstance(data, list):
            return "array"
        else:
            return "primitive"
    
    def _process_api_spec(self, data: Dict) -> str:
        """Process API specification JSON"""
        parts = []
        
        # Process metadata
        if 'info' in data:
            parts.append(f"API: {data['info'].get('title', 'Unknown')}")
            parts.append(f"Version: {data['info'].get('version', 'Unknown')}")
            parts.append(f"Description: {data['info'].get('description', '')}\n")
        
        # Process endpoints
        if 'paths' in data:
            parts.append("Endpoints:")
            for path, methods in data['paths'].items():
                for method, details in methods.items():
                    parts.append(f"\n{method.upper()} {path}")
                    parts.append(f"  Summary: {details.get('summary', '')}")
                    parts.append(f"  Description: {details.get('description', '')}")
                    
                    if 'parameters' in details:
                        parts.append("  Parameters:")
                        for param in details['parameters']:
                            parts.append(f"    - {param.get('name')}: {param.get('description', '')}")
        
        return "\n".join(parts)
    
    def _process_config(self, data: Dict) -> str:
        """Process configuration JSON"""
        def flatten_dict(d, parent_key=''):
            items = []
            for k, v in d.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(flatten_dict(v, new_key))
                else:
                    items.append(f"{new_key}: {v}")
            return items
        
        lines = flatten_dict(data)
        return "\n".join(lines)
    
    def _process_array(self, data: List) -> str:
        """Process JSON arrays"""
        parts = [f"JSON Array with {len(data)} items\n"]
        
        for i, item in enumerate(data[:20]):  # First 20 items
            if isinstance(item, dict):
                parts.append(f"Item {i+1}:")
                for key, value in item.items():
                    parts.append(f"  {key}: {value}")
            else:
                parts.append(f"Item {i+1}: {item}")
        
        if len(data) > 20:
            parts.append(f"\n... and {len(data) - 20} more items")
        
        return "\n".join(parts)
    
    def _process_generic_json(self, data) -> str:
        """Process generic JSON structure"""
        return json.dumps(data, indent=2)
    
    def process_document(
        self, 
        file_path: Path,
        metadata: Optional[Dict] = None
    ) -> Document:
        """
        Process a document file (PDF, JSON, or CSV) and create a Document object
        
        Args:
            file_path: Path to document file
            metadata: Optional metadata dictionary
            
        Returns:
            Document object with text and metadata
        """
        # Detect file type
        file_extension = file_path.suffix.lower()
        
        if file_extension not in self.supported_extensions:
            raise ValueError(f"Unsupported file type: {file_extension}. Supported: {self.supported_extensions}")
        
        # Extract text based on file type
        if file_extension == '.pdf':
            text = self.extract_text_from_pdf(file_path)
            file_type = 'pdf'
        elif file_extension == '.json':
            text = self.extract_text_from_json(file_path)
            file_type = 'json'
        elif file_extension == '.csv':
            text = self.extract_text_from_csv(file_path)
            file_type = 'csv'
        else:
            raise ValueError(f"Unsupported file extension: {file_extension}")
        
        # Build metadata
        doc_metadata = {
            'source': str(file_path),
            'filename': file_path.name,
            'file_type': file_type,
        }
        
        if metadata:
            doc_metadata.update(metadata)
        
        # Create Document
        document = Document(
            page_content=text,
            metadata=doc_metadata
        )
        
        return document
    
    # Keep backward compatibility - alias for existing code
    def process_pdf(
        self, 
        pdf_path: Path,
        metadata: Optional[Dict] = None
    ) -> Document:
        """
        Process a PDF file and create a Document object
        (Backward compatibility method)
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata dictionary
            
        Returns:
            Document object with text and metadata
        """
        return self.process_document(pdf_path, metadata)
    
    def process_directory(
        self, 
        directory_path: Path,
        recursive: bool = True,
        file_types: Optional[List[str]] = None
    ) -> List[Document]:
        """
        Process all supported files in a directory
        
        Args:
            directory_path: Path to directory containing documents
            recursive: Whether to search subdirectories
            file_types: Optional list of file extensions to process (e.g., ['.pdf', '.json'])
                       If None, processes all supported types
            
        Returns:
            List of Document objects
        """
        documents = []
        
        if not directory_path.exists():
            logger.error(f"Directory not found: {directory_path}")
            return documents
        
        # Determine which file types to process
        if file_types is None:
            file_types = self.supported_extensions
        
        # Find all matching files
        all_files = []
        for ext in file_types:
            if recursive:
                all_files.extend(list(directory_path.rglob(f"*{ext}")))
            else:
                all_files.extend(list(directory_path.glob(f"*{ext}")))
        
        logger.info(f"Found {len(all_files)} files in {directory_path}")
        
        # Process each file
        for file_path in all_files:
            try:
                doc = self.process_document(file_path)
                documents.append(doc)
                logger.info(f"Successfully processed: {file_path.name}")
            except Exception as e:
                logger.error(f"Failed to process {file_path.name}: {str(e)}")
                continue
        
        logger.info(f"Successfully processed {len(documents)} out of {len(all_files)} files")
        return documents


# Singleton instance (backward compatibility)
pdf_processor = PDFProcessor()