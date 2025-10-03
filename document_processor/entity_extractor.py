"""
Named Entity Recognition for extracting key information from payment documents
"""
from typing import Dict, List
from transformers import pipeline, AutoTokenizer, AutoModelForTokenClassification
import re
from datetime import datetime


class EntityExtractor:
    """Extract named entities and key information from payment documents"""
    
    def __init__(self):
        """Initialize the entity extractor with NER model"""
        # Load pre-trained NER model
        # This model recognizes: PERSON, ORGANIZATION, LOCATION
        model_name = "dslim/bert-base-NER"
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForTokenClassification.from_pretrained(model_name)
        self.ner_pipeline = pipeline(
            "ner",
            model=self.model,
            tokenizer=self.tokenizer,
            aggregation_strategy="simple"  # Combine consecutive entities
        )
    
    def extract_entities(self, text: str) -> Dict[str, List]:
        """
        Extract all entities from text
        
        Returns dictionary with entity types as keys:
        {
            'organizations': ['HDFC Bank', 'Paytm'],
            'transaction_ids': ['TXN123', 'TXN456'],
            'amounts': ['₹1250', '₹3500'],
            'dates': ['2025-01-15'],
            ...
        }
        """
        entities = {
            "organizations": [],
            "persons": [],
            "locations": [],
            "dates": [],
            "amounts": [],
            "transaction_ids": [],
            "account_numbers": [],
            "api_endpoints": [],
            "error_codes": []
        }
        
        # Extract using NER model (finds people, orgs, locations)
        ner_results = self.ner_pipeline(text[:1000])  # Limit for speed
        
        for entity in ner_results:
            entity_type = entity['entity_group']
            entity_text = entity['word']
            
            if entity_type == 'ORG':
                entities['organizations'].append(entity_text)
            elif entity_type == 'PER':
                entities['persons'].append(entity_text)
            elif entity_type == 'LOC':
                entities['locations'].append(entity_text)
        
        # Extract custom entities using regex (financial + technical)
        entities.update(self._extract_financial_entities(text))
        entities.update(self._extract_technical_entities(text))
        
        # Remove duplicates
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities
    
    def _extract_financial_entities(self, text: str) -> Dict:
        """Extract financial-specific entities"""
        entities = {
            "amounts": [],
            "transaction_ids": [],
            "account_numbers": [],
            "dates": []
        }
        
        # Extract monetary amounts
        # Matches: ₹1,250.00 or INR 1250 or $50.00
        amount_patterns = [
            r'₹\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'INR\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'Rs\.?\s*([0-9,]+(?:\.[0-9]{2})?)',
            r'\$\s*([0-9,]+(?:\.[0-9]{2})?)'
        ]
        for pattern in amount_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['amounts'].extend(matches)
        
        # Extract transaction IDs
        # Matches: TXN20250115001234 or TRANS_123456 or REF-ABC123
        txn_patterns = [
            r'(?:TXN|TRANS|TRANSACTION)[_\s]*(?:ID|NUMBER)?[:\s]*([A-Z0-9]{8,20})',
            r'(?:REF|REFERENCE)[_\s]*(?:ID|NUMBER)?[:\s]*([A-Z0-9]{8,20})',
            r'\b[A-Z]{3}[0-9]{10,}\b'  # Pattern like ABC1234567890
        ]
        for pattern in txn_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['transaction_ids'].extend(matches)
        
        # Extract account numbers (often masked: XXXX1234)
        account_patterns = [
            r'(?:ACCOUNT|ACC)[_\s]*(?:NO|NUMBER)?[:\s]*([X\d]{4,20})',
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'
        ]
        for pattern in account_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['account_numbers'].extend(matches)
        
        # Extract dates
        # Matches: 2025-01-15, 15/01/2025, Jan 15, 2025
        date_patterns = [
            r'\d{4}-\d{2}-\d{2}',  # ISO format
            r'\d{2}/\d{2}/\d{4}',  # US format
            r'\d{2}-\d{2}-\d{4}',  # EU format
            r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\s+\d{1,2},?\s+\d{4}'
        ]
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['dates'].extend(matches)
        
        return entities
    
    def _extract_technical_entities(self, text: str) -> Dict:
        """Extract technical entities (APIs, errors, etc.)"""
        entities = {
            "api_endpoints": [],
            "error_codes": [],
            "ip_addresses": [],
            "urls": []
        }
        
        # Extract API endpoints
        # Matches: /api/v1/process, GET /payment
        api_patterns = [
            r'/api/v?\d*/[\w/\-]+',
            r'(?:GET|POST|PUT|DELETE|PATCH)\s+([\w/\-]+)',
        ]
        for pattern in api_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['api_endpoints'].extend(matches)
        
        # Extract error codes
        # Matches: ERR_TIMEOUT, ERROR-503, 404
        error_patterns = [
            r'(?:ERROR|ERR)[_\s]*(?:CODE)?[:\s]*([A-Z0-9_\-]{3,10})',
            r'\b[45]\d{2}\b',  # HTTP error codes (400-599)
        ]
        for pattern in error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            entities['error_codes'].extend(matches)
        
        # Extract IP addresses
        ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
        entities['ip_addresses'] = re.findall(ip_pattern, text)
        
        # Extract URLs
        url_pattern = r'https?://[^\s<>"{}|\\^`\[\]]+'
        entities['urls'] = re.findall(url_pattern, text)
        
        return entities
    
    def extract_metrics(self, text: str) -> Dict:
        """
        Extract numerical metrics and KPIs from text
        
        Finds patterns like:
        - "success rate: 94.5%"
        - "response time: 450ms"
        - "transaction volume: 125,000"
        """
        metrics = {}
        
        # Extract percentages
        # Pattern: "metric name: 94.5%"
        percentage_pattern = r'(\w+(?:\s+\w+)?)\s*[:\s]+\s*([0-9]+(?:\.[0-9]+)?)\s*%'
        percentage_matches = re.findall(percentage_pattern, text, re.IGNORECASE)
        for metric_name, value in percentage_matches:
            key = metric_name.strip().lower().replace(' ', '_')
            metrics[key] = float(value)
        
        # Extract success/failure rates
        if 'success rate' in text.lower():
            rate_match = re.search(r'success rate[:\s]+([0-9]+(?:\.[0-9]+)?)\s*%', text, re.IGNORECASE)
            if rate_match:
                metrics['success_rate'] = float(rate_match.group(1))
        
        # Extract response times
        time_patterns = [
            (r'response time[:\s]+([0-9]+)\s*ms', 'response_time_ms'),
            (r'latency[:\s]+([0-9]+)\s*ms', 'latency_ms'),
            (r'processing time[:\s]+([0-9]+)\s*(?:ms|seconds?)', 'processing_time')
        ]
        for pattern, key in time_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metrics[key] = int(match.group(1))
        
        # Extract volumes/counts
        volume_patterns = [
            (r'transaction volume[:\s]+([0-9,]+)', 'transaction_volume'),
            (r'total transactions[:\s]+([0-9,]+)', 'total_transactions'),
            (r'request count[:\s]+([0-9,]+)', 'request_count')
        ]
        for pattern, key in volume_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value = match.group(1).replace(',', '')
                metrics[key] = int(value)
        
        return metrics
    
    def extract_key_value_pairs(self, text: str) -> Dict:
        """
        Extract key-value pairs from structured text
        
        Matches patterns like:
        - Status: SUCCESS
        - Response Time: 450ms
        - Bank Name: HDFC
        """
        pairs = {}
        
        # Pattern: "Key: Value" or "Key = Value"
        pattern = r'(\w+(?:\s+\w+)?)\s*[:\=]\s*([^\n,;]+)'
        matches = re.findall(pattern, text)
        
        for key, value in matches:
            key = key.strip().lower().replace(' ', '_')
            value = value.strip()
            pairs[key] = value
        
        return pairs
    
    def extract_bank_names(self, text: str) -> List[str]:
        """Extract bank names from text"""
        # Common Indian banks
        indian_banks = [
            'SBI', 'State Bank', 'HDFC', 'ICICI', 'Axis Bank', 'Kotak',
            'Yes Bank', 'IndusInd', 'Bank of Baroda', 'Punjab National',
            'Canara Bank', 'Union Bank', 'Bank of India', 'Indian Bank',
            'IDBI', 'Federal Bank', 'RBL', 'Paytm Payments Bank'
        ]
        
        found_banks = []
        text_upper = text.upper()
        
        for bank in indian_banks:
            if bank.upper() in text_upper:
                found_banks.append(bank)
        
        return found_banks


# Singleton instance
entity_extractor = EntityExtractor()
