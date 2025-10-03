"""
Enhanced Query Router Module with Stronger Role Differentiation
Routes user queries to appropriate stakeholder handlers
"""

import logging
from typing import Dict, List
from config import settings

logger = logging.getLogger(__name__)


class QueryRouter:
    """Routes queries to appropriate stakeholder with weighted scoring"""
    
    def __init__(self):
        # Weighted keywords - high weight = strong indicator
        self.stakeholder_keywords = {
            'product_lead': {
                'high': ['conversion', 'adoption', 'growth', 'metrics', 'kpi', 'trends', 'volume', 'retention'],
                'medium': ['transaction', 'users', 'customer', 'success rate', 'performance', 'analytics'],
                'low': ['popular', 'payment method', 'usage', 'behavior']
            },
            'tech_lead': {
                'high': ['api', 'error', 'endpoint', 'integration', 'latency', 'timeout', 'debug'],
                'medium': ['technical', 'system', 'server', 'response time', 'failure', 'architecture'],
                'low': ['code', 'logs', 'performance', 'implementation']
            },
            'compliance_lead': {
                'high': ['kyc', 'aml', 'compliance', 'regulatory', 'audit', 'fraud', 'risk'],
                'medium': ['suspicious', 'policy', 'legal', 'violation', 'requirement'],
                'low': ['report', 'mandatory', 'guidelines', 'verification']
            },
            'bank_alliance_lead': {
                'high': ['sla', 'partnership', 'agreement', 'contract', 'partner', 'uptime'],
                'medium': ['bank', 'relationship', 'service level', 'vendor', 'alliance'],
                'low': ['hdfc', 'icici', 'sbi', 'axis', 'integration health']
            }
        }
        
        # Weight values
        self.weights = {
            'high': 5,
            'medium': 2,
            'low': 1
        }
    
    def route_query(self, query: str, user_role: str = None) -> str:
        """
        Determine which stakeholder should handle the query using weighted scoring
        
        Args:
            query: User's question
            user_role: Optional explicit role selection
            
        Returns:
            Stakeholder role identifier
        """
        # If user explicitly selected a role, use it
        if user_role and user_role in self.stakeholder_keywords:
            logger.info(f"Using user-selected role: {user_role}")
            return user_role
        
        # Otherwise, analyze query content with weighted scoring
        query_lower = query.lower()
        scores = {role: 0 for role in self.stakeholder_keywords.keys()}
        
        for stakeholder, keyword_groups in self.stakeholder_keywords.items():
            for weight_level, keywords in keyword_groups.items():
                weight = self.weights[weight_level]
                for keyword in keywords:
                    if keyword.lower() in query_lower:
                        scores[stakeholder] += weight
                        logger.debug(f"Matched '{keyword}' for {stakeholder} (+{weight})")
        
        # Get stakeholder with highest score
        best_match = max(scores, key=scores.get)
        best_score = scores[best_match]
        
        # Log all scores for debugging
        logger.info(f"Role scores: {scores}")
        
        # If no clear match, default to product_lead
        if best_score == 0:
            logger.info("No specific stakeholder match, defaulting to product_lead")
            return 'product_lead'
        
        logger.info(f"Routed to {best_match} (score: {best_score})")
        return best_match
    
    def get_doc_type_priority(self, stakeholder: str) -> List[str]:
        """
        Get prioritized document types for each stakeholder
        
        Args:
            stakeholder: Stakeholder role
            
        Returns:
            List of document types in priority order
        """
        priorities = {
            'product_lead': [
                'upi_transaction',
                'bank_api_response'
            ],
            'tech_lead': [
                'bank_api_response',
                'upi_transaction'
            ],
            'compliance_lead': [
                'compliance_report',
                'upi_transaction'
            ],
            'bank_alliance_lead': [
                'partnership_sla',
                'bank_api_response'
            ]
        }
        
        return priorities.get(stakeholder, ['upi_transaction'])
    
    def get_stakeholder_context(self, stakeholder: str) -> Dict:
        """
        Get detailed context information for a stakeholder
        
        Args:
            stakeholder: Stakeholder role
            
        Returns:
            Context dictionary with strict boundaries
        """
        contexts = {
            'product_lead': {
                'focus': 'business metrics, user behavior, product performance',
                'concerns': 'transaction success rates, user adoption, growth trends',
                'tone': 'data-driven and business-focused',
                'avoid': 'technical API details, compliance regulations, infrastructure',
                'preferred_docs': ['upi_transaction']
            },
            'tech_lead': {
                'focus': 'technical implementation, system performance, API integrations',
                'concerns': 'API reliability, error handling, system architecture',
                'tone': 'technical and solution-oriented',
                'avoid': 'business metrics, compliance details, partnership agreements',
                'preferred_docs': ['bank_api_response']
            },
            'compliance_lead': {
                'focus': 'regulatory requirements, risk management, audit trails',
                'concerns': 'compliance violations, fraud detection, policy adherence',
                'tone': 'formal and risk-aware',
                'avoid': 'technical implementation, business growth, infrastructure',
                'preferred_docs': ['compliance_report']
            },
            'bank_alliance_lead': {
                'focus': 'partner relationships, SLA performance, contractual obligations',
                'concerns': 'partner health, service quality, relationship management',
                'tone': 'relationship-focused and diplomatic',
                'avoid': 'internal technical details, compliance procedures, product features',
                'preferred_docs': ['partnership_sla', 'bank_api_response']
            }
        }
        
        return contexts.get(stakeholder, contexts['product_lead'])


# Singleton instance
query_router = QueryRouter()