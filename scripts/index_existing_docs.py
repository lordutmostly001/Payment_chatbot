"""
Batch process and index all PDFs in data/ folder
Run: python scripts/index_existing_docs.py
"""

import os
from pathlib import Path
import sys
import logging

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from vector_db.knowledge_base import knowledge_base

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def index_data_folder():
    """Process all PDFs in data/ folder"""
    data_dir = Path("data")
    
    if not data_dir.exists():
        logger.error("data/ folder not found. Creating it...")
        data_dir.mkdir()
        return
    
    pdf_files = list(data_dir.glob("*.pdf"))
    
    if not pdf_files:
        logger.warning("No PDF files found in data/ folder")
        return
    
    logger.info(f"Found {len(pdf_files)} PDF files to process")
    logger.info("=" * 60)
    
    successful = 0
    failed = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logger.info(f"\n[{i}/{len(pdf_files)}] Processing: {pdf_file.name}")
        
        try:
            result = knowledge_base.process_and_index_document(pdf_file)
            
            if result['success']:
                logger.info(f"✓ Success")
                logger.info(f"  - Document Type: {result['doc_type']}")
                logger.info(f"  - Confidence: {result['confidence']:.1f}%")
                logger.info(f"  - Chunks Indexed: {result['chunks_indexed']}")
                logger.info(f"  - Entities Found: {len(result.get('entities', []))}")
                successful += 1
            else:
                logger.error(f"✗ Failed: {result.get('error')}")
                failed += 1
                
        except Exception as e:
            logger.error(f"✗ Error: {str(e)}")
            failed += 1
    
    logger.info("\n" + "=" * 60)
    logger.info(f"Batch processing complete!")
    logger.info(f"  Successful: {successful}")
    logger.info(f"  Failed: {failed}")
    logger.info(f"  Total: {len(pdf_files)}")
    
    # Get updated index stats
    try:
        from vector_db.vector_search import vector_search
        stats = vector_search.get_index_stats()
        logger.info(f"\nPinecone Index Stats:")
        logger.info(f"  Total Vectors: {stats.get('total_vector_count', 'N/A')}")
    except Exception as e:
        logger.warning(f"Could not fetch index stats: {e}")


if __name__ == "__main__":
    logger.info("Starting batch document indexing...")
    index_data_folder()