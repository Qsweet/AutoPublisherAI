"""
FastAPI Authentication Dependencies

This module provides reusable authentication dependencies for FastAPI endpoints.
"""

from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError

from .jwt_handler import get_jwt_handler, JWTHandler


# HTTP Bearer security scheme
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    """
    Dependency to get current authenticated user from JWT token.
    
    Usage:
        @app.get("/protected")
        async def protected_endpoint(user: dict = Depends(get_current_user)):
            return {"user_id": user["user_id"]}
    
    Args:
        credentials: HTTP Bearer credentials from request header
        
    Returns:
        Decoded user information from token
        
    Raises:
        HTTPException: If token is invalid or expired
    """
    token = credentials.credentials
    
    try:
        jwt_handler = get_jwt_handler()
        payload = jwt_handler.verify_token(token)
        
        # Check token type
        if payload.get("type") != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return payload
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_api_key_user(
    x_api_key: Optional[str] = Header(None)
) -> dict:
    """
    Dependency to authenticate using API key.
    
    Usage:
        @app.get("/api/endpoint")
        async def endpoint(user: dict = Depends(get_api_key_user)):
            return {"user_id": user["user_id"]}
    
    Args:
        x_api_key: API key from X-API-Key header
        
    Returns:
        Decoded user information from API key
        
    Raises:
        HTTPException: If API key is invalid
    """
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )
    
    try:
        jwt_handler = get_jwt_handler()
        payload = jwt_handler.verify_token(x_api_key)
        
        # Check token type
        if payload.get("type") != "api_key":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key",
                headers={"WWW-Authenticate": "ApiKey"},
            )
        
        return payload
        
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid API key: {str(e)}",
            headers={"WWW-Authenticate": "ApiKey"},
        )


async def get_current_user_optional(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    """
    Optional authentication dependency.
    
    Returns user if authenticated, None otherwise.
    Useful for endpoints that work with or without authentication.
    
    Usage:
        @app.get("/optional")
        async def optional_endpoint(user: Optional[dict] = Depends(get_current_user_optional)):
            if user:
                return {"message": f"Hello, {user['user_id']}"}
            return {"message": "Hello, guest"}
    
    Args:
        credentials: Optional HTTP Bearer credentials
        
    Returns:
        Decoded user information or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


def require_role(required_role: str):
    """
    Dependency factory to require specific user role.
    
    Usage:
        @app.get("/admin")
        async def admin_endpoint(user: dict = Depends(require_role("admin"))):
            return {"message": "Admin access granted"}
    
    Args:
        required_role: Role name required to access endpoint
        
    Returns:
        Dependency function that checks user role
    """
    async def role_checker(user: dict = Depends(get_current_user)) -> dict:
        user_role = user.get("role", "user")
        
        if user_role != required_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {required_role}"
            )
        
        return user
    
    return role_checker


def require_permission(required_permission: str):
    """
    Dependency factory to require specific permission.
    
    Usage:
        @app.post("/articles")
        async def create_article(user: dict = Depends(require_permission("create:articles"))):
            return {"message": "Article created"}
    
    Args:
        required_permission: Permission required to access endpoint
        
    Returns:
        Dependency function that checks user permission
    """
    async def permission_checker(user: dict = Depends(get_current_user)) -> dict:
        permissions = user.get("permissions", [])
        
        if required_permission not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required permission: {required_permission}"
            )
        
        return user
    
    return permission_checker

