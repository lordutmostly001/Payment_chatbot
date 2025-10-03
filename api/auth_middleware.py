"""
Authentication Middleware
Simple token-based authentication for API endpoints
"""

from fastapi import HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import logging
import os

logger = logging.getLogger(__name__)

security = HTTPBearer()


class AuthMiddleware:
    """Simple token-based authentication"""
    
    def __init__(self, secret_token: str = None, bypass_auth: bool = False):
        self.secret_token = secret_token or "demo-token-change-in-production"
        # Enable bypass mode for development
        self.bypass_auth = bypass_auth or os.getenv("BYPASS_AUTH", "false").lower() == "true"
        
        if self.bypass_auth:
            logger.warning("⚠️  AUTH BYPASS ENABLED - FOR DEVELOPMENT ONLY!")
    
    def verify_token(self, credentials: HTTPAuthorizationCredentials) -> dict:
        """Verify bearer token"""
        # Development bypass
        if self.bypass_auth:
            logger.info("Auth bypassed (development mode)")
            return {"authenticated": True, "role": "admin", "username": "dev_user"}
        
        # Production token verification
        if credentials.credentials != self.secret_token:
            logger.warning(f"Invalid token attempt: {credentials.credentials[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        logger.info("Token verified successfully")
        return {"authenticated": True, "role": "user", "username": "authenticated_user"}


# Initialize with bypass enabled for development
# Change bypass_auth=False for production
auth_middleware = AuthMiddleware(bypass_auth=True)  # ← Set to True for testing


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> dict:
    """Dependency for protected routes"""
    return auth_middleware.verify_token(credentials)