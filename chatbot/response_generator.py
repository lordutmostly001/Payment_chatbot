"""
Response Generator using Ollama with Strong Role Differentiation
"""

import logging
import requests
from typing import Dict, List

logger = logging.getLogger(__name__)

# Strong role-specific system prompts
ROLE_PROMPTS = {
    "product_lead": """You are an experienced Product Lead at a payments company. Provide natural, conversational answers focusing on business metrics, user behavior, conversion rates, and product strategy.

Answer directly without stating your role. Focus on: success rates, transaction volumes, user adoption, growth trends, and customer experience.""",

    "tech_lead": """You are an experienced Technical Lead at a payments company. Provide natural, conversational answers focusing on APIs, system architecture, and technical implementation.

Answer directly without stating your role. Focus on: API integration, error handling, performance optimization, debugging, and technical solutions.""",

    "compliance_lead": """You are an experienced Compliance Lead at a payments company. Provide natural, conversational answers focusing on regulations, risk management, and audit requirements.

Answer directly without stating your role. Focus on: regulatory compliance, data privacy, audit trails, risk assessment, and legal requirements.""",

    "bank_alliance_lead": """You are an experienced Bank Alliance Lead at a payments company. Provide natural, conversational answers focusing on partnerships, SLAs, and relationship management.

Answer directly without stating your role. Focus on: SLA metrics, partner performance, integration reliability, and collaboration."""
}


class ResponseGenerator:
    """Generates role-specific responses using Ollama"""

    def __init__(self):
        self.ollama_url = "http://localhost:11434/api/generate"
        self.model = "llama3.2:3b"

    def generate_response(
        self,
        query: str,
        context_docs: List[Dict],
        stakeholder: str
    ) -> Dict:
        """Generate role-specific response using Ollama"""
        try:
            # Get role-specific system prompt
            system_prompt = ROLE_PROMPTS.get(stakeholder, ROLE_PROMPTS["product_lead"])

            # Build context
            context_text = self._build_context(context_docs)

            # Create role-based prompt
            full_prompt = f"""{system_prompt}

Context from documents:
{context_text}

Question: {query}

Provide a clear, natural answer based on the context. Be conversational and helpful."""

            # Call Ollama API
            logger.info(f"Generating {stakeholder} response with Ollama...")
            logger.info(f"Connecting to: {self.ollama_url}")
            logger.info(f"Using model: {self.model}")
            
            response = requests.post(
                self.ollama_url,
                json={
                    "model": self.model,
                    "prompt": full_prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.7,
                        "top_p": 0.9
                    }
                },
                timeout=60
            )

            logger.info(f"Ollama response status: {response.status_code}")
            
            if response.status_code == 200:
                answer = response.json()["response"]

                # Light post-processing
                answer = self._clean_response(answer)

                confidence = self._calculate_confidence(context_docs)

                logger.info(f"Response generated for {stakeholder}")
                return {
                    'success': True,
                    'answer': answer,
                    'stakeholder': stakeholder,
                    'confidence': confidence,
                    'sources': self._format_sources(context_docs),
                    'context_used': len(context_docs)
                }
            else:
                logger.error(f"Ollama error: {response.status_code}")
                logger.error(f"Response body: {response.text}")
                return self._mock_response(query, context_docs, stakeholder)

        except requests.exceptions.ConnectionError:
            logger.error("Cannot connect to Ollama. Make sure Ollama is running (ollama serve)")
            return self._mock_response(query, context_docs, stakeholder)
        except requests.exceptions.Timeout:
            logger.error("Ollama request timed out")
            return self._mock_response(query, context_docs, stakeholder)
        except Exception as e:
            logger.error(f"Error with Ollama: {str(e)}")
            return self._mock_response(query, context_docs, stakeholder)

    def _clean_response(self, answer: str) -> str:
        """Clean up the response"""
        # Remove any robotic self-references that might slip through
        phrases_to_remove = [
            "As a Product Lead, ",
            "As a Technical Lead, ",
            "As a Compliance Lead, ",
            "As a Bank Alliance Lead, ",
            "From a product perspective, ",
            "From a technical standpoint, ",
            "From a compliance perspective, ",
            "From a partnership perspective, "
        ]

        for phrase in phrases_to_remove:
            if answer.startswith(phrase):
                answer = answer[len(phrase):]

        return answer.strip()

    def _build_context(self, docs: List[Dict]) -> str:
        """Build context from documents"""
        if not docs:
            return "No relevant documents found."
        
        parts = []
        for i, doc in enumerate(docs, 1):
            parts.append(f"[Document {i}]")
            parts.append(f"Type: {doc.get('doc_type', 'Unknown')}")
            parts.append(f"Content: {doc.get('text', '')[:400]}")
            parts.append("")
        return "\n".join(parts)

    def _calculate_confidence(self, docs: List[Dict]) -> float:
        """Calculate confidence from doc scores"""
        if not docs:
            return 0.0
        scores = [doc.get('score', 0.0) for doc in docs]
        avg_score = sum(scores) / len(scores) if scores else 0.0
        return min(avg_score * 100, 100.0)

    def _format_sources(self, docs: List[Dict]) -> List[Dict]:
        """Format source info"""
        return [{
            'source': doc.get('source', 'Unknown'),
            'doc_type': doc.get('doc_type', 'Unknown'),
            'relevance_score': doc.get('score', 0.0),
            'preview': doc.get('text', '')[:200]
        } for doc in docs]

    def _mock_response(self, query: str, docs: List[Dict], stakeholder: str) -> Dict:
        """Fallback mock response if Ollama unavailable"""
        
        # FIXED: Check if docs exist BEFORE accessing
        if docs and len(docs) > 0:
            preview = docs[0].get('text', '')[:300]
            answer = f"Based on the available documentation:\n\n{preview}...\n\n[Note: LLM service temporarily unavailable. Please ensure Ollama is running with 'ollama serve']"
        else:
            answer = "I don't have enough context to answer this question. Please try rephrasing or provide more details.\n\n[Note: LLM service temporarily unavailable. Please ensure Ollama is running with 'ollama serve']"

        return {
            'success': True,
            'answer': answer,
            'stakeholder': stakeholder,
            'confidence': 60.0 if docs else 30.0,
            'sources': self._format_sources(docs),
            'context_used': len(docs)
        }


response_generator = ResponseGenerator()