"""
Document classification module for identifying payment document types
"""
from typing import Dict, List
import re
from transformers import pipeline
from config import settings, DOCUMENT_PATTERNS, STAKEHOLDER_CONFIG


class DocumentClassifier:
    """Classifies payment documents into predefined categories"""
    
    def __init__(self):
        """Initialize the document classifier"""
        self.patterns = DOCUMENT_PATTERNS
        
        # Using zero-shot classification - no training needed!
        # This model can classify into ANY categories we give it
        self.classifier = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli"
        )
        self.labels = settings.DOCUMENT_TYPES
    
    def classify_document(self, text: str, filename: str = "") -> Dict:
        """
        Classify a document into one of the predefined types
        
        Args:
            text: Document text content
            filename: Optional filename for additional context
            
        Returns:
            Dict with classification results
            {
                'doc_type': 'upi_transaction',
                'confidence': 0.89,
                'stakeholder_relevance': ['product_lead', 'compliance_lead']
            }
        """
        # Method 1: Rule-based classification (FAST - uses keywords)
        rule_based_type = self._rule_based_classify(text, filename)
        
        # Method 2: ML-based classification (ACCURATE - uses AI)
        ml_based_type, confidence = self._ml_based_classify(text)
        
        # Smart decision: Use rules if strong match, otherwise use ML
        if rule_based_type and self._has_strong_pattern_match(text, rule_based_type):
            doc_type = rule_based_type
            final_confidence = 0.85
        else:
            doc_type = ml_based_type
            final_confidence = confidence
        
        # Map to stakeholders who care about this document
        relevant_stakeholders = self._map_to_stakeholders(doc_type)
        
        return {
            "doc_type": doc_type,
            "confidence": final_confidence,
            "stakeholder_relevance": relevant_stakeholders,
            "classification_method": "rule_based" if rule_based_type == doc_type else "ml_based"
        }
    
    def _rule_based_classify(self, text: str, filename: str) -> str:
        """
        Rule-based classification using keyword matching
        
        How it works:
        1. Count how many keywords from each category appear
        2. Category with most matches wins
        3. Boost score if filename also matches
        """
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        scores = {}
        for doc_type, keywords in self.patterns.items():
            # Count keyword matches
            score = sum(1 for keyword in keywords if keyword in text_lower)
            
            # Boost score if filename matches
            if any(keyword in filename_lower for keyword in keywords):
                score += 2
            
            scores[doc_type] = score
        
        if scores:
            best_match = max(scores, key=scores.get)
            if scores[best_match] > 0:
                return best_match
        
        return None
    
    def _ml_based_classify(self, text: str) -> tuple:
        """
        ML-based classification using zero-shot learning
        
        Zero-shot = Model wasn't trained on our specific categories
        But it can still classify because it understands language!
        
        Returns: (predicted_type, confidence_score)
        """
        # Only send first 1000 chars for speed
        text_sample = text[:1000]
        
        # Ask model: "Which of these categories does this text belong to?"
        result = self.classifier(
            text_sample,
            candidate_labels=self.labels,
            multi_label=False
        )
        
        return result['labels'][0], result['scores'][0]
    
    def _has_strong_pattern_match(self, text: str, doc_type: str) -> bool:
        """
        Check if text has strong pattern match for doc_type
        
        Strong = at least 3 keywords present
        """
        keywords = self.patterns.get(doc_type, [])
        text_lower = text.lower()
        matches = sum(1 for keyword in keywords if keyword in text_lower)
        return matches >= 3
    
    def _map_to_stakeholders(self, doc_type: str) -> List[str]:
        """
        Map document type to relevant stakeholders
        
        Example:
        - UPI transaction → Product Lead, Compliance Lead
        - API logs → Tech Lead, Bank Alliance Lead
        """
        relevant_stakeholders = []
        
        for role, config in STAKEHOLDER_CONFIG.items():
            if doc_type in config["doc_types"]:
                relevant_stakeholders.append(role)
        
        return relevant_stakeholders
    
    def extract_metadata(self, text: str, doc_type: str) -> Dict:
        """
        Extract additional metadata based on document type
        
        Different doc types have different important fields:
        - Transactions: transaction_id, amount, status
        - APIs: status_code, response_time
        - Compliance: risk_level, compliance_status
        - SLAs: uptime, sla_status
        """
        metadata = {}
        
        if doc_type == "upi_transaction":
            metadata.update(self._extract_transaction_metadata(text))
        elif doc_type == "bank_api_response":
            metadata.update(self._extract_api_metadata(text))
        elif doc_type == "compliance_report":
            metadata.update(self._extract_compliance_metadata(text))
        elif doc_type == "partnership_sla":
            metadata.update(self._extract_sla_metadata(text))
        
        return metadata
    
    def _extract_transaction_metadata(self, text: str) -> Dict:
        """Extract transaction-specific metadata using regex patterns"""
        metadata = {}
        
        # Find transaction ID (e.g., TXN20250115001234)
        txn_match = re.search(r'(?:TXN|TRANS|ID)[:\s]+([A-Z0-9]{8,})', text, re.IGNORECASE)
        if txn_match:
            metadata['transaction_id'] = txn_match.group(1)
        
        # Find amount (e.g., ₹1,250.00 or INR 1250)
        amount_match = re.search(r'(?:amount|₹|INR|RS)[:\s]*([0-9,]+(?:\.[0-9]{2})?)', text, re.IGNORECASE)
        if amount_match:
            metadata['amount'] = amount_match.group(1)
        
        # Find status
        if 'success' in text.lower():
            metadata['status'] = 'success'
        elif 'fail' in text.lower() or 'error' in text.lower():
            metadata['status'] = 'failed'
        
        return metadata
    
    def _extract_api_metadata(self, text: str) -> Dict:
        """Extract API-specific metadata"""
        metadata = {}
        
        # Status code (e.g., 200, 503)
        status_match = re.search(r'(?:status|code)[:\s]*([0-9]{3})', text, re.IGNORECASE)
        if status_match:
            metadata['status_code'] = status_match.group(1)
        
        # Response time (e.g., 450ms, 2 seconds)
        time_match = re.search(r'(?:response time|latency)[:\s]*([0-9]+)\s*(?:ms|seconds?)', text, re.IGNORECASE)
        if time_match:
            metadata['response_time'] = time_match.group(1)
        
        return metadata
    
    def _extract_compliance_metadata(self, text: str) -> Dict:
        """Extract compliance-specific metadata"""
        metadata = {}
        
        # Risk level
        if 'high risk' in text.lower():
            metadata['risk_level'] = 'high'
        elif 'medium risk' in text.lower():
            metadata['risk_level'] = 'medium'
        elif 'low risk' in text.lower():
            metadata['risk_level'] = 'low'
        
        # Compliance status
        if 'compliant' in text.lower() and 'non' not in text.lower():
            metadata['compliance_status'] = 'compliant'
        elif 'non-compliant' in text.lower() or 'violation' in text.lower():
            metadata['compliance_status'] = 'non-compliant'
        
        return metadata
    
    def _extract_sla_metadata(self, text: str) -> Dict:
        """Extract SLA-specific metadata"""
        metadata = {}
        
        # Uptime percentage (e.g., 99.7%)
        uptime_match = re.search(r'uptime[:\s]*([0-9]{2,3}\.[0-9]+)%', text, re.IGNORECASE)
        if uptime_match:
            metadata['uptime'] = float(uptime_match.group(1))
        
        # SLA status
        if 'met' in text.lower() and 'sla' in text.lower():
            metadata['sla_status'] = 'met'
        elif 'breach' in text.lower() or 'violation' in text.lower():
            metadata['sla_status'] = 'breached'
        
        return metadata


# Singleton instance - import this in other files
classifier = DocumentClassifier()
