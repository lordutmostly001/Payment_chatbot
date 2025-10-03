"""
Configuration management for Payment Chatbot system
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import List
import os


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Configuration
    API_TITLE: str = "Payment Document Chatbot API"
    API_VERSION: str = "1.0.0"
    API_PREFIX: str = "/api/v1"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # OpenAI - YOUR API KEY GOES IN .env FILE
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o"
    
    # Pinecone - YOUR API KEY GOES IN .env FILE
    PINECONE_API_KEY: str = Field(default="", env="PINECONE_API_KEY")
    PINECONE_INDEX_NAME: str = "payment-chatbot"
    PINECONE_DIMENSION: int = 384  # Matches embedding model dimension
    PINECONE_METRIC: str = "cosine"

    # Vector Search Settings
    TOP_K_RESULTS: int = 3
    SIMILARITY_THRESHOLD: float = 0.7
    PINECONE_CLOUD: str = "aws"
    PINECONE_REGION: str = "us-east-1"
    
    # Model Configuration
    EMBEDDING_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    CLASSIFIER_MODEL: str = "distilbert-base-uncased"
    NER_MODEL: str = "dslim/bert-base-NER"
    QA_MODEL: str = "deepset/roberta-base-squad2"
    
    # Document Processing
    CHUNK_SIZE: int = 500  # Characters per chunk
    CHUNK_OVERLAP: int = 50  # Overlap between chunks
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: List[str] = [".pdf", ".txt", ".csv", ".json"]
    
    # Retrieval Configuration
    
    # Stakeholder Roles
    STAKEHOLDER_ROLES: List[str] = [
        "product_lead",
        "tech_lead", 
        "compliance_lead",
        "bank_alliance_lead"
    ]
    
    # Document Types
    DOCUMENT_TYPES: List[str] = [
        "upi_transaction",
        "bank_api_response",
        "compliance_report",
        "partnership_sla"
    ]
    
    class Config:
        env_file = ".env"  # Load from .env file
        case_sensitive = True


# Stakeholder configuration - defines what each role cares about
STAKEHOLDER_CONFIG = {
    "product_lead": {
        "name": "Product Lead",
        "focus_areas": ["metrics", "trends", "user_behavior", "performance"],
        "doc_types": ["upi_transaction", "bank_api_response"],
        "keywords": ["success rate", "volume", "popular", "trends", "conversion"]
    },
    "tech_lead": {
        "name": "Tech Lead",
        "focus_areas": ["errors", "performance", "integration", "api"],
        "doc_types": ["bank_api_response", "upi_transaction"],
        "keywords": ["error", "failure", "api", "response time", "integration", "bug"]
    },
    "compliance_lead": {
        "name": "Compliance Lead",
        "focus_areas": ["regulatory", "risk", "audit", "kyc"],
        "doc_types": ["compliance_report", "upi_transaction"],
        "keywords": ["suspicious", "kyc", "audit", "regulatory", "compliance", "risk"]
    },
    "bank_alliance_lead": {
        "name": "Bank Alliance Lead",
        "focus_areas": ["sla", "partnership", "integration_health"],
        "doc_types": ["partnership_sla", "bank_api_response"],
        "keywords": ["sla", "partnership", "agreement", "integration health", "uptime"]
    }
}

# Document classification patterns - keywords that identify document types
DOCUMENT_PATTERNS = {
    "upi_transaction": [
        "upi", "transaction", "payment", "transfer", "vpa", "merchant",
        "customer", "amount", "success", "failed"
    ],
    "bank_api_response": [
        "api", "endpoint", "response", "status code", "latency", 
        "integration", "webhook", "callback"
    ],
    "compliance_report": [
        "compliance", "audit", "kyc", "aml", "regulatory", "risk",
        "suspicious activity", "report"
    ],
    "partnership_sla": [
        "sla", "service level", "agreement", "uptime", "partnership",
        "contract", "penalty", "availability"
    ]
}




# Global settings instance - import this in other files

settings = Settings()