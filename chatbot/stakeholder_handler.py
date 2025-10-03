"""
Enhanced Stakeholder Handler Module with Strict Role Boundaries
Provides stakeholder-specific query handling with strong differentiation
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


class StakeholderHandler:
    """Handles stakeholder-specific query processing with strict role enforcement"""
    
    def __init__(self):
        # Strict role-specific system prompts with clear boundaries
        self.stakeholder_prompts = {
            'product_lead': """You are a Product Lead for a payment processing platform.

YOUR EXCLUSIVE FOCUS:
- Business metrics: conversion rates, transaction volumes, success rates
- User behavior: adoption patterns, customer preferences, usage trends
- Product performance: feature effectiveness, user satisfaction
- Growth strategy: market opportunities, product expansion

STRICTLY FORBIDDEN TOPICS (never discuss):
- Technical API details, error codes, or system architecture
- Compliance regulations, KYC/AML procedures, or audit requirements
- Partnership SLAs, contract terms, or vendor relationships
- Infrastructure, servers, or low-level implementation

RESPONSE STYLE:
- Lead with metrics and data points
- Use business terminology (ROI, conversion, retention, etc.)
- Focus on customer impact and revenue implications
- Provide actionable product recommendations

Remember: You are NOT a technical expert, compliance officer, or partnership manager. Stay in your lane.""",
            
            'tech_lead': """You are a Technical Lead for a payment processing platform.

YOUR EXCLUSIVE FOCUS:
- API integrations: endpoints, error codes, response formats
- System architecture: design patterns, scalability, performance
- Technical issues: debugging, error handling, latency optimization
- Implementation details: code-level solutions, technical stack

STRICTLY FORBIDDEN TOPICS (never discuss):
- Business metrics, conversion rates, or revenue discussions
- Compliance regulations, KYC/AML, or legal requirements
- Partnership agreements, SLAs, or vendor management
- High-level product strategy or marketing

RESPONSE STYLE:
- Include specific error codes and technical terms
- Suggest concrete implementation solutions
- Reference APIs, endpoints, and technical specifications
- Provide debugging steps and technical recommendations

Remember: You are NOT a product manager, compliance officer, or business analyst. Think like an engineer.""",
            
            'compliance_lead': """You are a Compliance Lead for a payment processing platform.

YOUR EXCLUSIVE FOCUS:
- Regulatory requirements: KYC, AML, GDPR, PCI-DSS
- Risk management: fraud detection, suspicious activity monitoring
- Audit compliance: documentation, reporting, evidence trails
- Legal obligations: policy enforcement, regulatory updates

STRICTLY FORBIDDEN TOPICS (never discuss):
- Technical implementation, API integrations, or code details
- Business growth metrics, conversion rates, or product features
- Partnership contracts or vendor relationships (unless compliance-related)
- System architecture or infrastructure

RESPONSE STYLE:
- Reference specific regulations and frameworks
- Emphasize risk mitigation and compliance requirements
- Use formal, precise language
- Highlight audit trails and documentation needs

Remember: You are NOT a developer, product manager, or partnership lead. Focus on legal and regulatory aspects.""",
            
            'bank_alliance_lead': """You are a Bank Alliance Lead for a payment processing platform.

YOUR EXCLUSIVE FOCUS:
- SLA performance: uptime, response times, service quality
- Partnership health: relationship status, communication effectiveness
- Contract terms: agreements, penalties, obligations
- Integration reliability: partner system availability, coordination

STRICTLY FORBIDDEN TOPICS (never discuss):
- Internal technical implementation or code-level details
- Internal business metrics or product features
- Compliance procedures or regulatory requirements (unless SLA-related)
- Customer-facing product functionality

RESPONSE STYLE:
- Reference specific SLA metrics and contractual terms
- Emphasize relationship management and collaboration
- Use diplomatic, partnership-focused language
- Highlight partner performance and coordination needs

Remember: You are NOT an internal technical lead or product manager. Focus on external partnerships and agreements."""
        }
        
        # Role-specific filtering terms
        self.role_filters = {
            'product_lead': {
                'required_terms': ['user', 'customer', 'transaction', 'rate', 'adoption', 'metric'],
                'forbidden_terms': ['API', 'endpoint', 'HTTP', 'status code', 'KYC', 'AML', 'SLA']
            },
            'tech_lead': {
                'required_terms': ['API', 'error', 'system', 'integration', 'technical', 'performance'],
                'forbidden_terms': ['conversion rate', 'user adoption', 'KYC', 'AML', 'SLA', 'contract']
            },
            'compliance_lead': {
                'required_terms': ['compliance', 'regulatory', 'KYC', 'AML', 'audit', 'risk'],
                'forbidden_terms': ['API', 'endpoint', 'code', 'conversion', 'SLA', 'partnership']
            },
            'bank_alliance_lead': {
                'required_terms': ['SLA', 'partnership', 'bank', 'partner', 'agreement', 'uptime'],
                'forbidden_terms': ['API error', 'code', 'conversion', 'KYC', 'AML', 'compliance']
            }
        }
    
    def get_system_prompt(self, stakeholder: str) -> str:
        """Get the strict system prompt for a stakeholder"""
        return self.stakeholder_prompts.get(
            stakeholder,
            self.stakeholder_prompts['product_lead']
        )
    
    def enhance_query(self, query: str, stakeholder: str) -> str:
        """
        Enhance query with strong stakeholder-specific context
        
        Args:
            query: Original user query
            stakeholder: Stakeholder role
            
        Returns:
            Enhanced query string with role enforcement
        """
        enhancements = {
            'product_lead': "As a Product Lead focused on business metrics and user behavior: ",
            'tech_lead': "As a Technical Lead focused on APIs and system implementation: ",
            'compliance_lead': "As a Compliance Lead focused on regulations and risk management: ",
            'bank_alliance_lead': "As a Bank Alliance Lead focused on partnerships and SLAs: "
        }
        
        prefix = enhancements.get(stakeholder, "")
        suffix = f"\n\nAnswer ONLY from the {stakeholder.replace('_', ' ').title()}'s perspective. Ignore information outside your domain."
        
        return f"{prefix}{query}{suffix}"
    
    def validate_response_relevance(self, response: str, stakeholder: str) -> bool:
        """
        Check if response adheres to role boundaries
        
        Args:
            response: Generated response text
            stakeholder: Stakeholder role
            
        Returns:
            True if response is relevant to the role
        """
        filters = self.role_filters.get(stakeholder, {})
        response_lower = response.lower()
        
        # Check for forbidden terms
        forbidden = filters.get('forbidden_terms', [])
        violations = [term for term in forbidden if term.lower() in response_lower]
        
        if violations:
            logger.warning(f"Response contains forbidden terms for {stakeholder}: {violations}")
            return False
        
        # Check for at least some required terms
        required = filters.get('required_terms', [])
        matches = [term for term in required if term.lower() in response_lower]
        
        if len(matches) < 2:  # At least 2 required terms should appear
            logger.warning(f"Response lacks required terminology for {stakeholder}")
            return False
        
        return True
    
    def format_response(
        self,
        response: str,
        sources: List[Dict],
        stakeholder: str
    ) -> Dict:
        """
        Format response with stakeholder-specific context and validation
        
        Args:
            response: Generated response text
            sources: Source documents used
            stakeholder: Stakeholder role
            
        Returns:
            Formatted response dictionary
        """
        # Validate response relevance
        is_relevant = self.validate_response_relevance(response, stakeholder)
        
        if not is_relevant:
            logger.warning(f"Response may not align with {stakeholder} role boundaries")
        
        return {
            'answer': response,
            'stakeholder': stakeholder,
            'sources': sources,
            'source_count': len(sources),
            'role_adherence': is_relevant
        }
    
    def filter_sources_by_role(self, sources: List[Dict], stakeholder: str) -> List[Dict]:
        """
        Filter and prioritize sources based on stakeholder role
        
        Args:
            sources: List of source documents
            stakeholder: Stakeholder role
            
        Returns:
            Filtered and prioritized sources
        """
        # Document type priorities per role
        doc_priorities = {
            'product_lead': ['upi_transaction', 'bank_api_response'],
            'tech_lead': ['bank_api_response', 'upi_transaction'],
            'compliance_lead': ['compliance_report', 'upi_transaction'],
            'bank_alliance_lead': ['partnership_sla', 'bank_api_response']
        }
        
        priorities = doc_priorities.get(stakeholder, [])
        
        # Sort sources by role relevance
        def get_priority(source):
            doc_type = source.get('doc_type', '')
            try:
                return priorities.index(doc_type)
            except ValueError:
                return len(priorities)  # Low priority for unmatched types
        
        return sorted(sources, key=get_priority)


# Singleton instance
stakeholder_handler = StakeholderHandler()