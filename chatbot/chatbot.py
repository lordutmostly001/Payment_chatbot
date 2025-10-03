"""
Enhanced Main Chatbot Module with Strong Role Differentiation
Orchestrates the complete chatbot pipeline with strict role boundaries
"""

import logging
from typing import Dict, Optional
from vector_db.knowledge_base import knowledge_base
from .query_router import query_router
from .stakeholder_handler import stakeholder_handler
from .response_generator import response_generator

logger = logging.getLogger(__name__)


class PaymentChatbot:
    """Main chatbot with enhanced role-specific processing"""
    
    def __init__(self):
        self.knowledge_base = knowledge_base
        self.query_router = query_router
        self.stakeholder_handler = stakeholder_handler
        self.response_generator = response_generator
    
    def chat(
        self,
        query: str,
        user_role: Optional[str] = None,
        top_k: int = 3
    ) -> Dict:
        """
        Complete chatbot pipeline with strong role differentiation
        
        Args:
            query: User's question
            user_role: Optional explicit role selection
            top_k: Number of documents to retrieve
            
        Returns:
            Response dictionary with role-specific answer
        """
        try:
            logger.info(f"Processing query: {query[:100]}...")
            
            # Step 1: Route to appropriate stakeholder with weighted scoring
            stakeholder = self.query_router.route_query(query, user_role)
            logger.info(f"Routed to stakeholder: {stakeholder}")
            
            # Get stakeholder context for logging
            context = self.query_router.get_stakeholder_context(stakeholder)
            logger.info(f"Stakeholder focus: {context['focus']}")
            logger.info(f"Avoiding topics: {context['avoid']}")
            
            # Step 2: Retrieve relevant documents with role-based filtering
            doc_priorities = self.query_router.get_doc_type_priority(stakeholder)
            logger.info(f"Document priorities for {stakeholder}: {doc_priorities}")
            
            context_docs = self.knowledge_base.query(
                question=query,
                stakeholder=stakeholder,
                top_k=top_k
            )
            logger.info(f"Retrieved {len(context_docs)} documents")
            
            # Step 3: Filter and prioritize sources by role
            filtered_docs = self.stakeholder_handler.filter_sources_by_role(
                context_docs,
                stakeholder
            )
            logger.info(f"Filtered to {len(filtered_docs)} role-relevant documents")
            
            # Step 4: Enhance query with role-specific context
            enhanced_query = self.stakeholder_handler.enhance_query(query, stakeholder)
            
            # Step 5: Generate strongly role-specific response
            response = self.response_generator.generate_response(
                query=enhanced_query,
                context_docs=filtered_docs,
                stakeholder=stakeholder
            )
            
            # Step 6: Validate role adherence
            if response.get('success'):
                is_valid = self.stakeholder_handler.validate_response_relevance(
                    response['answer'],
                    stakeholder
                )
                response['role_adherence'] = is_valid
                
                if not is_valid:
                    logger.warning(f"Response may not strictly adhere to {stakeholder} boundaries")
            
            # Step 7: Format final response
            formatted_response = self.stakeholder_handler.format_response(
                response['answer'],
                response.get('sources', []),
                stakeholder
            )
            
            # Merge responses
            final_response = {
                'success': response.get('success', True),
                'answer': formatted_response['answer'],
                'stakeholder': stakeholder,
                'confidence': response.get('confidence', 0.0),
                'sources': formatted_response['sources'],
                'context_used': response.get('context_used', len(filtered_docs)),
                'role_adherence': formatted_response.get('role_adherence', True),
                'stakeholder_context': {
                    'focus': context['focus'],
                    'concerns': context['concerns'],
                    'avoided_topics': context['avoid']
                }
            }
            
            logger.info(f"Response generated - Confidence: {final_response['confidence']:.1f}%, Role adherence: {final_response['role_adherence']}")
            return final_response
            
        except Exception as e:
            logger.error(f"Error in chatbot pipeline: {str(e)}", exc_info=True)
            return {
                'success': False,
                'error': str(e),
                'answer': "I encountered an error processing your question. Please try rephrasing or contact support.",
                'stakeholder': user_role or 'product_lead',
                'confidence': 0.0,
                'sources': [],
                'context_used': 0
            }
    
    def get_available_roles(self) -> Dict:
        """Get information about available stakeholder roles"""
        roles = {}
        for role in ['product_lead', 'tech_lead', 'compliance_lead', 'bank_alliance_lead']:
            context = self.query_router.get_stakeholder_context(role)
            roles[role] = {
                'display_name': role.replace('_', ' ').title(),
                'focus': context['focus'],
                'concerns': context['concerns'],
                'tone': context['tone'],
                'document_priority': self.query_router.get_doc_type_priority(role)
            }
        return roles


# Singleton instance
chatbot = PaymentChatbot()