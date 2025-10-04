"""
Document Upload API Endpoints
Handles PDF document uploads and processing
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from pathlib import Path
from typing import List, Dict
import logging
import shutil

from vector_db.knowledge_base import knowledge_base

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/documents", tags=["documents"])

# Upload directory
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a PDF document
    
    Args:
        file: PDF file to upload
        
    Returns:
        Processing results
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Save uploaded file
        file_path = UPLOAD_DIR / file.filename
        with open(file_path, 'wb') as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        logger.info(f"Uploaded file: {file.filename}")
        
        # Process the document
        result = knowledge_base.process_and_index_document(file_path)
        
        if result['success']:
            return {
                "success": True,
                "message": f"Document processed successfully",
                "filename": result['filename'],
                "doc_type": result['doc_type'],
                "confidence": result['confidence'],
                "chunks_indexed": result['chunks_indexed'],
                "entities": result['entities']
            }
        else:
            raise HTTPException(
                status_code=500,
                detail=result.get('error', 'Processing failed')
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-batch")
async def upload_documents(files: List[UploadFile] = File(...)):
    """
    Upload and process multiple PDF documents
    
    Args:
        files: List of PDF files
        
    Returns:
        Batch processing results
    """
    results = []
    
    for file in files:
        try:
            # Validate and save
            if not file.filename.endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "error": "Not a PDF file"
                })
                continue
            
            file_path = UPLOAD_DIR / file.filename
            with open(file_path, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Process
            result = knowledge_base.process_and_index_document(file_path)
            results.append(result)
            
        except Exception as e:
            results.append({
                "filename": file.filename,
                "success": False,
                "error": str(e)
            })
    
    successful = sum(1 for r in results if r.get('success'))
    
    return {
        "total": len(files),
        "successful": successful,
        "failed": len(files) - successful,
        "results": results
    }


@router.get("/stats")
async def get_stats():
    """Get knowledge base statistics"""
    try:
        stats = knowledge_base.get_stats()
        return {
            "success": True,
            "stats": stats
        }
    except Exception as e:
        logger.error(f"Error getting stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "documents",
        "message": "Document service is running"
    }
