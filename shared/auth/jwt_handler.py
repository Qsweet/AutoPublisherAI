"""
JWT Authentication Handler

This module provides JWT token generation and validation for API authentication.
Uses industry-standard practices for secure token management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import jwt
from jwt.exceptions import InvalidTokenError
import os


class JWTHandler:
    """
    Handles JWT token creation and validation.
    
    This class implements secure JWT authentication following OWASP guidelines.
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        algorithm: str = "HS256",
        access_token_expire_minutes: int = 30
    ):
        """
        Initialize JWT handler.
        
        Args:
            secret_key: Secret key for signing tokens (from environment)
            algorithm: JWT signing algorithm (default: HS256)
            access_token_expire_minutes: Token expiration time in minutes
        """
        self.secret_key = secret_key or os.getenv("JWT_SECRET_KEY")
        if not self.secret_key or self.secret_key == "CHANGE_THIS_TO_RANDOM_SECRET_KEY_IN_PRODUCTION":
            raise ValueError(
                "JWT_SECRET_KEY must be set in environment variables. "
                "Generate one with: openssl rand -hex 32"
            )
        
        self.algorithm = algorithm
        self.access_token_expire_minutes = access_token_expire_minutes
    
    def create_access_token(
        self,
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a new JWT access token.
        
        Args:
            data: Dictionary of claims to encode in the token
            expires_delta: Optional custom expiration time
            
        Returns:
            Encoded JWT token string
        """
        to_encode = data.copy()
        
        # Set expiration time
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        
        # Add standard claims
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access"
        })
        
        # Encode token
        encoded_jwt = jwt.encode(
            to_encode,
            self.secret_key,
            algorithm=self.algorithm
        )
        
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token string to verify
            
        Returns:
            Decoded token payload
            
        Raises:
            InvalidTokenError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except InvalidTokenError as e:
            raise InvalidTokenError(f"Token validation failed: {str(e)}")
    
    def create_api_key(self, user_id: str, api_key_name: str) -> str:
        """
        Create a long-lived API key for programmatic access.
        
        Args:
            user_id: User identifier
            api_key_name: Name/description of the API key
            
        Returns:
            Encoded API key token
        """
        data = {
            "user_id": user_id,
            "api_key_name": api_key_name,
            "type": "api_key"
        }
        
        # API keys expire after 1 year
        expires_delta = timedelta(days=365)
        
        return self.create_access_token(data, expires_delta)


# Global JWT handler instance
jwt_handler = None


def get_jwt_handler() -> JWTHandler:
    """
    Get or create global JWT handler instance.
    
    Returns:
        JWTHandler instance
    """
    global jwt_handler
    if jwt_handler is None:
        jwt_handler = JWTHandler()
    return jwt_handler

