from pathlib import Path
from document_processor.pdf_processor import pdf_processor

# Test JSON
json_doc = pdf_processor.process_document(Path('test_files/test_api.json'))
print("JSON Processing:")
print(f"  Extracted {len(json_doc.page_content)} characters")
print(f"  Metadata: {json_doc.metadata}")
print()

# Test CSV
csv_doc = pdf_processor.process_document(Path('test_files/test_transactions.csv'))
print("CSV Processing:")
print(f"  Extracted {len(csv_doc.page_content)} characters")
print(f"  Metadata: {csv_doc.metadata}")
